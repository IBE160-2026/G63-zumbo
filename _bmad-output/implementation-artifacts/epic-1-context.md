# Epic 1 Context: Oppsett

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Gjøre prosjektet klart til å bygges før funksjonaliteten starter. Det eksisterende uv-prosjektet i `backend/` ryddes til bare den valgte stacken, nøkler og cache holdes utenfor git, ruff og pytest settes opp slik at ingen test kan nå nettet, et ekte FHI-svar for influensa (tabell 724) lagres som fixture sammen med dimensjonslisten, og en enkel README forklarer installering, tester og at appen virker uten KI-nøkkel. Irene har sjekket FHIs egen ordlyd for kildehenvisningen til tabell 724. Alle senere epics bygger på dette: testene i resten av prosjektet forutsetter nettsperren og fixture-formatet herfra. Veiledende tid: 21.–22. november 2026.

## Stories

- Story 1.1: Rydde uv-prosjektet og holde nøkler og cache utenfor git
- Story 1.2: ruff og pytest uten nett
- Story 1.3: Lagre et ekte svar fra tabell 724 som fixture
- Story 1.4: Sjekke FHIs kildehenvisning for tabell 724 (Irene)
- Story 1.5: Enkel README

## Requirements & Constraints

- KI-nøkkelen ligger bare i `.env` i reporoten, som er ignorert av git. Repoet har `.env.example` med `ANTHROPIC_API_KEY=` og `ANTHROPIC_MODEL=`. Mellomlagringsmappen `.cache/` (i reporoten) er også ignorert.
- Alle automatiske tester kjører uten nett og uten KI-nøkkel, med lagrede svar i `tests/fixtures/`. Testene laster aldri `.env`.
- Alt unntatt KI-forklaringen skal virke uten KI-nøkkel; README skal si at `.env` er valgfri.
- Bare åpne, aggregerte data fra FHI. Ingen persondata, ingen innlogging.
- FHI skal alltid oppgis som kilde. Kildehenvisningen består av FHIs egen kildetekst (ordrett fra metadataene), tabellnummer, tabellnavn og hentedato. For 724: kildetekst «Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, Folkehelseinstituttet (FHI).» (sjekket 22.11.2026) og tabellnavn «RESPIaggr Influensa antall og andel» (bekreftet mot metadataene 23.11.2026). Story 1.4 er gjennomført.
- Skjulte verdier fra FHI kan komme som `..`, `.`, `:` eller tom verdi. De skal senere bli `None`, aldri `0` – fixturen må derfor bevare det rå svaret uendret.
- Felles ferdigkriterier for utviklerstories (alle unntatt Irenes): egne automatiske tester for akseptansekriteriene, `uv run pytest` består uten nett og nøkkel, `ruff check` og `ruff format --check` består, ingen import bryter avhengighetsretningen, og README oppdateres når installering, oppstart, konfigurasjon eller tester endres.
- Stories merket «(Irene)» gjøres manuelt og har ingen automatiske tester.

## Technical Decisions

**Stack:** Python 3.13, uv (`uv_build`). Avhengigheter i `backend/pyproject.toml` med `>=` og minimumsversjon, eksakt låst i `uv.lock`: FastAPI 0.165.0, Uvicorn 0.54.0, Jinja2 3.1.6, python-multipart 0.0.34, httpx 0.28.1, anthropic 2.11.0, python-dotenv 1.2.4, tzdata 2026.6. Utvikling: pytest 9.2.0, pytest-socket 0.8.1, respx 0.23.1, ruff 0.17.6. SQLAlchemy fjernes – ingen database, mellomlagring er JSON-filer.

- **Testoppsett:** pytest kjøres med `--disable-socket` som standard (i `pyproject.toml`), så alle nettverkskall feiler med `SocketBlockedError`. FHI mockes senere med `respx`, KI med en falsk klient.
- **Fixture-mapper:** `tests/fixtures/fhi/` (lagrede FHI-svar), `tests/fixtures/ki/`, `tests/fixtures/konstruert/` (grensetilfeller R1–R5); senere `tests/fixtures/testsett/`.
- **Fixture-format = cacheformat:** hver fil er `{"hentet": <ISO 8601 i UTC>, "svar": <rått FHI-svar>}`, slik at én tolker dekker både cache og tester. Cachen bruker filnavnene `fhi/<Utvalg.nøkkel>.json` og `fhi/<tabell>-dimensjoner.json`; dimensjonslisten for fixturen heter `724-dimensjoner.json`.
- **FHI-API (åpent, uten nøkkel), base `https://statistikk-data.fhi.no/api/open/v1/msis/Table/{tabell}/`:** `metadata` (GET), `dimension` (GET) og `data` (POST). Formatet på forespørselen og svaret ble avgjort mot ekte svar i story 1.3 (se under); bare `fhi.py` skal senere kjenne det.
- **Dimensjoner i tabell 724:** `dateusedforstatistics` (`2024-w40` … siste publiserte uke, ved planlegging `2026-w46`), `aldersgruppe` (`Alle`, `0-4 år`, `5-14 år`, `15-29 år`, `30-64 år`, `65-79 år`, `80+ år`, `Ukjent`), `surveillancetype` (`NONSTL`, `STL`), `influenzatypeandsubtype` (`A+B`, `A`, `B`), `MEASURE_TYPE` (`Detections`, `Tests`, `pos_rate`). Ingen sesongdimensjon i metadataene.
- **Utvalg for fixturen:** sesongen 2025/2026 (uke 40 til og med uke 20, dvs. `2025-w40` … `2026-w20`), `aldersgruppe=Alle`, `surveillancetype=NONSTL`, `influenzatypeandsubtype=A+B`, alle tre `MEASURE_TYPE`. Testen må minst sjekke at `hentet` og `svar` finnes og at `2025-w40` er med.
- **Dimensjonslisten** brukes senere til å finne siste publiserte uke (høyeste uke i `dateusedforstatistics`) og sesonglisten.
- **JSON (`json-stat2`) er valgt, ikke CSV (story 1.3). Endret 23. november 2026.** Med JSON blir `svar` i cachen og fixturene et vanlig JSON-objekt med tall som tall, og vi slipper å tolke CSV-tekst. Både koder og etiketter følger med. Tabell 724 har bare flagg 0 («Verdi finnes i tabellen»), og ekte data har ingen skjulte verdier. Derfor testes skjulte verdier med konstruerte data. Forespørselen, FLAGG og særheter i formatet står i `backend/tests/fixtures/fhi/README.md`.
- **Plassering:** Python-prosjektet ligger i `backend/` (`src/backend/`, `tests/`); `.gitignore`, `.env.example`, `.env`, `.cache/` og README ligger i reporoten. uv-kommandoene (`uv sync`, `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`) kjøres derfor fra `backend/`.
- **README og kjøring (story 1.5, AD-11):** README i reporoten beskriver installering med `uv sync`, tester med `uv run pytest` og ruff-kommandoene. Den sier at `.env` er valgfri (kopi av `.env.example`) og at alt unntatt KI-forklaringen virker uten nøkkel – appen starter uten `.env`. Oppstartskommandoen blir `cd backend && uv run uvicorn backend.web:app --reload`, men README har bare en plass for den til story 3.1 fyller den ut. Vercel er valgfritt og hører til epic 8. En automatisk test sjekker at README nevner `uv sync` og `uv run pytest`.
- **Konfigurasjon:** bare `config.py` leser miljøvariabler (`ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `CACHE_DIR`, `VERCEL`); ingen modul laster `.env` ved import.
- **Navn:** moduler, funksjoner og tester på norsk; ord fra rammeverk og biblioteker beholdes på engelsk.

## Cross-Story Dependencies

- 1.2 bygger på det ryddede prosjektet fra 1.1.
- 1.3 krever nettsperren og fixture-mappene fra 1.2. Hentingen gjøres manuelt én gang utenfor testene; testen leser bare filene.
- 1.1–1.4 er ferdige. 1.5 forutsetter 1.1–1.3; plassen for oppstartskommandoen fylles ut i story 3.1, og den endelige README-en testes fra en ny klone i epic 7.
- 1.4 er ferdig: kildeteksten står i addendumet og tabellnavnet er bekreftet i PRD-en. Kildehenvisningen i appen (epic 3) og testsettet (epic 7) bygger på dette.
- Fixturen og dimensjonslisten fra 1.3 er grunnlaget for tolkingen, sesonglisten og henting med `respx` i epic 2. Nettsperren og fixture-formatet gjelder alle senere tester.
