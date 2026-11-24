"""Tester for utkastet til prompten for KI-forklaringen (story 4.1).

Prompten får bare utvalg, tolkede uker, regelutslag og kildehenvisning
(FR-20, AD-6). Plassholderne skrives som `{navn}`, slik at story 4.3 kan
fylle dem ut med `str.format`.
"""

import re
from pathlib import Path

import backend

PROMPT = Path(backend.__file__).parent / "prompts" / "forklaring.md"
PLASSHOLDERE = {"utvalg", "uker", "regelutslag", "kildehenvisning"}


def tekst() -> str:
    return PROMPT.read_text(encoding="utf-8")


def test_prompten_har_nøyaktig_de_fire_plassholderne() -> None:
    funnet = re.findall(r"\{([^{}]*)\}", tekst())
    assert set(funnet) == PLASSHOLDERE
    assert len(funnet) == len(PLASSHOLDERE), "hver plassholder står én gang"


def test_prompten_kan_fylles_ut_med_format() -> None:
    utfylt = tekst().format(**{navn: f"<{navn}>" for navn in PLASSHOLDERE})
    assert "{" not in utfylt and "}" not in utfylt
    for navn in PLASSHOLDERE:
        assert f"<{navn}>" in utfylt


def test_prompten_ber_om_norsk_og_høyst_120_ord() -> None:
    t = tekst()
    assert "norsk" in t
    assert "høyst 120 ord" in t


def test_prompten_ber_ki_en_ikke_nevne_hentetidspunktet() -> None:
    # Irenes beslutning før merge av PR #67: en gjenbrukt forklaring skal ikke
    # vise et gammelt hentetidspunkt.
    assert "Ikke nevn når tallene ble hentet." in PROMPT.read_text(encoding="utf-8")
