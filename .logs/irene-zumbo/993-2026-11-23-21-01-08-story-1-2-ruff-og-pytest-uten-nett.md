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
