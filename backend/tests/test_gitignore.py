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


def _er_hemmelig_eller_cache(sti: str) -> bool:
    # Samme regler som .gitignore: .env og .env.* i alle mapper, men ikke
    # malene .env.example og .env.*.example. Alt under en .cache/-mappe.
    deler = sti.split("/")
    navn = deler[-1]
    if ".cache" in deler[:-1]:
        return True
    if navn == ".env.example" or (
        navn.startswith(".env.") and navn.endswith(".example")
    ):
        return False
    return navn == ".env" or navn.startswith(".env.")


def test_nøkler_og_cache_er_ikke_sjekket_inn(reporot: Path) -> None:
    ut = _git("ls-files", "-z", cwd=reporot)
    assert ut.returncode == 0, ut.stderr
    sporet = [sti for sti in ut.stdout.split("\0") if sti]
    assert [sti for sti in sporet if _er_hemmelig_eller_cache(sti)] == []


def test_env_example_har_nøklene(reporot: Path) -> None:
    linjer = (reporot / ".env.example").read_text(encoding="utf-8").splitlines()
    assert "ANTHROPIC_API_KEY=" in linjer
    assert "ANTHROPIC_MODEL=" in linjer
