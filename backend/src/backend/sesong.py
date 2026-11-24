"""Sesonger, ISO-uker og levetid for lagrede tall (FR-3, FR-7, AD-3, AD-5).

Modulen er en del av den rene kjernen (AD-1): den bruker aldri klokka, nettet
eller filer, og får «nå» som argument. En uke er en tuple `(år, ukenummer)` i
ISO-kalenderen, så uker kan sammenlignes og sorteres direkte.
"""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from backend.domene import er_sesong

FØRSTE_UKE = 40
"""Sesongen starter i uke 40 (PRD kapittel 3)."""

SISTE_UKE = 20
"""Sesongen slutter med uke 20 året etter."""

FØRSTE_SESONG = 2024
"""Startåret for den første sesongen appen viser (2024/2025, FR-3)."""

LEVETID = timedelta(hours=24)
"""Lagrede tall som er så gamle eller eldre, er utdaterte (FR-7, AD-5)."""

TOLERANSE = timedelta(minutes=5)
"""Så langt frem i tid kan `hentet` ligge og likevel regnes som ferskt."""

NORSK_TID = ZoneInfo("Europe/Oslo")

IsoUke = tuple[int, int]
"""En ISO-uke som `(år, ukenummer)`. Ikke det samme som `domene.Uke`, som har tall."""


def startår(sesong: str) -> int:
    """Første år i en sesong skrevet «2025/2026». Gir `ValueError` ellers.

    Formatet sjekkes med `domene.er_sesong`, slik at `Utvalg` og `sesong` godtar
    de samme sesongene.
    """
    if not er_sesong(sesong):
        raise ValueError(f"ugyldig sesong: {sesong!r}")
    return int(sesong[:4])


def navn(år: int) -> str:
    """Sesongen som starter i `år`, skrevet «2025/2026»."""
    return f"{år}/{år + 1}"


def _sjekk_uke(uke: IsoUke) -> IsoUke:
    """Gir uka som en tuple, eller `ValueError` hvis den ikke finnes."""
    try:
        år, ukenummer = uke
        if type(år) is not int or type(ukenummer) is not int:
            raise TypeError
        date.fromisocalendar(år, ukenummer, 1)
    except (TypeError, ValueError):
        raise ValueError(f"uka finnes ikke: {uke!r}") from None
    return (år, ukenummer)


def uker(sesong: str, siste_publiserte_uke: IsoUke | None = None) -> tuple[IsoUke, ...]:
    """Ukene i sesongen i rekkefølge: uke 40 til og med uke 20 året etter.

    Uke 53 er med når startåret har den (FR-3). Er `siste_publiserte_uke` gitt,
    stopper perioden ved den uka (sesongen som pågår, AD-3). Ligger den før
    sesongstart, er resultatet tomt.
    """
    år = startår(sesong)
    if siste_publiserte_uke is not None:
        siste_publiserte_uke = _sjekk_uke(siste_publiserte_uke)
    dag = date.fromisocalendar(år, FØRSTE_UKE, 1)
    slutt = date.fromisocalendar(år + 1, SISTE_UKE, 1)
    resultat = []
    while dag <= slutt:
        uke = dag.isocalendar()[:2]
        if siste_publiserte_uke is not None and uke > siste_publiserte_uke:
            break
        resultat.append(uke)
        dag += timedelta(weeks=1)
    return tuple(resultat)


def _må_ha_tidssone(felt: str, tid: datetime) -> None:
    if not isinstance(tid, datetime) or tid.utcoffset() is None:
        raise ValueError(f"{felt} må være et tidspunkt med tidssone")


def sesonger_fra_dato(nå: datetime) -> tuple[str, ...]:
    """Sesongene fra 2024/2025 til den som pågår, eldste først (reserve i AD-3).

    En sesong er med når mandag i uke 40 i startåret har kommet i norsk tid.
    Mellom sesongene (uke 21–39) er den siste sesongen som har startet, den som
    pågår. Brukes bare når FHIs dimensjonsliste ikke kan hentes eller leses.
    """
    _må_ha_tidssone("nå", nå)
    i_dag = nå.astimezone(NORSK_TID).date()
    siste = i_dag.year
    if i_dag < date.fromisocalendar(siste, FØRSTE_UKE, 1):
        siste -= 1
    return tuple(navn(år) for år in range(FØRSTE_SESONG, max(siste, FØRSTE_SESONG) + 1))


def er_utdatert(hentet: datetime, nå: datetime) -> bool:
    """Sann når tallene er hentet for 24 timer siden eller mer (FR-7, AD-5).

    Begge tidspunktene må ha tidssone. Tiden regnes i UTC, slik at skiftet til og
    fra sommertid ikke gjør en time for mye eller for lite. Ligger `hentet` mer
    enn fem minutter frem i tid, har klokka vært feil, og tallene regnes som
    utdaterte, slik at de hentes på nytt.
    """
    _må_ha_tidssone("hentet", hentet)
    _må_ha_tidssone("nå", nå)
    alder = nå.astimezone(UTC) - hentet.astimezone(UTC)
    return alder >= LEVETID or alder < -TOLERANSE
