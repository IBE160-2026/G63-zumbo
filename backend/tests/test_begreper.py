"""Tester for de faste begrepsforklaringene (story 3.6, FR-13).

Tekstene er Irenes fra story 3.5 (issue #19). Testene sjekker at alle sju
finnes, at hver har høyst tre setninger, og at modulen hører til den rene
kjernen.
"""

import ast
import re
import sys
from pathlib import Path

import pytest

from backend import begreper
from backend.begreper import BEGREPER, TYNT_DATAGRUNNLAG

NAVN = [
    "Andel positive",
    "Test og positiv prøve",
    "Sesong",
    "Aldersgruppe",
    "Overvåkingstype",
    "MSIS",
    "For tynt datagrunnlag",
]
"""De sju begrepene i FR-13, i samme rekkefølge."""


def setninger(tekst: str) -> int:
    """Antall setninger: punktum, spørsmålstegn eller utropstegn som står sist
    eller før mellomrom og stor bokstav.

    Slik telles ikke «1. mars» som to setninger.
    """
    return len(re.findall(r"[.!?](?=$|\s+[A-ZÆØÅ«])", tekst.strip()))


def test_alle_sju_begrepene_finnes() -> None:
    assert [b.navn for b in BEGREPER] == NAVN


@pytest.mark.parametrize("begrep", BEGREPER, ids=lambda b: b.nøkkel)
def test_hver_tekst_har_høyst_tre_setninger(begrep: begreper.Begrep) -> None:
    assert 1 <= setninger(begrep.tekst) <= 3, begrep.tekst


def test_setningstellingen() -> None:
    assert setninger("Én. To? Tre!") == 3
    assert setninger("Perioden går over 1. mars 2025. Da kom alle med.") == 2
    assert setninger("Andelen er 5 %. Den kan endre seg.") == 2


def test_nøklene_er_unike_og_gyldige_som_html_id() -> None:
    nøkler = [b.nøkkel for b in BEGREPER]
    assert len(set(nøkler)) == len(nøkler)
    for nøkkel in nøkler:
        assert re.fullmatch(r"[a-z0-9-]+", nøkkel), nøkkel
    assert BEGREPER[0].html_id == "begrep-andel-positive"


def test_varselets_begrep_finnes() -> None:
    begrep = next(b for b in BEGREPER if b.nøkkel == TYNT_DATAGRUNNLAG)
    assert begrep.navn == "For tynt datagrunnlag"


def test_overvåkingstype_nevner_klinisk_praksis_og_fyrtårnsystemet() -> None:
    tekst = next(b.tekst for b in BEGREPER if b.navn == "Overvåkingstype")
    assert "vanlig klinisk praksis" in tekst
    assert "Fyrtårnsystemet" in tekst


def test_test_og_positiv_prøve_sier_at_samme_person_kan_telles_flere_ganger() -> None:
    """Tallene teller analyser, ikke personer (PRD kapittel 3, «Test»)."""
    tekst = next(b.tekst for b in BEGREPER if b.navn == "Test og positiv prøve")
    assert "telles da flere ganger" in tekst


# --- Ren kjerne (AD-1) ---


def test_begreper_importerer_bare_standardbiblioteket() -> None:
    tre = ast.parse(Path(begreper.__file__).read_text(encoding="utf-8"))
    moduler: set[str] = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            moduler.add((node.module or "").split(".")[0])
    assert moduler <= set(sys.stdlib_module_names), moduler
