"""Viser forklaringsområdet på siden med en falsk Claude (story 4.5).

Slik kan du se alle tre utfallene i nettleseren uten en ekte KI-nøkkel:

    uv run python scripts/vis_forklaring.py forklaring
    uv run python scripts/vis_forklaring.py uten-nokkel
    uv run python scripts/vis_forklaring.py feil

Kjør fra `backend/` og åpne http://127.0.0.1:8001 i nettleseren, og trykk på
et viruskort. Tallene hentes fra FHI som vanlig, så du må ha
nett. Claude kalles aldri: «forklaring» gir den lagrede teksten fra
`tests/fixtures/ki/` etter to sekunder, så du rekker å se «Forklaringen lages …»,
og «feil» later som Claude ikke svarte. Den falske
forklaringen er den samme teksten for alle utvalg. Mellomlageret ligger i en midlertidig
mappe som slettes når du stopper med Ctrl+C, så den falske forklaringen havner
aldri i `.cache/ki/`. `.env` leses ikke.
"""

import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Self

import uvicorn
from anthropic.types import Message, TextBlock, Usage

from backend import web
from backend.config import Innstillinger

BACKEND = Path(__file__).resolve().parent.parent
FORKLARING = (
    (BACKEND / "tests" / "fixtures" / "ki" / "forklaring-influensa-2025-2026-alle.txt")
    .read_text(encoding="utf-8")
    .strip()
)
UTFALL = ("forklaring", "uten-nokkel", "feil")
MODELL = "claude-haiku-5-5"
PORT = 8001
"""En annen port enn den vanlige appen (8000), så begge kan kjøre samtidig."""


class FalskClaude:
    """Står i stedet for `anthropic.Anthropic`. Svarer uten å bruke nettet."""

    def __init__(self, feil: bool) -> None:
        self.feil = feil
        self.messages = self

    def __call__(self, **_: Any) -> Self:
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def create(self, **_: Any) -> Message:
        time.sleep(2)
        if self.feil:
            raise RuntimeError("falsk feil fra Claude")
        return Message(
            id="msg_falsk",
            type="message",
            role="assistant",
            model=MODELL,
            content=[TextBlock(type="text", text=FORKLARING)],
            stop_reason="end_turn",
            stop_sequence=None,
            usage=Usage(input_tokens=1, output_tokens=1),
        )


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in UTFALL:
        sys.exit("Bruk: uv run python scripts/vis_forklaring.py " + "|".join(UTFALL))
    utfall = sys.argv[1]
    nøkkel = None if utfall == "uten-nokkel" else "falsk-nøkkel"
    with tempfile.TemporaryDirectory(prefix="fhi-demo-") as mappe:
        innstillinger = Innstillinger(
            anthropic_api_key=nøkkel, anthropic_model=MODELL, cache_dir=Path(mappe)
        )
        app = web.lag_app(
            lambda: innstillinger, ny_ki_klient=FalskClaude(feil=utfall == "feil")
        )
        print(f"Utfall: {utfall}. Åpne http://127.0.0.1:{PORT}. Stopp med Ctrl+C.")
        uvicorn.run(app, host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
