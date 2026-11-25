"""Tester for varselet om tynt datagrunnlag på siden (story 3.4, FR-19, NFR-7).

FHI mockes med `respx`, cachen ligger i `tmp_path`, og klokka er fast. Ingen
test når nettet eller laster `.env`. Setningene i varselet kommer fra de ekte
kontrollreglene, ikke fra testen.
"""

import json
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from backend import kontrollregler, mellomlager, web
from backend.config import Innstillinger
from backend.domene import Dataserie, Uke, Utvalg, kildehenvisning
from backend.tjeneste import Resultat

FIXTURES = Path(__file__).parent / "fixtures"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
HENTET = datetime(2026, 11, 24, 10, 5, tzinfo=UTC)
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
UTVALG_2024 = Utvalg(1, "influensa", "2024/2025", "alle")
STI = "/resultat?mal=1&virus=influensa&sesong=2025/2026&alder=alle"
STI_2024 = "/resultat?mal=1&virus=influensa&sesong=2024/2025&alder=alle"
TEKST_R5 = (
    "Perioden går over 1. mars 2025. Fra den datoen er alle norske laboratorier "
    "med i tallene, så tall før og etter kan ikke sammenlignes direkte."
)


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DIMENSJONER = _svar("fhi/724-dimensjoner.json")
DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
R1 = _svar("konstruert/724-r1-19-positive.json")
R5 = _svar("konstruert/724-r5-2024-2025.json")


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


def _varsel(html: str) -> str | None:
    """HTML-en i varselet, eller `None` når siden ikke har varsel."""
    treff = re.search(r'<section class="varsel"(.*?)</section>', html, re.DOTALL)
    return treff[1] if treff else None


def _punkter(varsel: str) -> list[str]:
    return [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p)).strip()
        for p in re.findall(r"<li>(.*?)</li>", varsel, re.DOTALL)
    ]


def _r1_og_r5() -> Resultat:
    """Ti uker i 2024/2025 over 1. mars 2025, med 10 positive i alt.

    R1 (færre enn 20 positive) og R5 (perioden går over 1. mars 2025) slår inn.
    Reglene regnes ut med `kontrollregler.vurder`, slik `tjeneste` gjør.
    """
    uker = tuple(Uke(2025, n, 1000, 1) for n in range(5, 15))
    serie = Dataserie(UTVALG_2024, uker)
    utslag = tuple(kontrollregler.vurder(serie))
    return Resultat(UTVALG_2024, serie, utslag, kildehenvisning(724, HENTET))


# --- Med regelutslag (FR-19) ---


def test_varsel_med_r1_og_r5_samtidig(klient: TestClient) -> None:
    resultat = _r1_og_r5()
    assert [u.regel for u in resultat.regelutslag] == ["R1", "R5"]
    klient.app.state.tjeneste.svar = lambda utvalg, nå: resultat
    varsel = _varsel(klient.get(STI_2024).text)
    assert varsel is not None
    assert _punkter(varsel) == [u.tekst for u in resultat.regelutslag]
    assert _punkter(varsel)[1] == TEKST_R5
    assert "Det trengs minst 20" in _punkter(varsel)[0]


def test_varsel_har_ikon_og_overskrift(klient: TestClient) -> None:
    resultat = _r1_og_r5()
    klient.app.state.tjeneste.svar = lambda utvalg, nå: resultat
    varsel = _varsel(klient.get(STI_2024).text)
    assert varsel is not None
    assert 'aria-labelledby="varseltittel"' in varsel
    overskrift = re.search(r'<h2 id="varseltittel">(.*?)</h2>', varsel, re.DOTALL)
    assert overskrift
    # U+FE0E ber om ⚠ som tekst, ikke som fargeemoji.
    ikon = '<span class="varselikon" aria-hidden="true">⚠\ufe0e</span>'
    assert ikon in overskrift[1]
    tekst = re.sub(r"<[^>]+>", "", overskrift[1]).strip()
    assert tekst == "⚠\ufe0e For tynt datagrunnlag"
    assert "Tallene bør tolkes med forsiktighet fordi:" in varsel


def test_varselet_står_over_grafen_og_tabellen(klient: TestClient) -> None:
    resultat = _r1_og_r5()
    klient.app.state.tjeneste.svar = lambda utvalg, nå: resultat
    html = klient.get(STI_2024).text
    skjema = html.index('<form method="get"')
    varsel = html.index('<section class="varsel"')
    assert skjema < varsel < html.index('<figure class="graf"')
    assert varsel < html.index('<section class="tall"')


def test_varsel_med_ekte_regel_r5_fra_lagrede_tall(
    klient: TestClient, mappe: Path
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG_2024, R5, HENTET)
    varsel = _varsel(klient.get(STI_2024).text)
    assert varsel is not None
    assert _punkter(varsel) == [TEKST_R5]


def test_varsel_med_ekte_regel_r1_fra_lagrede_tall(
    klient: TestClient, mappe: Path
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, R1, HENTET)
    varsel = _varsel(klient.get(STI).text)
    assert varsel is not None
    punkter = _punkter(varsel)
    assert punkter == [
        (
            "Utvalget har bare 19 kjente positive prøver. "
            "Det trengs minst 20 for et sikkert tall."
        )
    ]


def test_varsel_også_med_sist_lagrede_tall(
    klient: TestClient, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    gammel = datetime(2026, 11, 20, 13, 5, tzinfo=UTC)
    mellomlager.lagre_svar(mappe, UTVALG_2024, R5, gammel)
    fhi_mock.routes["data"].side_effect = httpx.ConnectError("nede")
    html = klient.get(STI_2024).text
    assert "Sist lagrede tall" in html
    # Meldingen om lagrede tall står over varselet, og varselet over grafen.
    melding = html.index('<div class="melding"')
    assert melding < html.index('<section class="varsel"') < html.index("<figure")
    varsel = _varsel(html)
    assert varsel is not None
    assert _punkter(varsel) == [TEKST_R5]


def test_varselet_lenker_til_forklaringen_av_tynt_datagrunnlag(
    klient: TestClient,
) -> None:
    """Lenken peker på `<details>` med forklaringen av «For tynt datagrunnlag»
    (story 3.6, FR-19). `app.js` åpner den når lenken følges."""
    resultat = _r1_og_r5()
    klient.app.state.tjeneste.svar = lambda utvalg, nå: resultat
    html = klient.get(STI_2024).text
    varsel = _varsel(html)
    assert varsel is not None
    lenker = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]*)</a>', varsel)
    assert lenker == [("begrep-tynt-datagrunnlag", "Hva betyr dette?")]
    mål = re.search(
        r'<details id="begrep-tynt-datagrunnlag">\s*<summary>(.*?)</summary>',
        html,
    )
    assert mål and mål[1] == "For tynt datagrunnlag"
    assert html.count('id="begrep-tynt-datagrunnlag"') == 1
    # Skriptet som åpner forklaringen, lastes også her.
    assert "/static/app.js" in html


# --- Uten regelutslag (FR-19) ---


def test_ingen_varsel_uten_regelutslag(klient: TestClient, mappe: Path) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, HENTET)
    html = klient.get(STI).text
    assert "<tbody>" in html
    assert _varsel(html) is None
    # Bare begrepsforklaringen nederst nevner «For tynt datagrunnlag».
    før_begrepene = html.split('<section class="begreper"')[0]
    assert "For tynt datagrunnlag" not in før_begrepene


def test_ingen_varsel_uten_utvalg(klient: TestClient) -> None:
    assert (
        _varsel(
            klient.get("/resultat?mal=1&virus=ebola&sesong=2025/2026&alder=alle").text
        )
        is None
    )


def test_ingen_varsel_ved_ugyldig_utvalg(klient: TestClient) -> None:
    assert _varsel(klient.get("/resultat?alder=ukjent").text) is None


def test_ingen_varsel_når_det_ikke_finnes_tall(klient: TestClient) -> None:
    # Resultat uten serie, men med utslag: varselet hører til tallene og vises
    # ikke alene.
    resultat = Resultat(
        UTVALG, regelutslag=_r1_og_r5().regelutslag, melding="FHI svarer ikke."
    )
    klient.app.state.tjeneste.svar = lambda utvalg, nå: resultat
    assert _varsel(klient.get(STI).text) is None
