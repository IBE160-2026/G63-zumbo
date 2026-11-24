"""KI-forklaringen fra Claude, med tre utfall (FR-20, FR-22, NFR-1, AD-6).

Den eneste modulen som importerer `anthropic`. `forklar` gir alltid ett av tre
utfall og kaster aldri videre:

- `Forklaring(tekst)`: Claude svarte med en forklaring.
- `ManglerNøkkel`: ingen KI-nøkkel er satt. Da kalles ikke Claude.
- `KiFeil`: Claude svarte ikke, eller svaret kunne ikke brukes.

Teksten brukeren ser for `ManglerNøkkel` og `KiFeil` står i malene (FR-22).
Prompten i `prompts/forklaring.md` får bare utvalget, ukene, regelutslagene og
kildehenvisningen. Tallene for hver uke er de samme som i tabellen (Irenes
beslutning på #23), men skjulte tall og andeler som mangler, er skrevet
tydeligere for KI-en (Irenes beslutning før merge av PR #66).
"""

import hashlib
import json
import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import anthropic

from backend.config import Innstillinger
from backend.domene import Dataserie, Kildehenvisning, Regelutslag, Uke
from backend.formatering import andelstekst, kildetekst, tall, uke, utvalgstekst

logger = logging.getLogger(__name__)

PROMPT = Path(__file__).parent / "prompts" / "forklaring.md"

MAKS_TOKENS = 4096
"""Forklaringen er høyst 120 ord. Resten gir plass til tenkingen, som er på som
standard i `claude-haiku-5-5`. Når grensen nås, blir utfallet `KiFeil`."""

INNSATS = "low"
"""`effort` for Claude. En kort forklaring av noen tall trenger lite tenking."""

TIDSGRENSE = 15.0
"""Sekunder per forsøk. Med ett nytt forsøk kan kallet ta drøyt 30 sekunder i
alt. Siden venter likevel ikke på KI-en, for forklaringen hentes for seg
(NFR-2, AD-9)."""

FORSØK_PÅ_NYTT = 1
"""Antall nye forsøk SDK-en gjør ved nettverksfeil, 429 og 5xx."""


@dataclass(frozen=True)
class Forklaring:
    """Forklaringen Claude skrev."""

    tekst: str


@dataclass(frozen=True)
class ManglerNøkkel:
    """Ingen KI-nøkkel er satt, så Claude ble ikke kalt (FR-22, NFR-1)."""


@dataclass(frozen=True)
class KiFeil:
    """Claude svarte ikke, eller svaret kunne ikke brukes (FR-22)."""


Utfall = Forklaring | ManglerNøkkel | KiFeil


def ukelinje(verdi: Uke) -> str:
    """Én uke slik KI-en får den.

    Tallene er de samme som i tabellen («1 210», «20,8 %»), men ordene er
    tydeligere når et tall er skjult eller andelen ikke finnes (Irenes beslutning
    før merge av PR #66):

    - «uke 50: 1 210 tester, 252 positive, 20,8 %»
    - «uke 3: skjult antall tester, 5 positive, andel mangler»
    - «uke 41: 0 tester, 0 positive, andel kan ikke regnes ut»
    """
    tester = (
        "skjult antall tester"
        if verdi.tester is None
        else f"{tall(verdi.tester)} tester"
    )
    positive = (
        "skjult antall positive"
        if verdi.positive is None
        else f"{tall(verdi.positive)} positive"
    )
    andel = andelstekst(verdi)
    if verdi.andel is None:
        andel = f"andel {andel}"
    return f"{uke(verdi)}: {tester}, {positive}, {andel}"


@cache
def _mal() -> str:
    return PROMPT.read_text(encoding="utf-8")


def lag_prompt(
    serie: Dataserie, regelutslag: Iterable[Regelutslag], kilde: Kildehenvisning
) -> str:
    """Fyller ut prompten med utvalget, ukene, regelutslagene og kilden.

    Hver uke står på én linje, med de samme tallene som tabellen (`ukelinje`). Hvert regelutslag står
    på én linje med setningen fra varselet. Uten regelutslag står det ingenting
    der, slik prompten sier.
    """
    return _mal().format(
        utvalg=utvalgstekst(serie.utvalg),
        uker="\n".join(ukelinje(u) for u in serie.uker),
        regelutslag="\n".join(f"- {r.tekst}" for r in regelutslag),
        kildehenvisning=kildetekst(kilde),
    )


def nøkkel(serie: Dataserie, regelutslag: Iterable[Regelutslag], modell: str) -> str:
    """Nøkkelen til en lagret forklaring (AD-7).

    SHA-256 av kanonisk JSON (`sort_keys=True`) med utvalget, de tolkede ukene,
    regelutslagene, innholdet i promptfila og modellnavnet. Hentetidspunktet er
    ikke med, så de samme tallene gir samme nøkkel også etter en ny henting.
    Endrede tall, en endret prompt eller en annen modell gir ny nøkkel.
    """
    u = serie.utvalg
    innhold = {
        "utvalg": {
            "mal": u.mal,
            "virus": u.virus,
            "sesong": u.sesong,
            "aldersgruppe": u.aldersgruppe,
        },
        "uker": [[x.år, x.ukenummer, x.tester, x.positive] for x in serie.uker],
        "regelutslag": [[r.regel, r.tekst] for r in regelutslag],
        "prompt": _mal(),
        "modell": modell,
    }
    kanonisk = json.dumps(
        innhold, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(kanonisk.encode("utf-8")).hexdigest()


def _tekst(svar: Any) -> str | None:
    """Teksten i svaret, eller `None` når svaret ikke er en hel forklaring."""
    if getattr(svar, "stop_reason", None) != "end_turn":
        return None
    deler = [
        blokk.text
        for blokk in getattr(svar, "content", None) or []
        if getattr(blokk, "type", None) == "text"
    ]
    tekst = "".join(deler).strip()
    return tekst or None


def forklar(
    serie: Dataserie,
    regelutslag: Iterable[Regelutslag],
    kilde: Kildehenvisning,
    innstillinger: Innstillinger,
    ny_klient: Callable[..., Any] | None = None,
) -> Utfall:
    """Ber Claude forklare tallene for ett utvalg (AD-6).

    Uten nøkkel kalles ikke Claude, og utfallet er `ManglerNøkkel`. Ellers lages
    klienten med eksplisitt `api_key=`, slik at SDK-en aldri leter etter nøkler
    andre steder, og modellen er `innstillinger.anthropic_model`. Alle feil, også
    uventede, blir `KiFeil`, og bare feiltypen logges, aldri nøkkelen.

    `ny_klient` er `anthropic.Anthropic` når den er `None`. Testene sender inn
    en falsk klient og kaller aldri Claude på ekte (AD-10).
    """
    nøkkel = innstillinger.anthropic_api_key
    if not nøkkel:
        return ManglerNøkkel()
    try:
        prompt = lag_prompt(serie, regelutslag, kilde)
        # `with` lukker forbindelsene til klienten etter hvert kall.
        with (ny_klient or anthropic.Anthropic)(
            api_key=nøkkel, timeout=TIDSGRENSE, max_retries=FORSØK_PÅ_NYTT
        ) as klient:
            svar = klient.messages.create(
                model=innstillinger.anthropic_model,
                max_tokens=MAKS_TOKENS,
                output_config={"effort": INNSATS},
                messages=[{"role": "user", "content": prompt}],
            )
        tekst = _tekst(svar)
    except anthropic.APIStatusError as feil:
        logger.info(
            "KI-forklaringen feilet: %s (%s)", type(feil).__name__, feil.status_code
        )
        return KiFeil()
    except Exception as feil:  # noqa: BLE001 – forklar skal aldri kaste (AD-6)
        logger.info("KI-forklaringen feilet: %s", type(feil).__name__)
        return KiFeil()
    if tekst is None:
        logger.info(
            "KI-forklaringen kunne ikke brukes: stop_reason=%s",
            getattr(svar, "stop_reason", None),
        )
        return KiFeil()
    return Forklaring(tekst)
