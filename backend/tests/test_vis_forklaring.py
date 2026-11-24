"""Tester for demoskriptet med falsk Claude (story 4.5, `scripts/vis_forklaring.py`).

Skriptet startes ikke, så det blir verken server eller nettverkskall. Claude
kalles aldri (AD-10).
"""

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

import pytest

from backend import fhi, ki
from backend.config import Innstillinger
from backend.domene import Utvalg, kildehenvisning
from backend.tjeneste import Resultat, Tjeneste

SKRIPT = Path(__file__).parent.parent / "scripts" / "vis_forklaring.py"
FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "fhi"
    / "724-influensa-2025-2026-alle-nonstl.json"
)
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")


@pytest.fixture
def demo(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spesifikasjon = importlib.util.spec_from_file_location("vis_forklaring", SKRIPT)
    assert spesifikasjon and spesifikasjon.loader
    modul = importlib.util.module_from_spec(spesifikasjon)
    spesifikasjon.loader.exec_module(modul)
    monkeypatch.setattr(modul.time, "sleep", lambda _: None)
    return modul


def forklaring(demo: ModuleType, tmp_path: Path, *, feil: bool) -> ki.Utfall:
    serie = fhi.tolk(json.loads(FIXTURE.read_text(encoding="utf-8"))["svar"], UTVALG)
    resultat = Resultat(utvalg=UTVALG, serie=serie, kilde=kildehenvisning(724, NÅ))
    tjeneste = Tjeneste(
        Innstillinger("falsk-nøkkel", demo.MODELL, tmp_path),
        ny_ki_klient=demo.FalskClaude(feil=feil),
    )
    return tjeneste.forklaring(resultat, NÅ)


def test_falsk_claude_gir_den_lagrede_forklaringen(
    demo: ModuleType, tmp_path: Path
) -> None:
    assert forklaring(demo, tmp_path, feil=False) == ki.Forklaring(demo.FORKLARING)


def test_falsk_claude_kan_feile(demo: ModuleType, tmp_path: Path) -> None:
    assert forklaring(demo, tmp_path, feil=True) == ki.KiFeil()


def test_ukjent_utfall_stopper_skriptet(
    demo: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(demo.sys, "argv", ["vis_forklaring.py", "noe-annet"])
    with pytest.raises(SystemExit, match=r"forklaring\|uten-nokkel\|feil"):
        demo.main()


def test_demoen_bruker_ikke_den_vanlige_porten(demo: ModuleType) -> None:
    assert demo.PORT != 8000
