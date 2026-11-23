# Story 1.2: ruff og pytest uten nett

## 2026-11-23 kl. 21:01 — Irene Zumbo

### Oppgave
Bygge story 1.2 (issue #2) med `bmad-build`, med små commits på branch `story-1.2` fra main. Kjøre pytest og ruff og vise at sperren mot nettkall faktisk stopper et kall. Kjøre `bmad-code-review` og rette funnene eller begrunne avvisning. Sette story 1.2 til `done` i sprint-status i samme PR, pushe til `ibe` (også loggcommitene) og lage en PR med «Closes #2». Ikke merge.

### Plan
- `bmad-build`: epic-1-konteksten var gyldig og ble gjenbrukt. Spec: [spec-1-2-ruff-og-pytest-uten-nett](../../_bmad-output/implementation-artifacts/spec-1-2-ruff-og-pytest-uten-nett.md). Akseptansekriteriene var klare, ingen åpne spørsmål, oneshot-ruten (som 1.1).
- Avhengigheter med `uv add --dev`, så oppsettet i `pyproject.toml`, test for sperren, fixture-mapper og README, med én commit per del.
- `bmad-code-review` med fire lag (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor) i stedet for oneshot-stegets egen gjennomgang. Funnene ble sortert, rettet og committet, så pushet til `ibe` og PR laget.

### Resultat
- PR: https://github.com/IBE160-2026/G63-zumbo/pull/43 («Closes #2»), ikke merget. Branchen inneholder også loggcommiten b9b0394 fra story 1.4, som lå upushet på main.
- Commits: 17a7357 (spec, sprint-status `in-progress`), d813650 (pytest-socket 0.8.1, respx 0.23.1, ruff 0.17.6 som dev-avhengigheter, `uv.lock`), 9ad6121 (`[tool.pytest.ini_options]` med `testpaths` og `addopts = ["--disable-socket"]`, ruff `py313`/88 med `I`, `UP`, `B`, `PLW1510`), b94872f (`backend/tests/test_nettsperre.py`), dbc8a44 (`backend/tests/fixtures/{fhi,ki,konstruert}/.gitkeep` og `test_fixturemapper.py`), a913e07 (README), e0a1966, d9c7543 og 519f4b0 (rettelser etter gjennomgangen), a6fc5dc (triage, utsatt arbeid, sprint-status `done`).
- `uv run pytest`: 12 passed. `ruff check` og `ruff format --check` består. `uv lock --check` er OK.
- Sperren virker:
  - Et ukontrollert `httpx.get` mot FHI i en midlertidig test feilet med `SocketBlockedError: A test tried to use socket.getaddrinfo`. pytest-socket 0.8.1 stopper altså allerede navneoppslaget.
  - Med sperren slått av (`-p no:socket -o addopts=""`) feilet begge sperretestene (`DID NOT RAISE SocketBlockedError` / `ConnectError`), så testene beviser sperren.
  - Asynkron httpx blir også stoppet, og `respx` virker med sperren på (egen test).
- Sprint-status: `1-2-ruff-og-pytest-uten-nett: done`.

### Feil i den KI-genererte koden
Fant Claude selv, eller kodegjennomgangen, i koden Claude skrev:

1. **Feil kommentar (før commit):** Den første versjonen av httpx-testen påsto at pytest-socket ikke stopper DNS-oppslag, og brukte en IP-adresse av den grunn. Testkjøringen viste at `getaddrinfo` også blir stoppet.
2. **Sperretesten brukte den ekte FHI-verten (low):** Hvis sperren manglet, ville testen sendt en forespørsel til FHI før den feilet. Det skjedde faktisk under kontrollen med sperren slått av. Byttet til `statistikk-data.fhi.invalid`.
3. **README lovet for mye (low):** Den sa at testene «bruker lagrede svar» (mappene er tomme til 1.3) og at «ingen test kan» kalle FHI (en test kan melde seg ut med `enable_socket`). Omformulert.
4. **respx med sperren var ikke vist (low):** Lagt til test.
5. **Småting (low):** `PLW1510` var uforklart, og README sa ikke at ruff skal bestå før commit (AD-10).

Avvist: asynkron httpx slipper gjennom (false, sjekket), fixture-testen fanger ikke en manglende `.gitkeep` (false, en fersk klon feiler), `enable_socket` kan omgå sperren (bevisst utmelding) og `pytest` fra reporoten (README sier `cd backend`). Full triage står i specen.

### Åpne punkter
- FastAPIs `TestClient` feiler med `SocketBlockedError` under `--disable-socket` (asyncio sin self-pipe). Den første storyen med app-tester (epic 3) må legge til `--allow-unix-socket` i `addopts`. Sjekket: TCP og DNS er fortsatt stoppet med flagget.
- Ingen CI eller pre-commit kjører ruff og pytest automatisk. Står i deferred-work.md.

## 2026-11-23 kl. 21:58 — Irene Zumbo

### Oppgave
Merge PR #43 med `gh pr merge 43 --merge --delete-branch` og hente main.

### Plan
- Merget PR-en, byttet til main, hentet med `git pull --ff-only ibe main` og slettet den lokale branchen.

### Resultat
- PR #43 er merget (merge-commit 0a3bb08), og issue #2 er lukket. Branchen `story-1.2` er slettet både på `ibe` og lokalt.
- Lokal main er lik `ibe/main`. På main: `uv run pytest` 12 passed, og `ruff check` og `ruff format --check` består.

### Åpne punkter
Ingen nye. Punktene om `--allow-unix-socket` for TestClient og om CI/pre-commit står fortsatt åpne i `issues.md`.

## 2026-11-23 kl. 22:02 — Irene Zumbo

### Oppgave
«Før merge av PR #43»: legge `--allow-unix-socket` i `addopts` med en kommentar om FastAPIs testklient, legge til en test som viser at en lokal socketpair er tillatt, merke punktet om flagget som løst i deferred-work.md og skrive at CI vurderes i epic 7. Én commit på `story-1.2` og push til `ibe` sammen med loggcommiten. Ikke merge.

### Plan
- PR #43 var allerede merget og branchen slettet (forrige seksjon). `story-1.2` ble derfor laget på nytt fra main. Main hadde også den upushede loggcommiten bd0a9f3.
- Endringen ble lagt på den nye branchen, etterfulgt av en loggcommit. Ingen ny PR ble laget, siden brukeren ikke ba om det.

### Resultat
- Commit 6ec12ac:
  - `backend/pyproject.toml`: `addopts = ["--disable-socket", "--allow-unix-socket"]`, med en kommentar om testklienten.
  - `backend/tests/test_nettsperre.py`: ny test `test_lokal_socketpair_er_tillatt`.
  - deferred-work.md: punktet om flagget er merket løst, og CI-punktet sier «vurderes i epic 7 hvis det blir tid».
- `uv run pytest`: 13 passed. `ruff check` og `ruff format --check` består.
- Kontroller:
  - Med bare `--disable-socket` feiler den nye testen, mens de tre andre sperretestene består (TCP og DNS er fortsatt stoppet).
  - En midlertidig `TestClient(app).get("/")` består nå. Den feilet før med `SocketBlockedError`.
- `issues.md`: punktet om `--allow-unix-socket` er lukket, og CI-punktet er oppdatert.

### Åpne punkter
- Endringen er ikke i main, fordi PR #43 allerede var merget. Branchen `story-1.2` trenger en ny PR (laget som PR #44, se neste seksjon).

## 2026-11-23 kl. 22:06 — Irene Zumbo

### Oppgave
Lage en PR fra `story-1.2` til main med tittelen «Story 1.2 (oppfølging): tillat lokale sockets for FastAPIs testklient». Beskrivelsen skal ha «Refs #2» (ikke Closes), forklare at endringen kom etter at PR #43 var merget, og si at det ikke er kjørt full `bmad-code-review`, men at kontrollene er gjort. Ikke merge.

### Plan
- `gh pr create` med beskrivelsen fra en fil i scratchpad.

### Resultat
- PR: https://github.com/IBE160-2026/G63-zumbo/pull/44, ikke merget. Den inneholder bd0a9f3, 6ec12ac og b971ebc.
- Beskrivelsen har bakgrunn, endringer, kontroller (13 passed, ruff OK, den nye testen feiler uten flagget, TestClient består) og hvorfor det ikke er kjørt full kodegjennomgang.

### Åpne punkter
Ingen nye.

## 2026-11-23 kl. 22:08 — Irene Zumbo

### Oppgave
Merge PR #44 med `gh pr merge 44 --merge --delete-branch` og hente main.

### Plan
- Merget PR-en, byttet til main og hentet med `git pull --ff-only ibe main`.
- Den upushede loggcommiten fra forrige seksjon lå bare på den lokale `story-1.2`. Den ble flyttet til main med cherry-pick før branchen ble slettet.

### Resultat
- PR #44 er merget (merge-commit d1c15aa). Branchen `story-1.2` er slettet på `ibe` og lokalt.
- På main: `addopts = ["--disable-socket", "--allow-unix-socket"]`, `uv run pytest` 13 passed, og `ruff check` og `ruff format --check` består.

### Åpne punkter
Ingen nye. CI-punktet (vurderes i epic 7) står fortsatt åpent i `issues.md`.
