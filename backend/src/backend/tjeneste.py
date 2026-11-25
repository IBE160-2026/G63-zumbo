"""Setter sammen svaret for et utvalg (FR-3, FR-7, FR-8, AD-3, AD-5, AD-9).

`Tjeneste.svar` gir tallene, regelutslagene og kildehenvisningen for et utvalg.
Den bruker lagrede tall når de er ferske, og henter ellers nye fra FHI og lagrer
dem. Når FHI er nede, brukes lagrede tall merket «sist lagrede», ellers sier
svaret at det ikke finnes tall. `Tjeneste.sesonger` gir sesonglisten.
`Tjeneste.forklaring` gir KI-forklaringen for et svar, og bruker en lagret
forklaring når tallene er de samme (AD-7).

Modulen er en del av skallet: den bruker `fhi.hent`, `mellomlager` og tråder,
og får «nå» som argument. `FhiUtilgjengelig` fanges her og logges på nivå
INFO. Brukeren får bare faste norske meldinger uten FHI-koder (NFR-3).
"""

import logging
import threading
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from backend import fhi, ki, kontrollregler, mellomlager, sesong
from backend.config import Innstillinger
from backend.domene import (
    Dataserie,
    Kildehenvisning,
    Regelutslag,
    Utvalg,
    kildehenvisning,
)

logger = logging.getLogger(__name__)

SESONGTABELL = 724
"""Tabellen sesonglisten lages fra. Alle tre virus har samme uker (sjekket
25.11.2026), så én sesongliste holder.

Siste publiserte uke for et utvalg kommer fra datasvaret for utvalgets egen
tabell: datakallet ber om hele sesongen, og FHI sender bare de publiserte ukene
(`fhi.forespørsel`). Slik trengs ikke dimensjonslisten for 729 og 731, og en
side gjør ett kall færre når ingenting er lagret. Dimensjonslisten for
utvalgets tabell hentes bare når FHI avviser datakallet, for å se om sesongen
ikke er publisert ennå."""

PAUSE_ETTER_FEIL = timedelta(seconds=60)
"""Så lenge dimensjonslisten ikke hentes på nytt etter at FHI ikke svarte.

Siden henter både sesonglisten og tallene. Uten pausen kunne én sidevisning
vente på to tidsavbrudd (20 s) når FHI er nede (FR-8, NFR-2).
"""

Forklaring = ki.Forklaring
ManglerNøkkel = ki.ManglerNøkkel
KiFeil = ki.KiFeil
"""Utfallene av `Tjeneste.forklaring`, så `web` slipper å importere `ki`
(arkitektur §2)."""

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
    sann når FHI ikke svarte og tallene er de sist lagrede (FR-8). Da har både
    `serie` og `melding` en verdi, så bruk `serie is None`, ikke `melding`, for å
    se om det finnes tall. `melding` er en ferdig norsk setning som kan vises som
    den er.
    """

    utvalg: Utvalg
    serie: Dataserie | None = None
    regelutslag: tuple[Regelutslag, ...] = ()
    kilde: Kildehenvisning | None = None
    sist_lagrede: bool = False
    melding: str | None = None


class Tjeneste:
    """Henter, lagrer og vurderer tall for utvalg.

    Lages én gang av `web` med innstillingene. `klient` og `ny_ki_klient` brukes
    av testene. Kall som skjer samtidig for samme utvalg, deler ett kall til FHI
    (AD-9), og kall for samme forklaring deler ett kall til Claude.
    """

    def __init__(
        self,
        innstillinger: Innstillinger,
        klient: fhi.Klient | None = None,
        ny_ki_klient: Callable[..., Any] | None = None,
    ) -> None:
        self._innstillinger = innstillinger
        self._ny_ki_klient = ny_ki_klient
        self._mappe = innstillinger.cache_dir
        self._klient = klient
        self._lås = threading.Lock()
        self._pågår: dict[str, Future[Any]] = {}
        self._feilet: datetime | None = None

    # --- Én jobb per nøkkel ---

    def _én_gang[T](self, nøkkel: str, jobb: Callable[[], T]) -> T:
        """Kjører `jobb`, eller venter på den som allerede kjører for `nøkkel`.

        De som venter, får samme resultat eller samme feil som den som kjørte
        jobben. Slik gir samtidige kall bare ett kall til FHI, også når FHI
        er nede, og bare ett kall til Claude for samme forklaring. Ventetiden er
        begrenset av tidsgrensen i `fhi` (10 s), og for KI-forklaringen av
        tidsgrensen i `ki` (15 s per forsøk, drøyt 30 s i alt). De som venter,
        får resultatet regnet ut med eierens «nå», som er noen millisekunder
        unna.
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

    def _lagret_dimensjonsliste(
        self, tabell: int = SESONGTABELL
    ) -> mellomlager.Lagret | None:
        """Den lagrede dimensjonslisten for tabellen, eller `None` når den mangler
        eller ikke kan brukes."""
        lagret = mellomlager.les_dimensjoner(self._mappe, tabell)
        if lagret is None:
            return None
        try:
            fhi.siste_publiserte_uke(lagret.svar)
            fhi.sesonger(lagret.svar)
        except (ValueError, RecursionError) as feil:
            logger.info("Lagret dimensjonsliste kan ikke brukes: %r", feil)
            return None
        return lagret

    def _dimensjonsliste(
        self, nå: datetime, tving: bool = False, tabell: int = SESONGTABELL
    ) -> dict[str, Any]:
        """Fersk lagret dimensjonsliste for tabellen, ellers en ny fra FHI som
        lagres som `fhi/<tabell>-dimensjoner.json`.

        Gir `FhiUtilgjengelig` når den må hentes og FHI ikke svarer, og uten
        nytt kall i `PAUSE_ETTER_FEIL` etter at FHI ikke svarte. Cachen
        leses inne i den delte jobben, slik at et kall som kommer rett etter at
        et annet har hentet listen, bruker den lagrede listen.

        Med `tving` hentes listen fra FHI selv om den lagrede er fersk, og også
        rett etter en feil, fordi brukeren har bedt om nye tall (FR-25). Slik
        kommer en ny uke med, selv om listen ble lagret før FHI publiserte.
        """

        def hent() -> dict[str, Any]:
            if not tving:
                lagret = self._lagret_dimensjonsliste(tabell)
                if lagret is not None and not sesong.er_utdatert(lagret.hentet, nå):
                    return lagret.svar
                self._stopp_hvis_nylig_feil(nå)
            try:
                svar = fhi.hent_dimensjoner(tabell, klient=self._klient)
            except fhi.FhiUtilgjengelig:
                self._feilet = nå
                raise
            self._feilet = None
            self._lagre(mellomlager.lagre_dimensjoner, tabell, svar, nå)
            return svar

        jobb = f"dimensjoner-{tabell}" + ("-tving" if tving else "")
        return self._én_gang(jobb, hent)

    def _stopp_hvis_nylig_feil(self, nå: datetime) -> None:
        """Gir `FhiUtilgjengelig` uten kall når FHI ikke svarte for under
        `PAUSE_ETTER_FEIL` siden, på dimensjonslisten eller på tallene."""
        if self._feilet is not None and nå - self._feilet < PAUSE_ETTER_FEIL:
            raise fhi.FhiUtilgjengelig("FHI svarte ikke nylig, prøver ikke på nytt")

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
            logger.info("Sesonglisten kunne ikke hentes fra FHI: %r", feil)
        lagret = self._lagret_dimensjonsliste()
        if lagret is not None:
            return fhi.sesonger(lagret.svar)
        return sesong.sesonger_fra_dato(nå)

    # --- Svaret for et utvalg ---

    def svar(self, utvalg: Utvalg, nå: datetime, tving: bool = False) -> Resultat:
        """Tall, regelutslag og kildehenvisning for utvalget (FR-7, FR-8).

        Ferske lagrede tall brukes uten kall til FHI. Ellers hentes nye tall, som
        lagres. Når FHI er nede, brukes lagrede tall merket «sist lagrede», eller
        så gir svaret en melding om at det ikke finnes tall. Kontrollreglene
        gjelder alltid, også for lagrede tall.

        Med `tving` hentes tallene og dimensjonslisten fra FHI selv om de lagrede
        er ferske, og lagres med `nå` som nytt hentetidspunkt (FR-25). Når FHI
        ikke svarer, gjelder FR-8 som ellers. Samtidige tvungne hentinger for
        samme utvalg deler ett kall til FHI (AD-9).
        """
        jobb = utvalg.nøkkel + ("-tving" if tving else "")
        return self._én_gang(jobb, lambda: self._svar(utvalg, nå, tving))

    def _svar(self, utvalg: Utvalg, nå: datetime, tving: bool = False) -> Resultat:
        lagret = self._lagret_svar(utvalg)
        if not tving and lagret is not None and not sesong.er_utdatert(lagret[0], nå):
            return self._resultat(utvalg, lagret[1], lagret[0])
        try:
            if tving:
                # «Hent nyeste tall nå» henter også sesonglisten, så en ny sesong
                # kommer med (FR-25). Feiler den, prøver vi ikke datakallet i
                # tillegg. Da venter brukeren høyst én tidsgrense (10 s) (FR-8).
                self._dimensjonsliste(nå, tving=True)
            else:
                # Svarte ikke FHI nettopp, venter vi ikke på nytt (FR-8). Det
                # gjelder også siden etter «Hent nyeste tall nå».
                self._stopp_hvis_nylig_feil(nå)
            try:
                # Hele sesongen. Svaret slutter ved siste publiserte uke (AD-3).
                rått = fhi.hent(utvalg, klient=self._klient)
            except fhi.ForespørselAvvist:
                if self._ikke_publisert(utvalg, nå, tving):
                    return Resultat(
                        utvalg, melding=IKKE_PUBLISERT.format(sesong=utvalg.sesong)
                    )
                self._feilet = nå
                raise
            except fhi.FhiUtilgjengelig:
                self._feilet = nå
                raise
        except fhi.FhiUtilgjengelig as feil:
            logger.info("Tallene kunne ikke hentes fra FHI: %r", feil)
            if lagret is None:
                return Resultat(utvalg, melding=FHI_NEDE_INGEN_TALL)
            return self._resultat(
                utvalg, lagret[1], lagret[0], sist_lagrede=True, melding=FHI_NEDE_LAGRET
            )
        self._lagre(mellomlager.lagre_svar, utvalg, rått, nå)
        return self._resultat(utvalg, fhi.tolk(rått, utvalg), nå)

    def _ikke_publisert(self, utvalg: Utvalg, nå: datetime, tving: bool) -> bool:
        """Sann når tabellen ikke har publisert noen uke i utvalgets sesong.

        Spørres bare når FHI avviste datakallet. Dimensjonslisten for utvalgets
        egen tabell avgjør, slik at meldingen «ikke publisert ennå» bare vises
        når den stemmer (AD-3). Gir `FhiUtilgjengelig` når listen ikke kan hentes.
        """
        dimensjoner = self._dimensjonsliste(nå, tving, utvalg.tabell)
        return not sesong.uker(utvalg.sesong, fhi.siste_publiserte_uke(dimensjoner))

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

    # --- KI-forklaringen (AD-7) ---

    def forklaring(self, resultat: Resultat, nå: datetime) -> ki.Utfall:
        """KI-forklaringen for tallene i `resultat` (FR-20, FR-22, AD-7).

        Uten nøkkel er utfallet `ManglerNøkkel`, og verken lagrede forklaringer
        eller Claude brukes (FR-22). Finnes det en lagret forklaring for de samme
        tallene, promptene og modellen, brukes den uten å kalle Claude. Ellers
        kalles Claude, og bare en `Forklaring` lagres, med `nå` som tidspunktet
        den ble laget. Uten tall er utfallet `KiFeil`. Metoden kaster ikke.
        """
        if not self._innstillinger.anthropic_api_key:
            return ki.ManglerNøkkel()
        serie, kilde = resultat.serie, resultat.kilde
        if serie is None or kilde is None:
            logger.info("Ingen tall å forklare for %s", resultat.utvalg.nøkkel)
            return ki.KiFeil()
        regelutslag = resultat.regelutslag
        modell = self._innstillinger.anthropic_model
        try:
            nøkkel = ki.nøkkel(serie, regelutslag, modell)
        except (OSError, ValueError) as feil:
            logger.info("Prompten kunne ikke leses: %r", feil)
            return ki.KiFeil()

        def lag() -> ki.Utfall:
            lagret = mellomlager.les_forklaring(self._mappe, nøkkel)
            if lagret is not None:
                logger.info("Bruker lagret KI-forklaring %s", nøkkel)
                return ki.Forklaring(lagret.tekst)
            utfall = ki.forklar(
                serie, regelutslag, kilde, self._innstillinger, self._ny_ki_klient
            )
            if isinstance(utfall, ki.Forklaring):
                try:
                    mellomlager.lagre_forklaring(
                        self._mappe, nøkkel, nå, modell, utfall.tekst
                    )
                except (OSError, ValueError) as feil:
                    # Forklaringen vises likevel (AD-4).
                    logger.info("Kunne ikke lagre KI-forklaringen: %r", feil)
            return utfall

        return self._én_gang(f"ki-{nøkkel}", lag)

    def _lagre(self, lagre: Callable[..., None], *argumenter: Any) -> None:
        """Lagrer i cachen. En feil logges, og tallene vises likevel (AD-4)."""
        try:
            lagre(self._mappe, *argumenter)
        except OSError as feil:
            logger.info("Kunne ikke lagre i cachen: %r", feil)
