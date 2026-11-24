"""Tester for tabellen, kildehenvisningen og FR-8 på siden (story 3.2).

FR-8, FR-10–FR-12, AD-5, AD-8. FHI mockes med `respx`, cachen ligger i
`tmp_path`, og klokka er fast. Ingen test når nettet eller laster `.env`.
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

from backend import mellomlager, tjeneste, web
from backend.config import Innstillinger
from backend.domene import Uke, Utvalg

FIXTURES = Path(__file__).parent / "fixtures"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
HENTET = datetime(2026, 11, 24, 10, 5, tzinfo=UTC)  # kl. 11:05 norsk tid
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
STI = "/?mal=1&virus=influensa&sesong=2025/2026&alder=alle"
NB = " "
FOTNOTE_FLERE_POSITIVE = (
    "Flere positive prøver enn tester denne uka. Det kan skyldes hvordan prøvene "
    "er registrert. Tolk tallet med forsiktighet."
)


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DIMENSJONER = _svar("fhi/724-dimensjoner.json")
DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
R2 = _svar("konstruert/724-r2-4-av-20-uker.json")


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


def _rader(html: str) -> list[list[str]]:
    """Teksten i cellene i hver rad i tabellen, uten tagger."""
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    assert tbody, "fant ingen tabell"
    rader = []
    for rad in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody[1], re.DOTALL):
        celler = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", rad, re.DOTALL)
        rader.append([re.sub(r"<[^>]+>", "", c).strip() for c in celler])
    return rader


def _rad(html: str, ukenummer: int) -> list[str]:
    for rad in _rader(html):
        if re.match(rf"uke {ukenummer}(\D|$)", rad[0]):
            return rad
    raise AssertionError(f"fant ikke uke {ukenummer}")


# --- Filtrene (arkitektur §4) ---


@pytest.mark.parametrize(
    ("verdi", "tekst"),
    [(0, "0"), (999, "999"), (1210, f"1{NB}210"), (1234567, f"1{NB}234{NB}567")],
)
def test_tall_har_mellomrom_som_tusenskille(verdi: int, tekst: str) -> None:
    assert web.tall(verdi) == tekst


def test_skjult_tall_vises_som_skjult_ikke_0() -> None:
    assert web.tall(None) == "skjult"


@pytest.mark.parametrize(
    ("verdi", "tekst"),
    [
        (20.8, f"20,8{NB}%"),
        (20.84, f"20,8{NB}%"),
        (20.85, f"20,9{NB}%"),
        (0.0, f"0,0{NB}%"),
        (5.0, f"5,0{NB}%"),
        (112.5, f"112,5{NB}%"),
        (28.54484555266096, f"28,5{NB}%"),
    ],
)
def test_andel_med_en_desimal_og_komma(verdi: float, tekst: str) -> None:
    assert web.andel(verdi) == tekst


def test_andel_som_mangler_vises_som_mangler() -> None:
    assert web.andel(None) == "mangler"


def test_uke_vises_som_uke_og_nummer() -> None:
    assert web.uke(Uke(2025, 50, 10, 1)) == "uke 50"
    assert web.uke(Uke(2026, 1, 10, 1)) == "uke 1"


@pytest.mark.parametrize(
    ("tid", "tekst"),
    [
        (datetime(2026, 11, 20, 13, 5, tzinfo=UTC), "20.11.2026 kl. 14:05"),
        (datetime(2026, 7, 1, 22, 30, tzinfo=UTC), "02.07.2026 kl. 00:30"),
    ],
)
def test_tidspunkt_i_norsk_tid(tid: datetime, tekst: str) -> None:
    assert web.tidspunkt(tid) == tekst


# --- Tabellen (FR-11) ---


def test_tabellen_har_kolonnene_og_en_rad_per_uke(
    klient: TestClient, mappe: Path
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, HENTET)
    html = klient.get(STI).text
    overskrifter = re.findall(r'<th scope="col">(.*?)</th>', html)
    assert overskrifter == ["Uke", "Tester", "Positive prøver", "Andel positive"]
    rader = _rader(html)
    assert len(rader) == 33
    assert rader[0] == ["uke 40", f"7{NB}023", "64", f"0,9{NB}%"]
    assert _rad(html, 50) == ["uke 50", f"10{NB}748", f"3{NB}068", f"28,5{NB}%"]


def test_lagrede_tall_vises_uten_kall_til_fhi(
    klient: TestClient, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, HENTET)
    klient.get(STI)
    assert not fhi_mock.routes["data"].called


def test_skjulte_verdier_vises_som_skjult_og_mangler(
    klient: TestClient, mappe: Path
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, R2, HENTET)
    html = klient.get(STI).text
    rad = _rad(html, 51)
    assert rad[1:] == ["skjult", "5", "mangler"]
    assert rad[0].startswith("uke 51*")


def test_uke_med_0_tester_har_ingen_andel(klient: TestClient, mappe: Path) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, R2, HENTET)
    assert _rad(klient.get(STI).text, 47)[1:] == ["0", "0", "mangler"]


# --- Usikre uker (FR-10) ---


def test_usikre_uker_har_tegn_og_fotnote(klient: TestClient, mappe: Path) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, R2, HENTET)
    html = klient.get(STI).text
    assert _rad(html, 41)[0] == "uke 41* (usikker uke)"
    assert _rad(html, 40)[0] == "uke 40"
    assert _rad(html, 49)[0] == "uke 49"  # 30 tester er ikke usikker
    assert "* Usikker uke: færre enn 30 tester" in html


def test_flere_positive_enn_tester_har_egen_fotnote(
    klient: TestClient, mappe: Path
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, R2, HENTET)
    html = klient.get(STI).text
    rad = _rad(html, 1)
    assert rad == [
        "uke 1* (usikker uke)† (flere positive prøver enn tester)",
        "40",
        "45",
        f"112,5{NB}%",
    ]
    assert f"† {FOTNOTE_FLERE_POSITIVE}" in html


def test_ingen_fotnoter_uten_usikre_uker(klient: TestClient, mappe: Path) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, HENTET)
    html = klient.get(STI).text
    assert "Usikker uke:" not in html
    assert FOTNOTE_FLERE_POSITIVE not in html


# --- Kildehenvisning (FR-12) ---


def test_kildehenvisning_under_tabellen(klient: TestClient, mappe: Path) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, HENTET)
    html = klient.get(STI).text
    kilde = (
        "Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, "
        "Folkehelseinstituttet (FHI). Tabell 724 «RESPIaggr Influensa antall og "
        "andel». Hentet 24.11.2026 kl. 11:05."
    )
    assert kilde in html
    assert html.index("</table>") < html.index(kilde)


def test_nye_tall_har_hentetidspunktet_nå(klient: TestClient) -> None:
    html = klient.get(STI).text
    assert "Hentet 24.11.2026 kl. 13:00." in html


# --- FHI nede (FR-8) ---


def _fhi_nede(router: respx.MockRouter) -> None:
    for navn in ("dimensjoner", "data"):
        router.routes[navn].mock(side_effect=httpx.ConnectError("nede"))


def test_fhi_nede_med_lagrede_tall_viser_dem_med_dato(
    klient: TestClient, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    gammel = datetime(2026, 11, 20, 13, 5, tzinfo=UTC)
    mellomlager.lagre_svar(mappe, UTVALG, DATA, gammel)
    mellomlager.lagre_dimensjoner(mappe, 724, DIMENSJONER, gammel)
    _fhi_nede(fhi_mock)
    html = klient.get(STI).text
    assert tjeneste.FHI_NEDE_LAGRET in html
    assert "Sist lagrede tall, hentet 20.11.2026 kl. 14:05." in html
    assert len(_rader(html)) == 33
    assert "Hentet 20.11.2026 kl. 14:05." in html


def test_fhi_nede_uten_lagrede_tall_gir_ingen_tabell(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    _fhi_nede(fhi_mock)
    html = klient.get(STI).text
    assert tjeneste.FHI_NEDE_INGEN_TALL in html
    assert "Prøv igjen senere." in html
    assert "<table" not in html
    assert "Sist lagrede tall" not in html
    assert "Kilde:" not in html


# --- Uten JavaScript (AD-8) ---


def test_tabellen_står_i_html_uten_javascript(klient: TestClient, mappe: Path) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, HENTET)
    html = klient.get(STI).text
    assert "<table>" in html
    assert "<script" not in html
