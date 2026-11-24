"""Mellomlagring av rå FHI-svar som JSON-filer (AD-4, FR-7, FR-8).

Den eneste koden som leser og skriver i cachemappen. Hver fil inneholder
`{"hentet": <ISO 8601 i UTC>, "svar": <rått FHI-svar>}`, samme format som
fixturene i `tests/fixtures/fhi/`. Filnavn for et utvalg kommer bare fra
`Utvalg.nøkkel`. En fil som ikke kan leses, regnes som at den ikke finnes.
"""

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.domene import TABELLER, Utvalg

FHI_MAPPE = "fhi"


@dataclass(frozen=True)
class Lagret:
    """Et lagret svar med tidspunktet det ble hentet fra FHI (i UTC)."""

    hentet: datetime
    svar: dict[str, Any]


def svarfil(mappe: Path, utvalg: Utvalg) -> Path:
    """`<mappe>/fhi/<Utvalg.nøkkel>.json`. `nøkkel` gir bare trygge tegn."""
    return mappe / FHI_MAPPE / f"{utvalg.nøkkel}.json"


def dimensjonsfil(mappe: Path, tabell: int) -> Path:
    """`<mappe>/fhi/<tabell>-dimensjoner.json`, bare for kjente tabeller."""
    if type(tabell) is not int or tabell not in TABELLER:
        raise ValueError(f"ukjent tabell: {tabell!r}")
    return mappe / FHI_MAPPE / f"{tabell}-dimensjoner.json"


def _som_tekst(hentet: datetime) -> str:
    if not isinstance(hentet, datetime) or hentet.utcoffset() is None:
        raise ValueError("hentet må være et tidspunkt med tidssone")
    return hentet.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _skriv(fil: Path, svar: dict[str, Any], hentet: datetime) -> None:
    """Skriver via en midlertidig fil og `os.replace`, så ingen ser en halv fil."""
    if not isinstance(svar, dict):
        raise TypeError("svar må være et JSON-objekt")
    innhold = json.dumps(
        {"hentet": _som_tekst(hentet), "svar": svar}, ensure_ascii=False
    )
    fil.parent.mkdir(parents=True, exist_ok=True)
    fd, midlertidig = tempfile.mkstemp(
        dir=fil.parent, prefix=f".{fil.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as ut:
            ut.write(innhold)
            ut.flush()
            os.fsync(ut.fileno())
        os.replace(midlertidig, fil)
    except BaseException:
        Path(midlertidig).unlink(missing_ok=True)
        raise


def _les(fil: Path) -> Lagret | None:
    """Leser en fil. Alt som ikke er en gyldig fil, gir `None` (AD-4)."""
    try:
        innhold = json.loads(fil.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError):
        return None
    if not isinstance(innhold, dict) or set(innhold) != {"hentet", "svar"}:
        return None
    tekst, svar = innhold["hentet"], innhold["svar"]
    if not isinstance(tekst, str) or not isinstance(svar, dict):
        return None
    try:
        hentet = datetime.fromisoformat(tekst)
    except ValueError:
        return None
    if hentet.utcoffset() is None:
        return None
    return Lagret(hentet=hentet.astimezone(UTC), svar=svar)


def lagre_svar(
    mappe: Path, utvalg: Utvalg, svar: dict[str, Any], hentet: datetime
) -> None:
    """Lagrer det rå svaret for et utvalg. `OSError` sendes videre."""
    _skriv(svarfil(mappe, utvalg), svar, hentet)


def les_svar(mappe: Path, utvalg: Utvalg) -> Lagret | None:
    """Det lagrede svaret for et utvalg, eller `None`."""
    return _les(svarfil(mappe, utvalg))


def lagre_dimensjoner(
    mappe: Path, tabell: int, svar: dict[str, Any], hentet: datetime
) -> None:
    """Lagrer den rå dimensjonslisten for en tabell. `OSError` sendes videre."""
    _skriv(dimensjonsfil(mappe, tabell), svar, hentet)


def les_dimensjoner(mappe: Path, tabell: int) -> Lagret | None:
    """Den lagrede dimensjonslisten for en tabell, eller `None`."""
    return _les(dimensjonsfil(mappe, tabell))
