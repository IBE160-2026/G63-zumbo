"""De sju faste begrepsforklaringene på siden (FR-13, AD-8).

Tekstene er skrevet av Irene i story 3.5 (issue #19) og står her ordrett. De
lages aldri av KI. Hver tekst har høyst tre setninger.

Modulen er en del av den rene kjernen og importerer ingen andre moduler i
appen (arkitektur §2).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Begrep:
    """Ett begrep med forklaring.

    `nøkkel` brukes i HTML-id-en «begrep-<nøkkel>», så lenker kan peke på
    forklaringen.
    """

    nøkkel: str
    navn: str
    tekst: str

    @property
    def html_id(self) -> str:
        return f"begrep-{self.nøkkel}"


TYNT_DATAGRUNNLAG = "tynt-datagrunnlag"
"""Nøkkelen til forklaringen som varselet lenker til (FR-19)."""

BEGREPER: tuple[Begrep, ...] = (
    Begrep(
        "andel-positive",
        "Andel positive",
        (
            "Andel positive viser hvor mange prosent av prøvene som var positive. "
            "Ble 1 000 prøver undersøkt og viruset funnet i 50 av dem, er andelen 5"
            " %. Andelen påvirkes av hvem som blir testet og kan endre seg selv om "
            "smitten ikke gjør det."
        ),
    ),
    Begrep(
        "test-og-positiv-prove",
        "Test og positiv prøve",
        (
            "Tester er antall prøver som et laboratorium undersøkte for viruset den"
            " uka. Samme person kan bli testet flere ganger og telles da flere "
            "ganger. En positiv prøve betyr at viruset ble funnet, men den sier "
            "ikke hvor syk personen var."
        ),
    ),
    Begrep(
        "sesong",
        "Sesong",
        (
            "En sesong går fra uke 40 til uke 20 året etter. Det er omtrent fra "
            "oktober til mai, når influensa og RSV sprer seg mest. FHIs egne "
            "ukerapporter starter i uke 35 og kan derfor begynne litt tidligere enn"
            " appen."
        ),
    ),
    Begrep(
        "aldersgruppe",
        "Aldersgruppe",
        (
            "Du kan se tallene for én aldersgruppe eller for alle aldre samlet. "
            "Virus rammer aldersgrupper ulikt, og RSV er for eksempel vanligst hos "
            "de minste barna. Jo smalere gruppe du velger, jo færre tester er det "
            "og jo mer kan andelen svinge av tilfeldigheter."
        ),
    ),
    Begrep(
        "overvakingstype",
        "Overvåkingstype",
        (
            "Appen viser tall fra vanlig klinisk praksis, altså prøver som tas når "
            "en lege mener at pasienten bør testes. Fyrtårnsystemet er et mindre "
            "nettverk av leger over hele landet som tester pasienter for mange "
            "ulike luftveisvirus. Appen bruker vanlig klinisk praksis fordi det gir"
            " langt flere prøver."
        ),
    ),
    Begrep(
        "msis",
        "MSIS",
        (
            "MSIS står for Meldingssystem for smittsomme sykdommer og er et "
            "nasjonalt register som FHI har ansvaret for. Laboratoriene sender "
            "svarene på prøvene dit, også de negative, og derfor kan andelen "
            "positive regnes ut. Appen viser bare samlede tall og aldri noe om "
            "enkeltpersoner."
        ),
    ),
    Begrep(
        "tynt-datagrunnlag",
        "For tynt datagrunnlag",
        (
            "Varselet betyr at tallene er usikre og at du bør være forsiktig med å "
            "trekke konklusjoner. Det kan skyldes for få prøver eller uker, mange "
            "hull i tallene eller at perioden går over 1. mars 2025. Da kom alle "
            "laboratoriene med i registeret, så tall før og etter kan ikke "
            "sammenlignes direkte."
        ),
    ),
)
"""I samme rekkefølge som i FR-13."""
