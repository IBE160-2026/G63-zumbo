---
title: 'Story 1.2: ruff og pytest uten nett'
type: 'chore'
created: '2026-11-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Testene kan i dag nå nettet, så en test kan ved et uhell kalle FHI eller Claude (NFR-10). ruff er ikke en del av prosjektet, og fixture-mappene fra AD-10 finnes ikke (issue #2).

**Approach:** Legg inn pytest 9.2.0, pytest-socket 0.8.1, respx 0.23.1 og ruff 0.17.6 som utviklingsavhengigheter (`>=`). Sett `--disable-socket` som standard i `[tool.pytest.ini_options]` og konfigurer ruff i `backend/pyproject.toml`. Skriv en test som prøver å åpne en socket og forventer `SocketBlockedError`. Lag `tests/fixtures/fhi/`, `tests/fixtures/ki/` og `tests/fixtures/konstruert/`. `ruff check` og `ruff format --check` skal bestå.

</frozen-after-approval>

## Implementation Notes

- `tests/` er `backend/tests/` (arkitektur §6: Python-prosjektet ligger i `backend/`). Fixture-mappene blir `backend/tests/fixtures/{fhi,ki,konstruert}/`. Git sporer ikke tomme mapper, så hver får en `.gitkeep`.
- Ruff-reglene velger jeg selv, siden brukeren ikke merker valget: standardreglene pluss `I` (import-rekkefølge), `UP` (moderne Python), `B` (bugbear) og `PLW1510`, som fanget en feil i 1.1. `target-version = "py313"`, linjelengde 88.
- `testpaths = ["tests"]`, slik at `uv run pytest` fra `backend/` bare samler testene.
- `--disable-socket` uten `--allow-unix-socket`, ordrett etter AC-en. Hvis FastAPIs TestClient trenger unix-sockets (asyncio sin self-pipe), må det tas i storyen som innfører app-testene.
- `uv add --dev` la inn pytest-socket 0.8.1, respx 0.23.1 og ruff 0.17.6. pytest sto allerede med `>=9.2.0`.
- Overraskelse: pytest-socket 0.8.1 stopper også `socket.getaddrinfo`, så ikke engang navneoppslaget går ut. Den første kommentaren i testen påsto det motsatte og ble rettet før commit.
- pytest-socket gir en `UserWarning` hver gang en socket blir stoppet. I `test_nettsperre.py` filtreres den bort med `pytestmark`, siden testene utløser den med vilje.
- Kontroll: et ukontrollert `httpx.get` mot FHI i en test feilet med `SocketBlockedError`. Med `-p no:socket -o addopts=""` feiler begge sperretestene (`DID NOT RAISE` / `ConnectError`).
- TestClient-sjekken bekreftet mistanken om unix-sockets. Ført i deferred-work.md.
- Som i 1.1 ble oneshot-stegets Blind Hunter erstattet av en full `bmad-code-review` med fire lag.

## Review Triage Log

Diff: `git diff main...HEAD` uten `backend/uv.lock` og `_bmad-output/`. Lag: Blind Hunter (BH), Edge Case Hunter (ECH), Verification Gap (VG), Acceptance Auditor (AA). AA fant ingen brudd på akseptansekriteriene.

### Review Findings

- [x] [Review][Patch] README sa at testene «bruker lagrede svar» fra `tests/fixtures/`, men mappene har bare `.gitkeep` [README.md] — low (AA+ECH+BH). Omformulert: svarene skal ligge der, det første kommer i 1.3 (519f4b0).
- [x] [Review][Patch] README lovet at «ingen test kan kalle FHI eller Claude», men en test kan melde seg ut med `@pytest.mark.enable_socket` [README.md] — low (ECH). Endret til «ved et uhell», som er det sperren faktisk sikrer (519f4b0).
- [x] [Review][Patch] Sperretesten for httpx brukte den ekte FHI-verten, så et brudd på sperren ville sendt en forespørsel til FHI før testen feilet [backend/tests/test_nettsperre.py] — low (ECH+BH). Byttet til `statistikk-data.fhi.invalid` (RFC 2606). Uten sperren feiler testen nå med `ConnectError`, uten trafikk (e0a1966).
- [x] [Review][Patch] Ingen test viste at respx virker med sperren på, selv om det er slik FHI skal mockes (AD-10) [backend/tests/test_nettsperre.py] — low (BH). Lagt til `test_respx_virker_med_sperren_på` (e0a1966).
- [x] [Review][Patch] `PLW1510` sto uforklart blant regelfamiliene [backend/pyproject.toml] — low (BH). Lagt til en kommentar (d9c7543).
- [x] [Review][Patch] README sa ikke at ruff skal bestå før commit (AD-10) [README.md] — low (BH). Lagt til (519f4b0).
- [x] [Review][Defer] Ingenting kjører ruff automatisk, så `uv run pytest` er grønn selv om ruff feiler [backend/pyproject.toml] — medium (VG+AA+BH). Ingen CI eller pre-commit finnes ennå. Ført i deferred-work.md.
- [x] [Review][Defer] Risikoen for unix-sockets med TestClient står bare i specen [backend/pyproject.toml] — medium (BH). Bekreftet med en midlertidig test (se Implementation Notes). Ført i deferred-work.md og issues.md.

**Avvist:**
- false (ECH): asynkron httpx (`AsyncClient`) kan slippe gjennom sperren — en midlertidig test med `asyncio.run` og `AsyncClient().get` fikk `SocketBlockedError`. Sperren ligger på `socket.socket` og `getaddrinfo`, som også den asynkrone veien bruker.
- false (BH): fixture-testen fanger ikke en `.gitkeep` som mangler — i en fersk klon finnes mappen ikke, og `is_dir()` feiler. Forslaget (`.gitkeep` er en fil) består lokalt på samme måte, så det hjelper ikke.
- low (ECH): `@pytest.mark.enable_socket` eller `--force-enable-socket` kan slå av sperren — det er en bevisst utmelding, ikke et uhell. En conftest-vakt ville gitt mer kompleksitet for en sjelden situasjon. README er presisert i stedet.
- low (ECH): bare `pytest` fra reporoten finner ikke oppsettet — README sier `cd backend`, og VG viste at `uv run --project backend pytest backend/tests` finner det. Reporoten har ikke noe uv-prosjekt, så `uv run pytest` der feiler med en gang.
