# Utsatt arbeid

## Deferred from: code review of spec-1-1-rydde-uv-prosjektet-og-holde-nokler-og-cache-utenfor-git.md (2026-11-22)

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-rydde-uv-prosjektet-og-holde-nokler-og-cache-utenfor-git.md`
  summary: `config.les_innstillinger()` må behandle tom `ANTHROPIC_MODEL` og tom `ANTHROPIC_API_KEY` som ikke satt (bruk `os.getenv(...) or standard`).
  evidence: `.env.example` har `ANTHROPIC_MODEL=` og `ANTHROPIC_API_KEY=` med tomme verdier (AC i story 1.1). Kopieres fila uendret til `.env`, setter python-dotenv (`override=True`, AD-6) begge til `""`. Da gir `os.environ.get(navn, standard)` `""`, og en tom nøkkel kan bli tolket som at nøkkelen finnes. README og `.env.example` lover nå at tom modell gir standardmodellen.

## Deferred from: code review of spec-1-2-ruff-og-pytest-uten-nett.md (2026-11-23)

- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-ruff-og-pytest-uten-nett.md`
  summary: App-testene med FastAPIs `TestClient` trenger `--allow-unix-socket` i `addopts` ved siden av `--disable-socket`.
  evidence: Sjekket 23.11.: en `TestClient(app).get("/")` feiler med `SocketBlockedError: A test tried to use socket.socket` (asyncio sin self-pipe bruker `socket.socketpair`). Med `--allow-unix-socket` består den, og testene i `test_nettsperre.py` består fortsatt (TCP og DNS er fortsatt stoppet). Må tas i den første storyen med app-tester (epic 3).
- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-ruff-og-pytest-uten-nett.md`
  summary: Ingenting kjører `ruff check`, `ruff format --check` og `pytest` automatisk før commit eller push (ingen CI eller pre-commit).
  evidence: AD-10 sier at ruff skal bestå før commit. README sier det nå, men ingen test eller hook håndhever det, så `uv run pytest` er grønn selv om ruff feiler. Hører naturlig hjemme i en GitHub Actions-jobb eller pre-commit når det settes opp.
