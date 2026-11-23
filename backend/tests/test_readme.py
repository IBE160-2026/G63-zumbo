"""Sjekker at README i reporoten forklarer hvordan man kommer i gang (story 1.5)."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def readme() -> str:
    ut = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
        check=True,
    )
    return (Path(ut.stdout.strip()) / "README.md").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "kommando",
    ["uv sync", "uv run pytest", "uv run ruff check", "uv run ruff format --check"],
)
def test_readme_nevner_kommandoen(readme: str, kommando: str) -> None:
    assert kommando in readme


def test_readme_har_plass_for_oppstart(readme: str) -> None:
    assert "### Starte appen" in readme


def test_readme_sier_at_env_er_valgfri(readme: str) -> None:
    assert "`.env` er valgfri" in readme
    assert "uten KI-nøkkel" in readme
