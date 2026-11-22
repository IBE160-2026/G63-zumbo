# Epic 1 Context: Oppsett

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Gjøre prosjektet klart til å bygges før funksjonaliteten starter. Det eksisterende uv-prosjektet i `backend/` ryddes til bare den valgte stacken, nøkler og cache holdes utenfor git, ruff og pytest settes opp slik at ingen test kan nå nettet, et ekte FHI-svar for influensa (tabell 724) lagres som fixture, og en enkel README forklarer installering, tester og at appen virker uten KI-nøkkel. Irene sjekker i tillegg FHIs egen ordlyd for kildehenvisningen til tabell 724. Alle senere epics bygger på dette: testene i resten av prosjektet forutsetter nettsperren og fixture-formatet herfra. Veiledende tid: 21.–22. november 2026.

## Stories

- Story 1.1: Rydde uv-prosjektet og holde nøkler og cache utenfor git
- Story 1.2: ruff og pytest uten nett
- Story 1.3: Lagre et ekte svar fra tabell 724 som fixture
- Story 1.4: Sjekke FHIs kildehenvisning for tabell 724 (Irene)
- Story 1.5: Enkel README

## Requirements & Constraints

- KI-nøkkelen ligger bare i `.env` i reporoten, som er ignorert av git. Repoet har `.env.example` med `ANTHROPIC_API_KEY=` og `ANTHROPIC_MODEL=`.
- Mellomlagringsmappen `.cache/` (lokalt, i reporoten) skal være ignorert av git.
- Alle automatiske tester kjører uten nett og uten KI-nøkkel, med lagrede svar i `tests/fixtures/`. Testene laster aldri `.env`.
- Alt unntatt KI-forklaringen skal virke uten KI-nøkkel; README skal si at `.env` er valgfri.
- Bare åpne, aggregerte data fra FHI. Ingen persondata, ingen innlogging.
- FHI skal alltid oppgis som kilde. Kildehenvisningen består av MSIS-labdatabasen, FHI, tabellnummer, tabellnavn og hentedato. Tabellnavnet for 724 er antatt «RESPIaggr Influensa antall og andel» og skal bekreftes mot metadataene.
- Felles ferdigkriterier for utviklerstories (alle unntatt Irenes): egne automatiske tester for akseptansekriteriene, `uv run pytest` består uten nett og nøkkel, `ruff check` og `ruff format --check` består, ingen import bryter avhengighetsretningen, og README oppdateres når installering, oppstart, konfigurasjon eller tester endres.
- Stories merket «(Irene)» gjøres manuelt og har ingen automatiske tester.

## Technical Decisions

**Stack** (i `backend/pyproject.toml` med `>=` og versjonen under som minimum; `uv.lock` låser eksakte versjoner):

| Pakke | Versjon |
| --- | --- |
| Python | 3.13 |
| uv_build (byggesystem) | >=0.12.19,<0.13 |
| FastAPI | 0.165.0 |
| Uvicorn | 0.54.0 |
| Jinja2 | 3.1.6 |
| python-multipart | 0.0.34 |
| httpx | 0.28.1 |
| anthropic | 2.11.0 |
| python-dotenv | 1.2.4 |
| tzdata | 2026.6 |

Utviklingsavhengigheter: pytest 9.2.0, pytest-socket 0.8.1, respx 0.23.1, ruff 0.17.6. Chart.js 4.6.1 (CDN) og modellen `claude-haiku-5-5` brukes senere, ikke i dette epicet.

- **SQLAlchemy fjernes.** Det finnes ingen database; mellomlagring er JSON-filer. Ingen startmal brukes; det eksisterende uv-prosjektet ryddes.
- **Testoppsett:** pytest kjøres med `--disable-socket` som standard (satt i `pyproject.toml`), slik at alle nettverkskall feiler med `SocketBlockedError`. FHI mockes senere med `respx`, KI med en falsk klient. `ruff check` og `ruff format --check` konfigureres i `pyproject.toml`.
- **Fixture-mapper:** `tests/fixtures/fhi/` (lagrede FHI-svar), `tests/fixtures/ki/` (KI-tekster), `tests/fixtures/konstruert/` (grensetilfeller for kontrollreglene). Senere kommer `tests/fixtures/testsett/`.
- **Fixture-format = cacheformat:** hver fil er `{"hentet": <ISO 8601 i UTC>, "svar": <rått FHI-svar>}`, slik at én tolker dekker både cache og tester. Dimensjonslisten lagres som `724-dimensjoner.json` i samme format; den brukes senere til siste publiserte uke og sesonglisten.
- **FHI-API (åpent, uten nøkkel):** base `https://statistikk-data.fhi.no/api/open/v1/msis/Table/{tabell}/` med `metadata` (GET), `dimension` (GET) og `data` (POST). Utvalg for fixturen: tabell 724, `dateusedforstatistics` for sesongen 2025/2026 (fra `2025-w40`), `aldersgruppe=Alle`, `surveillancetype=NONSTL`, `influenzatypeandsubtype=A+B`, `MEASURE_TYPE` = `Detections`, `Tests`, `pos_rate`.
- **Utsatt til fixture-storyen:** valget mellom CSV og JSON fra FHI og hvordan FLAGG-kolonnen (brukes til å finne skjulte verdier) ser ut. CSV har kolonnene «Påvisninger», «Testede», «Andel (%)» og «FLAGG». Valget dokumenteres kort i `tests/fixtures/fhi/README.md`.
- **Plassering:** Python-prosjektet ligger i `backend/` (`src/backend/`, `tests/`), mens `.gitignore`, `.env.example`, `.env`, `.cache/` og README ligger i reporoten. Lokal oppstart blir `cd backend && uv run uvicorn backend.web:app --reload`, men kommandoen fylles først inn i README når web-appen finnes.
- **Konfigurasjon:** bare `config.py` leser miljøvariabler (`ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `CACHE_DIR`, `VERCEL`); ingen modul laster `.env` ved import.
- **Navn:** moduler, funksjoner og tester på norsk; ord fra rammeverk og biblioteker beholdes på engelsk.

## Cross-Story Dependencies

- 1.2 bygger på det ryddede prosjektet fra 1.1.
- 1.3 krever nettsperren fra 1.2 (henting gjøres manuelt én gang, testen leser bare filene) og fixture-mappene derfra.
- 1.5 forutsetter 1.1–1.3; plassen for oppstartskommandoen fylles ut i story 3.1.
- 1.4 (Irene) oppdaterer addendumet med FHIs ordrette kildetekst og dato, og bekrefter eller retter tabellnavnet i PRD-en. Kildehenvisningen som vises i appen (epic 3) og testsettet (epic 7) avhenger av dette.
- Fixturen fra 1.3 er grunnlaget for tolkingen og henting med `respx` i epic 2. Nettsperren og fixture-formatet gjelder alle senere tester.
