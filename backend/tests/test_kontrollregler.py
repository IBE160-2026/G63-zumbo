"""Tester for kontrollreglene (story 2.7 og 2.8, FR-14–FR-19, SM-3, AD-1, AD-10).

Grensetilfellene ligger som konstruerte FHI-svar i `fixtures/konstruert/`, i samme
format som cachen. De tolkes med `fhi.tolk`, slik appen gjør med ekte svar.
"""

import ast
import json
import sys
from pathlib import Path

import pytest

from backend import fhi, kontrollregler
from backend.domene import Dataserie, Regelutslag, Uke, Utvalg

KONSTRUERT = Path(__file__).parent / "fixtures" / "konstruert"
ALLE_2025 = Utvalg(1, "influensa", "2025/2026", "alle")


def serie_fra_fixtur(navn: str, utvalg: Utvalg = ALLE_2025) -> Dataserie:
    svar = json.loads((KONSTRUERT / navn).read_text(encoding="utf-8"))["svar"]
    return fhi.tolk(svar, utvalg)


def serie_av(*tall: tuple[int | None, int | None]) -> Dataserie:
    """En serie fra uke 40 i 2025 med (tester, positive) per uke."""
    uker = []
    for i, (tester, positive) in enumerate(tall):
        år, uke = (2025, 40 + i) if 40 + i <= 52 else (2026, 40 + i - 52)
        uker.append(Uke(år, uke, tester, positive))
    return Dataserie(ALLE_2025, tuple(uker))


def utslag_for(serie: Dataserie, regel: str) -> Regelutslag | None:
    treff = [u for u in kontrollregler.vurder(serie) if u.regel == regel]
    assert len(treff) <= 1
    return treff[0] if treff else None


# --- R1: få positive prøver (FR-14) ---


def test_r1_slår_inn_ved_19_positive() -> None:
    serie = serie_fra_fixtur("724-r1-19-positive.json")
    assert len(serie.uker) == 10
    assert sum(1 for u in serie.uker if u.positive is None) == 1
    utslag = utslag_for(serie, "R1")
    assert utslag == Regelutslag(
        "R1",
        "Utvalget har bare 19 positive prøver. Det trengs minst 20 for et sikkert tall.",
    )


def test_r1_slår_ikke_inn_ved_20_positive() -> None:
    serie = serie_fra_fixtur("724-r1-20-positive.json")
    assert sum(1 for u in serie.uker if u.positive is None) == 1
    assert utslag_for(serie, "R1") is None


def test_r1_teller_ikke_skjulte_verdier_som_noe() -> None:
    # 19 kjente positive og én skjult verdi gir fortsatt utslag.
    serie = serie_av((100, 19), (100, None), (None, None))
    assert "19 positive" in utslag_for(serie, "R1").tekst


def test_r1_teller_kjente_positive_når_bare_testene_er_skjult() -> None:
    serie = serie_av((100, 10), (None, 10))
    assert utslag_for(serie, "R1") is None


@pytest.mark.parametrize(
    ("positive", "tekst"),
    [
        (0, "Utvalget har ingen positive prøver."),
        (1, "Utvalget har bare 1 positiv prøve."),
        (6, "Utvalget har bare 6 positive prøver."),
    ],
)
def test_r1_setningen_bruker_de_faktiske_tallene(positive: int, tekst: str) -> None:
    utslag = utslag_for(serie_av((100, positive)), "R1")
    assert utslag.tekst.startswith(tekst)


# --- R2: mange uker med få tester (FR-15) ---


def test_r2_slår_ikke_inn_ved_4_av_20_uker() -> None:
    serie = serie_fra_fixtur("724-r2-4-av-20-uker.json")
    assert len(serie.uker) == 20
    # Fixturen har også en uke med 30 tester, en med skjult antall tester og en
    # med flere positive enn tester. Teller noen av dem, blir det 5 av 20.
    assert sum(1 for u in serie.uker if u.tester == 30) == 1
    assert sum(1 for u in serie.uker if u.tester is None) == 1
    assert sum(1 for u in serie.uker if u.flere_positive_enn_tester) == 1
    assert utslag_for(serie, "R2") is None


def test_r2_slår_inn_ved_5_av_20_uker() -> None:
    serie = serie_fra_fixtur("724-r2-5-av-20-uker.json")
    assert utslag_for(serie, "R2") == Regelutslag(
        "R2", "5 av 20 uker har færre enn 30 tester."
    )


def test_r2_29_tester_teller_og_30_teller_ikke() -> None:
    # 1 av 4 uker er 25 % (utslag). Med 30 tester er det 0 av 4.
    assert utslag_for(serie_av((29, 1), (100, 5), (100, 5), (100, 5)), "R2")
    assert utslag_for(serie_av((30, 1), (100, 5), (100, 5), (100, 5)), "R2") is None


def test_r2_teller_ikke_skjult_antall_tester() -> None:
    serie = serie_av((None, 1), (100, 5), (100, 5), (100, 5))
    assert serie.uker[0].usikker
    assert utslag_for(serie, "R2") is None


def test_r2_teller_ikke_flere_positive_enn_tester_med_minst_30_tester() -> None:
    # Testen fra story 2.4 (deferred-work): uka er usikker, men har 30 tester
    # eller mer, så den telles ikke i R2.
    serie = serie_av((40, 45), (100, 5), (100, 5), (100, 5))
    assert serie.uker[0].usikker and serie.uker[0].flere_positive_enn_tester
    assert utslag_for(serie, "R2") is None


def test_r2_teller_uke_med_0_tester() -> None:
    serie = serie_av((0, 3), (100, 5), (100, 5), (100, 5))
    assert utslag_for(serie, "R2").tekst == "1 av 4 uker har færre enn 30 tester."


# --- R3: mange manglende uker (FR-16) ---


def test_r3_slår_ikke_inn_ved_2_av_10_uker() -> None:
    serie = serie_fra_fixtur("724-r3-2-av-10-uker.json")
    assert len(serie.uker) == 10
    # Én av de to manglende ukene har to skjulte verdier. Teller den to ganger,
    # blir det 3 av 10.
    assert sum(1 for u in serie.uker if u.tester is None and u.positive is None) == 1
    assert utslag_for(serie, "R3") is None


def test_r3_slår_inn_ved_3_av_10_uker() -> None:
    serie = serie_fra_fixtur("724-r3-3-av-10-uker.json")
    assert len(serie.uker) == 10
    assert utslag_for(serie, "R3") == Regelutslag(
        "R3", "3 av 10 uker mangler tall eller har skjulte tall."
    )


# --- Alle regler ---


def test_ingen_utslag_gir_tom_liste() -> None:
    assert kontrollregler.vurder(serie_av(*[(100, 5)] * 10)) == []


def test_utslagene_kommer_i_rekkefølge() -> None:
    serie = serie_av((10, 1), (None, None), (None, None))
    assert [u.regel for u in kontrollregler.vurder(serie)] == ["R1", "R2", "R3"]


def test_tom_serie_gir_bare_r1() -> None:
    serie = Dataserie(ALLE_2025, ())
    assert [u.regel for u in kontrollregler.vurder(serie)] == ["R1"]


# --- Ren kjerne (AD-1) ---


def test_kontrollregler_importerer_bare_domene_og_standardbiblioteket() -> None:
    tre = ast.parse(Path(kontrollregler.__file__).read_text(encoding="utf-8"))
    moduler: set[str] = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "kontrollregler skal ikke ha relative importer"
            moduler.add(node.module or "")
    utenfor = {m for m in moduler if m.split(".")[0] not in sys.stdlib_module_names}
    assert utenfor <= {"backend.domene"}, utenfor
