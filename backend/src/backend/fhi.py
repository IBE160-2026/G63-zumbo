"""Henting og tolking av svar fra FHIs åpne API, formatet `json-stat2` (AD-3).

`hent` og `hent_dimensjoner` er den eneste koden som kaller
`statistikk-data.fhi.no`. Alle feil derfra blir `FhiUtilgjengelig`.

Tolkefunksjonene (`tolk`, `siste_publiserte_uke`, `sesonger`, `les_ukekode`) er
rene (AD-1): de bruker ikke nettet, filer eller klokka, og bruker bare
standardbiblioteket, `domene` og `sesong`. Formatet og særhetene står i
`tests/fixtures/fhi/README.md`. Bare denne modulen og `domene` kjenner FHIs koder
(AD-2).
"""

import math
import re
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import httpx

from backend import sesong
from backend.domene import ALDERSGRUPPER, Dataserie, Uke, Utvalg
from backend.sesong import IsoUke

UKEDIMENSJON = "dateusedforstatistics"
MÅLTALL = "MEASURE_TYPE"
POSITIVE = "Detections"
TESTER = "Tests"
ANDEL = "pos_rate"
ALDERSDIMENSJON = "aldersgruppe"

FASTE_FILTRE: Mapping[int, Mapping[str, str]] = {
    724: {"influenzatypeandsubtype": "A+B", "surveillancetype": "NONSTL"},
    729: {"rsvtype": "A+B", "surveillancetype": "NONSTL"},
    731: {"surveillancetype": "NONSTL"},
}
"""Faste valg per tabell: totalen for virustypen og vanlig klinisk praksis.

For 729 (RSV) er `rsvtype` `A+B` totalen, også prøver med ukjent type. FHIs
etikett for den vises aldri (PRD-ens addendum, «Sjekk av RSV-totalen»). 731
(SARS-CoV-2) har ingen typedimensjon, så der er bare overvåkingstypen fast.
"""

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
    Gir `ValueError` når listen ikke har noen sesong, slik at `tjeneste` kan
    bruke reserven `sesong.sesonger_fra_dato`.
    """
    startår = set()
    for kode in _ukekoder_i_dimensjonslisten(dimensjoner):
        år, uke = les_ukekode(kode)
        if uke >= sesong.FØRSTE_UKE:
            startår.add(år)
        elif uke <= sesong.SISTE_UKE:
            startår.add(år - 1)
    resultat = tuple(
        sesong.navn(år) for år in sorted(startår) if år >= sesong.FØRSTE_SESONG
    )
    if not resultat:
        raise ValueError("dimensjonslisten har ingen sesonger")
    return resultat


# --- Datasvaret (`POST …/Table/<tabell>/data`, `json-stat2`) ---


def _kategorier(svar: Mapping[str, Any], dimensjon: str) -> list[str]:
    """Kodene i en dimensjon i rekkefølgen de har i `value`."""
    indeks = svar["dimension"][dimensjon]["category"]["index"]
    if isinstance(indeks, Mapping):
        koder = sorted(indeks, key=indeks.__getitem__)
        if [indeks[k] for k in koder] != list(range(len(koder))):
            raise ValueError(f"plassene i {dimensjon} er ikke 0, 1, 2, …")
    elif isinstance(indeks, Sequence) and not isinstance(indeks, str):
        koder = list(indeks)
    else:
        raise TypeError(f"ugyldig kategoriliste for {dimensjon}")
    if len(set(koder)) != len(koder):
        raise ValueError(f"{dimensjon} har samme kode flere ganger")
    return koder


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
    mangler = set(forventet) - set(ider)
    if mangler:
        raise ValueError(f"svaret mangler {sorted(mangler)}")
    for dimensjon in ider:
        if dimensjon in (UKEDIMENSJON, MÅLTALL):
            continue
        if dimensjon not in forventet:
            # For eksempel en typedimensjon i et svar fra 724 eller 729 som
            # tolkes som SARS-CoV-2.
            raise ValueError(f"svaret har {dimensjon!r}, som utvalget ikke har")
        koder = _kategorier(svar, dimensjon)
        if len(koder) != 1:
            raise ValueError(f"{dimensjon} har {len(koder)} kategorier, ikke 1")
        if koder[0] != forventet[dimensjon]:
            raise ValueError(f"{dimensjon} er {koder[0]!r}, ikke det som ble valgt")


def tolk(
    rått_svar: Mapping[str, Any],
    utvalg: Utvalg,
    siste_publiserte_uke: IsoUke | None = None,
) -> Dataserie:
    """Lager en `Dataserie` med én `Uke` per forventet uke (AD-3, FR-6).

    `rått_svar` er `svar` fra FHI eller cachen. Ukene er `sesong.uker` for
    utvalgets sesong frem til `siste_publiserte_uke` (fra dimensjonslisten).
    Uten den, eller hvis svaret har en høyere uke, brukes den høyeste uka i
    svaret. En uke FHI ikke sendte, og skjulte verdier, blir `None`, aldri 0
    (FR-11, FR-16). Et svar som ikke har riktig form, eller som ikke gjelder
    utvalget (også uker utenfor sesongen), gir `ValueError`.
    """
    try:
        return _tolk(rått_svar, utvalg, siste_publiserte_uke)
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as feil:
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

    if UKEDIMENSJON not in ider or MÅLTALL not in ider:
        raise ValueError("svaret mangler uker eller måltall")
    ukeplass = {
        les_ukekode(kode): i for i, kode in enumerate(_kategorier(svar, UKEDIMENSJON))
    }
    alle_uker = set(sesong.uker(utvalg.sesong))
    if not ukeplass or not set(ukeplass) <= alle_uker:
        raise ValueError(f"svaret har uker utenfor sesongen {utvalg.sesong}")
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

    # Siste publiserte uke er minst den høyeste uka FHI sendte, slik at ingen
    # publiserte tall forsvinner hvis dimensjonslisten er eldre enn svaret.
    siste = max(ukeplass) if siste is None else max(siste, max(ukeplass))
    uker = []
    for uke in sesong.uker(utvalg.sesong, siste):
        tester = positive = None
        if uke in ukeplass:
            plass = ukeplass[uke] * steg[UKEDIMENSJON]
            positive = _tall(verdi(plass + måltall[POSITIVE] * steg[MÅLTALL]))
            tester = _tall(verdi(plass + måltall[TESTER] * steg[MÅLTALL]))
        uker.append(Uke(uke[0], uke[1], tester, positive))
    return Dataserie(utvalg=utvalg, uker=tuple(uker))


# --- Henting fra FHI (skallet, AD-3) ---

BASE_URL = "https://statistikk-data.fhi.no/api/open/v1/msis"
TOTAL_TIDSGRENSE = 10.0
"""Hele kallet gir opp etter 10 sekunder (FR-8), også navneoppslaget (DNS)."""

TIDSGRENSE = httpx.Timeout(TOTAL_TIDSGRENSE)
"""Grensen for hvert steg i `httpx`. Den gjør at tråden bak et kall som har gitt
opp, også stopper av seg selv."""

HODER = {"Accept": "application/json", "User-Agent": "fhi-helsedata/0.1"}

Klient = httpx.Client
"""Klienten `hent` kan få. Andre moduler bruker dette navnet, slik at bare
`fhi.py` importerer `httpx` (AD-3)."""


class FhiUtilgjengelig(Exception):
    """FHI svarte ikke, svarte med feil, eller sendte et ugyldig svar (FR-8).

    Den opprinnelige feilen ligger i `__cause__`, slik at `tjeneste` kan logge
    den. Meldingen er teknisk og skal ikke vises til brukeren.
    """


def ukekode(uke: IsoUke) -> str:
    """`(2025, 40)` → `"2025-w40"`, slik FHI skriver uker."""
    år, ukenummer = sesong.sjekk_uke(uke)
    return f"{år}-w{ukenummer:02d}"


def forespørsel(utvalg: Utvalg, siste_publiserte_uke: IsoUke) -> dict[str, Any]:
    """Kroppen i `POST …/Table/<tabell>/data` for utvalget (FR-2, FR-6).

    Ukene er sesongens uker frem til siste publiserte uke. Gir `ValueError` for
    en tabell som ikke kan hentes ennå, eller en sesong uten publiserte uker.
    """
    if utvalg.tabell not in FASTE_FILTRE:
        raise ValueError(f"tabell {utvalg.tabell} kan ikke hentes ennå")
    uker = sesong.uker(utvalg.sesong, siste_publiserte_uke)
    if not uker:
        raise ValueError(f"sesongen {utvalg.sesong} har ingen publiserte uker")
    filtre = {
        UKEDIMENSJON: [ukekode(u) for u in uker],
        ALDERSDIMENSJON: [ALDERSGRUPPER[utvalg.aldersgruppe].fhi_kode],
        **{kode: [verdi] for kode, verdi in FASTE_FILTRE[utvalg.tabell].items()},
        MÅLTALL: [POSITIVE, TESTER, ANDEL],
    }
    return {
        "dimensions": [
            {"code": kode, "filter": "item", "values": verdier}
            for kode, verdier in filtre.items()
        ],
        "response": {"format": "json-stat2"},
    }


def _kall(
    metode: str, url: str, klient: httpx.Client | None, **kwargs: Any
) -> dict[str, Any]:
    """Ett kall til FHI med 10 sekunders grense for hele kallet (FR-8).

    Kallet kjøres i en egen tråd, fordi `httpx` bare har grenser per steg og
    ingen for navneoppslaget. Når grensen er nådd, gir vi opp med
    `FhiUtilgjengelig`. Tråden stopper av seg selv når grensen per steg slår
    inn. Ingen nye forsøk: `tjeneste` bruker lagrede tall i stedet (FR-8).
    """
    utfører = ThreadPoolExecutor(max_workers=1, thread_name_prefix="fhi")
    try:
        fremtid = utfører.submit(_kall_i_tråd, metode, url, klient, kwargs)
        try:
            return fremtid.result(timeout=TOTAL_TIDSGRENSE)
        except TimeoutError as feil:
            raise FhiUtilgjengelig(
                f"{metode} {url}: ga opp etter {TOTAL_TIDSGRENSE} s"
            ) from feil
    finally:
        utfører.shutdown(wait=False, cancel_futures=True)


def _kall_i_tråd(
    metode: str, url: str, klient: httpx.Client | None, kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Selve kallet. Alle feil, også ugyldig JSON, blir `FhiUtilgjengelig`."""
    try:
        if klient is None:
            with httpx.Client(timeout=TIDSGRENSE) as ny_klient:
                svar = ny_klient.request(metode, url, headers=HODER, **kwargs)
        else:
            svar = klient.request(
                metode, url, headers=HODER, timeout=TIDSGRENSE, **kwargs
            )
        svar.raise_for_status()
        innhold = svar.json()
    except (httpx.HTTPError, httpx.InvalidURL, ValueError, RuntimeError) as feil:
        # RuntimeError dekker RecursionError (dypt nøstet JSON),
        # httpx.StreamError og en klient som er lukket.
        raise FhiUtilgjengelig(f"{metode} {url}: {feil!r}") from feil
    if not isinstance(innhold, dict):
        raise FhiUtilgjengelig(f"{metode} {url}: svaret er ikke et JSON-objekt")
    return innhold


def hent_dimensjoner(
    tabell: int, *, klient: httpx.Client | None = None
) -> dict[str, Any]:
    """Henter dimensjonslisten for tabellen, rått (AD-3, AD-4).

    Svaret sjekkes med `siste_publiserte_uke` og `sesonger` før det returneres.
    """
    url = f"{BASE_URL}/Table/{tabell}/dimension"
    svar = _kall("GET", url, klient)
    try:
        siste_publiserte_uke(svar)
        sesonger(svar)
    except (ValueError, RecursionError) as feil:
        raise FhiUtilgjengelig(f"GET {url}: ugyldig dimensjonsliste") from feil
    return svar


def hent(
    utvalg: Utvalg,
    siste_publiserte_uke: IsoUke,
    *,
    klient: httpx.Client | None = None,
) -> dict[str, Any]:
    """Henter tallene for utvalget fra FHI, rått (FR-6, FR-8, AD-3).

    Svaret sjekkes med `tolk` før det returneres, slik at bare svar som kan
    tolkes havner i cachen. Gir `FhiUtilgjengelig` ved tidsavbrudd etter
    10 sekunder, nettverksfeil, HTTP-feil (også 3xx) og ugyldig svar.
    Gir `ValueError` for et utvalg som ikke kan hentes (se `forespørsel`).
    """
    kropp = forespørsel(utvalg, siste_publiserte_uke)
    url = f"{BASE_URL}/Table/{utvalg.tabell}/data"
    svar = _kall("POST", url, klient, json=kropp)
    try:
        tolk(svar, utvalg, siste_publiserte_uke)
    except (ValueError, RecursionError) as feil:
        raise FhiUtilgjengelig(f"POST {url}: ugyldig svar") from feil
    return svar
