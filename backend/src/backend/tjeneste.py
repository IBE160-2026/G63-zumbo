"""Setter sammen svaret for et utvalg (FR-3, FR-7, FR-8, AD-3, AD-5, AD-9).

`Tjeneste.svar` gir tallene, regelutslagene og kildehenvisningen for et utvalg.
Den bruker lagrede tall når de er ferske, og henter ellers nye fra FHI og lagrer
dem. Når FHI er nede, brukes lagrede tall merket «sist lagrede», ellers sier
svaret at det ikke finnes tall. `Tjeneste.sesonger` gir sesonglisten.

Modulen er en del av skallet: den bruker `fhi.hent`, `mellomlager` og tråder,
og får «nå» som argument. `FhiUtilgjengelig` fanges her og logges på nivå
INFO. Brukeren får bare faste norske meldinger uten FHI-koder (NFR-3).
"""

import logging
import threading
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend import fhi, kontrollregler, mellomlager, sesong
from backend.config import Innstillinger
from backend.domene import (
    VIRUS,
    Dataserie,
    Kildehenvisning,
    Regelutslag,
    Utvalg,
    kildehenvisning,
)

logger = logging.getLogger(__name__)

SESONGTABELL = 724
"""Tabellen sesonglisten lages fra. Alle tre virus har samme sesonger (AD-3)."""

IKKE_KLART = "Tall for {virus} kan ikke vises i appen ennå. Velg influensa."
FHI_NEDE_LAGRET = (
    "Tallene kunne ikke hentes fra FHI akkurat nå. Du ser de sist lagrede tallene."
)
FHI_NEDE_INGEN_TALL = (
    "Tallene kunne ikke hentes fra FHI akkurat nå, og det finnes ingen lagrede "
    "tall for dette utvalget. Prøv igjen senere."
)
IKKE_PUBLISERT = (
    "FHI har ikke publisert tall for sesongen {sesong} ennå. Prøv igjen senere."
)


@dataclass(frozen=True)
class Resultat:
    """Svaret for ett utvalg.

    `serie` er `None` når det ikke finnes tall å vise. Da sier `melding` hvorfor.
    `kilde.hentet` er tidspunktet tallene ble hentet fra FHI. `sist_lagrede` er
    sann når FHI ikke svarte og tallene er de sist lagrede (FR-8). `melding` er
    en ferdig norsk setning som kan vises som den er.
    """

    utvalg: Utvalg
    serie: Dataserie | None = None
    regelutslag: tuple[Regelutslag, ...] = ()
    kilde: Kildehenvisning | None = None
    sist_lagrede: bool = False
    melding: str | None = None


class Tjeneste:
    """Henter, lagrer og vurderer tall for utvalg.

    Lages én gang av `web` med innstillingene. `klient` brukes av testene. Kall
    som skjer samtidig for samme utvalg, deler ett kall til FHI (AD-9).
    """

    def __init__(
        self, innstillinger: Innstillinger, klient: fhi.Klient | None = None
    ) -> None:
        self._mappe = innstillinger.cache_dir
        self._klient = klient
        self._lås = threading.Lock()
        self._pågår: dict[str, Future[Any]] = {}

    # --- Én jobb per nøkkel ---

    def _én_gang[T](self, nøkkel: str, jobb: Callable[[], T]) -> T:
        """Kjører `jobb`, eller venter på den som allerede kjører for `nøkkel`.

        De som venter, får samme resultat eller samme feil som den som kjørte
        jobben. Slik gir samtidige kall bare ett kall til FHI, også når FHI
        er nede.
        """
        with self._lås:
            fremtid = self._pågår.get(nøkkel)
            eier = fremtid is None
            if eier:
                fremtid = Future()
                self._pågår[nøkkel] = fremtid
        if not eier:
            return fremtid.result()
        try:
            resultat = jobb()
        except BaseException as feil:
            fremtid.set_exception(feil)
            raise
        else:
            fremtid.set_result(resultat)
            return resultat
        finally:
            with self._lås:
                del self._pågår[nøkkel]

    # --- Dimensjonslisten og sesonger ---

    def _lagret_dimensjonsliste(self) -> mellomlager.Lagret | None:
        """Den lagrede dimensjonslisten, eller `None` når den mangler eller ikke
        kan brukes."""
        lagret = mellomlager.les_dimensjoner(self._mappe, SESONGTABELL)
        if lagret is None:
            return None
        try:
            fhi.siste_publiserte_uke(lagret.svar)
            fhi.sesonger(lagret.svar)
        except (ValueError, RecursionError):
            return None
        return lagret

    def _dimensjonsliste(self, nå: datetime) -> dict[str, Any]:
        """Fersk lagret dimensjonsliste, ellers en ny fra FHI som lagres.

        Gir `FhiUtilgjengelig` når den må hentes og FHI ikke svarer.
        """
        lagret = self._lagret_dimensjonsliste()
        if lagret is not None and not sesong.er_utdatert(lagret.hentet, nå):
            return lagret.svar

        def hent() -> dict[str, Any]:
            svar = fhi.hent_dimensjoner(SESONGTABELL, klient=self._klient)
            self._lagre(mellomlager.lagre_dimensjoner, SESONGTABELL, svar, nå)
            return svar

        return self._én_gang(f"dimensjoner-{SESONGTABELL}", hent)

    def sesonger(self, nå: datetime) -> tuple[str, ...]:
        """Sesongene brukeren kan velge, eldste først (FR-3, AD-3).

        Listen kommer fra FHIs dimensjonsliste (lagret eller hentet). Når FHI er
        nede, brukes en lagret liste selv om den er gammel. Bare når ingen liste
        finnes, brukes reserven `sesong.sesonger_fra_dato(nå)`. Listene blandes
        aldri, slik at en sesong uten publiserte uker ikke vises i uke 40.
        """
        try:
            return fhi.sesonger(self._dimensjonsliste(nå))
        except fhi.FhiUtilgjengelig as feil:
            logger.info("Sesonglisten kunne ikke hentes fra FHI: %r", feil.__cause__)
        lagret = self._lagret_dimensjonsliste()
        if lagret is not None:
            return fhi.sesonger(lagret.svar)
        return sesong.sesonger_fra_dato(nå)

    # --- Svaret for et utvalg ---

    def svar(self, utvalg: Utvalg, nå: datetime) -> Resultat:
        """Tall, regelutslag og kildehenvisning for utvalget (FR-7, FR-8).

        Ferske lagrede tall brukes uten kall til FHI. Ellers hentes nye tall, som
        lagres. Når FHI er nede, brukes lagrede tall merket «sist lagrede», eller
        så gir svaret en melding om at det ikke finnes tall. Kontrollreglene
        gjelder alltid, også for lagrede tall.
        """
        if utvalg.tabell not in fhi.FASTE_FILTRE:
            # RSV og SARS-CoV-2 kommer i epic 6.
            return Resultat(
                utvalg, melding=IKKE_KLART.format(virus=VIRUS[utvalg.virus].navn)
            )
        return self._én_gang(utvalg.nøkkel, lambda: self._svar(utvalg, nå))

    def _svar(self, utvalg: Utvalg, nå: datetime) -> Resultat:
        lagret = self._lagret_svar(utvalg)
        if lagret is not None and not sesong.er_utdatert(lagret[0], nå):
            return self._resultat(utvalg, lagret[1], lagret[0])
        try:
            siste = fhi.siste_publiserte_uke(self._dimensjonsliste(nå))
            if not sesong.uker(utvalg.sesong, siste):
                return Resultat(
                    utvalg, melding=IKKE_PUBLISERT.format(sesong=utvalg.sesong)
                )
            rått = fhi.hent(utvalg, siste, klient=self._klient)
        except fhi.FhiUtilgjengelig as feil:
            logger.info("Tallene kunne ikke hentes fra FHI: %r", feil.__cause__)
            if lagret is None:
                return Resultat(utvalg, melding=FHI_NEDE_INGEN_TALL)
            return self._resultat(
                utvalg, lagret[1], lagret[0], sist_lagrede=True, melding=FHI_NEDE_LAGRET
            )
        self._lagre(mellomlager.lagre_svar, utvalg, rått, nå)
        return self._resultat(utvalg, fhi.tolk(rått, utvalg, siste), nå)

    def _lagret_svar(self, utvalg: Utvalg) -> tuple[datetime, Dataserie] | None:
        """Det lagrede svaret tolket, eller `None` når det mangler eller ikke kan
        tolkes. Svaret har ukene som ble bedt om, så siste uke trengs ikke."""
        lagret = mellomlager.les_svar(self._mappe, utvalg)
        if lagret is None:
            return None
        try:
            return lagret.hentet, fhi.tolk(lagret.svar, utvalg)
        except (ValueError, RecursionError) as feil:
            logger.info("Lagret svar for %s kan ikke tolkes: %r", utvalg.nøkkel, feil)
            return None

    @staticmethod
    def _resultat(
        utvalg: Utvalg,
        serie: Dataserie,
        hentet: datetime,
        *,
        sist_lagrede: bool = False,
        melding: str | None = None,
    ) -> Resultat:
        return Resultat(
            utvalg=utvalg,
            serie=serie,
            regelutslag=tuple(kontrollregler.vurder(serie)),
            kilde=kildehenvisning(utvalg.tabell, hentet),
            sist_lagrede=sist_lagrede,
            melding=melding,
        )

    def _lagre(self, lagre: Callable[..., None], *argumenter: Any) -> None:
        """Lagrer i cachen. En feil logges, og tallene vises likevel (AD-4)."""
        try:
            lagre(self._mappe, *argumenter)
        except OSError as feil:
            logger.info("Kunne ikke lagre i cachen: %r", feil)
