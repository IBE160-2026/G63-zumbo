"""Tall, uker og kilder slik siden viser dem (arkitektur §4).

All formatering for visning står her, og bare her. `web` bruker funksjonene som
Jinja2-filtre, og `ki` bruker de samme funksjonene når prompten fylles ut, slik
at KI-en får tallene nøyaktig slik de står i tabellen (Irenes beslutning på #23).

Modulen er ren: den importerer bare `domene` og standardbiblioteket.
"""

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

from backend.domene import ALDERSGRUPPER, VIRUS, Kildehenvisning, Uke, Utvalg

NORSK_TID = ZoneInfo("Europe/Oslo")
"""Hentetidspunktet vises i norsk tid (AD-5). Lagret tid er UTC."""

HARDT_MELLOMROM = "\u00a0"
"""Mellomrom som ikke brytes, i tall og foran «%» (arkitektur §4)."""


def tall(verdi: int | None) -> str:
    """«1 210» med mellomrom som tusenskille. `None` er en skjult verdi (FR-11)."""
    if verdi is None:
        return "skjult"
    return f"{verdi:,}".replace(",", HARDT_MELLOMROM)


def avrundet(verdi: float) -> Decimal:
    """Andelen med én desimal, avrundet halvt opp. Brukes av både tabellen og
    grafen, så de viser samme tall."""
    return Decimal(repr(verdi)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def andel(verdi: float | None) -> str:
    """«20,8 %» med én desimal, avrundet halvt opp. `None` blir «mangler»."""
    if verdi is None:
        return "mangler"
    return f"{avrundet(verdi)}".replace(".", ",") + HARDT_MELLOMROM + "%"


def andelstekst(verdi: Uke) -> str:
    """Andelen i en uke slik tabellen viser den.

    «mangler» bare når et tall er skjult eller mangler (FR-11). En uke med
    0 tester har kjente tall, men andelen kan ikke regnes ut (Irenes beslutning
    24.11.2026). Er antall tester 0 og antall positive skjult, er et tall skjult,
    og uka viser «mangler».
    """
    if verdi.andel is not None or verdi.manglende:
        return andel(verdi.andel)
    return "kan ikke regnes ut"


def uke(verdi: Uke) -> str:
    """«uke 50»."""
    return f"uke {verdi.ukenummer}"


def utvalgstekst(verdi: Utvalg) -> str:
    """«Influensa, sesongen 2025/2026, alle aldersgrupper» (FR-9)."""
    alder = ALDERSGRUPPER[verdi.aldersgruppe].etikett
    return f"{VIRUS[verdi.virus].navn}, sesongen {verdi.sesong}, {alder[0].lower()}{alder[1:]}"


def tidspunkt(verdi: datetime) -> str:
    """«20.11.2026 kl. 14:05» i norsk tid (AD-5)."""
    return verdi.astimezone(NORSK_TID).strftime("%d.%m.%Y kl. %H:%M")


def kildetekst(kilde: Kildehenvisning) -> str:
    """Kildehenvisningen slik den står under grafen (FR-12).

    «Kilde: … Tabell 724 «RESPIaggr Influensa antall og andel». Hentet
    20.11.2026 kl. 14:05.» Den samme teksten brukes ved KI-forklaringen (FR-20).
    """
    return (
        f"{kilde.kildetekst} Tabell {kilde.tabell} «{kilde.tabellnavn}». "
        f"Hentet {tidspunkt(kilde.hentet)}."
    )


def ukelinje(verdi: Uke) -> str:
    """Én uke slik raden står i tabellen: «uke 50: 1 210 tester, 252 positive,
    20,8 %» (Irenes beslutning på #23).

    Et skjult tall står som «skjult» foran ordet, slik tabellen viser det i
    kolonnen: «uke 3: skjult tester, 5 positive, mangler».
    """
    return (
        f"{uke(verdi)}: {tall(verdi.tester)} tester, "
        f"{tall(verdi.positive)} positive, {andelstekst(verdi)}"
    )
