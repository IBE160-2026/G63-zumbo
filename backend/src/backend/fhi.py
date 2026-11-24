"""Tolking av svar fra FHIs åpne API, formatet `json-stat2` (AD-3).

Tolkefunksjonene her er rene (AD-1): de bruker ikke nettet, filer eller klokka,
og importerer bare standardbiblioteket, `domene` og `sesong`. Formatet og
særhetene står i `tests/fixtures/fhi/README.md`. Bare denne modulen og `domene`
kjenner FHIs koder (AD-2).
"""

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

from backend import sesong
from backend.domene import ALDERSGRUPPER, Dataserie, Uke, Utvalg
from backend.sesong import IsoUke

UKEDIMENSJON = "dateusedforstatistics"
MÅLTALL = "MEASURE_TYPE"
POSITIVE = "Detections"
TESTER = "Tests"
ALDERSDIMENSJON = "aldersgruppe"

FASTE_FILTRE: Mapping[int, Mapping[str, str]] = {
    724: {"influenzatypeandsubtype": "A+B", "surveillancetype": "NONSTL"},
}
"""Faste valg per tabell: totalen for virustypen og vanlig klinisk praksis."""

SKJULTE_VERDIER = frozenset({"..", ".", ":", ""})
"""Tekster FHI bruker for en skjult verdi (PRD kapittel 3). `null` er også skjult."""

_UKEKODE = re.compile(r"([0-9]{4})-w([0-9]{2})")


def les_ukekode(kode: str) -> IsoUke:
    """`"2025-w40"` → `(2025, 40)`. Gir `ValueError` for andre former og uker som
    ikke finnes."""
    treff = _UKEKODE.fullmatch(kode) if isinstance(kode, str) else None
    if not treff:
        raise ValueError(f"ukjent ukekode: {kode!r}")
    return sesong.sjekk_uke((int(treff[1]), int(treff[2])))


# --- Dimensjonslisten (`GET …/Table/<tabell>/dimension`) ---


def _ukekoder_i_dimensjonslisten(dimensjoner: Mapping[str, Any]) -> list[str]:
    try:
        (ukedimensjon,) = [
            d for d in dimensjoner["dimensions"] if d["code"] == UKEDIMENSJON
        ]
        return [k["value"] for k in ukedimensjon["categories"]]
    except (KeyError, TypeError, ValueError) as feil:
        raise ValueError("dimensjonslisten mangler ukene") from feil


def siste_publiserte_uke(dimensjoner: Mapping[str, Any]) -> IsoUke:
    """Den høyeste uka i dimensjonslisten (AD-3)."""
    uker = [les_ukekode(k) for k in _ukekoder_i_dimensjonslisten(dimensjoner)]
    if not uker:
        raise ValueError("dimensjonslisten har ingen uker")
    return max(uker)


def sesonger(dimensjoner: Mapping[str, Any]) -> tuple[str, ...]:
    """Sesongene som har minst én publisert uke, eldste først (FR-3, AD-3).

    Uke 21–39 hører ikke til noen sesong. Sesonger før 2024/2025 tas ikke med.
    """
    startår = set()
    for kode in _ukekoder_i_dimensjonslisten(dimensjoner):
        år, uke = les_ukekode(kode)
        if uke >= sesong.FØRSTE_UKE:
            startår.add(år)
        elif uke <= sesong.SISTE_UKE:
            startår.add(år - 1)
    return tuple(
        sesong.navn(år) for år in sorted(startår) if år >= sesong.FØRSTE_SESONG
    )


# --- Datasvaret (`POST …/Table/<tabell>/data`, `json-stat2`) ---


def _kategorier(svar: Mapping[str, Any], dimensjon: str) -> list[str]:
    """Kodene i en dimensjon i rekkefølgen de har i `value`."""
    indeks = svar["dimension"][dimensjon]["category"]["index"]
    if isinstance(indeks, Mapping):
        return sorted(indeks, key=indeks.__getitem__)
    if isinstance(indeks, Sequence) and not isinstance(indeks, str):
        return list(indeks)
    raise ValueError(f"ugyldig kategoriliste for {dimensjon}")


def _tall(verdi: Any) -> int | None:
    """Et antall fra FHI, eller `None` for en skjult verdi. Aldri 0 for skjult."""
    if verdi is None:
        return None
    if isinstance(verdi, str) and verdi.strip() in SKJULTE_VERDIER:
        return None
    if isinstance(verdi, bool) or not isinstance(verdi, int | float):
        raise TypeError(f"ugyldig antall: {verdi!r}")
    if not math.isfinite(verdi) or verdi < 0 or int(verdi) != verdi:
        raise ValueError(f"ugyldig antall: {verdi!r}")
    return int(verdi)


def _sjekk_filtre(svar: Mapping[str, Any], utvalg: Utvalg, ider: list[str]) -> None:
    """Svaret må gjelde akkurat utvalget, ellers kan vi vise feil tall (FR-6)."""
    forventet = {
        ALDERSDIMENSJON: ALDERSGRUPPER[utvalg.aldersgruppe].fhi_kode,
        **FASTE_FILTRE.get(utvalg.tabell, {}),
    }
    if utvalg.tabell not in FASTE_FILTRE:
        raise ValueError(f"tabell {utvalg.tabell} kan ikke tolkes ennå")
    for dimensjon in ider:
        if dimensjon in (UKEDIMENSJON, MÅLTALL):
            continue
        koder = _kategorier(svar, dimensjon)
        if len(koder) != 1:
            raise ValueError(f"{dimensjon} har {len(koder)} kategorier, ikke 1")
        if dimensjon in forventet and koder[0] != forventet[dimensjon]:
            raise ValueError(f"{dimensjon} er {koder[0]!r}, ikke det som ble valgt")
    mangler = set(forventet) - set(ider)
    if mangler:
        raise ValueError(f"svaret mangler {sorted(mangler)}")


def tolk(
    rått_svar: Mapping[str, Any],
    utvalg: Utvalg,
    siste_publiserte_uke: IsoUke | None = None,
) -> Dataserie:
    """Lager en `Dataserie` med én `Uke` per forventet uke (AD-3, FR-6).

    `rått_svar` er `svar` fra FHI eller cachen. Ukene er `sesong.uker` for
    utvalgets sesong frem til `siste_publiserte_uke` (fra dimensjonslisten).
    Uten den brukes den høyeste uka i svaret. En uke FHI ikke sendte, og skjulte
    verdier, blir `None`, aldri 0 (FR-11, FR-16). Et svar som ikke har riktig
    form eller ikke gjelder utvalget, gir `ValueError`.
    """
    try:
        return _tolk(rått_svar, utvalg, siste_publiserte_uke)
    except (KeyError, TypeError, IndexError, AttributeError) as feil:
        raise ValueError(f"ugyldig svar fra FHI: {feil!r}") from feil


def _tolk(svar: Mapping[str, Any], utvalg: Utvalg, siste: IsoUke | None) -> Dataserie:
    ider = list(svar["id"])
    størrelser = list(svar["size"])
    if len(ider) != len(størrelser) or len(set(ider)) != len(ider):
        raise ValueError("id og size passer ikke sammen")
    for dimensjon, størrelse in zip(ider, størrelser, strict=True):
        if len(_kategorier(svar, dimensjon)) != størrelse:
            raise ValueError(f"size passer ikke med kategoriene i {dimensjon}")
    _sjekk_filtre(svar, utvalg, ider)

    # Plassen i `value` for en kombinasjon: siste dimensjon varierer raskest.
    steg = {}
    gange = 1
    for dimensjon, størrelse in reversed(list(zip(ider, størrelser, strict=True))):
        steg[dimensjon] = gange
        gange *= størrelse

    ukeplass = {
        les_ukekode(kode): i for i, kode in enumerate(_kategorier(svar, UKEDIMENSJON))
    }
    måltall = {kode: i for i, kode in enumerate(_kategorier(svar, MÅLTALL))}
    if POSITIVE not in måltall or TESTER not in måltall:
        raise ValueError("svaret mangler antall positive eller antall tester")

    verdier = svar["value"]
    if isinstance(verdier, Mapping):

        def verdi(plass: int) -> Any:
            return verdier.get(str(plass))
    elif isinstance(verdier, Sequence) and not isinstance(verdier, str):
        if len(verdier) != gange:
            raise ValueError("value har feil lengde")

        def verdi(plass: int) -> Any:
            return verdier[plass]
    else:
        raise TypeError("value mangler")

    if siste is None:
        if not ukeplass:
            raise ValueError("svaret har ingen uker")
        siste = max(ukeplass)
    uker = []
    for uke in sesong.uker(utvalg.sesong, siste):
        tester = positive = None
        if uke in ukeplass:
            plass = ukeplass[uke] * steg[UKEDIMENSJON]
            positive = _tall(verdi(plass + måltall[POSITIVE] * steg[MÅLTALL]))
            tester = _tall(verdi(plass + måltall[TESTER] * steg[MÅLTALL]))
        uker.append(Uke(uke[0], uke[1], tester, positive))
    return Dataserie(utvalg=utvalg, uker=tuple(uker))
