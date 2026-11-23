---
title: 'Story 1.2: ruff og pytest uten nett'
type: 'chore'
created: '2026-11-23'
status: 'in-progress'
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
