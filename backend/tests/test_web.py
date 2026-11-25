"""Tester for nettsiden med FastAPIs testklient (story 3.1, FR-1–FR-5, AD-6, AD-9).

FHI mockes med `respx`, og cachen ligger i `tmp_path`. Ingen test når nettet
eller laster `.env`.
"""

import inspect
import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from backend import config, tjeneste, web
from backend.config import Innstillinger
from backend.domene import ALDERSGRUPPER, MALER

FIXTURES = Path(__file__).parent / "fixtures"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DIMENSJONER = _svar("fhi/724-dimensjoner.json")
DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
FHI_KODER = ("NONSTL", "A+B", "pos_rate", "dateusedforstatistics", "Non-Sentinel")


@pytest.fixture
def fhi_mock() -> Iterator[respx.MockRouter]:
    with respx.mock(assert_all_called=False) as router:
        router.get(DIMENSJON_URL, name="dimensjoner").respond(json=DIMENSJONER)
        router.post(DATA_URL, name="data").respond(json=DATA)
        yield router


@pytest.fixture
def innstillinger(tmp_path: Path) -> Innstillinger:
    return Innstillinger(None, "modell", tmp_path / "cache")


@pytest.fixture
def klient(
    innstillinger: Innstillinger, fhi_mock: respx.MockRouter
) -> Iterator[TestClient]:
    with TestClient(web.lag_app(lambda: innstillinger)) as testklient:
        yield testklient


def _valgt(html: str, felt: str) -> list[str]:
    """Verdiene som er forhåndsvalgt i nedtrekkslisten `felt`."""
    liste = re.search(rf'<select id="{felt}".*?</select>', html, re.DOTALL)
    assert liste, f"fant ikke feltet {felt}"
    return re.findall(r'<option value="([^"]*)" selected>', liste[0])


def _verdier(html: str, felt: str) -> list[str]:
    liste = re.search(rf'<select id="{felt}".*?</select>', html, re.DOTALL)
    assert liste, f"fant ikke feltet {felt}"
    return re.findall(r'<option value="([^"]*)"', liste[0])


# --- Skjemaet uten parametre (FR-1–FR-4) ---


def test_uten_parametre_vises_bare_skjemaet(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    svar = klient.get("/")
    assert svar.status_code == 200
    assert '<form method="get" action="/"' in svar.text
    assert "Vis tallene" in svar.text
    assert 'role="alert"' not in svar.text
    assert 'role="status"' not in svar.text
    assert not fhi_mock.routes["data"].called


def test_mal_1_vises_som_spørsmål(klient: TestClient) -> None:
    html = klient.get("/").text
    assert _verdier(html, "mal") == [str(nr) for nr in MALER]
    assert "Vis andel positive tester for [virus] i sesongen [sesong]" in html
    assert MALER[1].tittel not in html


def test_influensa_og_rsv_kan_velges(klient: TestClient) -> None:
    html = klient.get("/").text
    assert _verdier(html, "virus") == ["influensa", "rsv"]
    assert ">Influensa<" in html
    assert ">RSV<" in html
    assert "SARS-CoV-2" not in html


def test_sesongene_med_siste_som_standard(klient: TestClient) -> None:
    html = klient.get("/").text
    assert _verdier(html, "sesong") == ["2024/2025", "2025/2026", "2026/2027"]
    assert _valgt(html, "sesong") == ["2026/2027"]


def test_alle_aldersgrupper_er_standard(klient: TestClient) -> None:
    html = klient.get("/").text
    assert _verdier(html, "alder") == list(ALDERSGRUPPER)
    assert _valgt(html, "alder") == ["alle"]
    for gruppe in ALDERSGRUPPER.values():
        assert f">{gruppe.etikett}<" in html
    assert "Ukjent" not in html


def test_alle_felt_har_label(klient: TestClient) -> None:
    html = klient.get("/").text
    for felt in web.PARAMETRE:
        assert f'<label for="{felt}">' in html
        assert f'<select id="{felt}" name="{felt}">' in html


# --- Språk og FHI-koder (NFR-3, AD-2) ---


@pytest.mark.parametrize(
    "sti", ["/", "/?mal=1&virus=influensa&sesong=1999/2000&alder=ukjent"]
)
def test_siden_er_norsk_uten_fhi_koder(klient: TestClient, sti: str) -> None:
    html = klient.get(sti).text
    assert '<html lang="nb">' in html
    for kode in FHI_KODER:
        assert kode not in html


# --- Ugyldige parametre (FR-5, AD-9) ---


@pytest.mark.parametrize(
    ("sti", "melding"),
    [
        ("/?mal=9&virus=influensa&sesong=2025/2026", "Velg en mal:"),
        ("/?mal=1&virus=ebola&sesong=2025/2026", "Velg et virus:"),
        ("/?mal=1&virus=influensa&sesong=1999/2000", "Velg en sesong:"),
        ("/?mal=1&virus=influensa&sesong=2025/2026&alder=99", "Velg en aldersgruppe:"),
        ("/?virus=influensa", "Velg en mal:"),
    ],
)
def test_ugyldig_utvalg_gir_melding_og_ingen_henting(
    klient: TestClient, fhi_mock: respx.MockRouter, sti: str, melding: str
) -> None:
    svar = klient.get(sti)
    assert svar.status_code == 200
    assert 'role="alert"' in svar.text
    assert melding in svar.text
    assert not fhi_mock.routes["data"].called


def test_melding_viser_ikke_verdien_brukeren_sendte(klient: TestClient) -> None:
    html = klient.get("/?mal=1&virus=%3Cscript%3Eondt&sesong=2025/2026").text
    assert "Velg et virus:" in html
    assert "ondt" not in html
    assert "<script>" not in html


def test_gyldig_utvalg_henter_tall(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    svar = klient.get("/?mal=1&virus=influensa&sesong=2025/2026&alder=alle")
    assert svar.status_code == 200
    assert 'role="alert"' not in svar.text
    assert fhi_mock.routes["data"].call_count == 1
    assert _valgt(svar.text, "sesong") == ["2025/2026"]


@pytest.mark.parametrize("sti", ["/?mal=&virus=&sesong=&alder=", "/?mal=%20&alder="])
def test_tomme_parametre_gir_bare_skjemaet(
    klient: TestClient, fhi_mock: respx.MockRouter, sti: str
) -> None:
    svar = klient.get(sti)
    assert svar.status_code == 200
    assert 'role="alert"' not in svar.text
    assert not fhi_mock.routes["data"].called


def test_parametre_med_mellomrom_avvises_av_domene(klient: TestClient) -> None:
    html = klient.get("/?mal=1&virus=influensa%20&sesong=2025/2026").text
    assert "Velg et virus:" in html


def test_valgene_er_forhåndsvalgt_etter_innsending(klient: TestClient) -> None:
    html = klient.get("/?mal=1&virus=influensa&sesong=2024/2025&alder=0-4").text
    assert _valgt(html, "mal") == ["1"]
    assert _valgt(html, "virus") == ["influensa"]
    assert _valgt(html, "sesong") == ["2024/2025"]
    assert _valgt(html, "alder") == ["0-4"]


@pytest.mark.parametrize(
    "sti",
    [
        "/?mal=9&virus=ebola&sesong=1999/2000&alder=99",
        "/?mal=1&virus=sars-cov-2&sesong=2025/2026",
    ],
)
def test_ukjente_valg_viser_standardvalget(klient: TestClient, sti: str) -> None:
    html = klient.get(sti).text
    assert _valgt(html, "mal") == ["1"]
    assert _valgt(html, "virus") == ["influensa"]
    assert _valgt(html, "alder") == ["alle"]
    if "1999" in sti:
        assert _valgt(html, "sesong") == ["2026/2027"]


# --- FHI nede (FR-8) ---


def test_skjemaet_vises_når_fhi_er_nede(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.routes["dimensjoner"].mock(side_effect=httpx.ConnectError("nede"))
    svar = klient.get("/")
    assert svar.status_code == 200
    assert _verdier(svar.text, "sesong")
    assert 'role="alert"' not in svar.text


def test_fhi_nede_gir_melding_og_ett_kall_per_side(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.routes["dimensjoner"].mock(side_effect=httpx.ConnectError("nede"))
    svar = klient.get("/?mal=1&virus=influensa&sesong=2025/2026")
    assert svar.status_code == 200
    assert tjeneste.FHI_NEDE_INGEN_TALL in svar.text
    # Sesonglisten og tallene venter ikke hver sin tidsgrense.
    assert fhi_mock.routes["dimensjoner"].call_count == 1
    assert not fhi_mock.routes["data"].called


def test_sars_cov_2_gir_melding_fra_tjeneste_uten_henting(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    html = klient.get("/?mal=1&virus=sars-cov-2&sesong=2025/2026").text
    assert (
        "Tall for SARS-CoV-2 kan ikke vises i appen ennå. Velg influensa eller RSV."
        in html
    )
    assert not fhi_mock.routes["data"].called


# --- RSV, tabell 729 (story 6.1) ---

RSV_DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/729/data"
RSV_DIMENSJON_URL = (
    "https://statistikk-data.fhi.no/api/open/v1/msis/Table/729/dimension"
)


def test_rsv_viser_tall_og_kilde_for_729(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.get(RSV_DIMENSJON_URL, name="rsv-dimensjoner").respond(
        json=_svar("fhi/729-dimensjoner.json")
    )
    fhi_mock.post(RSV_DATA_URL, name="rsv-data").respond(
        json=_svar("fhi/729-rsv-2025-2026-alle-nonstl.json")
    )
    svar = klient.get("/?mal=1&virus=rsv&sesong=2025/2026")
    html = svar.text
    assert svar.status_code == 200
    assert fhi_mock.routes["rsv-data"].call_count == 1
    assert not fhi_mock.routes["data"].called
    assert _valgt(html, "virus") == ["rsv"]
    assert "<table" in html
    assert (
        "Kilde: MSIS-labdatabase og Referanselaboratoriet for RS-virus, "
        "Folkehelseinstituttet (FHI). Tabell 729 «RESPIaggr RSV antall og andel»."
    ) in html
    assert "RS-virus (A+B)" not in html
    for kode in (*FHI_KODER, "rsvtype"):
        assert kode not in html


# --- Innstillinger (AD-6) ---


def test_innstillingene_leses_en_gang_ved_oppstart(
    innstillinger: Innstillinger, fhi_mock: respx.MockRouter
) -> None:
    kall = []

    def les() -> Innstillinger:
        kall.append(1)
        return innstillinger

    app = web.lag_app(les)
    assert kall == []
    with TestClient(app) as testklient:
        assert kall == [1]
        testklient.get("/")
        testklient.get("/?mal=1&virus=influensa&sesong=2025/2026")
    assert kall == [1]


def test_bare_web_kaller_les_innstillinger() -> None:
    kilde = Path(config.__file__).parent
    brukere = [
        fil.name
        for fil in kilde.rglob("*.py")
        if fil.name != "config.py"
        and "les_innstillinger" in fil.read_text(encoding="utf-8")
    ]
    assert brukere == ["web.py"]


def test_appen_bruker_les_innstillinger_fra_config() -> None:
    standard = inspect.signature(web.lag_app).parameters["les_innstillinger"].default
    assert standard is config.les_innstillinger
