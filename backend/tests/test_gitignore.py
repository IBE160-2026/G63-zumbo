"""Sjekker at nøkler og cache holdes utenfor git (NFR-9, AD-4, AD-6)."""

import subprocess
from pathlib import Path

import pytest


def _git(*argumenter: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *argumenter], cwd=cwd, capture_output=True, text=True, check=False
    )


@pytest.fixture(scope="module")
def reporot() -> Path:
    ut = _git("rev-parse", "--show-toplevel", cwd=Path(__file__).parent)
    assert ut.returncode == 0, f"fant ikke git-repoet: {ut.stderr}"
    return Path(ut.stdout.strip())


def _er_ignorert(sti: str, reporot: Path) -> bool:
    # --no-index: sjekk reglene i .gitignore, ikke om fila allerede er sporet.
    ut = _git("check-ignore", "--no-index", "-q", sti, cwd=reporot)
    assert ut.returncode in (0, 1), f"git check-ignore feilet: {ut.stderr}"
    return ut.returncode == 0


@pytest.mark.parametrize("sti", [".env", ".env.local", ".cache/x.json"])
def test_nøkler_og_cache_er_ignorert(sti: str, reporot: Path) -> None:
    assert _er_ignorert(sti, reporot)


def test_env_example_er_ikke_ignorert(reporot: Path) -> None:
    assert not _er_ignorert(".env.example", reporot)


def test_nøkler_og_cache_er_ikke_sjekket_inn(reporot: Path) -> None:
    ut = _git("ls-files", "--", ".env", ".cache", cwd=reporot)
    assert ut.returncode == 0, ut.stderr
    assert ut.stdout == ""


def test_env_example_har_nøklene(reporot: Path) -> None:
    linjer = (reporot / ".env.example").read_text(encoding="utf-8").splitlines()
    assert "ANTHROPIC_API_KEY=" in linjer
    assert "ANTHROPIC_MODEL=" in linjer
