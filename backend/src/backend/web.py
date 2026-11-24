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
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

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
    Dataserie,
    UgyldigUtvalg,
    Uke,
    Utvalg,
)
from backend.tjeneste import KLARE_VIRUS, Resultat, Tjeneste

if TYPE_CHECKING:
    # Bare for typen til testklienten. `web` kaller aldri `fhi` (AD-1).
    from backend import fhi

MAPPE = Path(__file__).parent
PARAMETRE = ("mal", "virus", "sesong", "alder")
"""Query-parametrene for et utvalg (AD-9)."""

NORSK_TID = ZoneInfo("Europe/Oslo")
"""Hentetidspunktet vises i norsk tid (AD-5). Lagret tid er UTC."""

HARDT_MELLOMROM = "\u00a0"
"""Mellomrom som ikke brytes, i tall og foran «%» (arkitektur §4)."""


# --- Jinja2-filtre: all formatering for visning skjer her (arkitektur §4) ---


def tall(verdi: int | None) -> str:
    """«1 210» med mellomrom som tusenskille. `None` er en skjult verdi (FR-11)."""
    if verdi is None:
        return "skjult"
    return f"{verdi:,}".replace(",", HARDT_MELLOMROM)


def _avrundet(verdi: float) -> Decimal:
    """Andelen med én desimal, avrundet halvt opp. Brukes av både tabellen og
    grafen, så de viser samme tall."""
    return Decimal(repr(verdi)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def andel(verdi: float | None) -> str:
    """«20,8 %» med én desimal, avrundet halvt opp. `None` blir «mangler»."""
    if verdi is None:
        return "mangler"
    return f"{_avrundet(verdi)}".replace(".", ",") + HARDT_MELLOMROM + "%"


def uke(verdi: Uke) -> str:
    """«uke 50»."""
    return f"uke {verdi.ukenummer}"


def utvalgstekst(verdi: Utvalg) -> str:
    """«Influensa, sesongen 2025/2026, alle aldersgrupper» (FR-9)."""
    alder = ALDERSGRUPPER[verdi.aldersgruppe].etikett
    return f"{VIRUS[verdi.virus].navn}, sesongen {verdi.sesong}, {alder[0].lower()}{alder[1:]}"


def grafdata(serie: Dataserie) -> dict[str, Any]:
    """Tallene grafen tegner, fra samme `Dataserie` som tabellen (AD-8).

    Manglende uker (og uker med 0 tester) har `null` som andel, så linjen får
    brudd (FR-9). `usikker` sier hvilke punkter som får åpen sirkel (FR-10).
    """
    return {
        "uker": [uke(u) for u in serie.uker],
        "andel": [
            None if u.andel is None else float(_avrundet(u.andel)) for u in serie.uker
        ],
        "usikker": [u.usikker for u in serie.uker],
        "tekster": {"x": "Uke", "y": "Andel positive (%)"},
    }


def alternativtekst(serie: Dataserie) -> str:
    """Alternativtekst for grafen med utvalg og hovedtrekk (NFR-6)."""
    tekst = (
        f"Linjegraf over andel positive tester uke for uke. "
        f"{utvalgstekst(serie.utvalg)}."
    )
    med_andel = [u for u in serie.uker if u.andel is not None]
    if not serie.uker or not med_andel:
        return tekst + " Ingen uker har en andel som kan vises."
    tekst += f" Grafen viser {uke(serie.uker[0])} til {uke(serie.uker[-1])}."
    høyest = max(med_andel, key=lambda u: u.andel)
    siste = med_andel[-1]
    tekst += f" Andelen var høyest i {uke(høyest)} med {andel(høyest.andel)}."
    if siste is not høyest:
        tekst += (
            f" I {uke(siste)}, den siste uka med tall, var den {andel(siste.andel)}."
        )
    usikre = sum(u.usikker for u in serie.uker)
    if usikre:
        om_usikre = "uke er usikker" if usikre == 1 else "uker er usikre"
        tekst += f" {usikre} {om_usikre} og markert med åpen sirkel."
    return tekst


def tidspunkt(verdi: datetime) -> str:
    """«20.11.2026 kl. 14:05» i norsk tid (AD-5)."""
    return verdi.astimezone(NORSK_TID).strftime("%d.%m.%Y kl. %H:%M")


maler = Jinja2Templates(directory=MAPPE / "templates")
maler.env.filters.update(
    tall=tall,
    andel=andel,
    uke=uke,
    tidspunkt=tidspunkt,
    utvalgstekst=utvalgstekst,
    grafdata=grafdata,
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
            },
        )

    return app


app = lag_app()
