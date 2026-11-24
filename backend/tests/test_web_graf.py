"""Tester for grafen på siden (story 3.3, FR-9, FR-10, NFR-6, NFR-7, AD-8).

FHI mockes med `respx`, cachen ligger i `tmp_path`, og klokka er fast. Ingen
test når nettet eller laster `.env`. Selve tegningen i nettleseren testes
ikke her. Testene sjekker dataene og HTML-en `app.js` bruker.
"""

import json
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from typing import Any

import pytest
import respx
from fastapi.testclient import TestClient

from backend import mellomlager, web
from backend.config import Innstillinger
from backend.domene import Dataserie, Uke, Utvalg, kildehenvisning
from backend.tjeneste import Resultat

FIXTURES = Path(__file__).parent / "fixtures"
STATIC = Path(web.__file__).parent / "static"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
HENTET = datetime(2026, 11, 24, 10, 5, tzinfo=UTC)
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
STI = "/?mal=1&virus=influensa&sesong=2025/2026&alder=alle"
CHART_JS = (
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.6.1/dist/chart.umd.min.js" '
    'integrity="sha384-Emf5ZVIUiarAdhkgtqK+5/Z5qIvM6QoVrS+qAVtfyZVuD5lIHrac0me485+Antp0" '
    'crossorigin="anonymous" defer></script>'
)


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DIMENSJONER = _svar("fhi/724-dimensjoner.json")
DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
R2 = _svar("konstruert/724-r2-4-av-20-uker.json")
R3 = _svar("konstruert/724-r3-3-av-10-uker.json")


@pytest.fixture
def fhi_mock() -> Iterator[respx.MockRouter]:
    with respx.mock(assert_all_called=False) as router:
        router.get(DIMENSJON_URL, name="dimensjoner").respond(json=DIMENSJONER)
        router.post(DATA_URL, name="data").respond(json=DATA)
        yield router


@pytest.fixture
def mappe(tmp_path: Path) -> Path:
    return tmp_path / "cache"


@pytest.fixture
def klient(mappe: Path, fhi_mock: respx.MockRouter) -> Iterator[TestClient]:
    innstillinger = Innstillinger(None, "modell", mappe)
    app = web.lag_app(lambda: innstillinger, klokke=lambda: NÅ)
    with TestClient(app) as testklient:
        yield testklient


def _side(klient: TestClient, mappe: Path, svar: dict[str, Any]) -> str:
    mellomlager.lagre_svar(mappe, UTVALG, svar, HENTET)
    return klient.get(STI).text


def _grafdata(html: str) -> dict[str, Any]:
    blokk = re.search(
        r'<script type="application/json" id="grafdata">(.*?)</script>',
        html,
        re.DOTALL,
    )
    assert blokk, "fant ikke JSON-blokken"
    return json.loads(blokk[1])


def _tabell(html: str) -> list[list[str]]:
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    assert tbody, "fant ingen tabell"
    rader = []
    for rad in re.findall(r"<tr>(.*?)</tr>", tbody[1], re.DOTALL):
        celler = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", rad, re.DOTALL)
        rader.append([re.sub(r"<[^>]+>", "", c).strip() for c in celler])
    return rader


def _som_tabell(andel: float) -> str:
    """Andelen i JSON skrevet slik tabellen viser den."""
    return f"{andel:.1f}".replace(".", ",") + " %"


# --- JSON-blokken har samme tall som tabellen (FR-9, AD-8) ---


@pytest.mark.parametrize("svar", [DATA, R2, R3], ids=["ekte", "r2", "r3"])
def test_jsonblokken_har_samme_tall_som_tabellen(
    klient: TestClient, mappe: Path, svar: dict[str, Any]
) -> None:
    html = _side(klient, mappe, svar)
    graf = _grafdata(html)
    tabell = _tabell(html)
    assert len(graf["uker"]) == len(graf["andel"]) == len(graf["usikker"])
    assert len(graf["uker"]) == len(tabell)
    rader = zip(graf["uker"], graf["andel"], graf["andel_tekst"], tabell, strict=True)
    for uke, andel, andel_tekst, rad in rader:
        assert re.match(rf"{uke}(\D|$)", rad[0])
        assert andel_tekst == rad[3]
        if andel is not None:
            assert _som_tabell(andel) == rad[3]


def test_jsonblokken_med_ekte_tall(klient: TestClient, mappe: Path) -> None:
    graf = _grafdata(_side(klient, mappe, DATA))
    assert graf["uker"][:3] == ["uke 40", "uke 41", "uke 42"]
    assert graf["andel"][:3] == [0.9, 1.6, 2.0]
    assert graf["andel_tekst"][:3] == ["0,9\u00a0%", "1,6\u00a0%", "2,0\u00a0%"]


def test_akseteksten_står_i_malen(klient: TestClient, mappe: Path) -> None:
    html = _side(klient, mappe, DATA)
    assert 'data-tekst-x="Uke"' in html
    assert 'data-tekst-y="Andel positive (%)"' in html
    assert 'data-tekst-usikker="usikker uke"' in html


def test_manglende_uker_er_null(klient: TestClient, mappe: Path) -> None:
    graf = _grafdata(_side(klient, mappe, R3))
    manglende = [
        u for u, a in zip(graf["uker"], graf["andel"], strict=True) if a is None
    ]
    assert manglende == ["uke 42", "uke 45", "uke 47"]
    assert 0 not in graf["andel"]


# --- Usikre uker (FR-10, NFR-7) ---


def test_usikre_uker_er_markert_også_flere_positive_enn_tester(
    klient: TestClient, mappe: Path
) -> None:
    graf = _grafdata(_side(klient, mappe, R2))
    usikre = [u for u, us in zip(graf["uker"], graf["usikker"], strict=True) if us]
    # 29, 20, 10 og 0 tester, skjult antall tester (uke 51) og 45 positive av
    # 40 tester (uke 1) er usikre. 30 tester (uke 49) er ikke usikker.
    assert usikre == ["uke 41", "uke 43", "uke 45", "uke 47", "uke 51", "uke 1"]
    i = graf["uker"].index("uke 1")
    assert graf["andel"][i] == 112.5


def test_grafen_har_forklaring_av_markeringen(klient: TestClient, mappe: Path) -> None:
    html = _side(klient, mappe, R2)
    forklaring = re.search(r'<p class="grafforklaring">(.*?)</p>', html, re.DOTALL)
    assert forklaring
    tekst = re.sub(r"<[^>]+>", "", forklaring[1])
    assert "● Sikker uke" in tekst
    assert "○ Usikker uke: færre enn 30 tester eller flere positive" in tekst
    assert "Uker uten andel (skjult antall tester eller 0 tester) gir brudd" in tekst


def test_forklaringen_vises_også_uten_usikre_uker(
    klient: TestClient, mappe: Path
) -> None:
    # Irenes beslutning 24.11.2026: forklaringen av fylt og åpen sirkel vises
    # alltid. De ekte tallene for 2025/2026 har ingen usikre uker.
    html = _side(klient, mappe, DATA)
    assert not any(_grafdata(html)["usikker"])
    forklaring = re.search(r'<p class="grafforklaring">(.*?)</p>', html, re.DOTALL)
    assert forklaring
    assert "○ Usikker uke" in re.sub(r"<[^>]+>", "", forklaring[1])


def test_app_js_gir_usikre_uker_åpen_sirkel() -> None:
    kode = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "graf.usikker.map((u) => (u ? bakgrunn : linje))" in kode
    assert "spanGaps: false" in kode
    assert 'pointStyle: "circle"' in kode
    # Fargene app.js leser, finnes i style.css.
    css = (STATIC / "style.css").read_text(encoding="utf-8")
    for navn in re.findall(r'farge\("(--[a-z-]+)"\)', kode):
        assert f"{navn}:" in css
    # Nøklene app.js leser, finnes i grafdata.
    data = web.grafdata(Dataserie(UTVALG, (Uke(2025, 40, 10, 1),)))
    for nøkkel in re.findall(r"graf\.([a-z_]+)", kode):
        assert nøkkel in data


# --- Tittel og alternativtekst (FR-9, NFR-6) ---


def test_grafen_har_tittel_med_utvalget(klient: TestClient, mappe: Path) -> None:
    html = _side(klient, mappe, DATA)
    assert (
        '<h2 id="graftittel">Influensa, sesongen 2025/2026, alle aldersgrupper</h2>'
        in html
    )


def test_alternativtekst_med_utvalg_og_hovedtrekk(
    klient: TestClient, mappe: Path
) -> None:
    html = _side(klient, mappe, DATA)
    lerret = re.search(r'<canvas id="graf" role="img" aria-label="([^"]*)"', html)
    assert lerret
    tekst = unescape(lerret[1])
    assert tekst.startswith(
        "Linjegraf over andel positive tester uke for uke. "
        "Influensa, sesongen 2025/2026, alle aldersgrupper."
    )
    assert "Grafen viser uke 40 til uke 20." in tekst
    assert "Andelen var høyest i uke 51 med 28,8 %." in tekst
    assert "den siste uka med tall" in tekst
    # Samme tekst står i lerretet og i reserveteksten, som vises når grafen
    # ikke kan tegnes (uten JavaScript eller Chart.js).
    assert f">{lerret[1]}</canvas>" in html
    assert f'<p class="grafreserve">{lerret[1]}</p>' in html
    assert '<div class="grafboks" hidden>' in html


def test_alternativtekst_nevner_usikre_uker() -> None:
    serie = Dataserie(UTVALG, (Uke(2025, 40, 100, 10), Uke(2025, 41, 20, 1)))
    tekst = web.alternativtekst(serie)
    assert "Andelen var høyest i uke 40 med 10,0 %." in tekst
    assert "I uke 41, den siste uka med tall, var den 5,0 %." in tekst
    assert "1 uke er usikker og markert med åpen sirkel." in tekst


def test_alternativtekst_teller_bare_tegnede_sirkler_og_brudd() -> None:
    serie = Dataserie(
        UTVALG,
        (
            Uke(2025, 40, 100, 10),
            Uke(2025, 41, 20, 1),
            Uke(2025, 42, 25, 2),
            Uke(2025, 43, None, 3),
            Uke(2025, 44, 0, 2),
        ),
    )
    tekst = web.alternativtekst(serie)
    assert "2 uker er usikre og markert med åpen sirkel." in tekst
    assert "2 uker har ingen andel og gir brudd i linjen." in tekst


def test_alternativtekst_når_siste_uke_er_høyest() -> None:
    serie = Dataserie(UTVALG, (Uke(2025, 40, 100, 1), Uke(2025, 41, 100, 9)))
    tekst = web.alternativtekst(serie)
    assert "Andelen var høyest i uke 41 med 9,0\u00a0%." in tekst
    assert "den siste uka med tall" not in tekst
    assert "usikker" not in tekst
    assert "brudd" not in tekst


def test_ingen_graf_uten_andeler(klient: TestClient) -> None:
    serie = Dataserie(UTVALG, (Uke(2025, 40, None, None), Uke(2025, 41, 0, 0)))
    resultat = Resultat(UTVALG, serie, kilde=kildehenvisning(724, HENTET))
    klient.app.state.tjeneste.svar = lambda utvalg, nå: resultat
    html = klient.get(STI).text
    assert "<table>" in html
    assert 'id="graf"' not in html
    # Chart.js og grafdata lastes ikke. app.js lastes alltid, for den åpner
    # begrepsforklaringene (story 3.6).
    assert "chart.umd" not in html
    assert 'id="grafdata"' not in html


def test_alternativtekst_uten_andeler() -> None:
    serie = Dataserie(UTVALG, (Uke(2025, 40, None, None),))
    assert web.alternativtekst(serie).endswith("Ingen uker har en andel som kan vises.")


# --- Skriptene (AD-8) ---


def test_chart_js_fra_jsdelivr_med_fast_versjon_og_integrity(
    klient: TestClient, mappe: Path
) -> None:
    html = _side(klient, mappe, DATA)
    assert CHART_JS in html
    assert '<script src="http://testserver/static/app.js" defer></script>' in html


def test_bare_egen_javascript_i_app_js(klient: TestClient, mappe: Path) -> None:
    html = _side(klient, mappe, DATA)
    skript = re.findall(r"<script([^>]*)>(.*?)</script>", html, re.DOTALL)
    for attributter, innhold in skript:
        if 'type="application/json"' in attributter:
            continue
        assert innhold == "", "JavaScript skal bare ligge i static/app.js"
        assert "chart.js@4.6.1" in attributter or "/static/app.js" in attributter
    assert len(skript) == 3


def test_bare_app_js_uten_tall(klient: TestClient) -> None:
    skript = re.findall(r'<script src="([^"]+)"', klient.get("/").text)
    assert len(skript) == 1
    assert skript[0].endswith("/static/app.js")


def test_app_js_serveres(klient: TestClient) -> None:
    svar = klient.get("/static/app.js")
    assert svar.status_code == 200
    assert "new Chart(" in svar.text


def test_jsonblokken_er_trygg_inne_i_script() -> None:
    utvalg = Utvalg(1, "influensa", "2025/2026", "alle")
    data = web.grafdata(Dataserie(utvalg, (Uke(2025, 40, 10, 1),)))
    tekst = web.maler.env.from_string("{{ d|tojson }}").render(d=data)
    assert "</" not in tekst
    assert json.loads(tekst) == data
