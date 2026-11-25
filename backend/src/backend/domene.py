"""Domenemodellen: felles dataklasser og faste lister (AD-2).

Begrepene følger PRD kapittel 3. Modulen er en del av den rene kjernen (AD-1):
den importerer bare standardbiblioteket og bruker aldri klokka, nettet eller filer.
Skjulte og manglende verdier er `None`, aldri `0`.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
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
    `andel` regnes alltid ut her fra `positive` og `tester`, slik at den ikke kan
    bli stående gammel eller avvike fra tallene.
    """

    år: int
    ukenummer: int
    tester: int | None
    positive: int | None

    def __post_init__(self) -> None:
        try:
            date.fromisocalendar(self.år, self.ukenummer, 1)
        except ValueError:
            raise ValueError(f"uka finnes ikke: {self.år}-w{self.ukenummer}") from None
        for navn in ("tester", "positive"):
            verdi = getattr(self, navn)
            if verdi is not None and verdi < 0:
                raise ValueError(f"{navn} kan ikke være negativ: {verdi}")

    @property
    def andel(self) -> float | None:
        """Andel positive i prosent: positive delt på tester, ganget med 100.

        `None` for en manglende uke, aldri 0 (FR-11). `None` også når uka har
        0 tester, fordi andelen da ikke kan regnes ut. En slik uke er usikker,
        men ikke manglende (tallene er ikke skjult).
        """
        if self.manglende or not self.tester:
            return None
        return self.positive * 100 / self.tester

    @property
    def manglende(self) -> bool:
        """Sann når antall tester eller antall positive er skjult (FR-16)."""
        return self.tester is None or self.positive is None

    @property
    def flere_positive_enn_tester(self) -> bool:
        """Sann når uka har flere positive prøver enn tester (andel over 100 %).

        Endret 24. november 2026: Irenes beslutning i story 2.4: andelen vises
        som den er, og uka er usikker med en fotnote. Med 0 tester kan andelen
        ikke regnes ut (`andel` er `None`), men uka er likevel usikker.
        """
        return (
            self.tester is not None
            and self.positive is not None
            and self.positive > self.tester
        )

    @property
    def usikker(self) -> bool:
        """Sann ved færre enn 30 tester, skjult antall tester, eller flere
        positive enn tester (FR-10).

        Endret 24. november 2026: Irenes beslutning i story 2.4: en uke med flere positive enn tester er også usikker.
        Kontrollregel R2 bruker ikke denne egenskapen. Den teller bare uker med
        et kjent antall tester under 30 (FR-15).
        """
        return (
            self.tester is None
            or self.tester < GRENSE_USIKKER_UKE
            or self.flere_positive_enn_tester
        )


class UgyldigUtvalg(ValueError):
    """Parametrene gir ikke et gyldig utvalg (FR-5).

    Meldingen er på norsk, sier hva som må rettes og kan vises til brukeren som
    den er. Den inneholder aldri verdien brukeren sendte eller FHI-koder (NFR-3).
    """


_TRYGG_NØKKEL = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
_SESONG = re.compile(r"([0-9]{4})/([0-9]{4})")


def er_sesong(tekst: object) -> bool:
    """Sann for en sesong skrevet «2025/2026», der andre år er første år + 1."""
    treff = isinstance(tekst, str) and _SESONG.fullmatch(tekst)
    return bool(treff) and int(treff[2]) == int(treff[1]) + 1


def _liste(navn: list[str]) -> str:
    """«a», «a eller b», «a, b eller c»."""
    if len(navn) == 1:
        return navn[0]
    return ", ".join(navn[:-1]) + " eller " + navn[-1]


def _spørsmål(mal: Mal, virus: str, sesong: str, sesonger: list[str]) -> str:
    """Malens spørsmål med valgene som er gyldige, slik skjemaet viste det (FR-1).

    Et gyldig virus og en gyldig sesong settes inn. Ellers står «viruset du
    velger» og «du velger», så meldingen aldri gjentar en ugyldig verdi fra
    adressen. Virusnavn som er vanlige ord, får liten forbokstav («influensa»),
    mens forkortelser som «RSV» og «SARS-CoV-2» står som de er.
    """
    virustekst = "viruset du velger"
    if virus in VIRUS:
        navn = VIRUS[virus].navn
        virustekst = navn[0].lower() + navn[1:] if navn[1:2].islower() else navn
    sesongtekst = sesong if sesong in sesonger else "du velger"
    return mal.spørsmål.format(virus=virustekst, sesong=sesongtekst)


@dataclass(frozen=True)
class Utvalg:
    """Kombinasjonen brukeren har valgt (PRD kapittel 3).

    Feltene er nøklene i `MALER`, `VIRUS` og `ALDERSGRUPPER`, og sesongen skrevet
    som «2025/2026». Lag utvalg fra brukeren med `Utvalg.fra_parametre`, som er
    stedet der brukerens valg sjekkes og får en norsk melding (AD-9). `nøkkel`
    sjekker verdiene på nytt som et sikkerhetsnett for filnavnet.
    Overvåkingstypen er alltid vanlig klinisk praksis i v1.
    """

    mal: int
    virus: str
    sesong: str
    aldersgruppe: str = STANDARD_ALDERSGRUPPE

    @property
    def tabell(self) -> int:
        return VIRUS[self.virus].tabell

    @classmethod
    def fra_parametre(
        cls, parametre: Mapping[str, str], gyldige_sesonger: Iterable[str]
    ) -> "Utvalg":
        """Lager et utvalg fra query-parametrene `mal`, `virus`, `sesong`, `alder`.

        Bare de eksakte nøklene i listene godtas. Manglende eller tom `alder`
        gir «Alle aldersgrupper» (FR-4). Er noe galt, kastes `UgyldigUtvalg`
        med én setning per felt som må rettes (FR-5).

        Sesonger i `gyldige_sesonger` som ikke er skrevet «2025/2026», hoppes
        over, slik at et godkjent utvalg alltid har en gyldig `nøkkel`.
        """
        if isinstance(gyldige_sesonger, str):
            raise TypeError("gyldige_sesonger må være en liste, ikke én tekst")
        sesonger = list(dict.fromkeys(s for s in gyldige_sesonger if er_sesong(s)))
        mal = parametre.get("mal") or ""
        virus = parametre.get("virus") or ""
        sesong = parametre.get("sesong") or ""
        alder = parametre.get("alder") or STANDARD_ALDERSGRUPPE

        feil = []
        malnummer = {str(nr): nr for nr in MALER}.get(mal)
        if malnummer is None:
            spørsmål = _liste(
                [f"«{_spørsmål(m, virus, sesong, sesonger)}»" for m in MALER.values()]
            )
            feil.append(f"Velg en mal: {spørsmål}.")
        if virus not in VIRUS:
            navn = _liste([v.navn for v in VIRUS.values()])
            feil.append(f"Velg et virus: {navn}.")
        if sesong not in sesonger:
            if sesonger:
                feil.append(f"Velg en sesong: {_liste(sesonger)}.")
            else:
                feil.append("Det finnes ingen sesonger å velge nå. Prøv igjen senere.")
        if alder not in ALDERSGRUPPER:
            etiketter = _liste([g.etikett for g in ALDERSGRUPPER.values()])
            feil.append(f"Velg en aldersgruppe: {etiketter}.")
        if feil:
            raise UgyldigUtvalg(" ".join(feil))
        return cls(mal=malnummer, virus=virus, sesong=sesong, aldersgruppe=alder)

    @property
    def nøkkel(self) -> str:
        """Filnavnet for utvalget i cachen, uten filendelse (AD-4).

        Bare `a-z`, `0-9` og `-`, likt for like utvalg og ulikt for ulike. For
        eksempel `mal1-influensa-2025-2026-80pluss`. Gir `ValueError` for et
        utvalg med verdier som ikke finnes i listene, også når det er laget uten
        `fra_parametre`, slik at ingen verdi kan bli et farlig filnavn.
        """
        if (
            type(self.mal) is not int
            or self.mal not in MALER
            or self.virus not in VIRUS
            or self.aldersgruppe not in ALDERSGRUPPER
            or not er_sesong(self.sesong)
        ):
            raise ValueError("utvalget gir ikke et trygt filnavn")
        deler = [f"mal{self.mal}", self.virus, self.sesong, self.aldersgruppe]
        nøkkel = "-".join(deler).replace("/", "-").replace("+", "pluss")
        if not _TRYGG_NØKKEL.fullmatch(nøkkel):
            raise ValueError("utvalget gir ikke et trygt filnavn")
        return nøkkel


@dataclass(frozen=True)
class Dataserie:
    """Ukene for ett utvalg.

    `fhi.tolk` (story 2.4) lager serien med én `Uke` per forventet uke, i
    rekkefølge (AD-3). Dataklassen sjekker ikke dette selv.
    """

    utvalg: Utvalg
    uker: tuple[Uke, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "uker", tuple(self.uker))


REGLER = ("R1", "R2", "R3", "R4", "R5")


@dataclass(frozen=True)
class Regelutslag:
    """At én kontrollregel slo inn, med en ferdig setning på enkel norsk."""

    regel: str
    tekst: str

    def __post_init__(self) -> None:
        if self.regel not in REGLER:
            raise ValueError(f"ukjent kontrollregel: {self.regel!r}")
        if not self.tekst.strip():
            raise ValueError("regelutslaget mangler tekst")


@dataclass(frozen=True)
class Kildehenvisning:
    """Henvisning til FHI-tabellen tallene kommer fra (PRD kapittel 3, FR-12).

    `hentet` er tidspunktet for hentingen, med tidssone. Formatering for visning
    skjer i `formatering`.
    """

    kildetekst: str
    tabell: int
    tabellnavn: str
    hentet: datetime


def kildehenvisning(tabell: int, hentet: datetime) -> Kildehenvisning:
    """Lager kildehenvisningen for en tabell.

    Bruk alltid denne og ikke `Kildehenvisning(...)` direkte, slik at teksten
    og tabellnavnet kommer fra `TABELLER` (konvensjonen «Kildehenvisning»).
    """
    if tabell not in TABELLER:
        raise ValueError(f"ukjent tabell: {tabell}")
    if hentet.utcoffset() is None:
        raise ValueError("hentet må ha tidssone")
    t = TABELLER[tabell]
    return Kildehenvisning(
        kildetekst=t.kildetekst, tabell=t.nummer, tabellnavn=t.navn, hentet=hentet
    )
