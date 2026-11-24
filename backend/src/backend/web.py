"""Nettsiden: FastAPI-appen og rutene (AD-8, AD-9, AD-11).

Start lokalt fra `backend/` med `uv run uvicorn backend.web:app --reload`.

`web` gjør bare HTTP og HTML. Brukerens valg sjekkes i
`domene.Utvalg.fra_parametre`, og tallene kommer fra `tjeneste`. Innstillingene
leses én gang, ved oppstart, og aldri ved import, slik at testene ikke laster
`.env` (AD-6, AD-10).
"""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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
from backend.tjeneste import KLARE_VIRUS, Resultat, Tjeneste

if TYPE_CHECKING:
    # Bare for typen til testklienten. `web` kaller aldri `fhi` (AD-1).
    from backend import fhi

MAPPE = Path(__file__).parent
PARAMETRE = ("mal", "virus", "sesong", "alder")
"""Query-parametrene for et utvalg (AD-9)."""

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
) -> FastAPI:
    """Lager appen. Testene sender inn egne innstillinger, en `klient` og en
    fast `klokke`.

    `les_innstillinger` kalles én gang, når appen starter (AD-6).
    """

    @asynccontextmanager
    async def levetid(app: FastAPI) -> AsyncIterator[None]:
        app.state.tjeneste = Tjeneste(les_innstillinger(), klient=klient)
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
                "begreper": BEGREPER,
                "tynt_datagrunnlag": next(
                    b.html_id for b in BEGREPER if b.nøkkel == TYNT_DATAGRUNNLAG
                ),
            },
        )

    return app


app = lag_app()
