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
  status: løst 2026-11-23 i story 1.3 — §8 og epic-konteksten sier nå at `json-stat2` er valgt.

## Deferred from: code review of spec-1-5-enkel-readme.md (2026-11-23)

- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-enkel-readme.md`
  summary: Lag en test som viser at testene aldri laster `.env`, når python-dotenv tas i bruk (AD-6, AD-10).
  evidence: README og AD-10 sier at testene aldri leser `.env`. Det stemmer i dag fordi ingen kode laster `.env`, men ingen test håndhever det. Når `config.py` eller `web` begynner å kalle `load_dotenv`, kan en import ved et uhell lese en ekte nøkkel. Testen kan legge en falsk `.env` med `ANTHROPIC_API_KEY` i `tmp_path` og sjekke at verdien ikke havner i miljøet.

## Deferred from: code review of spec-2-1-domenemodellen.md (2026-11-23)

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-domenemodellen.md`
  summary: Avgjør i story 2.4 om `Uke` skal avvise flere positive enn tester (andel over 100 %).
  evidence: `Uke(2025, 40, 100, 200)` gir i dag `andel == 200.0`. Vi vet ikke om FHI kan ha flere påvisninger enn testede i en uke (for eksempel hvis én person teller som påvisning for både A og B). En sperre i `Uke` ville da gjort at `fhi.tolk` feiler på ekte data. Sjekk dette mot FHI-dataene i story 2.4 før vi legger inn en sperre. Alvorlighet ukjent (ikke bekreftet).
  status: løst 2026-11-24 i story 2.4 — Irenes beslutning: ingen sperre. Andelen vises som den er (over 100 %), og uka er usikker med en fotnote (`Uke.flere_positive_enn_tester`, FR-10). R2 teller fortsatt bare færre enn 30 tester. Fixturen for 724 har ingen slike uker.

## Deferred from: code review of spec-2-4-tolke-fhi-svar-til-en-komplett-dataserie.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-2-4-tolke-fhi-svar-til-en-komplett-dataserie.md`
  summary: Tabellen og grafen (story 3.2 og 3.3) må vise en egen fotnote på enkel norsk for uker med `Uke.flere_positive_enn_tester`, i tillegg til markeringen som usikker uke (FR-10).
  evidence: Irenes beslutning 24.11.2026. Bare egenskapen finnes i `domene`. Teksten står som eksempel i PRD FR-10. En uke med 0 tester og positive over 0 har ingen andel (kan ikke dele på 0), men skal likevel ha fotnoten.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-4-tolke-fhi-svar-til-en-komplett-dataserie.md`
  summary: Story 2.7 (R2) må ha en test som viser at en uke med flere positive enn tester og minst 30 tester ikke telles i R2.
  evidence: Irenes beslutning 24.11.2026 og FR-15. `Uke.usikker` er nå sann for slike uker, så R2 må telle `tester < 30` direkte og ikke bruke `usikker`. Ingen test håndhever det ennå.

## Deferred from: code review of spec-2-5-hente-fra-fhi-med-tidsgrense.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-2-5-hente-fra-fhi-med-tidsgrense.md`
  summary: `tjeneste` (story 2.9) må ikke kalle `fhi.hent` for RSV og SARS-CoV-2 før epic 6, og bare for sesonger fra `fhi.sesonger(dimensjoner)` (eller reserven).
  evidence: `fhi.forespørsel` gir `ValueError` for tabell 729 og 731 og for en sesong uten publiserte uker (for eksempel uke 40 før FHI har publisert). `Utvalg.fra_parametre` godtar `rsv` og `sars-cov-2`, så en URL kan nå dit. `tjeneste` fanger bare `FhiUtilgjengelig`. Enten må `tjeneste` gi en norsk melding for virus som ikke er klare, eller `fra_parametre` må få listen over virus som kan velges.
