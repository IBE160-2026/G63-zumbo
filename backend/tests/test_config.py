"""Tester for innstillingene (story 2.6, AD-4, AD-6, AD-10).

Testene sender alltid inn `miljø` og laster aldri den ekte `.env`.
"""

import ast
import importlib
import os
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


def test_import_av_config_laster_ikke_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=skal-ikke-lastes\n")
    importlib.reload(config)
    assert "ANTHROPIC_API_KEY" not in os.environ


def test_ingen_kode_kjøres_ved_import() -> None:
    tre = ast.parse(Path(config.__file__).read_text(encoding="utf-8"))
    for node in tre.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            pytest.fail(f"kall ved import på linje {node.lineno}")


def test_bare_config_leser_miljøvariabler() -> None:
    src = Path(config.__file__).parent
    treff = [
        str(fil.relative_to(src))
        for fil in src.rglob("*.py")
        if any(
            ord_ in fil.read_text(encoding="utf-8")
            for ord_ in ("os.environ", "os.getenv", "load_dotenv")
        )
    ]
    assert treff == ["config.py"]
