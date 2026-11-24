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
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend import config
from backend.config import Innstillinger
from backend.domene import (
    ALDERSGRUPPER,
    MALER,
    STANDARD_ALDERSGRUPPE,
    VIRUS,
    UgyldigUtvalg,
    Utvalg,
)
from backend.tjeneste import KLARE_VIRUS, Resultat, Tjeneste

if TYPE_CHECKING:
    # Bare for typen til testklienten. `web` kaller aldri `fhi` (AD-1).
    from backend import fhi

MAPPE = Path(__file__).parent
PARAMETRE = ("mal", "virus", "sesong", "alder")
"""Query-parametrene for et utvalg (AD-9)."""

maler = Jinja2Templates(directory=MAPPE / "templates")


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
) -> FastAPI:
    """Lager appen. Testene sender inn egne innstillinger og en `klient`.

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
        nå = datetime.now(UTC)
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
            },
        )

    return app


app = lag_app()
