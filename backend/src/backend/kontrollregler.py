"""Kontrollreglene som sier fra når datagrunnlaget er for tynt (FR-14–FR-19).

Modulen er en del av den rene kjernen (AD-1): den importerer bare `domene` og
standardbiblioteket. Reglene regnes over alle forventede uker i serien (AD-3).
Grensene står i PRD kapittel 6.5 og skal aldri svekkes for å gi færre varsler.
"""

from backend.domene import GRENSE_USIKKER_UKE, Dataserie, Regelutslag

GRENSE_POSITIVE = 20
"""R1: færre positive prøver enn dette gir utslag (FR-14)."""

GRENSE_PROSENT_UKER = 20
"""R2 og R3: mer enn denne andelen av ukene (i prosent) gir utslag (FR-15, FR-16)."""


def _over_grensen(antall: int, uker: int) -> bool:
    """Sann når `antall` er mer enn 20 % av `uker`.

    Regnes med heltall, slik at 4 av 20 (20 %) ikke gir utslag og 5 av 20 gir det.
    """
    return antall * 100 > GRENSE_PROSENT_UKER * uker


def _r1(serie: Dataserie) -> Regelutslag | None:
    """R1: summen av kjente positive prøver er under 20 (FR-14).

    Skjulte verdier (`None`) telles ikke. Kjente positive i en uke der bare
    antall tester er skjult, telles med.
    """
    positive = sum(u.positive for u in serie.uker if u.positive is not None)
    if positive >= GRENSE_POSITIVE:
        return None
    if positive == 0:
        antall = "ingen positive prøver"
    elif positive == 1:
        antall = "bare 1 positiv prøve"
    else:
        antall = f"bare {positive} positive prøver"
    return Regelutslag(
        "R1",
        f"Utvalget har {antall}. "
        f"Det trengs minst {GRENSE_POSITIVE} for et sikkert tall.",
    )


def _r2(serie: Dataserie) -> Regelutslag | None:
    """R2: mer enn 20 % av ukene har et kjent antall tester under 30 (FR-15).

    Bruker ikke `Uke.usikker`: uker med skjult antall tester telles under R3, og
    uker med flere positive enn tester telles bare hvis de har under 30 tester.
    """
    få = sum(
        1 for u in serie.uker if u.tester is not None and u.tester < GRENSE_USIKKER_UKE
    )
    if not _over_grensen(få, len(serie.uker)):
        return None
    return Regelutslag(
        "R2",
        f"{få} av {len(serie.uker)} uker har færre enn {GRENSE_USIKKER_UKE} tester.",
    )


def _r3(serie: Dataserie) -> Regelutslag | None:
    """R3: mer enn 20 % av ukene er manglende (FR-16).

    En uke med to skjulte verdier er én manglende uke.
    """
    manglende = sum(1 for u in serie.uker if u.manglende)
    if not _over_grensen(manglende, len(serie.uker)):
        return None
    return Regelutslag(
        "R3",
        f"{manglende} av {len(serie.uker)} uker mangler tall eller har skjulte tall.",
    )


def vurder(serie: Dataserie) -> list[Regelutslag]:
    """Gir ett `Regelutslag` per regel som slår inn, i rekkefølgen R1, R2, R3.

    Tom liste betyr at ingen regel slo inn, og at det ikke skal vises varsel
    (FR-19, konvensjonen «Regelutslag»).
    """
    utslag = (regel(serie) for regel in (_r1, _r2, _r3))
    return [u for u in utslag if u is not None]
