"""Tester for henting fra FHI med tidsgrense (story 2.5, FR-2, FR-6, FR-8, AD-3).

FHI mockes med `respx`. Ingen test når nettet (`--disable-socket`).
"""

import ast
import json
import threading
import time
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from backend import fhi
from backend.domene import Utvalg

FIXTURES = Path(__file__).parent / "fixtures"
SRC = Path(fhi.__file__).parent


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
DIMENSJONER = _svar("fhi/724-dimensjoner.json")
KONSTRUERT = _svar("konstruert/724-skjulte-verdier.json")
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
SISTE = (2026, 46)
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"


# --- Vellykket svar ---


@respx.mock
def test_hent_gir_det_rå_svaret_fra_fixturen() -> None:
    rute = respx.post(DATA_URL).respond(json=DATA)
    assert fhi.hent(UTVALG, SISTE) == DATA
    assert rute.call_count == 1


@respx.mock
def test_forespørselen_har_riktig_tabell_og_filtre() -> None:
    rute = respx.post(DATA_URL).respond(json=DATA)
    fhi.hent(UTVALG, SISTE)
    kropp = json.loads(rute.calls.last.request.content)
    filtre = {d["code"]: d["values"] for d in kropp["dimensions"]}
    assert all(d["filter"] == "item" for d in kropp["dimensions"])
    assert kropp["response"] == {"format": "json-stat2"}
    assert list(filtre) == [
        "dateusedforstatistics",
        "aldersgruppe",
        "influenzatypeandsubtype",
        "surveillancetype",
        "MEASURE_TYPE",
    ]
    assert filtre["aldersgruppe"] == ["Alle"]
    assert filtre["influenzatypeandsubtype"] == ["A+B"]
    assert filtre["surveillancetype"] == ["NONSTL"]
    assert filtre["MEASURE_TYPE"] == ["Detections", "Tests", "pos_rate"]
    # Samme uker som i forespørselen bak fixturen (README-en).
    assert filtre["dateusedforstatistics"] == list(
        DATA["dimension"]["dateusedforstatistics"]["category"]["index"]
    )


@respx.mock
def test_valgt_aldersgruppe_og_ukene_frem_til_siste_publiserte_uke() -> None:
    utvalg = Utvalg(1, "influensa", "2026/2027", "80+")
    rute = respx.post(DATA_URL).respond(json=KONSTRUERT)
    fhi.hent(utvalg, (2026, 46))
    filtre = {
        d["code"]: d["values"]
        for d in json.loads(rute.calls.last.request.content)["dimensions"]
    }
    assert filtre["aldersgruppe"] == ["80+ år"]
    assert filtre["dateusedforstatistics"] == [f"2026-w{u}" for u in range(40, 47)]


def test_ukekoden_har_to_sifre_og_liten_w() -> None:
    assert fhi.ukekode((2027, 1)) == "2027-w01"
    assert fhi.ukekode((2026, 53)) == "2026-w53"


@pytest.mark.parametrize(
    ("utvalg", "siste"),
    [
        (Utvalg(1, "rsv", "2025/2026", "alle"), SISTE),
        (Utvalg(1, "influensa", "2027/2028", "alle"), SISTE),
    ],
)
def test_forespørsel_som_ikke_kan_lages_gir_valueerror(
    utvalg: Utvalg, siste: tuple[int, int]
) -> None:
    with pytest.raises(ValueError):
        fhi.forespørsel(utvalg, siste)


@respx.mock
def test_hent_dimensjoner_med_egen_funksjon() -> None:
    rute = respx.get(DIMENSJON_URL).respond(json=DIMENSJONER)
    svar = fhi.hent_dimensjoner(724)
    assert svar == DIMENSJONER
    assert rute.call_count == 1
    assert fhi.siste_publiserte_uke(svar) == SISTE


@respx.mock
def test_tidsgrensen_er_10_sekunder() -> None:
    rute = respx.post(DATA_URL).respond(json=DATA)
    fhi.hent(UTVALG, SISTE)
    tidsgrense = rute.calls.last.request.extensions["timeout"]
    assert tidsgrense == {"connect": 10.0, "read": 10.0, "write": 10.0, "pool": 10.0}


@respx.mock
def test_egen_klient_brukes_og_får_tidsgrensen() -> None:
    rute = respx.post(DATA_URL).respond(json=DATA)
    with httpx.Client(timeout=60) as klient:
        assert fhi.hent(UTVALG, SISTE, klient=klient) == DATA
    assert rute.calls.last.request.extensions["timeout"]["read"] == 10.0


# --- Feil blir alltid FhiUtilgjengelig ---

FEIL = [
    httpx.ReadTimeout("tidsavbrudd"),
    httpx.ConnectTimeout("tidsavbrudd"),
    httpx.PoolTimeout("tidsavbrudd"),
    httpx.ConnectError("ingen forbindelse"),
    httpx.RemoteProtocolError("brutt"),
]


@respx.mock
@pytest.mark.parametrize("feil", FEIL, ids=lambda f: type(f).__name__)
def test_tidsavbrudd_og_nettverksfeil(feil: Exception) -> None:
    respx.post(DATA_URL).mock(side_effect=feil)
    with pytest.raises(fhi.FhiUtilgjengelig) as fanget:
        fhi.hent(UTVALG, SISTE)
    assert fanget.value.__cause__ is feil


@respx.mock
@pytest.mark.parametrize("status", [500, 502, 503, 404, 400, 429, 301, 302])
def test_http_feil(status: int) -> None:
    respx.post(DATA_URL).respond(status, json={"feil": "noe gikk galt"})
    with pytest.raises(fhi.FhiUtilgjengelig) as fanget:
        fhi.hent(UTVALG, SISTE)
    assert isinstance(fanget.value.__cause__, httpx.HTTPStatusError)


UGYLDIGE_SVAR = {
    "ikke-json": {"text": "<html>Vedlikehold</html>"},
    "tom": {"content": b""},
    "liste": {"json": [1, 2, 3]},
    "tomt-objekt": {"json": {}},
    "feil-aldersgruppe": {"json": KONSTRUERT},
    "ugyldig-utf8": {"content": b'{"a": "\xff"}'},
    "dypt-nøstet": {"content": b"[" * 100_000 + b"]" * 100_000},
}


@respx.mock
@pytest.mark.parametrize("svar", UGYLDIGE_SVAR.values(), ids=list(UGYLDIGE_SVAR))
def test_ugyldig_svar(svar: dict[str, Any]) -> None:
    respx.post(DATA_URL).respond(200, **svar)
    with pytest.raises(fhi.FhiUtilgjengelig) as fanget:
        fhi.hent(UTVALG, SISTE)
    assert fanget.value.__cause__ is not None or "JSON-objekt" in str(fanget.value)


@respx.mock
def test_lukket_klient_gir_fhiutilgjengelig() -> None:
    respx.post(DATA_URL).respond(json=DATA)
    klient = httpx.Client()
    klient.close()
    with pytest.raises(fhi.FhiUtilgjengelig):
        fhi.hent(UTVALG, SISTE, klient=klient)


@respx.mock
def test_hele_kallet_gir_opp_etter_tidsgrensen(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Et svar som drypper inn eller et navneoppslag som henger, stoppes av
    # grensen for hele kallet, ikke bare av grensen per steg.
    monkeypatch.setattr(fhi, "TOTAL_TIDSGRENSE", 0.2)
    slipp = threading.Event()

    def henger(request: httpx.Request) -> httpx.Response:
        slipp.wait(5)
        return httpx.Response(200, json=DATA)

    respx.post(DATA_URL).mock(side_effect=henger)
    start = time.monotonic()
    try:
        with pytest.raises(fhi.FhiUtilgjengelig) as fanget:
            fhi.hent(UTVALG, SISTE)
        assert time.monotonic() - start < 2
        assert isinstance(fanget.value.__cause__, TimeoutError)
    finally:
        slipp.set()


def test_total_tidsgrense_er_10_sekunder() -> None:
    assert fhi.TOTAL_TIDSGRENSE == 10.0


@respx.mock
def test_hodene_ber_om_json() -> None:
    rute = respx.post(DATA_URL).respond(json=DATA)
    fhi.hent(UTVALG, SISTE)
    hoder = rute.calls.last.request.headers
    assert hoder["accept"] == "application/json"
    assert hoder["content-type"] == "application/json"
    assert hoder["user-agent"].startswith("fhi-helsedata")


@respx.mock
@pytest.mark.parametrize(
    "svar",
    [
        {"side_effect": httpx.ReadTimeout("tidsavbrudd")},
        {"return_value": httpx.Response(500)},
        {"return_value": httpx.Response(200, text="ikke json")},
        {"return_value": httpx.Response(200, json={"dimensions": []})},
        {
            "return_value": httpx.Response(
                200,
                json={
                    "dimensions": [
                        {
                            "code": "dateusedforstatistics",
                            "categories": [
                                {"value": "2026-w21"},
                                {"value": "2026-w39"},
                            ],
                        }
                    ]
                },
            )
        },
    ],
    ids=["tidsavbrudd", "500", "ikke-json", "uten-uker", "uten-sesong"],
)
def test_dimensjonslisten_gir_også_fhiutilgjengelig(svar: dict[str, Any]) -> None:
    respx.get(DIMENSJON_URL).mock(**svar)
    with pytest.raises(fhi.FhiUtilgjengelig) as fanget:
        fhi.hent_dimensjoner(724)
    assert fanget.value.__cause__ is not None


def test_fhiutilgjengelig_er_ikke_en_valueerror() -> None:
    # `tjeneste` skal kunne skille FHI-feil fra programmeringsfeil.
    assert not issubclass(fhi.FhiUtilgjengelig, ValueError)


# --- Bare fhi.py kaller FHI (AD-3) ---


def test_bare_fhi_py_kaller_fhi() -> None:
    treff = [
        str(fil.relative_to(SRC))
        for fil in SRC.rglob("*.py")
        if "statistikk-data" in fil.read_text(encoding="utf-8")
        or "fhi.no" in fil.read_text(encoding="utf-8")
    ]
    assert treff == ["fhi.py"]


def _importerer_httpx(fil: Path) -> bool:
    moduler: set[str] = set()
    for node in ast.walk(ast.parse(fil.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            moduler |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            moduler.add(node.module or "")
    return any(m.split(".")[0] == "httpx" for m in moduler)


def test_bare_fhi_py_importerer_httpx() -> None:
    treff = [
        str(fil.relative_to(SRC)) for fil in SRC.rglob("*.py") if _importerer_httpx(fil)
    ]
    assert treff == ["fhi.py"]
