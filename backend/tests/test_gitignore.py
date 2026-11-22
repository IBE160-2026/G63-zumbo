"""Sjekker at nøkler og cache holdes utenfor git (NFR-9, AD-4, AD-6)."""

import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git mangler")


def _reporot() -> Path:
    ut = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(ut.stdout.strip())


def _er_ignorert(sti: str) -> bool:
    # --no-index: sjekk reglene i .gitignore, ikke om fila allerede er sporet.
    ut = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", sti],
        cwd=_reporot(),
        capture_output=True,
        text=True,
        check=False,
    )
    if ut.returncode not in (0, 1):
        raise RuntimeError(f"git check-ignore feilet: {ut.stderr}")
    return ut.returncode == 0


@pytest.mark.parametrize("sti", [".env", ".cache/x.json"])
def test_nøkler_og_cache_er_ignorert(sti: str) -> None:
    assert _er_ignorert(sti)


def test_env_example_er_ikke_ignorert() -> None:
    assert not _er_ignorert(".env.example")


def test_env_example_har_nøklene() -> None:
    linjer = (_reporot() / ".env.example").read_text(encoding="utf-8").splitlines()
    assert "ANTHROPIC_API_KEY=" in linjer
    assert "ANTHROPIC_MODEL=" in linjer
