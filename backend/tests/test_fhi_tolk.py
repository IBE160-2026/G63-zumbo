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
        ((2026, 20), 4552, 37, 0.8128295),
    ],
)
def test_tre_uker_stemmer_med_fixturen(
    uke: tuple[int, int], tester: int, positive: int, andel: float
) -> None:
    serie = fhi.tolk(DATA, UTVALG)
    (funnet,) = [u for u in serie.uker if (u.år, u.ukenummer) == uke]
    assert (funnet.tester, funnet.positive) == (tester, positive)
    assert funnet.andel == pytest.approx(andel, abs=1e-4)


def test_andelen_stemmer_med_fhis_pos_rate_for_alle_uker() -> None:
    # Fixturen har uke først og måltall sist (se README-en), og lister som index.
    assert DATA["id"][0] == "dateusedforstatistics"
    assert DATA["id"][-1] == "MEASURE_TYPE"
    ukekoder = DATA["dimension"]["dateusedforstatistics"]["category"]["index"]
    måltall = DATA["dimension"]["MEASURE_TYPE"]["category"]["index"]
    plass = måltall.index("pos_rate")
    fra_fhi = {
        fhi.les_ukekode(kode): DATA["value"][i * len(måltall) + plass]
        for i, kode in enumerate(ukekoder)
    }
    serie = fhi.tolk(DATA, UTVALG)
    assert len(fra_fhi) == len(serie.uker)
    for uke in serie.uker:
        forventet = fra_fhi[(uke.år, uke.ukenummer)]
        assert uke.andel == pytest.approx(forventet, abs=1e-4)


def test_fixturen_har_ingen_manglende_eller_usikre_uker() -> None:
    serie = fhi.tolk(DATA, UTVALG)
    assert not any(u.manglende or u.usikker for u in serie.uker)
    # Irenes beslutning i story 2.4: sjekket at ingen uke har flere positive enn tester.
    assert not any(u.flere_positive_enn_tester for u in serie.uker)


def test_uten_siste_publiserte_uke_brukes_høyeste_uke_i_svaret() -> None:
    assert fhi.tolk(DATA, UTVALG) == fhi.tolk(DATA, UTVALG, (2026, 46))


def _svar_til_uke_45() -> dict[str, Any]:
    """Det konstruerte svaret med ukene 40–45 (uke 46 heter uke 44 i stedet)."""
    svar = copy.deepcopy(KONSTRUERT)
    kategori = svar["dimension"]["dateusedforstatistics"]["category"]
    kategori["index"] = [f"2026-w{u}" for u in (40, 41, 42, 43, 45, 44)]
    del kategori["label"]
    return svar


def test_sesongen_som_pågår_stopper_ved_siste_publiserte_uke() -> None:
    serie = fhi.tolk(_svar_til_uke_45(), UTVALG_80, (2026, 45))
    assert [u.ukenummer for u in serie.uker] == list(range(40, 46))
    serie = fhi.tolk(_svar_til_uke_45(), UTVALG_80, (2026, 47))
    assert [u.ukenummer for u in serie.uker] == list(range(40, 48))


def test_uker_i_svaret_etter_siste_publiserte_uke_forsvinner_ikke() -> None:
    assert len(fhi.tolk(DATA, UTVALG, (2025, 45)).uker) == 33
    serie = fhi.tolk(KONSTRUERT, UTVALG_80, (2026, 42))
    assert serie.uker[-1] == Uke(2026, 46, 29, 0)


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
@pytest.mark.parametrize("funksjon", [fhi.siste_publiserte_uke, fhi.sesonger])
def test_ugyldig_dimensjonsliste(funksjon: Any, dimensjoner: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        funksjon(dimensjoner)


def test_dimensjonsliste_uten_noen_sesong_gir_valueerror() -> None:
    with pytest.raises(ValueError):
        fhi.sesonger(_dimensjoner("2026-w21", "2026-w39"))


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


@pytest.mark.parametrize(
    "verdi", ["12", "x", True, -1, 1.5, float("nan"), float("inf"), [1], 10**400]
)
def test_ugyldig_antall_gir_valueerror(verdi: Any) -> None:
    svar = copy.deepcopy(KONSTRUERT)
    svar["value"][1] = verdi
    with pytest.raises(ValueError):
        fhi.tolk(svar, UTVALG_80)


def test_heltall_skrevet_som_desimaltall_godtas() -> None:
    svar = copy.deepcopy(KONSTRUERT)
    svar["value"][0:2] = [12.0, 250.0]
    assert fhi.tolk(svar, UTVALG_80).uker[0] == Uke(2026, 40, 250, 12)


@pytest.mark.parametrize("siste", [None, (2026, 46)])
def test_svar_for_feil_sesong_gir_valueerror(siste: tuple[int, int] | None) -> None:
    with pytest.raises(ValueError, match="utenfor sesongen"):
        fhi.tolk(KONSTRUERT, Utvalg(1, "influensa", "2025/2026", "80+"), siste)
    with pytest.raises(ValueError, match="utenfor sesongen"):
        fhi.tolk(DATA, Utvalg(1, "influensa", "2026/2027", "alle"), siste)


def test_svar_med_en_uke_utenfor_sesongen_gir_valueerror() -> None:
    svar = copy.deepcopy(KONSTRUERT)
    kategori = svar["dimension"]["dateusedforstatistics"]["category"]
    kategori["index"] = [f"2026-w{u}" for u in (39, 41, 42, 43, 45, 46)]
    with pytest.raises(ValueError, match="utenfor sesongen"):
        fhi.tolk(svar, UTVALG_80)


def test_plassene_i_index_brukes_ikke_rekkefølgen_på_nøklene() -> None:
    svar = copy.deepcopy(KONSTRUERT)
    svar["dimension"]["MEASURE_TYPE"]["category"]["index"] = {
        "Tests": 1,
        "pos_rate": 2,
        "Detections": 0,
    }
    uker = svar["dimension"]["dateusedforstatistics"]["category"]
    uker["index"] = dict(reversed(list(uker["index"].items())))
    assert fhi.tolk(svar, UTVALG_80) == fhi.tolk(KONSTRUERT, UTVALG_80)


@pytest.mark.parametrize(
    "indeks",
    [
        {"Detections": 0, "Tests": 2, "pos_rate": 3},
        {"Detections": 0, "Tests": 0, "pos_rate": 2},
        ["Detections", "Tests", "Tests"],
    ],
)
def test_ugyldige_plasser_i_index_gir_valueerror(indeks: Any) -> None:
    svar = copy.deepcopy(KONSTRUERT)
    svar["dimension"]["MEASURE_TYPE"]["category"]["index"] = indeks
    with pytest.raises(ValueError):
        fhi.tolk(svar, UTVALG_80)


def test_samme_uke_to_ganger_gir_valueerror() -> None:
    svar = copy.deepcopy(KONSTRUERT)
    kategori = svar["dimension"]["dateusedforstatistics"]["category"]
    kategori["index"] = [f"2026-w{u}" for u in (40, 41, 42, 43, 45, 45)]
    with pytest.raises(ValueError):
        fhi.tolk(svar, UTVALG_80)


def test_flere_aldersgrupper_i_svaret_gir_valueerror() -> None:
    svar = copy.deepcopy(KONSTRUERT)
    svar["dimension"]["aldersgruppe"]["category"]["index"] = {"80+ år": 0, "Alle": 1}
    svar["size"][1] = 2
    rader = [svar["value"][i : i + 3] for i in range(0, len(svar["value"]), 3)]
    svar["value"] = [x for rad in rader for x in rad + rad]
    with pytest.raises(ValueError, match="kategorier"):
        fhi.tolk(svar, UTVALG_80)


@pytest.mark.parametrize("dimensjon", ["surveillancetype", "influenzatypeandsubtype"])
def test_svar_uten_et_fast_filter_gir_valueerror(dimensjon: str) -> None:
    svar = copy.deepcopy(KONSTRUERT)
    plass = svar["id"].index(dimensjon)
    del svar["id"][plass], svar["size"][plass], svar["dimension"][dimensjon]
    with pytest.raises(ValueError, match="mangler"):
        fhi.tolk(svar, UTVALG_80)


def test_flere_positive_enn_tester_gjennom_tolk() -> None:
    # Irenes beslutning i story 2.4: andelen vises som den er, og uka er usikker.
    svar = copy.deepcopy(KONSTRUERT)
    svar["value"][0:2] = [300, 250]
    uke = fhi.tolk(svar, UTVALG_80).uker[0]
    assert uke == Uke(2026, 40, 250, 300)
    assert uke.andel == 120.0
    assert uke.flere_positive_enn_tester
    assert uke.usikker
    assert not uke.manglende


def test_andre_tabeller_kan_ikke_tolkes_ennå() -> None:
    with pytest.raises(ValueError):
        fhi.tolk(KONSTRUERT, Utvalg(1, "rsv", "2026/2027", "80+"))


# --- Ren kjerne (AD-1) ---

SKALLFUNKSJONER = {"_kall", "_kall_i_tråd", "hent", "hent_dimensjoner"}
"""Funksjonene i fhi.py som får bruke nettet. Alle andre skal være rene (AD-1)."""


def test_fhi_importerer_ikke_andre_skallmoduler() -> None:
    tre = ast.parse(Path(fhi.__file__).read_text(encoding="utf-8"))
    moduler: set[str] = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            moduler.add(node.module or "")
    forbudt = {"anthropic", "backend.mellomlager", "backend.config", "backend.web"}
    assert moduler & forbudt == set()
    assert {m for m in moduler if m.startswith("backend")} <= {
        "backend",
        "backend.domene",
        "backend.sesong",
    }


def test_alle_andre_funksjoner_enn_skallet_er_rene() -> None:
    tre = ast.parse(Path(fhi.__file__).read_text(encoding="utf-8"))
    funksjoner = {
        node.name: node for node in tre.body if isinstance(node, ast.FunctionDef)
    }
    assert SKALLFUNKSJONER <= set(funksjoner)
    assert {"tolk", "siste_publiserte_uke", "sesonger"} <= set(funksjoner)
    urent = SKALLFUNKSJONER | {"httpx", "open", "socket", "ThreadPoolExecutor"}
    for navn, funksjon in funksjoner.items():
        if navn in SKALLFUNKSJONER:
            continue
        brukt = {n.id for n in ast.walk(funksjon) if isinstance(n, ast.Name)}
        assert brukt & urent == set(), (navn, brukt & urent)
        assert not any(
            isinstance(n, ast.Import | ast.ImportFrom) for n in ast.walk(funksjon)
        ), navn


# --- Fixturen for tabell 729, RSV (story 6.1) ---

RSV_DATA = _svar("fhi/729-rsv-2025-2026-alle-nonstl.json")
RSV_DIMENSJONER = _svar("fhi/729-dimensjoner.json")
RSV_UTVALG = Utvalg(1, "rsv", "2025/2026", "alle")


def test_rsv_fixturen_gir_én_uke_per_uke_i_sesongen() -> None:
    serie = fhi.tolk(RSV_DATA, RSV_UTVALG, fhi.siste_publiserte_uke(RSV_DIMENSJONER))
    assert serie.utvalg == RSV_UTVALG
    assert [(u.år, u.ukenummer) for u in serie.uker] == list(sesong.uker("2025/2026"))
    assert not any(u.manglende or u.usikker for u in serie.uker)


@pytest.mark.parametrize(
    ("uke", "tester", "positive", "andel"),
    [
        ((2025, 40), 6487, 13, 0.2004008),
        ((2025, 52), 4951, 165, 3.33266),
        ((2026, 20), 4461, 104, 2.331316),
    ],
)
def test_rsv_tre_uker_stemmer_med_fixturen(
    uke: tuple[int, int], tester: int, positive: int, andel: float
) -> None:
    serie = fhi.tolk(RSV_DATA, RSV_UTVALG)
    (funnet,) = [u for u in serie.uker if (u.år, u.ukenummer) == uke]
    assert (funnet.tester, funnet.positive) == (tester, positive)
    assert funnet.andel == pytest.approx(andel, abs=1e-4)


def test_rsv_dimensjonslisten_har_samme_uker_som_724() -> None:
    assert fhi.siste_publiserte_uke(RSV_DIMENSJONER) == fhi.siste_publiserte_uke(
        DIMENSJONER
    )
    assert fhi.sesonger(RSV_DIMENSJONER) == fhi.sesonger(DIMENSJONER)


def test_svar_fra_724_tolket_som_rsv_gir_valueerror() -> None:
    with pytest.raises(ValueError, match="rsvtype"):
        fhi.tolk(DATA, RSV_UTVALG)


def test_svar_fra_729_tolket_som_influensa_gir_valueerror() -> None:
    with pytest.raises(ValueError):
        fhi.tolk(RSV_DATA, UTVALG)


def test_rsv_svar_med_annen_rsvtype_gir_valueerror() -> None:
    svar = copy.deepcopy(RSV_DATA)
    svar["dimension"]["rsvtype"]["category"]["index"] = ["A"]
    svar["dimension"]["rsvtype"]["category"]["label"] = {"A": "RS-virus A"}
    with pytest.raises(ValueError, match="rsvtype"):
        fhi.tolk(svar, RSV_UTVALG)


# --- Fixturen for tabell 731, SARS-CoV-2 (story 6.2) ---

SARS_DATA = _svar("fhi/731-sars-cov-2-2025-2026-alle-nonstl.json")
SARS_DIMENSJONER = _svar("fhi/731-dimensjoner.json")
SARS_UTVALG = Utvalg(1, "sars-cov-2", "2025/2026", "alle")


def test_sars_cov_2_fixturen_gir_én_uke_per_uke_i_sesongen() -> None:
    serie = fhi.tolk(SARS_DATA, SARS_UTVALG, fhi.siste_publiserte_uke(SARS_DIMENSJONER))
    assert serie.utvalg == SARS_UTVALG
    assert [(u.år, u.ukenummer) for u in serie.uker] == list(sesong.uker("2025/2026"))
    assert not any(u.manglende or u.usikker for u in serie.uker)


@pytest.mark.parametrize(
    ("uke", "tester", "positive", "andel"),
    [
        ((2025, 40), 7109, 471, 6.625404),
        ((2025, 52), 5691, 210, 3.690037),
        ((2026, 20), 4543, 14, 0.3081664),
    ],
)
def test_sars_cov_2_tre_uker_stemmer_med_fixturen(
    uke: tuple[int, int], tester: int, positive: int, andel: float
) -> None:
    # I 731-svaret står `aldersgruppe` foran ukene i `id`.
    assert SARS_DATA["id"][0] == "aldersgruppe"
    serie = fhi.tolk(SARS_DATA, SARS_UTVALG)
    (funnet,) = [u for u in serie.uker if (u.år, u.ukenummer) == uke]
    assert (funnet.tester, funnet.positive) == (tester, positive)
    assert funnet.andel == pytest.approx(andel, abs=1e-4)


def test_sars_cov_2_dimensjonslisten_har_samme_uker_som_724() -> None:
    assert fhi.siste_publiserte_uke(SARS_DIMENSJONER) == fhi.siste_publiserte_uke(
        DIMENSJONER
    )
    assert fhi.sesonger(SARS_DIMENSJONER) == fhi.sesonger(DIMENSJONER)


@pytest.mark.parametrize(
    ("svar", "typedimensjon"),
    [(DATA, "influenzatypeandsubtype"), (RSV_DATA, "rsvtype")],
    ids=["724", "729"],
)
def test_svar_med_typedimensjon_tolket_som_sars_cov_2_gir_valueerror(
    svar: dict[str, Any], typedimensjon: str
) -> None:
    with pytest.raises(ValueError, match=typedimensjon):
        fhi.tolk(svar, SARS_UTVALG)


@pytest.mark.parametrize("utvalg", [UTVALG, RSV_UTVALG], ids=["influensa", "rsv"])
def test_svar_fra_731_tolket_som_annet_virus_gir_valueerror(utvalg: Utvalg) -> None:
    # 731 har ingen typedimensjon, så svaret mangler den utvalget krever.
    with pytest.raises(ValueError, match="mangler"):
        fhi.tolk(SARS_DATA, utvalg)


def test_sars_cov_2_svar_med_annen_overvåkingstype_gir_valueerror() -> None:
    svar = copy.deepcopy(SARS_DATA)
    svar["dimension"]["surveillancetype"]["category"]["index"] = ["STL"]
    svar["dimension"]["surveillancetype"]["category"]["label"] = {"STL": "Sentinel"}
    with pytest.raises(ValueError, match="surveillancetype"):
        fhi.tolk(svar, SARS_UTVALG)


def test_alle_tabellene_i_virus_har_faste_filtre() -> None:
    from backend.domene import VIRUS

    assert {v.tabell for v in VIRUS.values()} <= set(fhi.FASTE_FILTRE)
