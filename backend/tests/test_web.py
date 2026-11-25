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
TABELL_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/{}"
DATA_URL = TABELL_URL.format("724/data")
DIMENSJON_URL = TABELL_URL.format("724/dimension")
RSV_DATA_URL = TABELL_URL.format("729/data")
RSV_DIMENSJON_URL = TABELL_URL.format("729/dimension")
SARS_DATA_URL = TABELL_URL.format("731/data")
SARS_DIMENSJON_URL = TABELL_URL.format("731/dimension")


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
        # RSV og SARS-CoV-2 (story 6.1, 6.2), som forsiden også viser (FR-27).
        router.get(RSV_DIMENSJON_URL, name="rsv-dimensjoner").respond(
            json=_svar("fhi/729-dimensjoner.json")
        )
        router.post(RSV_DATA_URL, name="rsv-data").respond(
            json=_svar("fhi/729-rsv-2025-2026-alle-nonstl.json")
        )
        router.get(SARS_DIMENSJON_URL, name="sars-dimensjoner").respond(
            json=_svar("fhi/731-dimensjoner.json")
        )
        router.post(SARS_DATA_URL, name="sars-data").respond(
            json=_svar("fhi/731-sars-cov-2-2025-2026-alle-nonstl.json")
        )
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


def _etiketter(html: str, felt: str) -> list[str]:
    """Teksten brukeren ser for hvert valg i nedtrekkslisten `felt`."""
    liste = re.search(rf'<select id="{felt}".*?</select>', html, re.DOTALL)
    assert liste, f"fant ikke feltet {felt}"
    return re.findall(r"<option [^>]*>([^<]*)</option>", liste[0])


def _verdier(html: str, felt: str) -> list[str]:
    liste = re.search(rf'<select id="{felt}".*?</select>', html, re.DOTALL)
    assert liste, f"fant ikke feltet {felt}"
    return re.findall(r'<option value="([^"]*)"', liste[0])


def _skjult(html: str, felt: str) -> str | None:
    """Verdien i det skjulte feltet `felt` i skjemaet, eller `None`."""
    treff = re.search(rf'<input type="hidden" name="{felt}" value="([^"]*)">', html)
    return treff[1] if treff else None


# --- Skjemaet på resultatsiden (FR-1–FR-4, FR-27) ---

SIDE = "/resultat?mal=1&virus=influensa&sesong=2025/2026&alder=alle"


def test_resultatsiden_har_skjema_med_skjult_mal_og_virus(klient: TestClient) -> None:
    html = klient.get(SIDE).text
    assert '<form method="get" action="/resultat" class="skjema">' in html
    assert "Vis tallene" in html
    assert _skjult(html, "mal") == "1"
    assert _skjult(html, "virus") == "influensa"
    assert '<select id="mal"' not in html
    assert '<select id="virus"' not in html
    assert MALER[1].tittel not in html


@pytest.mark.parametrize(
    ("virus", "navn"),
    [("influensa", "Influensa"), ("rsv", "RSV"), ("sars-cov-2", "SARS-CoV-2")],
)
def test_overskriften_viser_viruset(klient: TestClient, virus: str, navn: str) -> None:
    html = klient.get(f"/resultat?mal=1&virus={virus}&sesong=2025/2026").text
    assert f"<h1>{navn}</h1>" in html
    assert f"<title>{navn} – Tall fra FHI om luftveisvirus</title>" in html
    assert _skjult(html, "virus") == virus


def test_ugyldig_virus_viser_melding_og_lenke_uten_skjema(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    html = klient.get("/resultat?mal=1&virus=ebola&sesong=2025/2026").text
    assert "Velg et virus: Influensa, RSV eller SARS-CoV-2." in html
    assert '<a href="/">← Til forsiden</a>' in html
    assert "<title>Tall fra FHI om luftveisvirus</title>" in html
    assert 'class="skjema"' not in html
    assert not fhi_mock.routes["data"].called


def test_sesongene_med_siste_som_standard(klient: TestClient) -> None:
    html = klient.get("/resultat?mal=1&virus=influensa&sesong=1999/2000").text
    assert _verdier(html, "sesong") == ["2024/2025", "2025/2026", "2026/2027"]
    assert _valgt(html, "sesong") == ["2026/2027"]


def test_alle_aldersgrupper_er_standard(klient: TestClient) -> None:
    html = klient.get("/resultat?mal=1&virus=influensa&sesong=2025/2026").text
    assert _verdier(html, "alder") == list(ALDERSGRUPPER)
    assert _valgt(html, "alder") == ["alle"]
    for gruppe in ALDERSGRUPPER.values():
        assert f">{gruppe.etikett}<" in html
    assert "Ukjent" not in html


def test_synlige_felt_har_label(klient: TestClient) -> None:
    html = klient.get(SIDE).text
    for felt in ("sesong", "alder"):
        assert f'<label for="{felt}">' in html
        assert f'<select id="{felt}" name="{felt}">' in html


# --- Språk og FHI-koder (NFR-3, AD-2) ---


@pytest.mark.parametrize(
    "sti",
    ["/", "/resultat?mal=1&virus=influensa&sesong=1999/2000&alder=ukjent"],
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
        ("/resultat?mal=9&virus=influensa&sesong=2025/2026", "Velg en mal:"),
        ("/resultat?mal=1&virus=ebola&sesong=2025/2026", "Velg et virus:"),
        ("/resultat?mal=1&virus=influensa&sesong=1999/2000", "Velg en sesong:"),
        (
            "/resultat?mal=1&virus=influensa&sesong=2025/2026&alder=99",
            "Velg en aldersgruppe:",
        ),
        ("/resultat?virus=influensa", "Velg en mal:"),
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
    html = klient.get("/resultat?mal=1&virus=%3Cscript%3Eondt&sesong=2025/2026").text
    assert "Velg et virus:" in html
    assert "ondt" not in html
    assert "<script>" not in html


def test_gyldig_utvalg_henter_tall(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    svar = klient.get("/resultat?mal=1&virus=influensa&sesong=2025/2026&alder=alle")
    assert svar.status_code == 200
    assert 'role="alert"' not in svar.text
    assert fhi_mock.routes["data"].call_count == 1
    assert _valgt(svar.text, "sesong") == ["2025/2026"]


@pytest.mark.parametrize(
    "sti",
    ["/resultat", "/resultat?mal=&virus=&sesong=&alder=", "/resultat?mal=%20&alder="],
)
def test_resultatsiden_uten_valg_sender_til_forsiden(
    klient: TestClient, fhi_mock: respx.MockRouter, sti: str
) -> None:
    svar = klient.get(sti, follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/"
    assert not fhi_mock.routes["data"].called


def test_parametre_med_mellomrom_avvises_av_domene(klient: TestClient) -> None:
    html = klient.get("/resultat?mal=1&virus=influensa%20&sesong=2025/2026").text
    assert "Velg et virus:" in html


def test_valgene_er_forhåndsvalgt_etter_innsending(klient: TestClient) -> None:
    html = klient.get("/resultat?mal=1&virus=rsv&sesong=2024/2025&alder=0-4").text
    assert _skjult(html, "mal") == "1"
    assert _skjult(html, "virus") == "rsv"
    assert _valgt(html, "sesong") == ["2024/2025"]
    assert _valgt(html, "alder") == ["0-4"]


def test_ukjente_valg_viser_standardvalget(klient: TestClient) -> None:
    html = klient.get("/resultat?mal=9&virus=influensa&sesong=1999/2000&alder=99").text
    assert "Velg en mal:" in html
    assert _skjult(html, "mal") == "1"
    assert _skjult(html, "virus") == "influensa"
    assert _valgt(html, "alder") == ["alle"]
    assert _valgt(html, "sesong") == ["2026/2027"]


def test_nytt_utvalg_fra_skjemaet_gjelder_samme_virus(klient: TestClient) -> None:
    """Skjemaet sender mal, virus, sesong og alder til `/resultat` (FR-27)."""
    html = klient.get(SIDE).text
    skjema = re.search(
        r'<form method="get" action="/resultat".*?</form>', html, re.DOTALL
    )
    assert skjema
    navn = re.findall(r'name="([^"]+)"', skjema[0])
    assert navn == ["mal", "virus", "sesong", "alder"]
    svar = klient.get(
        "/resultat",
        params={
            "mal": "1",
            "virus": "influensa",
            "sesong": "2024/2025",
            "alder": "0-4",
        },
    )
    assert svar.status_code == 200
    assert "<h1>Influensa</h1>" in svar.text
    assert _valgt(svar.text, "sesong") == ["2024/2025"]
    assert _valgt(svar.text, "alder") == ["0-4"]


# --- FHI nede (FR-8) ---


def test_skjemaet_vises_når_fhi_er_nede(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.routes["dimensjoner"].mock(side_effect=httpx.ConnectError("nede"))
    svar = klient.get("/resultat?mal=1&virus=influensa&sesong=1999/2000")
    assert svar.status_code == 200
    assert _verdier(svar.text, "sesong")


def test_fhi_nede_gir_melding_og_ett_kall_per_side(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.routes["dimensjoner"].mock(side_effect=httpx.ConnectError("nede"))
    svar = klient.get("/resultat?mal=1&virus=influensa&sesong=2025/2026")
    assert svar.status_code == 200
    assert tjeneste.FHI_NEDE_INGEN_TALL in svar.text
    # Sesonglisten og tallene venter ikke hver sin tidsgrense.
    assert fhi_mock.routes["dimensjoner"].call_count == 1
    assert not fhi_mock.routes["data"].called


# --- RSV, tabell 729 (story 6.1) ---


def test_rsv_viser_tall_og_kilde_for_729(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    svar = klient.get("/resultat?mal=1&virus=rsv&sesong=2025/2026")
    html = svar.text
    assert svar.status_code == 200
    assert fhi_mock.routes["rsv-data"].call_count == 1
    assert not fhi_mock.routes["data"].called
    assert _skjult(html, "virus") == "rsv"
    assert "<table" in html
    assert (
        "Kilde: MSIS-labdatabase og Referanselaboratoriet for RS-virus, "
        "Folkehelseinstituttet (FHI). Tabell 729 «RESPIaggr RSV antall og andel»."
    ) in html
    assert "RS-virus (A+B)" not in html
    for kode in (*FHI_KODER, "rsvtype"):
        assert kode not in html


# --- SARS-CoV-2, tabell 731 (story 6.2) ---


def test_sars_cov_2_viser_tall_og_kilde_for_731(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    svar = klient.get("/resultat?mal=1&virus=sars-cov-2&sesong=2025/2026")
    html = svar.text
    assert svar.status_code == 200
    assert fhi_mock.routes["sars-data"].call_count == 1
    assert not fhi_mock.routes["data"].called
    assert _skjult(html, "virus") == "sars-cov-2"
    assert "<table" in html
    assert "kan ikke vises i appen ennå" not in html
    assert (
        "Kilde: MSIS-labdatabase og Referanselaboratoriet for koronavirus med "
        "utbruddspotensiale, Folkehelseinstituttet (FHI). Tabell 731 "
        "«RESPIaggr SARS-CoV-2 antall og andel»."
    ) in html
    for kode in (*FHI_KODER, "surveillancetype", "MEASURE_TYPE", "Detections"):
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
        testklient.get("/resultat?mal=1&virus=influensa&sesong=2025/2026")
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
