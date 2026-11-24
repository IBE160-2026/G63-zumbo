"""Tester for `formatering` (story 4.3, arkitektur §4).

Tabellen på siden og prompten til KI-en bruker de samme funksjonene, så ukene
står likt begge steder (Irenes beslutning på #23).
"""

import ast
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend import formatering, web
from backend.domene import Uke, kildehenvisning

NBSP = " "


@pytest.mark.parametrize(
    ("verdi", "tekst"),
    [
        (
            Uke(2025, 50, 1210, 252),
            f"uke 50: 1{NBSP}210 tester, 252 positive, 20,8{NBSP}%",
        ),
        (Uke(2026, 3, None, 5), "uke 3: skjult tester, 5 positive, mangler"),
        (Uke(2026, 3, 40, None), "uke 3: 40 tester, skjult positive, mangler"),
        (Uke(2025, 41, 0, 0), "uke 41: 0 tester, 0 positive, kan ikke regnes ut"),
    ],
)
def test_ukelinje_viser_uka_slik_tabellen_gjør(verdi: Uke, tekst: str) -> None:
    assert formatering.ukelinje(verdi) == tekst


def test_ukelinje_bruker_de_samme_tekstene_som_tabellen() -> None:
    u = Uke(2025, 50, 12345, 678)
    assert formatering.ukelinje(u) == (
        f"{web.uke(u)}: {web.tall(u.tester)} tester, "
        f"{web.tall(u.positive)} positive, {web.andelstekst(u)}"
    )


def test_kildetekst_er_den_samme_som_under_grafen() -> None:
    kilde = kildehenvisning(724, datetime(2026, 11, 20, 13, 5, tzinfo=UTC))
    assert formatering.kildetekst(kilde) == (
        "Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, "
        "Folkehelseinstituttet (FHI). Tabell 724 «RESPIaggr Influensa antall og "
        "andel». Hentet 20.11.2026 kl. 14:05."
    )


def test_formatering_importerer_bare_domene_og_standardbiblioteket() -> None:
    tre = ast.parse(Path(formatering.__file__).read_text(encoding="utf-8"))
    moduler: set[str] = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            moduler.add(node.module or "")
    utenfor = {m for m in moduler if m.split(".")[0] not in sys.stdlib_module_names}
    assert utenfor <= {"backend.domene"}, utenfor
