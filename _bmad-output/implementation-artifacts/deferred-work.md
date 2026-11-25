# Utsatt arbeid

## Deferred from: code review of spec-1-1-rydde-uv-prosjektet-og-holde-nokler-og-cache-utenfor-git.md (2026-11-22)

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-rydde-uv-prosjektet-og-holde-nokler-og-cache-utenfor-git.md`
  summary: `config.les_innstillinger()` må behandle tom `ANTHROPIC_MODEL` og tom `ANTHROPIC_API_KEY` som ikke satt (bruk `os.getenv(...) or standard`).
  evidence: `.env.example` har `ANTHROPIC_MODEL=` og `ANTHROPIC_API_KEY=` med tomme verdier (AC i story 1.1). Kopieres fila uendret til `.env`, setter python-dotenv (`override=True`, AD-6) begge til `""`. Da gir `os.environ.get(navn, standard)` `""`, og en tom nøkkel kan bli tolket som at nøkkelen finnes. README og `.env.example` lover nå at tom modell gir standardmodellen.
  status: løst 2026-11-24 i story 2.6 — `config._verdi` regner tomme verdier (også bare mellomrom) som ikke satt, testet i `test_tomme_verdier_fra_env_example_regnes_som_ikke_satt`.

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
  status: løst 2026-11-24 i story 2.6 — `les_innstillinger` tar `miljø` som argument, og testene sender det alltid inn. `test_import_av_config_laster_ikke_env` importerer `config` i en egen prosess med en falsk `dotenv`, og en AST-test stopper `dotenv`-kall utenfor funksjoner.

## Deferred from: code review of spec-2-1-domenemodellen.md (2026-11-23)

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-domenemodellen.md`
  summary: Avgjør i story 2.4 om `Uke` skal avvise flere positive enn tester (andel over 100 %).
  evidence: `Uke(2025, 40, 100, 200)` gir i dag `andel == 200.0`. Vi vet ikke om FHI kan ha flere påvisninger enn testede i en uke (for eksempel hvis én person teller som påvisning for både A og B). En sperre i `Uke` ville da gjort at `fhi.tolk` feiler på ekte data. Sjekk dette mot FHI-dataene i story 2.4 før vi legger inn en sperre. Alvorlighet ukjent (ikke bekreftet).
  status: løst 2026-11-24 i story 2.4 — Irenes beslutning: ingen sperre. Andelen vises som den er (over 100 %), og uka er usikker med en fotnote (`Uke.flere_positive_enn_tester`, FR-10). R2 teller fortsatt bare færre enn 30 tester. Fixturen for 724 har ingen slike uker.

## Deferred from: code review of spec-2-4-tolke-fhi-svar-til-en-komplett-dataserie.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-2-4-tolke-fhi-svar-til-en-komplett-dataserie.md`
  summary: Tabellen og grafen (story 3.2 og 3.3) må vise en egen fotnote på enkel norsk for uker med `Uke.flere_positive_enn_tester`, i tillegg til markeringen som usikker uke (FR-10).
  evidence: Irenes beslutning 24.11.2026. Bare egenskapen finnes i `domene`. Teksten står som eksempel i PRD FR-10. En uke med 0 tester og positive over 0 har ingen andel (kan ikke dele på 0), men skal likevel ha fotnoten.
  status: oppdatert 2026-11-24 (story 2.7–2.8) — Irene har bestemt teksten: «Flere positive prøver enn tester denne uka. Det kan skyldes hvordan prøvene er registrert. Tolk tallet med forsiktighet.» Den står i PRD FR-10 og skal brukes ordrett. Fortsatt åpent: teksten finnes ikke i koden ennå.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-4-tolke-fhi-svar-til-en-komplett-dataserie.md`
  summary: Story 2.7 (R2) må ha en test som viser at en uke med flere positive enn tester og minst 30 tester ikke telles i R2.
  evidence: Irenes beslutning 24.11.2026 og FR-15. `Uke.usikker` er nå sann for slike uker, så R2 må telle `tester < 30` direkte og ikke bruke `usikker`. Ingen test håndhever det ennå.
  status: løst 2026-11-24 i story 2.7 — `test_r2_teller_ikke_flere_positive_enn_tester_med_minst_30_tester` og fixturen `724-r2-4-av-20-uker.json` (45 positive av 40 tester).

## Deferred from: code review of spec-2-5-hente-fra-fhi-med-tidsgrense.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-2-5-hente-fra-fhi-med-tidsgrense.md`
  summary: `tjeneste` (story 2.9) må ikke kalle `fhi.hent` for RSV og SARS-CoV-2 før epic 6, og bare for sesonger fra `fhi.sesonger(dimensjoner)` (eller reserven).
  evidence: `fhi.forespørsel` gir `ValueError` for tabell 729 og 731 og for en sesong uten publiserte uker (for eksempel uke 40 før FHI har publisert). `Utvalg.fra_parametre` godtar `rsv` og `sars-cov-2`, så en URL kan nå dit. `tjeneste` fanger bare `FhiUtilgjengelig`. Enten må `tjeneste` gi en norsk melding for virus som ikke er klare, eller `fra_parametre` må få listen over virus som kan velges.
  status: løst 2026-11-24 i story 2.9 — `tjeneste.svar` stopper tabeller som ikke finnes i `fhi.FASTE_FILTRE` med «Tall for RSV kan ikke vises i appen ennå. Velg influensa.», og en sesong uten publiserte uker med en egen melding, før `fhi.hent` (`test_rsv_og_sars_cov_2_gir_norsk_melding_uten_kall`, `test_sesong_uten_publiserte_uker_gir_melding_uten_datakall`).

## Deferred from: code review of spec-3-1-velge-mal-og-utvalg-pa-siden.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-3-1-velge-mal-og-utvalg-pa-siden.md`
  summary: Meldingen fra `Utvalg.fra_parametre` for ukjent virus nevner RSV og SARS-CoV-2, selv om skjemaet bare tilbyr influensa til epic 6.
  evidence: `fra_parametre` lister alle nøklene i `domene.VIRUS`. Velger brukeren RSV, svarer `tjeneste` «Velg influensa», så brukeren kommer ikke feil ut, men teksten er upresis. Løses av seg selv i epic 6, eller ved å gi `fra_parametre` listen over klare virus. Lav alvorlighet.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-1-velge-mal-og-utvalg-pa-siden.md`
  summary: Meldingen for ukjent mal bruker malens tittel («Andel positive tester uke for uke»), mens skjemaet viser malen som spørsmål (FR-1).
  evidence: `fra_parametre` bygger `Velg en mal: «{m.tittel}»`. Gjelder bare en manipulert URL. Kan vurderes når mal 2 kommer (epic 8). Lav alvorlighet.

## Deferred from: code review of spec-3-2-tabell-kildehenvisning-og-feilmelding.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-3-2-tabell-kildehenvisning-og-feilmelding.md`
  summary: Irene bør avgjøre om andelen for en uke med 0 tester skal vise «mangler» eller en annen tekst (for eksempel «kan ikke regnes ut»).
  evidence: `andel(None)` gir «mangler» både for skjulte tall og for 0 tester (FR-10: «ingen andel»). Ved siden av de kjente tallene «0» og «45» kan «mangler» leses som at FHI har skjult andelen. Ordvalg, lav alvorlighet. Kan tas med i brukertestingen (epic 5).
  status: løst 2026-11-24 i story 3.4 — Irenes beslutning: en uke med 0 tester viser «kan ikke regnes ut». «mangler» brukes bare for skjulte tall (`web.andelstekst`, PRD FR-11).

## Deferred from: code review of spec-3-3-graf-uke-for-uke.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-3-3-graf-uke-for-uke.md`
  summary: Ingen test kjører `app.js` i en nettleser, så åpen sirkel, brudd i linjen og fargene fra CSS sjekkes bare indirekte.
  evidence: Repoet har ingen JS- eller nettlesertester. Testene sjekker JSON-blokken, HTML-en, at fargene `app.js` leser finnes i `style.css`, og at nøklene finnes i `grafdata`. En røyktest med Playwright (for eksempel `Chart.getChart('graf').data.datasets[0].pointBackgroundColor` for R2-fixturen) passer i story 3.7. Medium, ikke bekreftet som feil.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-3-graf-uke-for-uke.md`
  summary: Irene bør bekrefte at uker med skjult antall tester eller 0 tester gir brudd i linjen i grafen (ingen åpen sirkel), og bare markeres som usikre i tabellen.
  evidence: Slike uker har ingen andel, så det finnes ikke noe punkt å tegne (FR-9: manglende uker gir brudd). FR-10 sier at de er usikre «i grafen og tabellen». Forklaringen under grafen og alternativteksten sier nå at uker uten andel gir brudd i linjen. Lav: skjulte verdier er ikke sett i ekte data.
  status: løst 2026-11-24 i story 3.4 — Irenes beslutning: brudd i linjen for uker uten andel er godkjent, og forklaringen av fylt og åpen sirkel vises alltid (PRD FR-9 og FR-10).

## Deferred from: code review of spec-3-4-varsel-om-tynt-datagrunnlag.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-3-4-varsel-om-tynt-datagrunnlag.md`
  summary: Varselet mangler lenken til begrepsforklaringen for «for tynt datagrunnlag» (FR-19, fjerde punkt). Den skal legges til i story 3.6.
  evidence: Begrepsforklaringene finnes ikke før 3.5 og 3.6 (epic-3-context, avhengigheter). Malen for varselet i `index.html` har ingen lenke ennå. Story 3.6 må legge til lenken og en test for den.
  status: løst 2026-11-24 i story 3.6 — varselet har lenken «Hva betyr dette?» til `#begrep-tynt-datagrunnlag`, og `app.js` åpner forklaringen. Testet i `test_varselet_lenker_til_forklaringen_av_tynt_datagrunnlag`.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-4-varsel-om-tynt-datagrunnlag.md`
  summary: Irene bør vurdere om overskriften «For tynt datagrunnlag» passer når bare R5 slår inn (perioden går over 1. mars 2025). R5 handler om sammenlignbarhet, ikke om for få tall.
  evidence: Overskriften følger PRD-ens skisse (§6.0) og begrepet «Varsel om tynt datagrunnlag» (PRD kapittel 3), som gjelder alle fem reglene. Alle utvalg i 2024/2025 får varselet bare på grunn av R5. Ordvalg, lav alvorlighet. Passer å ta med i brukertestingen (epic 5).
  status: løst 2026-11-24 i story 3.7 — Irenes beslutning: overskriften beholdes som «For tynt datagrunnlag».

## Deferred from: code review of spec-4-3-ki-forklaring-med-tre-utfall.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-4-3-ki-forklaring-med-tre-utfall.md`
  summary: Ingen test sammenligner den ferdige HTML-tabellen med `formatering.ukelinje`.
  evidence: I dag sikres likheten ved at Jinja2-filtrene er de samme funksjonene (`test_tabellen_bruker_de_samme_funksjonene_som_prompten`). Får tabellen egne tekster i `index.html`, bør testen sammenligne den ferdige tabellen.

## Deferred from: code review of spec-4-4-mellomlagre-ki-forklaringen.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-4-4-mellomlagre-ki-forklaringen.md`
  summary: Nøkkelen for KI-forklaringen tar ikke med effort, max_tokens eller formateringen av ukene, så endringer i ki.py gir ikke ny forklaring.
  evidence: ki.nøkkel hasher bare promptfila, tallene og modellen (AD-7). En versjonskonstant i nøkkelen, eller hashing av den ferdige prompten uten hentetidspunktet, ville løst det. Inntil da må .cache/ki/ slettes etter slike endringer.
  status: løst 2026-11-24 før merge av PR #67 — Irenes beslutning: `ki.UKEFORMAT` er med i nøkkelen, så en endring i ukeformatet gir ny forklaring når tallet økes. `.cache/ki/` trenger ikke slettes for hånd.
- source_spec: `_bmad-output/implementation-artifacts/spec-4-4-mellomlagre-ki-forklaringen.md`
  summary: Prompten har «Hentet <tidspunkt>», men nøkkelen har det ikke, så en gjenbrukt forklaring kan sitere et eldre hentetidspunkt.
  evidence: kildetekst(kilde) i lag_prompt har tidspunktet, og ki.nøkkel utelater det med vilje (AD-7). Det må Irene bestemme: ta tidspunktet ut av prompten, eller be KI-en ikke nevne det.
  status: løst 2026-11-24 før merge av PR #67 — Irenes beslutning: prompten sier «Ikke nevn når tallene ble hentet. Det står ved siden av forklaringen.»

## Deferred from: code review of spec-4-5-forklaringen-pa-siden.md (2026-11-24)

- source_spec: `_bmad-output/implementation-artifacts/spec-4-5-forklaringen-pa-siden.md`
  summary: Ingen automatisk test viser at app.js setter inn fragmentet fra /forklaring, eller at feilteksten vises ved 400 og nettverksfeil.
  evidence: test_app_js_henter_fragmentet_og_bruker_feilteksten leser bare kildeteksten. Prosjektet har ingen nettlesertest (samme hull som grafen, story 3.7). Sjekkes for hånd med scripts/vis_forklaring.py.

## Deferred from: code review of spec-4-6-hente-nyeste-tall-na.md (2026-11-25)

- source_spec: `_bmad-output/implementation-artifacts/spec-4-6-hente-nyeste-tall-na.md`
  summary: POST /hent-nyeste har ingen grense for hvor ofte FHI kan kalles, og ingen sjekk av opprinnelse (CSRF).
  evidence: tving hopper over cachen og PAUSE_ETTER_FEIL, og _én_gang slår bare sammen samtidige kall. Det gjelder først når appen er offentlig (story 8.3, Vercel). En minste avstand mellom tvungne hentinger per utvalg ville løst det.
- source_spec: `_bmad-output/implementation-artifacts/spec-4-6-hente-nyeste-tall-na.md`
  summary: På Vercel kan GET / etter 303 treffe en annen instans enn POST, med en annen /tmp-cache.
  evidence: Mellomlageret er /tmp/fhi-helsedata-cache per instans. Den nye hentingen kan være lagret på én instans mens neste side vises fra en annen. Sjekkes i story 8.3.
