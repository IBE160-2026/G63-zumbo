"""Tester for svaret for et utvalg (story 2.9, FR-3, FR-7, FR-8, AD-3, AD-5, AD-9).

FHI mockes med `respx`, og cachen ligger i `tmp_path`. Ingen test når nettet.
"""

import copy
import json
import logging
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from backend import kontrollregler, mellomlager, sesong, tjeneste
from backend.config import Innstillinger
from backend.domene import Utvalg
from backend.tjeneste import Tjeneste

FIXTURES = Path(__file__).parent / "fixtures"


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
DIMENSJONER = _svar("fhi/724-dimensjoner.json")
R1_19 = _svar("konstruert/724-r1-19-positive.json")
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"


def _dimensjoner_til(siste: str) -> dict[str, Any]:
    """Dimensjonslisten med uker til og med `siste` (for eksempel `"2026-w20"`)."""
    kopi = copy.deepcopy(DIMENSJONER)
    for dimensjon in kopi["dimensions"]:
        if dimensjon["code"] == "dateusedforstatistics":
            dimensjon["categories"] = [
                k for k in dimensjon["categories"] if k["value"] <= siste
            ]
    return kopi


@pytest.fixture
def mappe(tmp_path: Path) -> Path:
    return tmp_path / "cache"


@pytest.fixture
def tj(mappe: Path) -> Tjeneste:
    return Tjeneste(Innstillinger(None, "modell", mappe))


@pytest.fixture
def fhi_mock() -> respx.MockRouter:
    with respx.mock(assert_all_called=False) as router:
        router.get(DIMENSJON_URL, name="dimensjoner").respond(json=DIMENSJONER)
        router.post(DATA_URL, name="data").respond(json=DATA)
        yield router


def _fhi_nede(router: respx.MockRouter, feil: Exception | None = None) -> None:
    feil = feil or httpx.ConnectError("nede")
    router.routes["dimensjoner"].mock(side_effect=feil)
    router.routes["data"].mock(side_effect=feil)


# --- Ferske og utdaterte tall (FR-7, AD-5) ---


def test_ferske_lagrede_tall_brukes_uten_kall_til_fhi(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    hentet = NÅ - timedelta(hours=23, minutes=59)
    mellomlager.lagre_svar(mappe, UTVALG, DATA, hentet)
    resultat = tj.svar(UTVALG, NÅ)
    assert not fhi_mock.calls
    assert resultat.serie is not None and len(resultat.serie.uker) == 33
    assert resultat.kilde is not None and resultat.kilde.hentet == hentet
    assert resultat.kilde.tabell == 724
    assert resultat.sist_lagrede is False
    assert resultat.melding is None


def test_utdaterte_tall_hentes_på_nytt_og_lagres(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, R1_19, NÅ - timedelta(hours=24))
    resultat = tj.svar(UTVALG, NÅ)
    assert fhi_mock.routes["data"].call_count == 1
    assert resultat.kilde is not None and resultat.kilde.hentet == NÅ
    assert resultat.sist_lagrede is False and resultat.melding is None
    lagret = mellomlager.les_svar(mappe, UTVALG)
    assert lagret is not None and lagret.svar == DATA and lagret.hentet == NÅ
    # Dimensjonslisten lagres også, så neste utvalg ikke trenger å hente den.
    assert mellomlager.les_dimensjoner(mappe, 724) is not None


def test_uten_lagrede_tall_hentes_tall_frem_til_siste_publiserte_uke(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    resultat = tj.svar(UTVALG, NÅ)
    kropp = json.loads(fhi_mock.routes["data"].calls.last.request.content)
    uker = next(
        d["values"] for d in kropp["dimensions"] if d["code"] == "dateusedforstatistics"
    )
    assert uker[0] == "2025-w40" and uker[-1] == "2026-w20"
    assert resultat.serie is not None
    assert (
        resultat.serie.uker[-1].år == 2026 and resultat.serie.uker[-1].ukenummer == 20
    )


def test_svaret_har_serie_regelutslag_og_kilde(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    resultat = tj.svar(UTVALG, NÅ)
    assert resultat.serie is not None
    assert resultat.regelutslag == tuple(kontrollregler.vurder(resultat.serie))
    assert resultat.kilde is not None
    assert resultat.kilde.tabellnavn == "RESPIaggr Influensa antall og andel"
    assert resultat.kilde.kildetekst.startswith("Kilde: MSIS-labdatabase")


def test_fersk_dimensjonsliste_hentes_ikke_på_nytt(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    mellomlager.lagre_dimensjoner(mappe, 724, DIMENSJONER, NÅ - timedelta(hours=1))
    tj.svar(UTVALG, NÅ)
    assert fhi_mock.routes["dimensjoner"].call_count == 0
    assert fhi_mock.routes["data"].call_count == 1


# --- FHI nede (FR-8) ---


@pytest.mark.parametrize(
    "feil", [httpx.ConnectError("nede"), httpx.ReadTimeout("tidsavbrudd")]
)
def test_fhi_nede_gir_sist_lagrede_tall_med_kontrollregler(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter, feil: Exception
) -> None:
    hentet = NÅ - timedelta(days=3)
    mellomlager.lagre_svar(mappe, UTVALG, R1_19, hentet)
    _fhi_nede(fhi_mock, feil)
    resultat = tj.svar(UTVALG, NÅ)
    assert resultat.sist_lagrede is True
    assert resultat.melding == tjeneste.FHI_NEDE_LAGRET
    assert resultat.kilde is not None and resultat.kilde.hentet == hentet
    # Kontrollreglene gjelder også for lagrede tall.
    assert [u.regel for u in resultat.regelutslag] == ["R1"]


def test_data_feiler_etter_at_dimensjonslisten_er_hentet(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, NÅ - timedelta(days=2))
    fhi_mock.routes["data"].respond(status_code=500)
    resultat = tj.svar(UTVALG, NÅ)
    assert resultat.sist_lagrede is True and resultat.serie is not None


def test_fhi_nede_uten_lagrede_tall_gir_melding(
    tj: Tjeneste, fhi_mock: respx.MockRouter, caplog: pytest.LogCaptureFixture
) -> None:
    _fhi_nede(fhi_mock)
    with caplog.at_level(logging.INFO, logger="backend.tjeneste"):
        resultat = tj.svar(UTVALG, NÅ)
    assert resultat.serie is None and resultat.kilde is None
    assert resultat.regelutslag == ()
    assert resultat.melding == tjeneste.FHI_NEDE_INGEN_TALL
    assert "ConnectError" in caplog.text


def test_lagret_fil_som_ikke_kan_tolkes_regnes_som_manglende(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    # Et gyldig svar, men for en annen aldersgruppe.
    mellomlager.lagre_svar(
        mappe, UTVALG, _svar("konstruert/724-skjulte-verdier.json"), NÅ
    )
    _fhi_nede(fhi_mock)
    resultat = tj.svar(UTVALG, NÅ)
    assert resultat.serie is None
    assert resultat.melding == tjeneste.FHI_NEDE_INGEN_TALL


def test_meldingene_har_ingen_fhi_koder() -> None:
    tekster = [
        tjeneste.IKKE_KLART,
        tjeneste.FHI_NEDE_LAGRET,
        tjeneste.FHI_NEDE_INGEN_TALL,
        tjeneste.IKKE_PUBLISERT,
    ]
    for kode in ("NONSTL", "A+B", "724", "Table", "http"):
        assert all(kode not in tekst for tekst in tekster)


def test_lagring_som_feiler_gir_likevel_tall(
    tmp_path: Path, fhi_mock: respx.MockRouter
) -> None:
    fil = tmp_path / "ikke-en-mappe"
    fil.write_text("", encoding="utf-8")
    resultat = Tjeneste(Innstillinger(None, "modell", fil)).svar(UTVALG, NÅ)
    assert resultat.serie is not None and resultat.melding is None


# --- Utvalg som ikke kan hentes ennå (åpne punkter fra 2.3 og 2.5) ---


@pytest.mark.parametrize(
    ("virus", "navn"), [("rsv", "RSV"), ("sars-cov-2", "SARS-CoV-2")]
)
def test_rsv_og_sars_cov_2_gir_norsk_melding_uten_kall(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter, virus: str, navn: str
) -> None:
    resultat = tj.svar(Utvalg(1, virus, "2025/2026"), NÅ)
    assert resultat.serie is None
    assert (
        resultat.melding
        == f"Tall for {navn} kan ikke vises i appen ennå. Velg influensa."
    )
    assert not fhi_mock.calls
    assert not mappe.exists()


def test_sesong_uten_publiserte_uker_gir_melding_uten_datakall(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.routes["dimensjoner"].respond(json=_dimensjoner_til("2026-w20"))
    resultat = tj.svar(Utvalg(1, "influensa", "2026/2027"), NÅ)
    assert resultat.serie is None
    assert resultat.melding == (
        "FHI har ikke publisert tall for sesongen 2026/2027 ennå. Prøv igjen senere."
    )
    assert fhi_mock.routes["data"].call_count == 0


# --- Sesonglisten (FR-3, AD-3) ---


def test_sesonger_fra_fhi_lagres(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    assert tj.sesonger(NÅ) == ("2024/2025", "2025/2026", "2026/2027")
    assert mellomlager.les_dimensjoner(mappe, 724) is not None
    tj.sesonger(NÅ)
    assert fhi_mock.routes["dimensjoner"].call_count == 1


def test_fhis_liste_vinner_over_reserven_i_uke_40(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    uke_40 = datetime(2026, 9, 28, 12, 0, tzinfo=UTC)
    assert "2026/2027" in sesong.sesonger_fra_dato(uke_40)
    fhi_mock.routes["dimensjoner"].respond(json=_dimensjoner_til("2026-w20"))
    assert tj.sesonger(uke_40) == ("2024/2025", "2025/2026")


def test_fhi_nede_gir_lagret_sesongliste_selv_om_den_er_gammel(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    mellomlager.lagre_dimensjoner(
        mappe, 724, _dimensjoner_til("2026-w20"), NÅ - timedelta(days=30)
    )
    _fhi_nede(fhi_mock)
    assert tj.sesonger(NÅ) == ("2024/2025", "2025/2026")


@pytest.mark.parametrize("lagret", [None, "{ikke json", '{"hentet": 1}'])
def test_fhi_nede_uten_brukbar_liste_gir_reserven(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter, lagret: str | None
) -> None:
    if lagret is not None:
        fil = mellomlager.dimensjonsfil(mappe, 724)
        fil.parent.mkdir(parents=True)
        fil.write_text(lagret, encoding="utf-8")
    _fhi_nede(fhi_mock)
    assert tj.sesonger(NÅ) == sesong.sesonger_fra_dato(NÅ)


# --- Samtidige kall (AD-9) ---


def test_to_samtidige_kall_deler_ett_kall_til_fhi(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    startet = threading.Event()
    slipp = threading.Event()

    def treg(_: httpx.Request) -> httpx.Response:
        startet.set()
        assert slipp.wait(5)
        return httpx.Response(200, json=DATA)

    fhi_mock.routes["data"].mock(side_effect=treg)
    resultater: list[tjeneste.Resultat] = []

    def kall() -> None:
        resultater.append(tj.svar(UTVALG, NÅ))

    første = threading.Thread(target=kall)
    første.start()
    assert startet.wait(5)
    andre = threading.Thread(target=kall)
    andre.start()
    andre.join(0.2)  # Den andre venter på det første kallet.
    slipp.set()
    første.join(5)
    andre.join(5)
    assert len(resultater) == 2
    assert resultater[0] == resultater[1]
    assert fhi_mock.routes["data"].call_count == 1
    assert fhi_mock.routes["dimensjoner"].call_count == 1


def test_feil_i_jobben_gis_videre_og_nøkkelen_frigis(tj: Tjeneste) -> None:
    def feiler() -> None:
        raise RuntimeError("feil")

    with pytest.raises(RuntimeError):
        tj._én_gang("nøkkel", feiler)
    assert tj._én_gang("nøkkel", lambda: 42) == 42
