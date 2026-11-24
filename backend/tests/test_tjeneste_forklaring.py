"""Tester for den mellomlagrede KI-forklaringen (story 4.4, AD-7, FR-25).

`Tjeneste.forklaring` bruker en lagret forklaring når tallene, prompten og
modellen er de samme, og kaller ellers Claude. Testene bruker en falsk klient
og `tmp_path` som cache. De kaller aldri Claude (AD-10).
"""

import json
import threading
from concurrent.futures import Future
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Self

import pytest
from anthropic.types import Message, TextBlock, Usage

from backend import fhi, ki, mellomlager, tjeneste
from backend.config import Innstillinger
from backend.domene import Dataserie, Regelutslag, Uke, Utvalg, kildehenvisning
from backend.tjeneste import Resultat, Tjeneste

FIXTURES = Path(__file__).parent / "fixtures"
FORKLARING = (
    (FIXTURES / "ki" / "forklaring-influensa-2025-2026-alle.txt")
    .read_text(encoding="utf-8")
    .strip()
)
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
_lagret = json.loads(
    (FIXTURES / "fhi" / "724-influensa-2025-2026-alle-nonstl.json").read_text(
        encoding="utf-8"
    )
)
SERIE = fhi.tolk(_lagret["svar"], UTVALG)
HENTET = datetime(2026, 11, 23, 21, 20, 15, tzinfo=UTC)
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
MODELL = "claude-haiku-5-5"


def resultat(
    serie: Dataserie = SERIE,
    regelutslag: tuple[Regelutslag, ...] = (),
    hentet: datetime = HENTET,
) -> Resultat:
    return Resultat(
        utvalg=serie.utvalg,
        serie=serie,
        regelutslag=regelutslag,
        kilde=kildehenvisning(724, hentet),
    )


def svar(tekst: str = FORKLARING, stop_reason: str = "end_turn") -> Message:
    return Message(
        id="msg_falsk",
        type="message",
        role="assistant",
        model=MODELL,
        content=[TextBlock(type="text", text=tekst)],
        stop_reason=stop_reason,
        stop_sequence=None,
        usage=Usage(input_tokens=1, output_tokens=1),
    )


class FalskKlient:
    """Står i stedet for `anthropic.Anthropic` og teller kallene."""

    def __init__(self, *svarene: Any) -> None:
        self.svarene = list(svarene) or [svar()]
        self.kall: list[dict[str, Any]] = []
        self.messages = self

    def __call__(self, **_: Any) -> Self:
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def create(self, **kwargs: Any) -> Any:
        self.kall.append(kwargs)
        neste = self.svarene[min(len(self.kall), len(self.svarene)) - 1]
        if isinstance(neste, BaseException):
            raise neste
        return neste


@pytest.fixture
def mappe(tmp_path: Path) -> Path:
    return tmp_path / "cache"


def tjeneste_med(
    mappe: Path,
    klient: FalskKlient,
    nøkkel: str | None = "falsk-nøkkel",
    modell: str = MODELL,
) -> Tjeneste:
    return Tjeneste(Innstillinger(nøkkel, modell, mappe), ny_ki_klient=klient)


def ki_filer(mappe: Path) -> list[Path]:
    ki_mappe = mappe / "ki"
    return sorted(ki_mappe.iterdir()) if ki_mappe.exists() else []


# --- Lagring og gjenbruk ---


def test_forklaringen_lagres_med_laget_modell_og_tekst(mappe: Path) -> None:
    klient = FalskKlient()
    utfall = tjeneste_med(mappe, klient).forklaring(resultat(), NÅ)
    assert utfall == ki.Forklaring(FORKLARING)
    nøkkel = ki.nøkkel(SERIE, (), MODELL)
    assert ki_filer(mappe) == [mappe / "ki" / f"{nøkkel}.json"]
    assert json.loads(ki_filer(mappe)[0].read_text(encoding="utf-8")) == {
        "laget": "2026-11-24T12:00:00Z",
        "modell": MODELL,
        "tekst": FORKLARING,
    }


def test_samme_tall_bruker_lagret_tekst_uten_å_kalle_claude(mappe: Path) -> None:
    første = FalskKlient()
    tjeneste_med(mappe, første).forklaring(resultat(), NÅ)
    # En ny tjeneste (ny oppstart) og et nytt hentetidspunkt: samme tall.
    andre = FalskKlient(svar("En helt annen tekst."))
    utfall = tjeneste_med(mappe, andre).forklaring(
        resultat(hentet=HENTET + timedelta(days=1)), NÅ + timedelta(days=1)
    )
    assert utfall == ki.Forklaring(FORKLARING)
    assert len(første.kall) == 1
    assert andre.kall == []


def test_endrede_tall_gir_nytt_kall_og_ny_fil(mappe: Path) -> None:
    klient = FalskKlient(svar("Første."), svar("Andre."))
    tj = tjeneste_med(mappe, klient)
    tj.forklaring(resultat(), NÅ)
    første = SERIE.uker[0]
    endret = Dataserie(
        UTVALG,
        (Uke(første.år, første.ukenummer, første.tester, 65), *SERIE.uker[1:]),
    )
    assert tj.forklaring(resultat(endret), NÅ) == ki.Forklaring("Andre.")
    assert len(klient.kall) == 2
    assert len(ki_filer(mappe)) == 2


def test_endrede_regelutslag_gir_nytt_kall(mappe: Path) -> None:
    klient = FalskKlient(svar("Første."), svar("Andre."))
    tj = tjeneste_med(mappe, klient)
    tj.forklaring(resultat(), NÅ)
    utslag = (Regelutslag("R1", "Færre enn 20 positive prøver i alt."),)
    assert tj.forklaring(resultat(regelutslag=utslag), NÅ) == ki.Forklaring("Andre.")
    assert len(klient.kall) == 2


def test_endret_prompt_gir_nytt_kall(
    mappe: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    klient = FalskKlient(svar("Første."), svar("Andre."))
    tj = tjeneste_med(mappe, klient)
    tj.forklaring(resultat(), NÅ)
    ny_prompt = ki.PROMPT.read_text(encoding="utf-8") + "\nEn ny regel.\n"
    monkeypatch.setattr(ki, "_mal", lambda: ny_prompt)
    assert tj.forklaring(resultat(), NÅ) == ki.Forklaring("Andre.")
    assert len(klient.kall) == 2
    assert "En ny regel." in klient.kall[1]["messages"][0]["content"]


def test_endret_modell_gir_nytt_kall(mappe: Path) -> None:
    første = FalskKlient(svar("Haiku."))
    tjeneste_med(mappe, første).forklaring(resultat(), NÅ)
    andre = FalskKlient(svar("Sonnet."))
    utfall = tjeneste_med(mappe, andre, modell="claude-sonnet-5-5").forklaring(
        resultat(), NÅ
    )
    assert utfall == ki.Forklaring("Sonnet.")
    assert len(andre.kall) == 1
    assert andre.kall[0]["model"] == "claude-sonnet-5-5"


# --- Feil lagres ikke ---


def test_ki_feil_lagres_ikke_og_neste_kall_prøver_igjen(mappe: Path) -> None:
    klient = FalskKlient(RuntimeError("nede"), svar("Nå gikk det."))
    tj = tjeneste_med(mappe, klient)
    assert tj.forklaring(resultat(), NÅ) == ki.KiFeil()
    assert ki_filer(mappe) == []
    assert tj.forklaring(resultat(), NÅ) == ki.Forklaring("Nå gikk det.")
    assert len(klient.kall) == 2
    assert len(ki_filer(mappe)) == 1


def test_ubrukelig_svar_lagres_ikke(mappe: Path) -> None:
    klient = FalskKlient(svar(stop_reason="max_tokens"))
    assert tjeneste_med(mappe, klient).forklaring(resultat(), NÅ) == ki.KiFeil()
    assert ki_filer(mappe) == []


def test_mangler_nøkkel_lagres_ikke_og_kaller_ikke_claude(mappe: Path) -> None:
    klient = FalskKlient()
    tj = tjeneste_med(mappe, klient, nøkkel=None)
    assert tj.forklaring(resultat(), NÅ) == ki.ManglerNøkkel()
    assert klient.kall == []
    assert ki_filer(mappe) == []


def test_uten_nøkkel_brukes_heller_ikke_lagret_forklaring(mappe: Path) -> None:
    # FR-22: uten nøkkel står det at forklaringen krever en KI-nøkkel.
    tjeneste_med(mappe, FalskKlient()).forklaring(resultat(), NÅ)
    tj = tjeneste_med(mappe, FalskKlient(), nøkkel=None)
    assert tj.forklaring(resultat(), NÅ) == ki.ManglerNøkkel()


def test_uten_tall_kalles_ikke_claude(mappe: Path) -> None:
    klient = FalskKlient()
    tom = Resultat(UTVALG, melding="Ingen tall.")
    assert tjeneste_med(mappe, klient).forklaring(tom, NÅ) == ki.KiFeil()
    assert klient.kall == []


# --- Cachen ---


def test_forklaringen_vises_selv_om_den_ikke_kan_lagres(
    mappe: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def full_disk(*_: Any) -> None:
        raise OSError("disken er full")

    monkeypatch.setattr(mellomlager, "lagre_forklaring", full_disk)
    utfall = tjeneste_med(mappe, FalskKlient()).forklaring(resultat(), NÅ)
    assert utfall == ki.Forklaring(FORKLARING)


def test_ødelagt_lagret_forklaring_gir_nytt_kall(mappe: Path) -> None:
    fil = mellomlager.forklaringsfil(mappe, ki.nøkkel(SERIE, (), MODELL))
    fil.parent.mkdir(parents=True)
    fil.write_text("{ødelagt", encoding="utf-8")
    klient = FalskKlient()
    assert tjeneste_med(mappe, klient).forklaring(resultat(), NÅ) == ki.Forklaring(
        FORKLARING
    )
    assert len(klient.kall) == 1
    assert mellomlager.les_forklaring(mappe, ki.nøkkel(SERIE, (), MODELL)) is not None


def test_prompt_som_ikke_kan_leses_gir_ki_feil(
    mappe: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def mangler() -> str:
        raise FileNotFoundError("forklaring.md")

    monkeypatch.setattr(ki, "_mal", mangler)
    klient = FalskKlient()
    assert tjeneste_med(mappe, klient).forklaring(resultat(), NÅ) == ki.KiFeil()
    assert klient.kall == []


# --- Samtidige kall (AD-9) ---


def test_samtidige_kall_for_samme_tall_deler_ett_kall_til_claude(
    mappe: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    startet, slipp, venter = threading.Event(), threading.Event(), threading.Event()

    class Fremtid(Future):
        def result(self, timeout: float | None = None) -> Any:
            venter.set()
            return super().result(timeout)

    monkeypatch.setattr(tjeneste, "Future", Fremtid)

    class TregKlient(FalskKlient):
        def create(self, **kwargs: Any) -> Any:
            startet.set()
            assert slipp.wait(5)
            return super().create(**kwargs)

    klient = TregKlient()
    tj = tjeneste_med(mappe, klient)
    resultater: list[ki.Utfall] = []
    tråder = [
        threading.Thread(
            target=lambda: resultater.append(tj.forklaring(resultat(), NÅ))
        )
        for _ in range(2)
    ]
    tråder[0].start()
    assert startet.wait(5)
    tråder[1].start()
    assert venter.wait(5), "det andre kallet venter ikke på det første"
    slipp.set()
    for tråd in tråder:
        tråd.join(5)
        assert not tråd.is_alive()
    assert resultater == [ki.Forklaring(FORKLARING)] * 2
    assert len(klient.kall) == 1
