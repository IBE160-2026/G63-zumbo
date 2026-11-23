"""Domenemodellen: felles dataklasser og faste lister (AD-2).

Begrepene følger PRD kapittel 3. Modulen er en del av den rene kjernen (AD-1):
den importerer bare standardbiblioteket og bruker aldri klokka, nettet eller filer.
Skjulte og manglende verdier er `None`, aldri `0`.
"""

from dataclasses import dataclass
from types import MappingProxyType

GRENSE_USIKKER_UKE = 30
"""En uke med færre tester enn dette er usikker (PRD kapittel 3, FR-10)."""


@dataclass(frozen=True)
class Tabell:
    """En FHI-tabell med navn og FHIs egen kildetekst (PRD kapittel 4, addendum)."""

    nummer: int
    navn: str
    kildetekst: str


@dataclass(frozen=True)
class Virus:
    nøkkel: str
    navn: str
    tabell: int


@dataclass(frozen=True)
class Aldersgruppe:
    nøkkel: str
    etikett: str
    fhi_kode: str


@dataclass(frozen=True)
class Mal:
    nummer: int
    tittel: str
    spørsmål: str


TABELLER = MappingProxyType(
    {
        724: Tabell(
            724,
            "RESPIaggr Influensa antall og andel",
            "Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, "
            "Folkehelseinstituttet (FHI).",
        ),
        729: Tabell(
            729,
            "RESPIaggr RSV antall og andel",
            "Kilde: MSIS-labdatabase og Referanselaboratoriet for RS-virus, "
            "Folkehelseinstituttet (FHI).",
        ),
        731: Tabell(
            731,
            "RESPIaggr SARS-CoV-2 antall og andel",
            "Kilde: MSIS-labdatabase og Referanselaboratoriet for koronavirus med "
            "utbruddspotensiale, Folkehelseinstituttet (FHI).",
        ),
    }
)
"""Tabellene i v1. Kildetekstene er ordrett fra FHIs metadata (addendum, story 1.4)."""

VIRUS = MappingProxyType(
    {
        "influensa": Virus("influensa", "Influensa", 724),
        "rsv": Virus("rsv", "RSV", 729),
        "sars-cov-2": Virus("sars-cov-2", "SARS-CoV-2", 731),
    }
)
"""Virus → tabell (FR-2)."""

ALDERSGRUPPER = MappingProxyType(
    {
        "alle": Aldersgruppe("alle", "Alle aldersgrupper", "Alle"),
        "0-4": Aldersgruppe("0-4", "0–4 år", "0-4 år"),
        "5-14": Aldersgruppe("5-14", "5–14 år", "5-14 år"),
        "15-29": Aldersgruppe("15-29", "15–29 år", "15-29 år"),
        "30-64": Aldersgruppe("30-64", "30–64 år", "30-64 år"),
        "65-79": Aldersgruppe("65-79", "65–79 år", "65-79 år"),
        "80+": Aldersgruppe("80+", "80+ år", "80+ år"),
    }
)
"""De sju aldersgruppevalgene i rekkefølge, med «Alle» først (FR-4).

«Ukjent alder» (FHI: `Ukjent`) tilbys ikke.
"""

STANDARD_ALDERSGRUPPE = "alle"

MALER = MappingProxyType(
    {
        1: Mal(
            1,
            "Andel positive tester uke for uke",
            "Vis andel positive tester for {virus} i sesongen {sesong}",
        ),
    }
)
"""Malene i v1. Mal 2 (strekkmål) legges til i epic 8 (PRD kapittel 5)."""


@dataclass(frozen=True)
class Uke:
    """Tallene for én ISO-uke (PRD kapittel 3).

    `tester` og `positive` er `None` når verdien er skjult eller mangler.
    `andel` er andel positive i prosent. Den regnes ut fra `positive` og `tester`
    når den ikke er oppgitt, og er alltid `None` for en manglende uke (FR-11).
    """

    år: int
    ukenummer: int
    tester: int | None
    positive: int | None
    andel: float | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.ukenummer <= 53:
            raise ValueError(f"ugyldig ukenummer: {self.ukenummer}")
        for navn in ("tester", "positive"):
            verdi = getattr(self, navn)
            if verdi is not None and verdi < 0:
                raise ValueError(f"{navn} kan ikke være negativ: {verdi}")
        if self.manglende:
            andel = None
        elif self.andel is not None:
            andel = self.andel
        elif self.tester:
            andel = self.positive * 100 / self.tester
        else:
            andel = None
        object.__setattr__(self, "andel", andel)

    @property
    def manglende(self) -> bool:
        """Sann når antall tester eller antall positive er skjult (FR-16)."""
        return self.tester is None or self.positive is None

    @property
    def usikker(self) -> bool:
        """Sann ved færre enn 30 tester eller skjult antall tester (FR-10)."""
        return self.tester is None or self.tester < GRENSE_USIKKER_UKE
