# G63 — Biobytes

Prosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng). Gjennomføres solo etter godkjenning fra faglærer.

## Prosjekt: FHI Helsedata-utforsker

KI-assistert applikasjon for å utforske FHIs åpne statistikk om smittsomme sykdommer og laboratoriefunn.

## Medlemmer

- Irene Zumbo

## Dokumentasjon

- [Product Brief (proposal)](docs/product-brief.md)

## Kom i gang

Krever uv (https://docs.astral.sh/uv/).

    cd backend
    uv sync
    uv run pytest
    uv run ruff check
    uv run ruff format --check

Alle tre kommandoene skal bestå før hver commit. Testene kjører uten nett: `pytest-socket` stopper alle nettverkskall, så ingen test kan kalle FHI eller Claude ved et uhell. Lagrede svar fra FHI og KI skal ligge i `backend/tests/fixtures/` (det første kommer i story 1.3).

`.env` er valgfri. Uten KI-nøkkel virker alt unntatt KI-forklaringen. Vil du ha KI-forklaringen, kopierer du `.env.example` til `.env` i reporoten og fyller inn `ANTHROPIC_API_KEY`. `ANTHROPIC_MODEL` kan stå tom; da brukes standardmodellen. `.env` og mellomlageret i `.cache/` holdes utenfor git.

## Struktur

- backend/: Python-prosjekt (uv)
- docs/: prosjektdokumentasjon
