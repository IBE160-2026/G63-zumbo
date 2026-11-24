# G63 — Biobytes

Prosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng). Gjennomføres solo etter godkjenning fra faglærer.

## Prosjekt: FHI Helsedata-utforsker

KI-assistert applikasjon for å utforske FHIs åpne statistikk om smittsomme sykdommer og laboratoriefunn.

## Medlemmer

- Irene Zumbo

## Dokumentasjon

- [Product Brief (proposal)](docs/product-brief.md)

## Kom i gang

Krever git og [uv](https://docs.astral.sh/uv/) (se lenken for hvordan uv installeres). uv henter selv riktig Python-versjon (3.13). Alle `uv`-kommandoene kjøres fra `backend/`.

### Installere

    git clone https://github.com/IBE160-2026/G63-zumbo.git
    cd G63-zumbo/backend
    uv sync

`uv sync` installerer appen og utviklingsverktøyene (pytest, pytest-socket, respx og ruff) med versjonene som er låst i `uv.lock`.

### Kjøre testene og ruff

Fra `backend/`:

    uv run pytest
    uv run ruff check
    uv run ruff format --check

Alle tre kommandoene skal bestå før hver commit. Testene kjører uten nett: `pytest-socket` stopper alle nettverkskall, så ingen test kan kalle FHI eller Claude ved et uhell. Testene trenger heller ingen KI-nøkkel og leser aldri `.env`. De bruker lagrede svar i `backend/tests/fixtures/`. Ekte svar fra FHI for tabell 724 ligger i `backend/tests/fixtures/fhi/`, og README-en der forklarer formatet og hvordan de ble hentet.

### Starte appen

Web-appen finnes ikke ennå. Kommandoen for å starte den lokalt skrives inn her i story 3.1.

### KI-nøkkel er valgfri

`.env` er valgfri. Appen virker uten KI-nøkkel: alt unntatt KI-forklaringen virker. Vil du ha KI-forklaringen, kopierer du `.env.example` til `.env` i reporoten og fyller inn `ANTHROPIC_API_KEY`. Fra reporoten:

    cp .env.example .env

`ANTHROPIC_MODEL` kan stå tom; da brukes standardmodellen. `.env` og mellomlageret i `.cache/` holdes utenfor git.

### Mellomlager

Svar fra FHI lagres i `.cache/` i reporoten. Tall du har sett før, brukes uten nytt kall, også når FHI er nede (da merket «sist lagrede»), og tall som er 24 timer eller eldre, hentes på nytt (`tjeneste.py`, story 2.9). Siden som viser tallene, kommer i epic 3. Vil du ha mellomlageret et annet sted, setter du `CACHE_DIR` i `.env` eller i miljøet. En relativ sti regnes fra reporoten. På Vercel (miljøvariabelen `VERCEL` finnes) brukes `/tmp/fhi-helsedata-cache` når `CACHE_DIR` ikke er satt. Mappen kan slettes når som helst; alt hentes på nytt.

## Struktur

- backend/: Python-prosjekt (uv)
- docs/: prosjektdokumentasjon
