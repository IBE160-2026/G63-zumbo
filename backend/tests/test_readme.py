"""Sjekker at README i reporoten forklarer hvordan man kommer i gang (story 1.5)."""

from pathlib import Path

import pytest

# backend/tests/test_readme.py -> reporoten. Trenger ikke git.
README = Path(__file__).resolve().parents[2] / "README.md"


@pytest.fixture(scope="module")
def readme() -> str:
    return README.read_text(encoding="utf-8")


def _seksjon(readme: str, overskrift: str) -> str:
    etter = readme.split(overskrift, 1)[1]
    return etter.split("\n#", 1)[0]


@pytest.mark.parametrize(
    "kommando",
    ["uv sync", "uv run pytest", "uv run ruff check", "uv run ruff format --check"],
)
def test_readme_nevner_kommandoen(readme: str, kommando: str) -> None:
    assert kommando in readme


def test_readme_har_plass_for_oppstart(readme: str) -> None:
    # Plassen fylles ut i story 3.1 (AD-11). Da må denne testen endres med vilje.
    assert "### Starte appen" in readme
    assert "story 3.1" in _seksjon(readme, "### Starte appen")


def test_readme_sier_at_env_er_valgfri(readme: str) -> None:
    tekst = readme.lower()
    assert "`.env` er valgfri" in tekst
    assert "appen virker uten ki-nøkkel" in tekst
