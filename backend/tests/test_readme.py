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


def test_readme_har_oppstartskommandoen(readme: str) -> None:
    # Fylt ut i story 3.1 (AD-11).
    seksjon = _seksjon(readme, "### Starte appen")
    assert "uv run uvicorn backend.web:app --reload" in seksjon
    assert "backend/" in seksjon
    assert "http://127.0.0.1:8000" in seksjon
    assert "story 3.1" not in seksjon


def test_readme_sier_at_env_er_valgfri(readme: str) -> None:
    tekst = readme.lower()
    assert "`.env` er valgfri" in tekst
    assert "appen virker uten ki-nøkkel" in tekst


def test_readme_forklarer_hvordan_nøkkelen_settes_i_env(readme: str) -> None:
    # Story 4.3 (NFR-9).
    seksjon = _seksjon(readme, "### KI-nøkkel er valgfri")
    assert "cp .env.example .env" in seksjon
    assert "ANTHROPIC_API_KEY=" in seksjon
    assert "claude-haiku-5-5" in seksjon
    assert "Start appen på nytt" in seksjon
    assert "vinner over" in seksjon
    assert "tom verdi regnes som ikke satt" in seksjon.lower()
