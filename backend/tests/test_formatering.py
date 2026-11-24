"""Tester for `formatering` (story 4.3, arkitektur §4).

Tabellen på siden og prompten til KI-en bruker de samme funksjonene, så tallene
er de samme begge steder (Irenes beslutning på #23).
"""

import ast
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend import formatering, web
from backend.domene import kildehenvisning


@pytest.mark.parametrize(
    "navn", ["tall", "andelstekst", "uke", "kildetekst", "utvalgstekst"]
)
def test_tabellen_bruker_de_samme_funksjonene_som_prompten(navn: str) -> None:
    # Tabellen og kilden på siden lages med Jinja2-filtrene i `web`. Er filtrene
    # de samme funksjonene som `ki` bruker, er tallene de samme.
    assert web.maler.env.filters[navn] is getattr(formatering, navn)


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
