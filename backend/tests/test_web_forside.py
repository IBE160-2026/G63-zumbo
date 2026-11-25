"""Tester for forsiden med viruskort og resultatsiden på `/resultat` (story 3.8).

FR-26, FR-27, AD-9, NFR-3. FHI mockes med `respx`, og cachen ligger i
`tmp_path`. Ingen test når nettet, FHI eller Claude (AD-10).
"""

import copy
import html as html_modul
import json
import re
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from backend import mellomlager, tjeneste, web
from backend.config import Innstillinger
from backend.domene import Dataserie, Uke, Utvalg
from backend.tjeneste import Resultat

FIXTURES = Path(__file__).parent / "fixtures"
URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/{}/{}"
TABELLER = {
    "influensa": (724, "fhi/724-influensa-2025-2026-alle-nonstl.json"),
    "rsv": (729, "fhi/729-rsv-2025-2026-alle-nonstl.json"),
    "sars-cov-2": (731, "fhi/731-sars-cov-2-2025-2026-alle-nonstl.json"),
}
SESONG = "2025/2026"
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
HENTET = datetime(2026, 11, 20, 13, 5, tzinfo=UTC)
FHI_KODER = (
    "NONSTL",
    "A+B",
    "pos_rate",
    "dateusedforstatistics",
    "Non-Sentinel",
    "RS-virus (A+B)",
)
INTRO = (
    "Se hvordan influensa, RSV og koronavirus utvikler seg uke for uke i Norge, "
    "med tall fra Folkehelseinstituttet. Appen sier fra når tallene er for usikre "
    "til å trekke konklusjoner, og forklarer ordene underveis."
)
CHATBOT_TITTEL = "Hvorfor ikke bare spørre en chatbot?"
INGEN_TALL = "Tallene kan ikke vises akkurat nå."
TILBAKE = '<a href="/">← Til forsiden</a>'


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


def _uten_ny_sesong(tabell: int) -> dict[str, Any]:
    """Dimensjonslisten uten ukene i 2026/2027, så sesongen som pågår er
    2025/2026, den samme som datafixturene."""
    svar = copy.deepcopy(_svar(f"fhi/{tabell}-dimensjoner.json"))
    for dimensjon in svar["dimensions"]:
        if dimensjon["code"] == "dateusedforstatistics":
            dimensjon["categories"] = [
                k for k in dimensjon["categories"] if k["value"] < "2026-w40"
            ]
    return svar


@pytest.fixture
def fhi_mock() -> Iterator[respx.MockRouter]:
    with respx.mock(assert_all_called=False) as router:
        for virus, (tabell, data) in TABELLER.items():
            router.get(URL.format(tabell, "dimension"), name=f"{virus}-dim").respond(
                json=_uten_ny_sesong(tabell)
            )
            router.post(URL.format(tabell, "data"), name=virus).respond(
                json=_svar(data)
            )
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


def _kort(html: str) -> list[tuple[str, str]]:
    """`(href, tekst)` for hvert kort, i rekkefølge."""
    treff = re.findall(r'<a class="kort" href="([^"]*)">(.*?)</a>', html, re.DOTALL)
    return [
        (
            html_modul.unescape(href),
            re.sub(r"[ \t\n]+", " ", re.sub(r"<[^>]+>", " ", t)),
        )
        for href, t in treff
    ]


def _forside_med(
    klient: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    lag: Callable[[Utvalg], Resultat],
) -> list[tuple[str, str]]:
    """Kortene på forsiden når `tjeneste.svar` gir `lag(utvalg)`."""
    monkeypatch.setattr(tjeneste.Tjeneste, "svar", lambda _, utvalg, __: lag(utvalg))
    svar = klient.get("/")
    assert svar.status_code == 200
    return _kort(svar.text)


def _fhi_nede(router: respx.MockRouter) -> None:
    for route in router.routes:
        route.mock(side_effect=httpx.ConnectError("nede"))


# --- Forsiden med tall (FR-27) ---


def test_forsiden_har_overskrift_intro_og_tre_kort(klient: TestClient) -> None:
    svar = klient.get("/")
    assert svar.status_code == 200
    html = svar.text
    assert "<h1>Tall fra FHI om luftveisvirus</h1>" in html
    assert f'<p class="intro">{INTRO}</p>' in html
    assert len(_kort(html)) == 3
    # Ingen skjema og ingen KI-forklaring på forsiden.
    assert "<form" not in html
    assert 'id="forklaring"' not in html


def test_kortene_står_i_rekkefølge_med_lenke_til_sesongen_som_pågår(
    klient: TestClient,
) -> None:
    html = klient.get("/").text
    kort = _kort(html)
    # Kortet sier «Koronavirus», resten av appen «SARS-CoV-2».
    assert re.findall(r'<h2 class="kortnavn">(.*?)</h2>', html) == [
        "Influensa",
        "RSV",
        "Koronavirus (SARS-CoV-2)",
    ]
    for (href, _), virus in zip(kort, TABELLER, strict=True):
        del_ = urlsplit(href)
        assert del_.path == "/resultat"
        assert parse_qs(del_.query) == {
            "mal": ["1"],
            "virus": [virus],
            "sesong": [SESONG],
            "alder": ["alle"],
        }


@pytest.mark.parametrize("virus", list(TABELLER))
def test_kortet_viser_andelen_i_siste_uke_med_andel(
    klient: TestClient, fhi_mock: respx.MockRouter, virus: str
) -> None:
    html = klient.get("/").text
    (tekst,) = [t for h, t in _kort(html) if f"virus={virus}&" in h]
    resultat = klient.app.state.tjeneste.svar(Utvalg(1, virus, SESONG), NÅ)
    siste = web.siste_uke_med_andel(resultat.serie)
    assert siste is not None
    assert web.andel(siste.andel) in tekst
    assert re.search(r"\d+,\d\xa0%", tekst)
    assert f"uke {siste.ukenummer}" in tekst
    assert INGEN_TALL not in tekst
    assert "Sist lagrede" not in tekst
    # Kortet og resultatsiden bruker samme mellomlager.
    assert fhi_mock.routes[virus].call_count == 1


def test_forsiden_og_resultatsiden_deler_mellomlageret(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    klient.get("/")
    klient.get(f"/resultat?mal=1&virus=rsv&sesong={SESONG}&alder=alle")
    klient.get("/")
    for virus in TABELLER:
        assert fhi_mock.routes[virus].call_count == 1


def test_forsiden_er_uten_fhi_koder(klient: TestClient) -> None:
    html = klient.get("/").text
    assert '<html lang="nb">' in html
    for kode in FHI_KODER:
        assert kode not in html


def test_chatbotteksten_står_på_forsiden_og_ikke_på_resultatsiden(
    klient: TestClient,
) -> None:
    forside = klient.get("/").text
    assert f'<h2 id="chatbottittel">{CHATBOT_TITTEL}</h2>' in forside
    assert forside.index('<ul class="viruskort">') < forside.index(CHATBOT_TITTEL)
    assert "Dette er ikke en tjeneste fra FHI." in forside
    resultat = klient.get(f"/resultat?mal=1&virus=influensa&sesong={SESONG}").text
    assert CHATBOT_TITTEL not in resultat


def test_resultatsiden_har_lenken_tilbake(klient: TestClient) -> None:
    html = klient.get(f"/resultat?mal=1&virus=influensa&sesong={SESONG}").text
    assert TILBAKE in html
    assert html.index(TILBAKE) < html.index("<h1>Influensa</h1>")


def test_kortlenken_åpner_resultatsiden(klient: TestClient) -> None:
    href, _ = _kort(klient.get("/").text)[1]
    html = klient.get(href).text
    assert "<h1>RSV</h1>" in html
    assert "<table" in html


# --- Siste uke er usikker, FHI nede, ingen tall ---


def _serie(*uker: Uke) -> Dataserie:
    return Dataserie(Utvalg(1, "influensa", SESONG), uker)


def test_siste_uke_med_andel_hopper_over_uker_uten_andel() -> None:
    serie = _serie(Uke(2025, 40, 100, 10), Uke(2025, 41, 0, 0), Uke(2025, 42, None, 3))
    assert web.siste_uke_med_andel(serie) == serie.uker[0]
    assert web.siste_uke_med_andel(_serie(Uke(2025, 40, 0, 0))) is None
    assert web.siste_uke_med_andel(None) is None


def test_kortet_sier_fra_om_usikker_uke() -> None:
    utvalg = Utvalg(1, "influensa", SESONG)
    serie = _serie(Uke(2025, 49, 1000, 208), Uke(2025, 50, 20, 4))
    kort = web.viruskort(utvalg, Resultat(utvalg, serie))
    assert kort.andel == "20,0\xa0%"
    assert kort.uke == "uke 50"
    assert kort.usikker


def test_forsiden_sier_fra_om_usikker_uke_i_tekst(
    klient: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def lag(utvalg: Utvalg) -> Resultat:
        uker = (Uke(2025, 49, 1000, 208), Uke(2025, 50, 20, 4))
        return Resultat(utvalg, Dataserie(utvalg, uker))

    for _, tekst in _forside_med(klient, monkeypatch, lag):
        assert "20,0\xa0% Andel positive tester i uke 50, usikker uke" in tekst


def test_kortet_med_sikker_uke_sier_ikke_usikker() -> None:
    utvalg = Utvalg(1, "influensa", SESONG)
    serie = _serie(Uke(2025, 50, 1000, 208))
    kort = web.viruskort(utvalg, Resultat(utvalg, serie))
    assert (kort.andel, kort.uke, kort.usikker) == ("20,8\xa0%", "uke 50", False)


def test_fhi_nede_med_lagrede_tall_viser_dem_med_dato(
    klient: TestClient, fhi_mock: respx.MockRouter, mappe: Path
) -> None:
    for virus, (_, data) in TABELLER.items():
        mellomlager.lagre_svar(mappe, Utvalg(1, virus, SESONG), _svar(data), HENTET)
    # Sesonglisten er lagret, men gammel, så den må hentes på nytt.
    mellomlager.lagre_dimensjoner(mappe, 724, _uten_ny_sesong(724), HENTET)
    _fhi_nede(fhi_mock)
    svar = klient.get("/")
    assert svar.status_code == 200
    kort = _kort(svar.text)
    assert len(kort) == 3
    for href, tekst in kort:
        assert f"sesong={SESONG}" in href.replace("%2F", "/")
        assert re.search(r"\d+,\d\xa0%", tekst)
        assert "Sist lagrede tall, hentet 20.11.2026 kl. 14:05." in tekst


def test_fhi_nede_uten_lagrede_tall_gir_tekst_og_lenke(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    _fhi_nede(fhi_mock)
    svar = klient.get("/")
    assert svar.status_code == 200
    kort = _kort(svar.text)
    assert len(kort) == 3
    for href, tekst in kort:
        assert INGEN_TALL in tekst
        assert "%" not in tekst
        assert urlsplit(href).path == "/resultat"
        # Uten sesongliste er sesongen som pågår regnet fra datoen.
        assert parse_qs(urlsplit(href).query)["sesong"] == ["2026/2027"]


def test_fhi_nede_gir_ett_kall_på_forsiden(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    # Uten lagrede tall: pausen i `tjeneste` stopper kallene etter det første.
    _fhi_nede(fhi_mock)
    assert klient.get("/").status_code == 200
    assert sum(route.call_count for route in fhi_mock.routes) == 1


def test_feil_når_kortet_lages_gir_tekst_og_ikke_500(
    klient: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    ekte = web.viruskort

    def viruskort(utvalg: Utvalg, resultat: Resultat | None) -> web.Viruskort:
        if utvalg.virus == "rsv" and resultat is not None:
            raise ValueError("formateringen feilet")
        return ekte(utvalg, resultat)

    monkeypatch.setattr(web, "viruskort", viruskort)
    svar = klient.get("/")
    assert svar.status_code == 200
    kort = _kort(svar.text)
    assert INGEN_TALL in kort[1][1]
    assert "virus=rsv" in kort[1][0]
    assert INGEN_TALL not in kort[0][1]
    assert "Kortet for rsv kunne ikke lages" in caplog.text


def test_kort_uten_uke_med_andel_gir_tekst() -> None:
    utvalg = Utvalg(1, "influensa", SESONG)
    for resultat in (
        None,
        Resultat(utvalg, melding=tjeneste.FHI_NEDE_INGEN_TALL),
        Resultat(utvalg, _serie(Uke(2025, 40, 0, 0), Uke(2025, 41, None, 2))),
    ):
        kort = web.viruskort(utvalg, resultat)
        assert (kort.andel, kort.uke, kort.hentet) == (None, None, None)
        assert kort.adresse.startswith("/resultat?")


def test_forsiden_uten_uke_med_andel_gir_tekst_og_lenke(
    klient: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def lag(utvalg: Utvalg) -> Resultat:
        uker = (Uke(2025, 40, 0, 0), Uke(2025, 41, None, 2))
        return Resultat(utvalg, Dataserie(utvalg, uker))

    kort = _forside_med(klient, monkeypatch, lag)
    assert len(kort) == 3
    for href, tekst in kort:
        assert INGEN_TALL in tekst
        assert "%" not in tekst
        assert urlsplit(href).path == "/resultat"


def test_uventet_feil_i_ett_kort_gir_tekst_og_ikke_500(
    klient: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    ekte = tjeneste.Tjeneste.svar

    def svar(self: tjeneste.Tjeneste, utvalg: Utvalg, nå: datetime) -> Resultat:
        if utvalg.virus == "rsv":
            raise RuntimeError("uventet")
        return ekte(self, utvalg, nå)

    monkeypatch.setattr(tjeneste.Tjeneste, "svar", svar)
    svar_ = klient.get("/")
    assert svar_.status_code == 200
    kort = _kort(svar_.text)
    assert INGEN_TALL in kort[1][1]
    assert INGEN_TALL not in kort[0][1]
    assert INGEN_TALL not in kort[2][1]
    assert "Kortet for rsv kunne ikke lages" in caplog.text


def test_forsiden_kaller_ikke_ki(
    klient: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def stopp(*_: Any, **__: Any) -> None:
        raise AssertionError("forsiden skal ikke hente KI-forklaringer")

    monkeypatch.setattr(tjeneste.Tjeneste, "forklaring", stopp)
    assert klient.get("/").status_code == 200


# --- Adressene (AD-9) ---


@pytest.mark.parametrize(
    "query",
    [
        "mal=1&virus=rsv&sesong=2025/2026&alder=alle",
        "mal=1&virus=rsv&sesong=2025%2F2026&alder=alle&nyeste_feilet=1795000000",
        "virus=ebola",
        "nyeste_feilet=1",
    ],
)
def test_gamle_adresser_sendes_videre_med_301(
    klient: TestClient, fhi_mock: respx.MockRouter, query: str
) -> None:
    svar = klient.get("/?" + query, follow_redirects=False)
    assert svar.status_code == 301
    assert svar.headers["location"] == "/resultat?" + query
    assert not any(route.called for route in fhi_mock.routes)


@pytest.mark.parametrize("query", ["", "?mal=&virus=&sesong=&alder=", "?alder=%20"])
def test_forside_uten_valg_sendes_ikke_videre(klient: TestClient, query: str) -> None:
    svar = klient.get("/" + query, follow_redirects=False)
    assert svar.status_code == 200
    assert len(_kort(svar.text)) == 3


def test_ugyldig_valg_gir_melding_og_lenke_uten_henting(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    html = klient.get(f"/resultat?mal=1&virus=ebola&sesong={SESONG}").text
    assert "Velg et virus: Influensa, RSV eller SARS-CoV-2." in html
    assert TILBAKE in html
    assert "<form" not in html
    assert not any(fhi_mock.routes[v].called for v in TABELLER)


def test_hent_nyeste_sender_til_resultatsiden(klient: TestClient) -> None:
    svar = klient.post(
        "/hent-nyeste",
        data={"mal": "1", "virus": "rsv", "sesong": SESONG, "alder": "alle"},
        follow_redirects=False,
    )
    assert svar.status_code == 303
    del_ = urlsplit(svar.headers["location"])
    assert del_.path == "/resultat"
    assert parse_qs(del_.query)["virus"] == ["rsv"]
