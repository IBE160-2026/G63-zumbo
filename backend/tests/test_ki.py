"""Tester for KI-forklaringen med tre utfall (story 4.3, FR-20, FR-22, AD-6).

Testene bruker en falsk klient og tekst fra `tests/fixtures/ki/`. De kaller
aldri Claude og trenger verken nett eller nøkkel (AD-10).
"""

import ast
import inspect
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Self

import anthropic
import httpx2
import pytest
from anthropic.resources.messages import Messages
from anthropic.types import Message, TextBlock, Usage

from backend import fhi, ki
from backend.config import Innstillinger, les_innstillinger
from backend.domene import Dataserie, Regelutslag, Uke, Utvalg, kildehenvisning
from backend.formatering import kildetekst

FIXTURES = Path(__file__).parent / "fixtures"
FORKLARING = (FIXTURES / "ki" / "forklaring-influensa-2025-2026-alle.txt").read_text(
    encoding="utf-8"
)
NØKKEL = "falsk-nøkkel-123"
NBSP = "\u00a0"

_lagret = json.loads(
    (FIXTURES / "fhi" / "724-influensa-2025-2026-alle-nonstl.json").read_text(
        encoding="utf-8"
    )
)
SERIE = fhi.tolk(_lagret["svar"], Utvalg(1, "influensa", "2025/2026", "alle"))
KILDE = kildehenvisning(724, datetime.fromisoformat(_lagret["hentet"]))
UTSLAG = (Regelutslag("R2", "5 av 20 uker har færre enn 30 tester."),)


def innstillinger(
    nøkkel: str | None = NØKKEL, modell: str = "claude-haiku-5-5"
) -> Innstillinger:
    return Innstillinger(nøkkel, modell, Path("/ubrukt"))


def lag_svar(
    tekst: str = FORKLARING, stop_reason: str = "end_turn", model: str = "m"
) -> Message:
    return Message(
        id="msg_falsk",
        type="message",
        role="assistant",
        model=model,
        content=[TextBlock(type="text", text=tekst)] if tekst else [],
        stop_reason=stop_reason,
        stop_sequence=None,
        usage=Usage(input_tokens=1, output_tokens=1),
    )


class FalskKlient:
    """Står i stedet for `anthropic.Anthropic`. Husker hvordan den ble laget og
    kalt, og svarer med `svar` eller kaster `feil`."""

    def __init__(self, svar: Any = None, feil: BaseException | None = None) -> None:
        self.svar = svar if svar is not None else lag_svar()
        self.feil = feil
        self.laget_med: dict[str, Any] | None = None
        self.kall: list[dict[str, Any]] = []
        self.messages = self

        self.lukket = False

    def __call__(self, **kwargs: Any) -> "FalskKlient":
        # Argumentene må passe til den ekte klienten.
        inspect.signature(anthropic.Anthropic).bind(**kwargs)
        self.laget_med = kwargs
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.lukket = True

    def create(self, **kwargs: Any) -> Any:
        # Argumentene må passe til den ekte `messages.create`, så en feilstavet
        # parameter ikke bare blir `KiFeil` i drift.
        inspect.signature(Messages.create).bind(None, **kwargs)
        self.kall.append(kwargs)
        if self.feil is not None:
            raise self.feil
        return self.svar


def forklar(klient: FalskKlient, **kwargs: Any) -> ki.Utfall:
    return ki.forklar(
        SERIE,
        kwargs.pop("regelutslag", ()),
        KILDE,
        kwargs.pop("innstillinger", innstillinger()),
        ny_klient=klient,
    )


# --- Tre utfall ---


def test_med_nøkkel_gir_forklaringen_fra_claude() -> None:
    klient = FalskKlient()
    assert forklar(klient) == ki.Forklaring(FORKLARING.strip())
    assert len(klient.kall) == 1


@pytest.mark.parametrize("nøkkel", [None, ""])
def test_uten_nøkkel_kalles_ikke_claude(nøkkel: str | None) -> None:
    klient = FalskKlient()
    assert forklar(klient, innstillinger=innstillinger(nøkkel)) == ki.ManglerNøkkel()
    assert klient.laget_med is None
    assert klient.kall == []


def test_tom_nøkkel_i_miljøet_gir_mangler_nøkkel() -> None:
    klient = FalskKlient()
    tom = les_innstillinger({"ANTHROPIC_API_KEY": "", "ANTHROPIC_MODEL": ""})
    assert forklar(klient, innstillinger=tom) == ki.ManglerNøkkel()
    assert klient.kall == []


def _forespørsel() -> httpx2.Request:
    return httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


def _statusfeil(klasse: type[anthropic.APIStatusError], status: int) -> Exception:
    respons = httpx2.Response(status, request=_forespørsel())
    return klasse("feil", response=respons, body=None)


@pytest.mark.parametrize(
    "feil",
    [
        _statusfeil(anthropic.AuthenticationError, 401),
        _statusfeil(anthropic.NotFoundError, 404),
        _statusfeil(anthropic.RateLimitError, 429),
        _statusfeil(anthropic.InternalServerError, 500),
        anthropic.APIConnectionError(request=_forespørsel()),
        anthropic.APITimeoutError(request=_forespørsel()),
        RuntimeError("uventet"),
    ],
    ids=lambda f: type(f).__name__,
)
def test_feil_fra_claude_eller_nettet_gir_ki_feil(feil: Exception) -> None:
    assert forklar(FalskKlient(feil=feil)) == ki.KiFeil()


def test_feil_når_klienten_lages_gir_ki_feil() -> None:
    def ødelagt(**_: Any) -> Any:
        raise ValueError("kan ikke lage klient")

    assert ki.forklar(SERIE, (), KILDE, innstillinger(), ny_klient=ødelagt) == (
        ki.KiFeil()
    )


@pytest.mark.parametrize(
    "ubrukelig",
    [
        lag_svar(stop_reason="max_tokens"),
        lag_svar(stop_reason="refusal"),
        lag_svar(tekst=""),
        lag_svar(tekst="   \n"),
        object(),
    ],
    ids=["max_tokens", "refusal", "tomt", "bare-mellomrom", "ukjent-objekt"],
)
def test_svar_som_ikke_kan_brukes_gir_ki_feil(ubrukelig: Any) -> None:
    assert forklar(FalskKlient(svar=ubrukelig)) == ki.KiFeil()


@pytest.mark.parametrize(
    "klient",
    [
        FalskKlient(feil=_statusfeil(anthropic.AuthenticationError, 401)),
        FalskKlient(feil=RuntimeError(f"feil med {NØKKEL}")),
        FalskKlient(svar=lag_svar(stop_reason="max_tokens")),
    ],
    ids=["statusfeil", "uventet-feil-med-nøkkel", "ubrukelig-svar"],
)
def test_feilen_logges_uten_nøkkelen(
    klient: FalskKlient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG, logger="backend.ki")
    assert forklar(klient) == ki.KiFeil()
    assert caplog.records, "feilen skal logges"
    assert NØKKEL not in caplog.text


# --- Klient og modell (AD-6) ---


def test_klienten_lages_med_eksplisitt_nøkkel() -> None:
    klient = FalskKlient()
    forklar(klient)
    assert klient.laget_med is not None
    assert klient.laget_med["api_key"] == NØKKEL


def test_klienten_har_tidsgrense_og_lukkes() -> None:
    klient = FalskKlient()
    forklar(klient)
    assert klient.laget_med is not None
    assert klient.laget_med["timeout"] == ki.TIDSGRENSE
    assert klient.laget_med["max_retries"] == ki.FORSØK_PÅ_NYTT
    assert klient.lukket


def test_kallet_har_lengde_og_innsats() -> None:
    klient = FalskKlient()
    forklar(klient)
    assert klient.kall[0]["max_tokens"] == ki.MAKS_TOKENS
    assert klient.kall[0]["output_config"] == {"effort": "low"}


def test_standardmodellen_er_haiku() -> None:
    klient = FalskKlient()
    forklar(klient, innstillinger=les_innstillinger({"ANTHROPIC_API_KEY": NØKKEL}))
    assert klient.kall[0]["model"] == "claude-haiku-5-5"


def test_modellen_kan_overstyres_med_anthropic_model() -> None:
    klient = FalskKlient()
    valgt = les_innstillinger(
        {"ANTHROPIC_API_KEY": NØKKEL, "ANTHROPIC_MODEL": "claude-sonnet-5-5"}
    )
    forklar(klient, innstillinger=valgt)
    assert klient.kall[0]["model"] == "claude-sonnet-5-5"


def test_uten_ny_klient_brukes_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    klient = FalskKlient()
    monkeypatch.setattr(anthropic, "Anthropic", klient)
    utfall = ki.forklar(SERIE, (), KILDE, innstillinger())
    assert utfall == ki.Forklaring(FORKLARING.strip())
    assert klient.laget_med is not None


# --- Prompten (FR-20) ---


def test_claude_får_den_utfylte_prompten() -> None:
    klient = FalskKlient()
    forklar(klient, regelutslag=UTSLAG)
    assert klient.kall[0]["messages"] == [
        {"role": "user", "content": ki.lag_prompt(SERIE, UTSLAG, KILDE)}
    ]


def test_prompten_har_ukene_slik_de_står_i_tabellen() -> None:
    prompt = ki.lag_prompt(SERIE, (), KILDE)
    assert "Influensa, sesongen 2025/2026, alle aldersgrupper" in prompt
    assert f"uke 50: 10{NBSP}748 tester, 3{NBSP}068 positive, 28,5{NBSP}%" in prompt
    assert f"uke 20: 4{NBSP}552 tester, 37 positive, 0,8{NBSP}%" in prompt
    linjer = [linje for linje in prompt.splitlines() if linje.startswith("uke ")]
    assert len(linjer) == len(SERIE.uker)


def test_prompten_har_skjulte_og_manglende_tall_skrevet_tydelig() -> None:
    serie = Dataserie(
        SERIE.utvalg,
        (Uke(2025, 40, None, 3), Uke(2025, 41, 0, 0), Uke(2025, 42, 25, None)),
    )
    prompt = ki.lag_prompt(serie, (), KILDE)
    assert "uke 40: skjult antall tester, 3 positive, andel mangler" in prompt
    assert "uke 41: 0 tester, 0 positive, andel kan ikke regnes ut" in prompt
    assert "uke 42: 25 tester, skjult antall positive, andel mangler" in prompt


def test_prompten_har_regelutslag_og_kilde() -> None:
    prompt = ki.lag_prompt(SERIE, UTSLAG, KILDE)
    assert "- 5 av 20 uker har færre enn 30 tester." in prompt
    assert "Tabell 724 «RESPIaggr Influensa antall og andel»" in prompt
    assert "Hentet 23.11.2026 kl. 22:20." in prompt


def test_uten_regelutslag_er_feltet_tomt() -> None:
    prompt = ki.lag_prompt(SERIE, (), KILDE)
    etter = prompt.split("(tom hvis ingen slo inn):\n", 1)[1]
    assert etter.startswith("\n\nKilde:")


def test_prompten_har_ingen_ufylte_plassholdere() -> None:
    prompt = ki.lag_prompt(SERIE, UTSLAG, KILDE)
    for navn in ("{utvalg}", "{uker}", "{regelutslag}", "{kildehenvisning}"):
        assert navn not in prompt


def test_kilden_er_den_samme_som_under_grafen() -> None:
    assert kildetekst(KILDE) in ki.lag_prompt(SERIE, (), KILDE)


def test_kilde_står_ikke_to_ganger() -> None:
    # Irenes beslutning før merge av PR #66: FHIs tekst starter med «Kilde:».
    prompt = ki.lag_prompt(SERIE, (), KILDE)
    assert prompt.count("Kilde:") == 1
    assert prompt.rstrip().endswith(kildetekst(KILDE))


@pytest.mark.parametrize(
    ("tester", "positive", "tekst"),
    [
        (1210, 252, f"uke 50: 1{NBSP}210 tester, 252 positive, 20,8{NBSP}%"),
        (None, 5, "uke 50: skjult antall tester, 5 positive, andel mangler"),
        (40, None, "uke 50: 40 tester, skjult antall positive, andel mangler"),
        (
            None,
            None,
            "uke 50: skjult antall tester, skjult antall positive, andel mangler",
        ),
        (0, 0, "uke 50: 0 tester, 0 positive, andel kan ikke regnes ut"),
        (0, None, "uke 50: 0 tester, skjult antall positive, andel mangler"),
        (40, 45, f"uke 50: 40 tester, 45 positive, 112,5{NBSP}%"),
    ],
)
def test_ukelinje(tester: int | None, positive: int | None, tekst: str) -> None:
    assert ki.ukelinje(Uke(2025, 50, tester, positive)) == tekst


# --- Bare ki.py importerer anthropic (AD-6) ---

SRC = Path(ki.__file__).parent


def _importerer_anthropic(fil: Path) -> bool:
    tre = ast.parse(fil.read_text(encoding="utf-8"))
    moduler: set[str] = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            moduler.add(node.module or "")
    return any(m.split(".")[0] == "anthropic" for m in moduler)


def test_bare_ki_py_importerer_anthropic() -> None:
    treff = [
        str(fil.relative_to(SRC))
        for fil in SRC.rglob("*.py")
        if _importerer_anthropic(fil)
    ]
    assert treff == ["ki.py"]


def test_ki_importerer_bare_det_arkitekturen_tillater() -> None:
    tre = ast.parse(Path(ki.__file__).read_text(encoding="utf-8"))
    backend_moduler = {
        node.module
        for node in ast.walk(tre)
        if isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith("backend")
    }
    assert backend_moduler <= {
        "backend.config",
        "backend.domene",
        "backend.formatering",
    }


# --- Nøkkelen til en lagret forklaring (story 4.4, AD-7) ---

MODELL = "claude-haiku-5-5"


def test_nøkkelen_er_sha256_av_kanonisk_json() -> None:
    import hashlib

    forventet = {
        "utvalg": {
            "mal": 1,
            "virus": "influensa",
            "sesong": "2025/2026",
            "aldersgruppe": "alle",
        },
        "uker": [[u.år, u.ukenummer, u.tester, u.positive] for u in SERIE.uker],
        "regelutslag": [["R2", UTSLAG[0].tekst]],
        "prompt": ki.PROMPT.read_text(encoding="utf-8"),
        "modell": MODELL,
    }
    kanonisk = json.dumps(
        forventet, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    assert ki.nøkkel(SERIE, UTSLAG, MODELL) == (
        hashlib.sha256(kanonisk.encode("utf-8")).hexdigest()
    )


def test_samme_tall_gir_samme_nøkkel_også_med_nytt_hentetidspunkt() -> None:
    # Hentetidspunktet er ikke en del av serien eller nøkkelen.
    kopi = Dataserie(SERIE.utvalg, tuple(SERIE.uker))
    assert ki.nøkkel(kopi, list(UTSLAG), MODELL) == ki.nøkkel(SERIE, UTSLAG, MODELL)


def test_endrede_tall_gir_ny_nøkkel() -> None:
    første = SERIE.uker[0]
    endret = Uke(første.år, første.ukenummer, første.tester, første.positive + 1)
    serie = Dataserie(SERIE.utvalg, (endret, *SERIE.uker[1:]))
    assert ki.nøkkel(serie, (), MODELL) != ki.nøkkel(SERIE, (), MODELL)


def test_annet_utvalg_gir_ny_nøkkel() -> None:
    annet = Dataserie(Utvalg(1, "influensa", "2025/2026", "80+"), SERIE.uker)
    assert ki.nøkkel(annet, (), MODELL) != ki.nøkkel(SERIE, (), MODELL)


def test_endrede_regelutslag_gir_ny_nøkkel() -> None:
    assert ki.nøkkel(SERIE, UTSLAG, MODELL) != ki.nøkkel(SERIE, (), MODELL)


def test_annen_modell_gir_ny_nøkkel() -> None:
    assert ki.nøkkel(SERIE, (), "claude-sonnet-5-5") != ki.nøkkel(SERIE, (), MODELL)


def test_endret_prompt_gir_ny_nøkkel(monkeypatch: pytest.MonkeyPatch) -> None:
    før = ki.nøkkel(SERIE, (), MODELL)
    monkeypatch.setattr(ki, "_mal", lambda: "En annen prompt. {uker}")
    assert ki.nøkkel(SERIE, (), MODELL) != før


def test_nøkkelen_er_64_heksadesimale_tegn() -> None:
    assert re.fullmatch(r"[0-9a-f]{64}", ki.nøkkel(SERIE, (), MODELL))
