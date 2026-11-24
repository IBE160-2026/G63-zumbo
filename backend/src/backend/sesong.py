"""Sesonger, ISO-uker og levetid for lagrede tall (FR-3, FR-7, AD-3, AD-5).

Modulen er en del av den rene kjernen (AD-1): den bruker aldri klokka, nettet
eller filer, og får «nå» som argument. En uke er en tuple `(år, ukenummer)` i
ISO-kalenderen, så uker kan sammenlignes og sorteres direkte.
"""

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

FØRSTE_UKE = 40
"""Sesongen starter i uke 40 (PRD kapittel 3)."""

SISTE_UKE = 20
"""Sesongen slutter med uke 20 året etter."""

FØRSTE_SESONG = 2024
"""Startåret for den første sesongen appen viser (2024/2025, FR-3)."""

LEVETID = timedelta(hours=24)
"""Lagrede tall som er så gamle eller eldre, er utdaterte (FR-7, AD-5)."""

NORSK_TID = ZoneInfo("Europe/Oslo")

_SESONG = re.compile(r"([0-9]{4})/([0-9]{4})")

Uke = tuple[int, int]


def startår(sesong: str) -> int:
    """Første år i en sesong skrevet «2025/2026». Gir `ValueError` ellers."""
    treff = _SESONG.fullmatch(sesong) if isinstance(sesong, str) else None
    if not treff or int(treff[2]) != int(treff[1]) + 1:
        raise ValueError(f"ugyldig sesong: {sesong!r}")
    return int(treff[1])


def navn(år: int) -> str:
    """Sesongen som starter i `år`, skrevet «2025/2026»."""
    return f"{år}/{år + 1}"


def _sjekk_uke(uke: Uke) -> None:
    år, ukenummer = uke
    try:
        date.fromisocalendar(år, ukenummer, 1)
    except (TypeError, ValueError):
        raise ValueError(f"uka finnes ikke: {uke!r}") from None


def uker(sesong: str, siste_publiserte_uke: Uke | None = None) -> tuple[Uke, ...]:
    """Ukene i sesongen i rekkefølge: uke 40 til og med uke 20 året etter.

    Uke 53 er med når startåret har den (FR-3). Er `siste_publiserte_uke` gitt,
    stopper perioden ved den uka (sesongen som pågår, AD-3). Ligger den før
    sesongstart, er resultatet tomt.
    """
    år = startår(sesong)
    if siste_publiserte_uke is not None:
        _sjekk_uke(siste_publiserte_uke)
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

    Begge tidspunktene må ha tidssone. Et `hentet` frem i tid regnes som ferskt.
    """
    _må_ha_tidssone("hentet", hentet)
    _må_ha_tidssone("nå", nå)
    return nå - hentet >= LEVETID
