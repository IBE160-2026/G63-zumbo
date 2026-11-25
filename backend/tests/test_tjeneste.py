"""Tester for svaret for et utvalg (story 2.9, FR-3, FR-7, FR-8, AD-3, AD-5, AD-9).

FHI mockes med `respx`, og cachen ligger i `tmp_path`. Ingen test når nettet.
"""

import copy
import json
import logging
import threading
from collections.abc import Callable
from concurrent.futures import Future
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


def _data_til(svar: dict[str, Any], siste: str) -> dict[str, Any]:
    """Datasvaret med uker til og med `siste`, slik FHI svarer når de senere
    ukene i sesongen ikke er publisert ennå. Dimensjonene før uka har én
    kategori i fixturene, så ukene ligger i én sammenhengende blokk i `value`."""
    kopi = copy.deepcopy(svar)
    plass = kopi["id"].index("dateusedforstatistics")
    kategori = kopi["dimension"]["dateusedforstatistics"]["category"]
    uker = [u for u in kategori["index"] if u <= siste]
    kategori["index"] = uker
    kategori["label"] = {u: u for u in uker}
    assert all(størrelse == 1 for størrelse in kopi["size"][:plass])
    steg = 1
    for størrelse in kopi["size"][plass + 1 :]:
        steg *= størrelse
    kopi["size"][plass] = len(uker)
    kopi["value"] = kopi["value"][: len(uker) * steg]
    return kopi


def _uker_i_forespørselen(rute: respx.Route) -> list[str]:
    kropp = json.loads(rute.calls.last.request.content)
    return next(
        d["values"] for d in kropp["dimensions"] if d["code"] == "dateusedforstatistics"
    )


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
    # Tallene trenger ikke dimensjonslisten (AD-3, datasvaret har ukene).
    assert not fhi_mock.routes["dimensjoner"].called


def test_uten_lagrede_tall_hentes_tall_frem_til_siste_publiserte_uke(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    resultat = tj.svar(UTVALG, NÅ)
    uker = _uker_i_forespørselen(fhi_mock.routes["data"])
    assert uker[0] == "2025-w40" and uker[-1] == "2026-w20"
    assert resultat.serie is not None
    assert (
        resultat.serie.uker[-1].år == 2026 and resultat.serie.uker[-1].ukenummer == 20
    )


def test_sesongen_som_pågår_slutter_ved_siste_uke_i_datasvaret(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    # Forespørselen har hele sesongen. FHI sender bare de publiserte ukene, og
    # serien slutter ved den siste av dem, uten kall til dimensjonslisten.
    mellomlager.lagre_dimensjoner(mappe, 724, DIMENSJONER, NÅ)
    fhi_mock.routes["data"].respond(json=_data_til(DATA, "2026-w10"))
    resultat = tj.svar(UTVALG, NÅ)
    assert _uker_i_forespørselen(fhi_mock.routes["data"])[-1] == "2026-w20"
    assert resultat.serie is not None
    siste = resultat.serie.uker[-1]
    assert (siste.år, siste.ukenummer) == (2026, 10)
    assert len(resultat.serie.uker) == 23
    assert not fhi_mock.routes["dimensjoner"].called


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
        tjeneste.FHI_NEDE_LAGRET,
        tjeneste.FHI_NEDE_INGEN_TALL,
        tjeneste.IKKE_PUBLISERT.format(sesong="2026/2027"),
    ]
    for kode in ("NONSTL", "A+B", "724", "Table", "http"):
        assert all(kode not in tekst for tekst in tekster)


def test_lagring_som_feiler_gir_likevel_tall(
    tmp_path: Path, fhi_mock: respx.MockRouter, caplog: pytest.LogCaptureFixture
) -> None:
    fil = tmp_path / "ikke-en-mappe"
    fil.write_text("", encoding="utf-8")
    with caplog.at_level(logging.INFO, logger="backend.tjeneste"):
        resultat = Tjeneste(Innstillinger(None, "modell", fil)).svar(UTVALG, NÅ)
    assert resultat.serie is not None and resultat.melding is None
    assert "Kunne ikke lagre i cachen" in caplog.text


# --- RSV, tabell 729 (story 6.1, AD-3) ---

RSV_DATA = _svar("fhi/729-rsv-2025-2026-alle-nonstl.json")
RSV_DIMENSJONER = _svar("fhi/729-dimensjoner.json")
RSV_UTVALG = Utvalg(1, "rsv", "2025/2026", "alle")
RSV_DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/729/data"
RSV_DIMENSJON_URL = (
    "https://statistikk-data.fhi.no/api/open/v1/msis/Table/729/dimension"
)


@pytest.fixture
def rsv_mock(fhi_mock: respx.MockRouter) -> respx.MockRouter:
    fhi_mock.get(RSV_DIMENSJON_URL, name="rsv-dimensjoner").respond(
        json=RSV_DIMENSJONER
    )
    fhi_mock.post(RSV_DATA_URL, name="rsv-data").respond(json=RSV_DATA)
    return fhi_mock


def test_rsv_hentes_fra_729_med_ett_kall(
    tj: Tjeneste, mappe: Path, rsv_mock: respx.MockRouter
) -> None:
    resultat = tj.svar(RSV_UTVALG, NÅ)
    assert rsv_mock.routes["rsv-data"].call_count == 1
    assert not rsv_mock.routes["rsv-dimensjoner"].called
    assert not rsv_mock.routes["dimensjoner"].called
    assert not rsv_mock.routes["data"].called
    assert resultat.serie is not None and len(resultat.serie.uker) == 33
    assert resultat.serie.uker[0].positive == 13
    assert resultat.melding is None
    assert mellomlager.les_dimensjoner(mappe, 729) is None
    lagret = mellomlager.les_svar(mappe, RSV_UTVALG)
    assert lagret is not None and lagret.svar == RSV_DATA


def test_rsv_kilde_er_tabell_729(tj: Tjeneste, rsv_mock: respx.MockRouter) -> None:
    kilde = tj.svar(RSV_UTVALG, NÅ).kilde
    assert kilde is not None
    assert kilde.tabell == 729
    assert kilde.tabellnavn == "RESPIaggr RSV antall og andel"
    assert kilde.kildetekst == (
        "Kilde: MSIS-labdatabase og Referanselaboratoriet for RS-virus, "
        "Folkehelseinstituttet (FHI)."
    )
    assert kilde.hentet == NÅ


def test_siste_publiserte_uke_for_rsv_kommer_fra_729(
    tj: Tjeneste, mappe: Path, rsv_mock: respx.MockRouter
) -> None:
    # 724 har uke 46 lagret, men 729 har bare publisert til uke 10. Serien
    # følger 729-svaret (AD-3).
    mellomlager.lagre_dimensjoner(mappe, 724, DIMENSJONER, NÅ)
    rsv_mock.routes["rsv-data"].respond(json=_data_til(RSV_DATA, "2026-w10"))
    resultat = tj.svar(RSV_UTVALG, NÅ)
    assert resultat.serie is not None
    siste = resultat.serie.uker[-1]
    assert (siste.år, siste.ukenummer) == (2026, 10)
    assert not rsv_mock.routes["rsv-dimensjoner"].called


def test_sesonglisten_kommer_fortsatt_fra_724(
    tj: Tjeneste, rsv_mock: respx.MockRouter
) -> None:
    assert tj.sesonger(NÅ) == ("2024/2025", "2025/2026", "2026/2027")
    assert rsv_mock.routes["dimensjoner"].call_count == 1
    assert not rsv_mock.routes["rsv-dimensjoner"].called


def test_rsv_fhi_nede_venter_ikke_på_729_rett_etter_feil_på_724(
    tj: Tjeneste, rsv_mock: respx.MockRouter
) -> None:
    # Pausen etter feil er felles for FHI (FR-8).
    _fhi_nede(rsv_mock)
    tj.sesonger(NÅ)
    resultat = tj.svar(RSV_UTVALG, NÅ + timedelta(seconds=1))
    assert resultat.melding == tjeneste.FHI_NEDE_INGEN_TALL
    assert not rsv_mock.routes["rsv-dimensjoner"].called
    assert not rsv_mock.routes["rsv-data"].called


def test_tvungen_henting_for_rsv_henter_729_selv_om_alt_er_ferskt(
    tj: Tjeneste, mappe: Path, rsv_mock: respx.MockRouter
) -> None:
    # «Hent nyeste tall nå» for RSV (FR-25): tallene fra 729, og sesonglisten
    # fra 724, slik at en ny sesong kommer med.
    før = NÅ - timedelta(hours=2)
    mellomlager.lagre_dimensjoner(mappe, 724, DIMENSJONER, før)
    mellomlager.lagre_svar(mappe, RSV_UTVALG, RSV_DATA, før)
    resultat = tj.svar(RSV_UTVALG, NÅ, tving=True)
    assert rsv_mock.routes["rsv-data"].call_count == 1
    assert rsv_mock.routes["dimensjoner"].call_count == 1
    assert not rsv_mock.routes["rsv-dimensjoner"].called
    assert not rsv_mock.routes["data"].called
    assert resultat.kilde is not None and resultat.kilde.hentet == NÅ
    lagret = mellomlager.les_dimensjoner(mappe, 724)
    assert lagret is not None and lagret.hentet == NÅ


def test_rsv_venter_ikke_på_724_listen_som_hentes_samtidig(
    tj: Tjeneste, mappe: Path, rsv_mock: respx.MockRouter
) -> None:
    # Mens sesonglisten (724) hentes, henter et RSV-kall tallene sine uten å
    # vente (AD-9).
    startet, slipp = threading.Event(), threading.Event()

    def treg(_: httpx.Request) -> httpx.Response:
        startet.set()
        assert slipp.wait(5)
        return httpx.Response(200, json=DIMENSJONER)

    rsv_mock.routes["dimensjoner"].mock(side_effect=treg)
    sesonger: list[object] = []
    tråd = threading.Thread(target=lambda: sesonger.append(tj.sesonger(NÅ)))
    tråd.start()
    try:
        assert startet.wait(5)
        resultat = tj.svar(RSV_UTVALG, NÅ)
    finally:
        slipp.set()
        tråd.join(5)
    assert not tråd.is_alive()
    assert resultat.serie is not None
    assert rsv_mock.routes["rsv-data"].call_count == 1
    assert not rsv_mock.routes["rsv-dimensjoner"].called
    assert sesonger == [("2024/2025", "2025/2026", "2026/2027")]


def test_rsv_svar_fra_feil_tabell_gir_fhi_nede(
    tj: Tjeneste, mappe: Path, rsv_mock: respx.MockRouter
) -> None:
    rsv_mock.routes["rsv-data"].respond(json=DATA)
    resultat = tj.svar(RSV_UTVALG, NÅ)
    assert resultat.serie is None
    assert resultat.melding == tjeneste.FHI_NEDE_INGEN_TALL
    assert mellomlager.les_svar(mappe, RSV_UTVALG) is None


IKKE_PUBLISERT_400 = {
    "status": 400,
    "detail": "No matching categories found for dimension 'dateusedforstatistics'",
}
"""Svaret FHI gir når ingen av ukene i forespørselen er publisert (26.11.2026)."""


def test_sesong_uten_publiserte_uker_gir_melding_når_fhi_avviser_datakallet(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.routes["data"].respond(400, json=IKKE_PUBLISERT_400)
    fhi_mock.routes["dimensjoner"].respond(json=_dimensjoner_til("2026-w20"))
    resultat = tj.svar(Utvalg(1, "influensa", "2026/2027"), NÅ)
    assert resultat.serie is None
    assert resultat.melding == (
        "FHI har ikke publisert tall for sesongen 2026/2027 ennå. Prøv igjen senere."
    )
    assert fhi_mock.routes["data"].call_count == 1
    assert fhi_mock.routes["dimensjoner"].call_count == 1
    # Ikke en feil hos FHI, så neste kall venter ikke på pausen.
    tj.svar(UTVALG, NÅ)
    assert fhi_mock.routes["data"].call_count == 2


def test_avvist_datakall_for_rsv_sjekkes_mot_729_listen(
    tj: Tjeneste, mappe: Path, rsv_mock: respx.MockRouter
) -> None:
    # 724 har publisert uker i 2026/2027, men 729 ikke ennå (AD-3).
    mellomlager.lagre_dimensjoner(mappe, 724, DIMENSJONER, NÅ)
    kopi = copy.deepcopy(RSV_DIMENSJONER)
    for dimensjon in kopi["dimensions"]:
        if dimensjon["code"] == "dateusedforstatistics":
            dimensjon["categories"] = [
                k for k in dimensjon["categories"] if k["value"] <= "2026-w20"
            ]
    rsv_mock.routes["rsv-dimensjoner"].respond(json=kopi)
    rsv_mock.routes["rsv-data"].respond(400, json=IKKE_PUBLISERT_400)
    resultat = tj.svar(Utvalg(1, "rsv", "2026/2027"), NÅ)
    assert resultat.melding == tjeneste.IKKE_PUBLISERT.format(sesong="2026/2027")
    assert rsv_mock.routes["rsv-dimensjoner"].call_count == 1


def test_fersk_lagret_liste_uten_uker_svarer_uten_kall(
    tj: Tjeneste, mappe: Path, rsv_mock: respx.MockRouter
) -> None:
    # Etter et avvist datakall er 729-listen lagret. Neste visning av samme
    # sesong gjør ingen kall, slik som før (AD-3).
    kopi = copy.deepcopy(RSV_DIMENSJONER)
    for dimensjon in kopi["dimensions"]:
        if dimensjon["code"] == "dateusedforstatistics":
            dimensjon["categories"] = [
                k for k in dimensjon["categories"] if k["value"] <= "2026-w20"
            ]
    mellomlager.lagre_dimensjoner(mappe, 729, kopi, NÅ - timedelta(hours=1))
    resultat = tj.svar(Utvalg(1, "rsv", "2026/2027"), NÅ)
    assert resultat.melding == tjeneste.IKKE_PUBLISERT.format(sesong="2026/2027")
    assert not rsv_mock.calls


@pytest.mark.parametrize(
    ("virus", "liste_for_tabellen"), [("influensa", None), ("rsv", "rsv-dimensjoner")]
)
def test_tvungen_henting_for_sesong_uten_publiserte_uker_gir_melding(
    tj: Tjeneste,
    rsv_mock: respx.MockRouter,
    virus: str,
    liste_for_tabellen: str | None,
) -> None:
    # «Hent nyeste tall nå» i en sesong som ikke er publisert: 724-listen hentes
    # én gang, og for RSV hentes 729-listen i tillegg.
    til_uke_20 = _dimensjoner_til("2026-w20")
    rsv_mock.routes["dimensjoner"].respond(json=til_uke_20)
    rsv_mock.routes["rsv-dimensjoner"].respond(json=til_uke_20)
    for rute in ("data", "rsv-data"):
        rsv_mock.routes[rute].respond(400, json=IKKE_PUBLISERT_400)
    resultat = tj.svar(Utvalg(1, virus, "2026/2027"), NÅ, tving=True)
    assert resultat.melding == tjeneste.IKKE_PUBLISERT.format(sesong="2026/2027")
    assert rsv_mock.routes["dimensjoner"].call_count == 1
    if liste_for_tabellen:
        assert rsv_mock.routes[liste_for_tabellen].call_count == 1


def test_avvist_datakall_for_publisert_sesong_gir_fhi_nede(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    # Har sesongen publiserte uker, er 400 en feil, og FR-8 gjelder. Influensa
    # er i 724, så det er 724-listen som sjekkes.
    mellomlager.lagre_svar(mappe, UTVALG, DATA, NÅ - timedelta(days=2))
    fhi_mock.routes["data"].respond(400, json={"status": 400})
    resultat = tj.svar(UTVALG, NÅ)
    assert resultat.sist_lagrede is True
    assert resultat.melding == tjeneste.FHI_NEDE_LAGRET
    assert fhi_mock.routes["dimensjoner"].call_count == 1
    # Pausen etter feil gjelder (FR-8).
    tj.svar(Utvalg(1, "influensa", "2024/2025"), NÅ + timedelta(seconds=1))
    assert fhi_mock.routes["data"].call_count == 1


def test_avvist_datakall_når_listen_ikke_kan_hentes_gir_fhi_nede(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.routes["data"].respond(400, json=IKKE_PUBLISERT_400)
    fhi_mock.routes["dimensjoner"].mock(side_effect=httpx.ConnectError("nede"))
    resultat = tj.svar(Utvalg(1, "influensa", "2026/2027"), NÅ)
    assert resultat.serie is None
    assert resultat.melding == tjeneste.FHI_NEDE_INGEN_TALL


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


UTEN_UKER = '{"hentet": "2026-11-24T11:00:00Z", "svar": {"dimensions": []}}'
"""En fersk fil med riktig form, men uten uker."""


@pytest.mark.parametrize("lagret", [None, "{ikke json", '{"hentet": 1}', UTEN_UKER])
def test_fhi_nede_uten_brukbar_liste_gir_reserven(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter, lagret: str | None
) -> None:
    if lagret is not None:
        fil = mellomlager.dimensjonsfil(mappe, 724)
        fil.parent.mkdir(parents=True)
        fil.write_text(lagret, encoding="utf-8")
    _fhi_nede(fhi_mock)
    assert tj.sesonger(NÅ) == sesong.sesonger_fra_dato(NÅ)


def _skriv_dimensjonsfil(mappe: Path, innhold: str) -> None:
    fil = mellomlager.dimensjonsfil(mappe, 724)
    fil.parent.mkdir(parents=True, exist_ok=True)
    fil.write_text(innhold, encoding="utf-8")


def test_lagret_liste_uten_uker_hentes_på_nytt(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    _skriv_dimensjonsfil(mappe, UTEN_UKER)
    assert tj.sesonger(NÅ) == ("2024/2025", "2025/2026", "2026/2027")
    assert fhi_mock.routes["dimensjoner"].call_count == 1


def test_gammel_dimensjonsliste_hentes_på_nytt_når_fhi_svarer(
    tj: Tjeneste, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    mellomlager.lagre_dimensjoner(
        mappe, 724, _dimensjoner_til("2026-w10"), NÅ - timedelta(hours=24)
    )
    assert "2026/2027" in tj.sesonger(NÅ)
    assert fhi_mock.routes["dimensjoner"].call_count == 1


# --- Samtidige kall (AD-9) ---


def _to_samtidige(
    monkeypatch: pytest.MonkeyPatch,
    rute: respx.Route,
    svar: Callable[[], httpx.Response],
    første: Callable[[], object],
    andre: Callable[[], object],
) -> tuple[object, object]:
    """Kjører `første`, holder kallet til `rute` igjen til `andre` venter på
    den delte jobben, og slipper det så. Gir resultatene (eller feilene)."""
    startet, slipp, venter = threading.Event(), threading.Event(), threading.Event()

    class Fremtid(Future):
        def result(self, timeout: float | None = None) -> Any:
            venter.set()
            return super().result(timeout)

    monkeypatch.setattr(tjeneste, "Future", Fremtid)

    def treg(_: httpx.Request) -> httpx.Response:
        startet.set()
        assert slipp.wait(5)
        return svar()

    rute.mock(side_effect=treg)
    resultater: dict[str, object] = {}

    def kjør(navn: str, kall: Callable[[], object]) -> None:
        try:
            resultater[navn] = kall()
        except BaseException as feil:  # noqa: BLE001 - feilen vises i testen
            resultater[navn] = feil

    tråder = [
        threading.Thread(target=kjør, args=("første", første)),
        threading.Thread(target=kjør, args=("andre", andre)),
    ]
    tråder[0].start()
    assert startet.wait(5)
    tråder[1].start()
    assert venter.wait(5), "det andre kallet venter ikke på det første"
    slipp.set()
    for tråd in tråder:
        tråd.join(5)
        assert not tråd.is_alive()
    return resultater["første"], resultater["andre"]


def _nede() -> httpx.Response:
    raise httpx.ConnectError("nede")


def test_to_samtidige_kall_deler_ett_kall_til_fhi(
    tj: Tjeneste, fhi_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    a, b = _to_samtidige(
        monkeypatch,
        fhi_mock.routes["data"],
        lambda: httpx.Response(200, json=DATA),
        lambda: tj.svar(UTVALG, NÅ),
        lambda: tj.svar(UTVALG, NÅ),
    )
    assert isinstance(a, tjeneste.Resultat) and a.serie is not None
    assert a == b
    assert fhi_mock.routes["data"].call_count == 1
    assert not fhi_mock.routes["dimensjoner"].called


def test_to_samtidige_kall_deler_ett_kall_også_når_fhi_er_nede(
    tj: Tjeneste, fhi_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    a, b = _to_samtidige(
        monkeypatch,
        fhi_mock.routes["data"],
        _nede,
        lambda: tj.svar(UTVALG, NÅ),
        lambda: tj.svar(UTVALG, NÅ),
    )
    assert isinstance(a, tjeneste.Resultat)
    assert a.melding == tjeneste.FHI_NEDE_INGEN_TALL and a == b
    assert fhi_mock.routes["data"].call_count == 1


@pytest.mark.parametrize(
    ("svar", "forventet"),
    [
        (lambda: httpx.Response(200, json=DIMENSJONER), None),
        (_nede, "reserve"),
    ],
)
def test_samtidige_sesongkall_deler_ett_kall_til_fhi(
    tj: Tjeneste,
    fhi_mock: respx.MockRouter,
    monkeypatch: pytest.MonkeyPatch,
    svar: Callable[[], httpx.Response],
    forventet: str | None,
) -> None:
    a, b = _to_samtidige(
        monkeypatch,
        fhi_mock.routes["dimensjoner"],
        svar,
        lambda: tj.sesonger(NÅ),
        lambda: tj.sesonger(NÅ),
    )
    if forventet == "reserve":
        assert a == b == sesong.sesonger_fra_dato(NÅ)
    else:
        assert a == b == ("2024/2025", "2025/2026", "2026/2027")
    assert fhi_mock.routes["dimensjoner"].call_count == 1


def test_feil_i_jobben_gis_videre_og_nøkkelen_frigis(tj: Tjeneste) -> None:
    def feiler() -> None:
        raise RuntimeError("feil")

    with pytest.raises(RuntimeError):
        tj._én_gang("nøkkel", feiler)
    assert tj._én_gang("nøkkel", lambda: 42) == 42


# --- Pause etter at FHI ikke svarte (review av story 3.1) ---


def test_dimensjonslisten_hentes_ikke_på_nytt_rett_etter_feil(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    _fhi_nede(fhi_mock)
    tj.sesonger(NÅ)
    resultat = tj.svar(UTVALG, NÅ + timedelta(seconds=1))
    assert resultat.melding == tjeneste.FHI_NEDE_INGEN_TALL
    assert fhi_mock.routes["dimensjoner"].call_count == 1


def test_dimensjonslisten_prøves_igjen_etter_pausen(
    tj: Tjeneste, fhi_mock: respx.MockRouter
) -> None:
    _fhi_nede(fhi_mock)
    tj.sesonger(NÅ)
    fhi_mock.routes["dimensjoner"].mock(side_effect=None)
    fhi_mock.routes["dimensjoner"].respond(json=DIMENSJONER)
    tj.sesonger(NÅ + tjeneste.PAUSE_ETTER_FEIL - timedelta(seconds=1))
    assert fhi_mock.routes["dimensjoner"].call_count == 1
    tj.sesonger(NÅ + tjeneste.PAUSE_ETTER_FEIL)
    assert fhi_mock.routes["dimensjoner"].call_count == 2


# --- SARS-CoV-2, tabell 731 (story 6.2, AD-3) ---

SARS_DATA = _svar("fhi/731-sars-cov-2-2025-2026-alle-nonstl.json")
SARS_DIMENSJONER = _svar("fhi/731-dimensjoner.json")
SARS_UTVALG = Utvalg(1, "sars-cov-2", "2025/2026", "alle")
SARS_DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/731/data"
SARS_DIMENSJON_URL = (
    "https://statistikk-data.fhi.no/api/open/v1/msis/Table/731/dimension"
)


@pytest.fixture
def sars_mock(fhi_mock: respx.MockRouter) -> respx.MockRouter:
    fhi_mock.get(SARS_DIMENSJON_URL, name="sars-dimensjoner").respond(
        json=SARS_DIMENSJONER
    )
    fhi_mock.post(SARS_DATA_URL, name="sars-data").respond(json=SARS_DATA)
    return fhi_mock


def test_sars_cov_2_hentes_fra_731_med_ett_kall(
    tj: Tjeneste, mappe: Path, sars_mock: respx.MockRouter
) -> None:
    resultat = tj.svar(SARS_UTVALG, NÅ)
    assert not sars_mock.routes["sars-dimensjoner"].called
    assert sars_mock.routes["sars-data"].call_count == 1
    assert not sars_mock.routes["dimensjoner"].called
    assert not sars_mock.routes["data"].called
    assert resultat.serie is not None and len(resultat.serie.uker) == 33
    første = resultat.serie.uker[0]
    assert (første.positive, første.tester) == (471, 7109)
    assert resultat.melding is None
    assert mellomlager.les_dimensjoner(mappe, 731) is None
    lagret = mellomlager.les_svar(mappe, SARS_UTVALG)
    assert lagret is not None and lagret.svar == SARS_DATA


def test_sars_cov_2_kilde_er_tabell_731(
    tj: Tjeneste, sars_mock: respx.MockRouter
) -> None:
    kilde = tj.svar(SARS_UTVALG, NÅ).kilde
    assert kilde is not None
    assert kilde.tabell == 731
    assert kilde.tabellnavn == "RESPIaggr SARS-CoV-2 antall og andel"
    assert kilde.kildetekst == (
        "Kilde: MSIS-labdatabase og Referanselaboratoriet for koronavirus med "
        "utbruddspotensiale, Folkehelseinstituttet (FHI)."
    )
    assert kilde.hentet == NÅ


def test_siste_publiserte_uke_for_sars_cov_2_kommer_fra_731(
    tj: Tjeneste, mappe: Path, sars_mock: respx.MockRouter
) -> None:
    # 724 har uke 46 lagret, men 731 har bare publisert til uke 10.
    mellomlager.lagre_dimensjoner(mappe, 724, DIMENSJONER, NÅ)
    sars_mock.routes["sars-data"].respond(json=_data_til(SARS_DATA, "2026-w10"))
    resultat = tj.svar(SARS_UTVALG, NÅ)
    assert resultat.serie is not None
    siste = resultat.serie.uker[-1]
    assert (siste.år, siste.ukenummer) == (2026, 10)
    assert not sars_mock.routes["sars-dimensjoner"].called
    assert not sars_mock.routes["dimensjoner"].called
