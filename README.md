# G63 — Biobytes

Prosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng). Gjennomføres solo etter godkjenning fra faglærer.

## Prosjekt: FHI Helsedata-utforsker

KI-assistert applikasjon for å utforske FHIs åpne statistikk om smittsomme sykdommer og laboratoriefunn.

## Medlemmer

- Irene Zumbo

## Dokumentasjon

- [Product Brief (proposal)](docs/product-brief.md)

## Kom i gang

Krever [uv](https://docs.astral.sh/uv/). uv henter selv riktig Python-versjon (3.13). Alle kommandoene kjøres fra `backend/`.

### Installere

    cd backend
    uv sync

`uv sync` installerer appen og utviklingsverktøyene (pytest og ruff) med versjonene som er låst i `uv.lock`.

### Kjøre testene og ruff

    uv run pytest
    uv run ruff check
    uv run ruff format --check

Alle tre kommandoene skal bestå før hver commit. Testene kjører uten nett: `pytest-socket` stopper alle nettverkskall, så ingen test kan kalle FHI eller Claude ved et uhell. Testene trenger heller ingen KI-nøkkel og leser aldri `.env`. De bruker lagrede svar i `backend/tests/fixtures/`. Ekte svar fra FHI for tabell 724 ligger i `backend/tests/fixtures/fhi/`, og README-en der forklarer formatet og hvordan de ble hentet.

### Starte appen

Web-appen finnes ikke ennå. Kommandoen for å starte den lokalt skrives inn her i story 3.1.

### KI-nøkkel er valgfri

`.env` er valgfri. Appen virker uten KI-nøkkel. Da virker alt unntatt KI-forklaringen. Vil du ha KI-forklaringen, kopierer du `.env.example` til `.env` i reporoten og fyller inn `ANTHROPIC_API_KEY`. `ANTHROPIC_MODEL` kan stå tom; da brukes standardmodellen. `.env` og mellomlageret i `.cache/` holdes utenfor git.

## Struktur

- backend/: Python-prosjekt (uv)
- docs/: prosjektdokumentasjon
