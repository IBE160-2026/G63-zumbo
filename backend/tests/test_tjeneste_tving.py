"""Tester for tvungen henting uten mellomlager (story 4.6, FR-25, FR-8, AD-9).

`Tjeneste.svar(..., tving=True)` henter tallene og dimensjonslisten fra FHI
selv om de lagrede er ferske. FHI mockes med `respx`, og cachen ligger i
`tmp_path`. Ingen test når nettet.
"""

import json
import threading
from concurrent.futures import Future
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from backend import mellomlager, tjeneste
from backend.config import Innstillinger
from backend.domene import Utvalg
from backend.tjeneste import FHI_NEDE_LAGRET, Tjeneste

FIXTURES = Path(__file__).parent / "fixtures"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
FØR = NÅ - timedelta(hours=2)
"""Tallene ble lagret for to timer siden, så de er ferske (FR-7)."""


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
DIMENSJONER = _svar("fhi/724-dimensjoner.json")
R1_19 = _svar("konstruert/724-r1-19-positive.json")


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


@pytest.fixture
def ferske(mappe: Path) -> None:
    """Ferske lagrede tall (andre tall enn FHI har nå) og en fersk liste."""
    mellomlager.lagre_svar(mappe, UTVALG, R1_19, FØR)
    mellomlager.lagre_dimensjoner(mappe, 724, DIMENSJONER, FØR)


def _fhi_nede(router: respx.MockRouter) -> None:
    feil = httpx.ConnectError("nede")
    router.routes["dimensjoner"].mock(side_effect=feil)
    router.routes["data"].mock(side_effect=feil)


@pytest.mark.usefixtures("ferske")
def test_uten_tving_brukes_de_ferske_tallene(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    resultat = tj.svar(UTVALG, NÅ)
    assert not fhi_mock.calls
    assert resultat.kilde is not None and resultat.kilde.hentet == FØR


@pytest.mark.usefixtures("ferske")
def test_tving_henter_fra_fhi_selv_om_tallene_er_ferske(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    resultat = tj.svar(UTVALG, NÅ, tving=True)
    assert fhi_mock.routes["data"].call_count == 1
    assert resultat.kilde is not None and resultat.kilde.hentet == NÅ
    assert resultat.sist_lagrede is False and resultat.melding is None
    assert resultat.serie is not None and len(resultat.serie.uker) == 33


@pytest.mark.usefixtures("ferske")
def test_tving_lagrer_med_nytt_hentetidspunkt(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    tj.svar(UTVALG, NÅ, tving=True)
    lagret = mellomlager.les_svar(mappe, UTVALG)
    assert lagret is not None and lagret.svar == DATA and lagret.hentet == NÅ
    # Neste vanlige visning bruker de nye tallene uten nytt kall.
    kall = fhi_mock.routes["data"].call_count
    neste = tj.svar(UTVALG, NÅ)
    assert neste.kilde is not None and neste.kilde.hentet == NÅ
    assert fhi_mock.routes["data"].call_count == kall


@pytest.mark.usefixtures("ferske")
def test_tving_henter_også_dimensjonslisten(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    # En ny uke kan være publisert etter at listen ble lagret.
    tj.svar(UTVALG, NÅ, tving=True)
    assert fhi_mock.routes["dimensjoner"].call_count == 1
    lagret = mellomlager.les_dimensjoner(mappe, 724)
    assert lagret is not None and lagret.hentet == NÅ


@pytest.mark.usefixtures("ferske")
def test_tving_når_fhi_er_nede_gir_sist_lagrede_tall(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    _fhi_nede(fhi_mock)
    resultat = tj.svar(UTVALG, NÅ, tving=True)
    assert resultat.sist_lagrede is True
    assert resultat.melding == FHI_NEDE_LAGRET
    assert resultat.serie is not None
    assert resultat.kilde is not None and resultat.kilde.hentet == FØR
    # De lagrede tallene er urørt.
    lagret = mellomlager.les_svar(mappe, UTVALG)
    assert lagret is not None and lagret.svar == R1_19 and lagret.hentet == FØR


def test_tving_prøver_fhi_igjen_rett_etter_en_feil(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    # Brukeren har bedt om nye tall, så pausen etter en feil gjelder ikke.
    mellomlager.lagre_svar(mappe, UTVALG, R1_19, NÅ - timedelta(hours=30))
    _fhi_nede(fhi_mock)
    assert tj.svar(UTVALG, NÅ).sist_lagrede is True
    fhi_mock.routes["dimensjoner"].mock(side_effect=None)
    fhi_mock.routes["dimensjoner"].respond(json=DIMENSJONER)
    fhi_mock.routes["data"].mock(side_effect=None)
    fhi_mock.routes["data"].respond(json=DATA)
    senere = NÅ + timedelta(seconds=5)
    resultat = tj.svar(UTVALG, senere, tving=True)
    assert resultat.sist_lagrede is False
    assert resultat.kilde is not None and resultat.kilde.hentet == senere


def test_tving_uten_lagrede_tall_og_fhi_nede_gir_melding(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    _fhi_nede(fhi_mock)
    resultat = tj.svar(UTVALG, NÅ, tving=True)
    assert resultat.serie is None
    assert resultat.melding is not None and "ingen lagrede" in resultat.melding


def test_pausen_etter_feil_gjelder_også_datakallet(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    # Dimensjonslisten svarer, men tallene gjør det ikke (FR-8).
    mellomlager.lagre_svar(mappe, UTVALG, R1_19, NÅ - timedelta(hours=30))
    fhi_mock.routes["data"].mock(side_effect=httpx.ConnectError("nede"))
    assert tj.svar(UTVALG, NÅ).sist_lagrede is True
    assert tj.svar(UTVALG, NÅ + timedelta(seconds=30)).sist_lagrede is True
    assert fhi_mock.routes["data"].call_count == 1
    # Etter pausen prøves FHI igjen.
    tj.svar(UTVALG, NÅ + timedelta(seconds=61))
    assert fhi_mock.routes["data"].call_count == 2


def _hold_igjen(rute: respx.Route, antall: int) -> tuple[threading.Event, Any]:
    """Holder igjen kallene til `rute` til `slipp` settes. Gir `slipp` og en
    funksjon som venter til `antall` kall har startet."""
    slipp = threading.Event()
    startet = threading.Semaphore(0)

    def treg(_: httpx.Request) -> httpx.Response:
        startet.release()
        assert slipp.wait(5)
        return httpx.Response(200, json=DATA)

    rute.mock(side_effect=treg)

    def vent() -> None:
        for _ in range(antall):
            assert startet.acquire(timeout=5)

    return slipp, vent


def _i_tråd(kall: Any) -> tuple[threading.Thread, dict[str, Any]]:
    resultat: dict[str, Any] = {}
    tråd = threading.Thread(target=lambda: resultat.setdefault("r", kall()))
    tråd.start()
    return tråd, resultat


def test_tvunget_kall_blir_ikke_med_på_et_vanlig_kall(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    # Et vanlig kall henter utdaterte tall. Et tvunget kall som kommer samtidig,
    # henter selv i stedet for å vente på det vanlige.
    mellomlager.lagre_svar(mappe, UTVALG, R1_19, NÅ - timedelta(hours=30))
    slipp, vent = _hold_igjen(fhi_mock.routes["data"], 2)
    senere = NÅ + timedelta(seconds=1)
    vanlig, _ = _i_tråd(lambda: tj.svar(UTVALG, NÅ))
    tvunget, resultat = _i_tråd(lambda: tj.svar(UTVALG, senere, tving=True))
    vent()
    slipp.set()
    vanlig.join(5)
    tvunget.join(5)
    assert fhi_mock.routes["data"].call_count == 2
    assert resultat["r"].kilde.hentet == senere


def test_samtidige_tvungne_kall_deler_ett_kall_til_fhi(
    tj: Tjeneste, fhi_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    venter = threading.Event()

    class Fremtid(Future):
        def result(self, timeout: float | None = None) -> Any:
            venter.set()
            return super().result(timeout)

    monkeypatch.setattr(tjeneste, "Future", Fremtid)
    slipp, vent = _hold_igjen(fhi_mock.routes["data"], 1)
    første, a = _i_tråd(lambda: tj.svar(UTVALG, NÅ, tving=True))
    vent()
    andre, b = _i_tråd(lambda: tj.svar(UTVALG, NÅ, tving=True))
    assert venter.wait(5), "det andre tvungne kallet venter ikke på det første"
    slipp.set()
    første.join(5)
    andre.join(5)
    assert fhi_mock.routes["data"].call_count == 1
    assert a["r"] == b["r"]
