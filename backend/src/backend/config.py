"""Innstillinger fra miljøvariabler og `.env` (AD-4, AD-6).

Den eneste koden som leser miljøvariabler. Ingenting skjer ved import: `.env`
lastes bare når `les_innstillinger()` kalles uten `miljø`, og det gjør bare `web`,
én gang ved oppstart. Testene sender alltid inn `miljø` og leser aldri `.env`
(AD-10).
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REPOROT = Path(__file__).resolve().parents[3]
"""`backend/src/backend/config.py` → reporoten."""

STANDARD_MODELL = "claude-haiku-5-5"
VERCEL_CACHE = Path("/tmp/fhi-helsedata-cache")
LOKAL_CACHE = REPOROT / ".cache"


@dataclass(frozen=True)
class Innstillinger:
    """Innstillingene appen trenger. Nøkkelen er `None` når den ikke er satt."""

    anthropic_api_key: str | None
    anthropic_model: str
    cache_dir: Path

    def __repr__(self) -> str:
        # Nøkkelen skal aldri havne i en logg eller feilmelding (NFR-9).
        nøkkel = "satt" if self.anthropic_api_key else "ikke satt"
        return (
            f"Innstillinger(anthropic_api_key=<{nøkkel}>, "
            f"anthropic_model={self.anthropic_model!r}, cache_dir={self.cache_dir!r})"
        )


def _verdi(miljø: Mapping[str, str], navn: str) -> str | None:
    """Verdien til en miljøvariabel, eller `None` når den mangler eller er tom."""
    verdi = miljø.get(navn, "").strip()
    return verdi or None


def les_innstillinger(
    miljø: Mapping[str, str] | None = None, env_fil: Path = REPOROT / ".env"
) -> Innstillinger:
    """Leser innstillingene (AD-6).

    Uten `miljø` lastes `env_fil` (`.env` i reporoten) med `override=True`, slik
    at `.env` vinner over skallet, og så leses `os.environ`. Med `miljø` brukes
    bare den, og `.env` lastes ikke.

    Tomme verdier regnes som ikke satt. Cachemappen er `CACHE_DIR`, ellers
    `/tmp/fhi-helsedata-cache` når `VERCEL` finnes, ellers `.cache/` i reporoten
    (AD-4).
    """
    if miljø is None:
        load_dotenv(env_fil, override=True)
        miljø = os.environ
    if (cache := _verdi(miljø, "CACHE_DIR")) is not None:
        cache_dir = Path(cache).expanduser()
    elif "VERCEL" in miljø:
        cache_dir = VERCEL_CACHE
    else:
        cache_dir = LOKAL_CACHE
    return Innstillinger(
        anthropic_api_key=_verdi(miljø, "ANTHROPIC_API_KEY"),
        anthropic_model=_verdi(miljø, "ANTHROPIC_MODEL") or STANDARD_MODELL,
        cache_dir=cache_dir,
    )
