# Utsatt arbeid

## Deferred from: code review of spec-1-1-rydde-uv-prosjektet-og-holde-nokler-og-cache-utenfor-git.md (2026-11-22)

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-rydde-uv-prosjektet-og-holde-nokler-og-cache-utenfor-git.md`
  summary: `config.les_innstillinger()` må behandle tom `ANTHROPIC_MODEL` og tom `ANTHROPIC_API_KEY` som ikke satt (bruk `os.getenv(...) or standard`).
  evidence: `.env.example` har `ANTHROPIC_MODEL=` og `ANTHROPIC_API_KEY=` med tomme verdier (AC i story 1.1). Kopieres fila uendret til `.env`, setter python-dotenv (`override=True`, AD-6) begge til `""`. Da gir `os.environ.get(navn, standard)` `""`, og en tom nøkkel kan bli tolket som at nøkkelen finnes. README og `.env.example` lover nå at tom modell gir standardmodellen.

## Deferred from: code review of spec-1-2-ruff-og-pytest-uten-nett.md (2026-11-23)

- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-ruff-og-pytest-uten-nett.md`
  summary: App-testene med FastAPIs `TestClient` trenger `--allow-unix-socket` i `addopts` ved siden av `--disable-socket`.
  evidence: Sjekket 23.11.: en `TestClient(app).get("/")` feiler med `SocketBlockedError: A test tried to use socket.socket` (asyncio sin self-pipe bruker `socket.socketpair`). Med `--allow-unix-socket` består den, og testene i `test_nettsperre.py` består fortsatt (TCP og DNS er fortsatt stoppet). Må tas i den første storyen med app-tester (epic 3).
  status: løst 2026-11-23 i story 1.2 — `--allow-unix-socket` er lagt i `addopts`, og en test viser at en lokal socketpair er tillatt mens nettkall fortsatt stoppes.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-ruff-og-pytest-uten-nett.md`
  summary: Ingenting kjører `ruff check`, `ruff format --check` og `pytest` automatisk før commit eller push (ingen CI eller pre-commit).
  evidence: AD-10 sier at ruff skal bestå før commit. README sier det nå, men ingen test eller hook håndhever det, så `uv run pytest` er grønn selv om ruff feiler. Hører naturlig hjemme i en GitHub Actions-jobb eller pre-commit når det settes opp. Vurderes i epic 7 hvis det blir tid.

## Deferred from: code review of spec-1-3-lagre-et-ekte-svar-fra-tabell-724-som-fixture.md (2026-11-23)

- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-lagre-et-ekte-svar-fra-tabell-724-som-fixture.md`
  summary: Arkitekturen §8 («Utsatt») og `epic-1-context.md` bør si at FHI-svaret hentes som `json-stat2`, og peke til `backend/tests/fixtures/fhi/README.md`.
  evidence: §8 sier fortsatt at «Nøyaktig format på FHI-forespørselen (CSV eller JSON) og tolking av FLAGG-kolonnen» skal avgjøres. Epic-konteksten beskriver CSV-kolonnene «Påvisninger», «Testede», «Andel (%)» og «FLAGG». Story 1.3 valgte `json-stat2` (se README-en). Senere stories kan lese at saken er uavklart. Rettingen endrer planleggingsdokumenter, så den hører hjemme i en egen oppdatering (for eksempel med `bmad-architecture`).
