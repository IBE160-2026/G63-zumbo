"""Tester for innstillingene (story 2.6, AD-4, AD-6, AD-10).

Testene sender alltid inn `miljø` og laster aldri den ekte `.env`.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend import config
from backend.config import Innstillinger, les_innstillinger

REPOROT = Path(__file__).resolve().parents[2]


# --- Cachemappen ---


def test_cache_dir_vinner(tmp_path: Path) -> None:
    miljø = {"CACHE_DIR": str(tmp_path), "VERCEL": "1"}
    assert les_innstillinger(miljø).cache_dir == tmp_path


def test_vercel_gir_tmp() -> None:
    assert les_innstillinger({"VERCEL": "1"}).cache_dir == Path(
        "/tmp/fhi-helsedata-cache"
    )


def test_vercel_teller_også_med_tom_verdi() -> None:
    # AD-4: «miljøvariabelen VERCEL finnes».
    assert les_innstillinger({"VERCEL": ""}).cache_dir == Path(
        "/tmp/fhi-helsedata-cache"
    )


def test_lokalt_gir_cache_i_reporoten() -> None:
    assert les_innstillinger({}).cache_dir == REPOROT / ".cache"
    assert config.REPOROT == REPOROT


def test_tom_cache_dir_regnes_som_ikke_satt() -> None:
    assert les_innstillinger({"CACHE_DIR": "  "}).cache_dir == REPOROT / ".cache"


def test_relativ_cache_dir_regnes_fra_reporoten() -> None:
    assert les_innstillinger({"CACHE_DIR": "min-cache"}).cache_dir == (
        REPOROT / "min-cache"
    )


def test_cache_dir_med_tilde() -> None:
    cache = les_innstillinger({"CACHE_DIR": "~/fhi-cache"}).cache_dir
    assert cache == Path("~/fhi-cache").expanduser()


def test_cache_i_reporoten_er_i_gitignore() -> None:
    linjer = (REPOROT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".cache/" in linjer


# --- Nøkkel og modell ---


def test_uten_nøkkel_og_modell() -> None:
    innstillinger = les_innstillinger({})
    assert innstillinger.anthropic_api_key is None
    assert innstillinger.anthropic_model == "claude-haiku-5-5"


def test_tomme_verdier_fra_env_example_regnes_som_ikke_satt() -> None:
    # Kopieres .env.example uendret til .env, blir begge verdiene tomme.
    innstillinger = les_innstillinger({"ANTHROPIC_API_KEY": "", "ANTHROPIC_MODEL": ""})
    assert innstillinger.anthropic_api_key is None
    assert innstillinger.anthropic_model == "claude-haiku-5-5"


def test_nøkkel_og_modell_leses() -> None:
    innstillinger = les_innstillinger(
        {"ANTHROPIC_API_KEY": "falsk-nøkkel", "ANTHROPIC_MODEL": "annen-modell"}
    )
    assert innstillinger.anthropic_api_key == "falsk-nøkkel"
    assert innstillinger.anthropic_model == "annen-modell"


def test_nøkkelen_vises_ikke_i_repr() -> None:
    innstillinger = Innstillinger("hemmelig-123", "m", Path("/x"))
    assert "hemmelig-123" not in repr(innstillinger)
    assert "hemmelig-123" not in str(innstillinger)


# --- .env (AD-6, AD-10) ---


def test_env_fil_lastes_bare_uten_miljø(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env = tmp_path / ".env"
    env.write_text("ANTHROPIC_API_KEY=fra-env-fil\nCACHE_DIR=/fra/env\n")
    # setenv før delenv, slik at monkeypatch rydder bort det load_dotenv setter.
    for navn in ("ANTHROPIC_API_KEY", "CACHE_DIR"):
        monkeypatch.setenv(navn, "x")
        monkeypatch.delenv(navn)

    # Med miljø: .env lastes ikke.
    assert les_innstillinger({}, env_fil=env).anthropic_api_key is None
    assert "ANTHROPIC_API_KEY" not in os.environ

    # Uten miljø: .env lastes og vinner over skallet (override=True).
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fra-skallet")
    innstillinger = les_innstillinger(env_fil=env)
    assert innstillinger.anthropic_api_key == "fra-env-fil"
    assert innstillinger.cache_dir == Path("/fra/env")


def test_uten_env_fil_brukes_standardverdiene(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for navn in ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "CACHE_DIR", "VERCEL"):
        monkeypatch.delenv(navn, raising=False)
    innstillinger = les_innstillinger(env_fil=tmp_path / "finnes-ikke")
    assert innstillinger == Innstillinger(None, "claude-haiku-5-5", REPOROT / ".cache")


IMPORT_SJEKK = """
import sys, types
kall = []
falsk = types.ModuleType("dotenv")
for navn in ("load_dotenv", "find_dotenv", "dotenv_values"):
    setattr(falsk, navn, lambda *a, _n=navn, **k: kall.append(_n))
sys.modules["dotenv"] = falsk
import backend.config
assert kall == [], kall
backend.config.les_innstillinger({})
assert kall == [], kall
backend.config.les_innstillinger()
assert kall == ["load_dotenv"], kall
"""


def test_import_av_config_laster_ikke_env() -> None:
    # Egen prosess med en falsk dotenv, slik at et kall ved import faktisk
    # synes, uansett hvilken .env som ville blitt lest.
    resultat = subprocess.run(
        [sys.executable, "-c", IMPORT_SJEKK],
        capture_output=True,
        text=True,
        check=False,
        env={k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"},
    )
    assert resultat.returncode == 0, resultat.stderr


def test_ingen_dotenv_kall_utenfor_funksjoner() -> None:
    tre = ast.parse(Path(config.__file__).read_text(encoding="utf-8"))
    i_funksjoner = {
        id(n)
        for f in ast.walk(tre)
        if isinstance(f, ast.FunctionDef | ast.AsyncFunctionDef)
        for n in ast.walk(f)
    }
    for node in ast.walk(tre):
        if isinstance(node, ast.Call) and id(node) not in i_funksjoner:
            navn = ast.unparse(node.func)
            assert "dotenv" not in navn, f"{navn} kalles ved import"


def _bruker(fil: Path, navn: set[str]) -> bool:
    tre = ast.parse(fil.read_text(encoding="utf-8"))
    for node in ast.walk(tre):
        if (
            isinstance(node, ast.Name | ast.alias)
            and (getattr(node, "id", None) or getattr(node, "name", None)) in navn
        ):
            return True
        if isinstance(node, ast.Attribute) and node.attr in navn:
            return True
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
            "dotenv"
        ):
            return True
    return False


def test_bare_config_leser_miljøvariabler() -> None:
    src = Path(config.__file__).parent
    navn = {"environ", "getenv", "load_dotenv", "dotenv_values", "find_dotenv"}
    treff = [str(f.relative_to(src)) for f in src.rglob("*.py") if _bruker(f, navn)]
    assert treff == ["config.py"]
