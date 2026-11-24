"""Tester for tolkingen av FHI-svar (story 2.4, FR-3, FR-6, FR-11, FR-16, AD-3)."""

import ast
import copy
import json
from pathlib import Path
from typing import Any

import pytest

from backend import fhi, sesong
from backend.domene import Uke, Utvalg

FIXTURES = Path(__file__).parent / "fixtures"


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
DIMENSJONER = _svar("fhi/724-dimensjoner.json")
KONSTRUERT = _svar("konstruert/724-skjulte-verdier.json")
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
UTVALG_80 = Utvalg(1, "influensa", "2026/2027", "80+")


# --- Fixturen for tabell 724 ---


def test_én_uke_per_forventet_uke_i_sesongen() -> None:
    serie = fhi.tolk(DATA, UTVALG, fhi.siste_publiserte_uke(DIMENSJONER))
    assert serie.utvalg == UTVALG
    assert [(u.år, u.ukenummer) for u in serie.uker] == list(sesong.uker("2025/2026"))
    assert len(serie.uker) == 33


@pytest.mark.parametrize(
    ("uke", "tester", "positive", "andel"),
    [
        ((2025, 40), 7023, 64, 0.9112915),
        ((2025, 52), 5822, 1477, 25.36929),
        ((2026, 20), 4552, 37, None),
    ],
)
def test_tre_uker_stemmer_med_fixturen(
    uke: tuple[int, int], tester: int, positive: int, andel: float | None
) -> None:
    serie = fhi.tolk(DATA, UTVALG)
    (funnet,) = [u for u in serie.uker if (u.år, u.ukenummer) == uke]
    assert (funnet.tester, funnet.positive) == (tester, positive)
    assert funnet.andel == pytest.approx(positive * 100 / tester)
    if andel is not None:
        assert funnet.andel == pytest.approx(andel, abs=1e-4)


def test_andelen_stemmer_med_fhis_pos_rate_for_alle_uker() -> None:
    plass = {
        k: i
        for i, k in enumerate(DATA["dimension"]["MEASURE_TYPE"]["category"]["index"])
    }
    rader = [DATA["value"][i : i + 3] for i in range(0, len(DATA["value"]), 3)]
    serie = fhi.tolk(DATA, UTVALG)
    for uke, rad in zip(serie.uker, rader, strict=True):
        assert uke.andel == pytest.approx(rad[plass["pos_rate"]], abs=1e-4)


def test_fixturen_har_ingen_manglende_eller_usikre_uker() -> None:
    serie = fhi.tolk(DATA, UTVALG)
    assert not any(u.manglende or u.usikker for u in serie.uker)
    # Irenes beslutning i story 2.4: sjekket at ingen uke har flere positive enn tester.
    assert not any(u.flere_positive_enn_tester for u in serie.uker)


def test_uten_siste_publiserte_uke_brukes_høyeste_uke_i_svaret() -> None:
    assert fhi.tolk(DATA, UTVALG) == fhi.tolk(DATA, UTVALG, (2026, 46))


def test_sesongen_som_pågår_stopper_ved_siste_publiserte_uke() -> None:
    serie = fhi.tolk(DATA, UTVALG, (2025, 45))
    assert [(u.år, u.ukenummer) for u in serie.uker][-1] == (2025, 45)
    assert len(serie.uker) == 6


# --- Dimensjonslisten ---


def test_siste_publiserte_uke_fra_dimensjonslisten() -> None:
    assert fhi.siste_publiserte_uke(DIMENSJONER) == (2026, 46)


def test_sesonglisten_fra_dimensjonslisten() -> None:
    assert fhi.sesonger(DIMENSJONER) == ("2024/2025", "2025/2026", "2026/2027")


def _dimensjoner(*koder: str) -> dict[str, Any]:
    kategorier = [{"label": k, "value": k, "children": []} for k in koder]
    return {"dimensions": [{"code": "dateusedforstatistics", "categories": kategorier}]}


@pytest.mark.parametrize(
    ("koder", "forventet"),
    [
        (("2026-w21", "2026-w39"), ()),
        (("2026-w39", "2026-w40"), ("2026/2027",)),
        (("2027-w20",), ("2026/2027",)),
        (("2023-w45", "2024-w10", "2024-w40"), ("2024/2025",)),
        (("2026-w53", "2026-w40"), ("2026/2027",)),
    ],
)
def test_sesonger_bare_fra_uke_40_til_uke_20(
    koder: tuple[str, ...], forventet: tuple[str, ...]
) -> None:
    assert fhi.sesonger(_dimensjoner(*koder)) == forventet


def test_siste_publiserte_uke_tar_høyeste_uke_også_uten_rekkefølge() -> None:
    assert fhi.siste_publiserte_uke(_dimensjoner("2027-w02", "2026-w53")) == (2027, 2)


@pytest.mark.parametrize(
    "dimensjoner",
    [
        {},
        {"dimensions": []},
        _dimensjoner(),
        _dimensjoner("2026-W40"),
        _dimensjoner("2025-w53"),
    ],
)
def test_ugyldig_dimensjonsliste(dimensjoner: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        fhi.siste_publiserte_uke(dimensjoner)


# --- Konstruert svar med skjulte verdier og en manglende uke ---


def test_skjulte_verdier_og_manglende_uke_blir_none() -> None:
    serie = fhi.tolk(KONSTRUERT, UTVALG_80, (2026, 46))
    assert serie.uker == (
        Uke(2026, 40, 250, 12),
        Uke(2026, 41, None, 3),  # «..»
        Uke(2026, 42, 40, None),  # «.»
        Uke(2026, 43, None, None),  # «:» og tom verdi
        Uke(2026, 44, None, None),  # uka er ikke med i svaret
        Uke(2026, 45, 100, None),  # null
        Uke(2026, 46, 29, 0),  # en ekte null er 0
    )
    manglende = [u.ukenummer for u in serie.uker if u.manglende]
    assert manglende == [41, 42, 43, 44, 45]
    assert all(u.andel is None for u in serie.uker if u.manglende)
    assert serie.uker[-1].andel == 0.0
    assert serie.uker[-1].usikker


def test_ingen_skjult_verdi_blir_null() -> None:
    serie = fhi.tolk(KONSTRUERT, UTVALG_80)
    nuller = [
        (u.ukenummer, u.tester, u.positive)
        for u in serie.uker
        if 0 in (u.tester, u.positive)
    ]
    assert nuller == [(46, 29, 0)]


def test_konstruert_svar_frem_til_siste_publiserte_uke() -> None:
    serie = fhi.tolk(KONSTRUERT, UTVALG_80, (2026, 48))
    assert [u.ukenummer for u in serie.uker] == list(range(40, 49))
    assert serie.uker[-1].manglende


def test_verdiene_kan_være_et_objekt_med_plass_og_verdi() -> None:
    svar = copy.deepcopy(KONSTRUERT)
    svar["value"] = {str(i): v for i, v in enumerate(svar["value"]) if v is not None}
    svar["dimension"]["dateusedforstatistics"]["category"]["index"] = list(
        svar["dimension"]["dateusedforstatistics"]["category"]["index"]
    )
    assert fhi.tolk(svar, UTVALG_80) == fhi.tolk(KONSTRUERT, UTVALG_80)


def test_rekkefølgen_på_dimensjonene_følger_id() -> None:
    svar = copy.deepcopy(KONSTRUERT)
    rader = [svar["value"][i : i + 3] for i in range(0, len(svar["value"]), 3)]
    svar["id"] = ["MEASURE_TYPE", *svar["id"][:-1]]
    svar["size"] = [3, *svar["size"][:-1]]
    svar["value"] = [rad[m] for m in range(3) for rad in rader]
    assert fhi.tolk(svar, UTVALG_80) == fhi.tolk(KONSTRUERT, UTVALG_80)


# --- Ugyldige svar ---


def _endret(**endringer: Any) -> dict[str, Any]:
    svar = copy.deepcopy(KONSTRUERT)
    for sti, verdi in endringer.items():
        mål = svar
        *deler, siste = sti.split("__")
        for del_ in deler:
            mål = mål[del_]
        mål[siste] = verdi
    return svar


@pytest.mark.parametrize(
    "svar",
    [
        {},
        _endret(value=[1, 2, 3]),
        _endret(value="1,2,3"),
        _endret(size=[6, 1, 1, 1, 2]),
        _endret(id=["dateusedforstatistics", "aldersgruppe"]),
        _endret(dimension__aldersgruppe__category__index={"Alle": 0}),
        _endret(dimension__surveillancetype__category__index={"STL": 0}),
        _endret(dimension__influenzatypeandsubtype__category__index={"A": 0}),
        _endret(
            dimension__MEASURE_TYPE__category__index={"Detections": 0, "x": 1, "y": 2}
        ),
    ],
    ids=[
        "tomt",
        "feil-lengde",
        "value-tekst",
        "feil-size",
        "feil-id",
        "annen-aldersgruppe",
        "fyrtårn",
        "bare-a",
        "mangler-tester",
    ],
)
def test_ugyldig_svar_gir_valueerror(svar: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        fhi.tolk(svar, UTVALG_80)


@pytest.mark.parametrize("verdi", ["12", "x", True, -1, 1.5, float("nan"), [1]])
def test_ugyldig_antall_gir_valueerror(verdi: Any) -> None:
    svar = copy.deepcopy(KONSTRUERT)
    svar["value"][1] = verdi
    with pytest.raises(ValueError):
        fhi.tolk(svar, UTVALG_80)


def test_heltall_skrevet_som_desimaltall_godtas() -> None:
    svar = copy.deepcopy(KONSTRUERT)
    svar["value"][0:2] = [12.0, 250.0]
    assert fhi.tolk(svar, UTVALG_80).uker[0] == Uke(2026, 40, 250, 12)


def test_svar_for_feil_sesong_gir_bare_manglende_uker() -> None:
    serie = fhi.tolk(KONSTRUERT, Utvalg(1, "influensa", "2025/2026", "80+"), (2026, 46))
    assert len(serie.uker) == 33
    assert all(u.manglende for u in serie.uker)


def test_andre_tabeller_kan_ikke_tolkes_ennå() -> None:
    with pytest.raises(ValueError):
        fhi.tolk(KONSTRUERT, Utvalg(1, "rsv", "2026/2027", "80+"))


# --- Ren kjerne (AD-1) ---


def test_tolkingen_importerer_ikke_skallmoduler() -> None:
    tre = ast.parse(Path(fhi.__file__).read_text(encoding="utf-8"))
    moduler: set[str] = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            moduler.add(node.module or "")
    forbudt = {
        "httpx",
        "anthropic",
        "backend.mellomlager",
        "backend.config",
        "backend.web",
    }
    assert moduler & forbudt == set()
    assert {m for m in moduler if m.startswith("backend")} <= {
        "backend",
        "backend.domene",
        "backend.sesong",
    }
