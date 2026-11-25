"""Nettsiden: FastAPI-appen og rutene (AD-8, AD-9, AD-11).

Start lokalt fra `backend/` med `uv run uvicorn backend.web:app --reload`.

`web` gjør bare HTTP og HTML. Brukerens valg sjekkes i
`domene.Utvalg.fra_parametre`, og tallene kommer fra `tjeneste`. Innstillingene
leses én gang, ved oppstart, og aldri ved import, slik at testene ikke laster
`.env` (AD-6, AD-10).

KI-forklaringen hentes for seg med `GET /forklaring`, etter at siden er vist,
så `GET /` venter aldri på KI-en (FR-20, NFR-2, AD-9). Knappen «Hent nyeste
tall nå» sender `POST /hent-nyeste`, som henter uten mellomlager og svarer med
`303` til `GET /` for samme utvalg (FR-25, AD-9).
"""

import re
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import urlencode

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend import config
from backend.begreper import BEGREPER, TYNT_DATAGRUNNLAG
from backend.config import Innstillinger
from backend.domene import (
    ALDERSGRUPPER,
    MALER,
    STANDARD_ALDERSGRUPPE,
    VIRUS,
    Dataserie,
    UgyldigUtvalg,
    Utvalg,
)
from backend.formatering import (
    andel,
    andelstekst,
    avrundet,
    kildetekst,
    tall,
    tidspunkt,
    uke,
    utvalgstekst,
)
from backend.tjeneste import (
    FHI_NEDE_LAGRET,
    KLARE_VIRUS,
    Forklaring,
    ManglerNøkkel,
    Resultat,
    Tjeneste,
)

if TYPE_CHECKING:
    # Bare for typen til testklienten. `web` kaller aldri `fhi` (AD-1).
    from backend import fhi

MAPPE = Path(__file__).parent
PARAMETRE = ("mal", "virus", "sesong", "alder")
"""Query-parametrene for et utvalg (AD-9)."""

NYESTE = "nyeste_feilet"
"""Query-parameteret `POST /hent-nyeste` legger til når FHI ikke svarte. Verdien
er tidspunktet for forsøket i sekunder (Unix-tid), så `GET /` kan si at de viste
tallene er de sist lagrede (FR-8, FR-25)."""

NYESTE_GJELDER = timedelta(minutes=5)
"""Så lenge merket gjelder. Lastes adressen inn på nytt senere, eller er tallene
hentet etter forsøket, vises ingen melding om at FHI ikke svarte."""


def _mislykket_forsøk(verdi: str | None, nå: datetime) -> datetime | None:
    """Tidspunktet for et mislykket «Hent nyeste tall nå» når det er nylig,
    ellers `None` (også for en verdi som ikke er et tall)."""
    try:
        forsøk = datetime.fromtimestamp(int(verdi or ""), UTC)
    except (ValueError, OverflowError, OSError):
        return None
    if timedelta(0) <= nå - forsøk <= NYESTE_GJELDER:
        return forsøk
    return None


# --- Jinja2-filtre: formateringen står i `formatering` (arkitektur §4) ---


def grafdata(serie: Dataserie) -> dict[str, Any]:
    """Tallene grafen tegner, fra samme `Dataserie` som tabellen (AD-8).

    Uker uten andel (manglende uker og uker med 0 tester) har `null`, så linjen
    får brudd (FR-9). `andel_tekst`, `tester_tekst` og `positive_tekst` er
    tallene slik tabellen viser dem, til verktøytipset. `usikker` sier hvilke punkter som får åpen sirkel (FR-10).
    """
    return {
        "uker": [uke(u) for u in serie.uker],
        "andel": [
            None if u.andel is None else float(avrundet(u.andel)) for u in serie.uker
        ],
        "andel_tekst": [andelstekst(u) for u in serie.uker],
        "tester_tekst": [tall(u.tester) for u in serie.uker],
        "positive_tekst": [tall(u.positive) for u in serie.uker],
        "usikker": [u.usikker for u in serie.uker],
    }


def avsnitt(tekst: str) -> list[str]:
    """Teksten delt i avsnitt på tomme linjer, uten tomme avsnitt."""
    return [a.strip() for a in re.split(r"\n\s*\n", tekst) if a.strip()]


def utvalgsparametre(utvalg: Utvalg) -> dict[str, str]:
    """Query-parametrene for `utvalg`, de samme som skjemaet sender (AD-9)."""
    return {
        "mal": str(utvalg.mal),
        "virus": utvalg.virus,
        "sesong": utvalg.sesong,
        "alder": utvalg.aldersgruppe,
    }


def forklaringsadresse(utvalg: Utvalg) -> str:
    """`/forklaring` med de samme parametrene som siden for `utvalg` (AD-9)."""
    return "/forklaring?" + urlencode(utvalgsparametre(utvalg))


def har_andel(serie: Dataserie) -> bool:
    """Sann når minst én uke har en andel, så grafen har noe å tegne."""
    return any(u.andel is not None for u in serie.uker)


def alternativtekst(serie: Dataserie) -> str:
    """Alternativtekst for grafen med utvalg og hovedtrekk (NFR-6).

    Teksten beskriver det grafen viser: åpne sirkler bare for usikre uker med
    andel, og brudd i linjen for uker uten andel.
    """
    tekst = (
        f"Linjegraf over andel positive tester uke for uke. "
        f"{utvalgstekst(serie.utvalg)}."
    )
    med_andel = [u for u in serie.uker if u.andel is not None]
    if not med_andel:
        return tekst + " Ingen uker har en andel som kan vises."
    tekst += f" Grafen viser {uke(serie.uker[0])} til {uke(serie.uker[-1])}."
    høyest = max(med_andel, key=lambda u: u.andel)
    siste = med_andel[-1]
    tekst += f" Andelen var høyest i {uke(høyest)} med {andel(høyest.andel)}."
    if siste is not høyest:
        tekst += (
            f" I {uke(siste)}, den siste uka med tall, var den {andel(siste.andel)}."
        )
    åpne = sum(u.usikker for u in med_andel)
    if åpne:
        om = "uke er usikker" if åpne == 1 else "uker er usikre"
        tekst += f" {åpne} {om} og markert med åpen sirkel."
    uten = len(serie.uker) - len(med_andel)
    if uten:
        om = "uke har" if uten == 1 else "uker har"
        tekst += f" {uten} {om} ingen andel og gir brudd i linjen."
    return tekst


maler = Jinja2Templates(directory=MAPPE / "templates")
maler.env.filters.update(
    tall=tall,
    andel=andel,
    andelstekst=andelstekst,
    uke=uke,
    tidspunkt=tidspunkt,
    kildetekst=kildetekst,
    utvalgstekst=utvalgstekst,
    grafdata=grafdata,
    har_andel=har_andel,
    alternativtekst=alternativtekst,
    avsnitt=avsnitt,
    forklaringsadresse=forklaringsadresse,
)


def _spørsmål(mal_spørsmål: str) -> str:
    """Malens spørsmål med plass til valgene: «… for [virus] i sesongen [sesong]»."""
    return mal_spørsmål.format(virus="[virus]", sesong="[sesong]")


def _valgt(verdi: str, valg: list[str], standard: str | None = None) -> str:
    """Verdien som skal være valgt i en liste: brukerens valg når det finnes i
    listen, ellers `standard`, ellers det første valget.

    Slik viser skjemaet aldri et annet valg enn det som står der, også etter et
    ugyldig valg eller et virus som ikke er klart ennå.
    """
    if verdi in valg:
        return verdi
    return standard if standard is not None else (valg[0] if valg else "")


def lag_app(
    les_innstillinger: Callable[[], Innstillinger] = config.les_innstillinger,
    klient: "fhi.Klient | None" = None,
    klokke: Callable[[], datetime] = lambda: datetime.now(UTC),
    ny_ki_klient: Callable[..., Any] | None = None,
) -> FastAPI:
    """Lager appen. Testene sender inn egne innstillinger, en `klient`, en
    fast `klokke` og en falsk Claude (`ny_ki_klient`), så de aldri kaller
    Claude på ekte (AD-10).

    `les_innstillinger` kalles én gang, når appen starter (AD-6).
    """

    @asynccontextmanager
    async def levetid(app: FastAPI) -> AsyncIterator[None]:
        app.state.tjeneste = Tjeneste(
            les_innstillinger(), klient=klient, ny_ki_klient=ny_ki_klient
        )
        yield

    app = FastAPI(lifespan=levetid, docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=MAPPE / "static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    def forside(request: Request) -> HTMLResponse:
        tjeneste: Tjeneste = request.app.state.tjeneste
        nå = klokke()
        sesonger = tjeneste.sesonger(nå)
        parametre = {navn: request.query_params.get(navn, "") for navn in PARAMETRE}
        feilmelding: str | None = None
        resultat: Resultat | None = None
        if any(verdi.strip() for verdi in parametre.values()):
            # Verdiene sjekkes bare i `fra_parametre` (AD-9).
            try:
                utvalg = Utvalg.fra_parametre(parametre, sesonger)
            except UgyldigUtvalg as feil:
                feilmelding = str(feil)
            else:
                resultat = tjeneste.svar(utvalg, nå)
                forsøk = _mislykket_forsøk(request.query_params.get(NYESTE), nå)
                if (
                    forsøk is not None
                    and resultat.serie is not None
                    and resultat.kilde is not None
                    and resultat.kilde.hentet < forsøk
                    and not resultat.sist_lagrede
                ):
                    # «Hent nyeste tall nå» fikk nettopp ikke svar fra FHI, og
                    # tallene som vises, er eldre enn forsøket (FR-8, FR-25).
                    resultat = replace(
                        resultat, sist_lagrede=True, melding=FHI_NEDE_LAGRET
                    )

        mal_valg = [(str(m.nummer), _spørsmål(m.spørsmål)) for m in MALER.values()]
        virus_valg = [(n, VIRUS[n].navn) for n in KLARE_VIRUS]
        alder_valg = [(g.nøkkel, g.etikett) for g in ALDERSGRUPPER.values()]
        valgt = {
            "mal": _valgt(parametre["mal"], [v for v, _ in mal_valg]),
            "virus": _valgt(parametre["virus"], list(KLARE_VIRUS)),
            "sesong": _valgt(parametre["sesong"], list(reversed(sesonger))),
            "alder": _valgt(
                parametre["alder"], list(ALDERSGRUPPER), STANDARD_ALDERSGRUPPE
            ),
        }
        return maler.TemplateResponse(
            request,
            "index.html",
            {
                "maler": mal_valg,
                "virus": virus_valg,
                "sesonger": sesonger,
                "aldersgrupper": alder_valg,
                "valgt": valgt,
                "feilmelding": feilmelding,
                "resultat": resultat,
                "klare_virus": KLARE_VIRUS,
                "begreper": BEGREPER,
                "tynt_datagrunnlag": next(
                    b.html_id for b in BEGREPER if b.nøkkel == TYNT_DATAGRUNNLAG
                ),
            },
        )

    @app.post("/hent-nyeste")
    def hent_nyeste(
        request: Request,
        mal: Annotated[str, Form()] = "",
        virus: Annotated[str, Form()] = "",
        sesong: Annotated[str, Form()] = "",
        alder: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        """Henter tallene for utvalget fra FHI uten mellomlager (FR-25, AD-9).

        Svarer alltid med `303` til `GET /` for samme utvalg, så en oppdatering
        av siden ikke sender skjemaet på nytt. Når FHI ikke svarte, får adressen
        `nyeste_feilet` med tidspunktet for forsøket. Et ugyldig utvalg sendes videre uten henting, og
        `GET /` viser da feilmeldingen (FR-5).
        """
        tjeneste: Tjeneste = request.app.state.tjeneste
        nå = klokke()
        parametre = {"mal": mal, "virus": virus, "sesong": sesong, "alder": alder}
        try:
            utvalg = Utvalg.fra_parametre(parametre, tjeneste.sesonger(nå))
        except UgyldigUtvalg:
            return RedirectResponse("/?" + urlencode(parametre), status_code=303)
        resultat = tjeneste.svar(utvalg, nå, tving=True)
        adresse = utvalgsparametre(utvalg)
        if resultat.sist_lagrede:
            adresse[NYESTE] = str(int(nå.timestamp()))
        return RedirectResponse("/?" + urlencode(adresse), status_code=303)

    @app.get("/forklaring", response_class=HTMLResponse)
    def forklaring(request: Request) -> Response:
        """KI-forklaringen for utvalget som et HTML-fragment (FR-20, FR-22, AD-9).

        `app.js` setter fragmentet inn i forklaringsområdet bare når statusen
        er 200. Et ugyldig utvalg gir 400, og da viser `app.js` feilteksten fra
        `data-feiltekst`. Tekstene står i malene (AD-6).
        """
        tjeneste: Tjeneste = request.app.state.tjeneste
        nå = klokke()
        parametre = {navn: request.query_params.get(navn, "") for navn in PARAMETRE}
        uten_lagring = {"Cache-Control": "no-store"}
        try:
            utvalg = Utvalg.fra_parametre(parametre, tjeneste.sesonger(nå))
        except UgyldigUtvalg:
            return Response(
                "Ugyldig utvalg.",
                status_code=400,
                media_type="text/plain; charset=utf-8",
                headers=uten_lagring,
            )
        resultat = tjeneste.svar(utvalg, nå)
        utfall = tjeneste.forklaring(resultat, nå)
        return maler.TemplateResponse(
            request,
            "_forklaring.html",
            {
                "resultat": resultat,
                "forklaring": utfall.tekst if isinstance(utfall, Forklaring) else None,
                "uten_nøkkel": isinstance(utfall, ManglerNøkkel),
            },
            headers=uten_lagring,
        )

    return app


app = lag_app()
