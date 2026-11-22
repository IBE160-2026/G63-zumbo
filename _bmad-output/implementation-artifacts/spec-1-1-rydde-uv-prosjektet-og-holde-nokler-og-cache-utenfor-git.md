---
title: 'Story 1.1: Rydde uv-prosjektet og holde nøkler og cache utenfor git'
type: 'chore'
created: '2026-11-22'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `backend/pyproject.toml` har SQLAlchemy, som arkitekturen ikke bruker, og mangler avhengighetene appen skal bygge på. Reporoten har verken `.cache/` i `.gitignore` eller `.env.example`, så det er lett å sjekke inn cachefiler, og det finnes ingen mal for nøklene (issue #1).

**Approach:** Fjern SQLAlchemy og legg inn FastAPI 0.165.0, Uvicorn 0.54.0, Jinja2 3.1.6, python-multipart 0.0.34, httpx 0.28.1, anthropic 2.11.0, python-dotenv 1.2.4 og tzdata 2026.6 med `>=` som minimum. Kjør `uv lock`/`uv sync`. Legg `.cache/` i `.gitignore` i reporoten og lag `.env.example` med `ANTHROPIC_API_KEY=` og `ANTHROPIC_MODEL=`. Skriv en pytest-test som kjører `git check-ignore` og sjekker at `.env` og `.cache/x.json` er ignorert, og at `.env.example` ikke er det. Oppdater README med `.env.example`.

</frozen-after-approval>

## Implementation Notes

- Utenfor scope (story 1.2): ruff som dev-avhengighet, ruff-oppsett, pytest-socket og respx. I denne storyen kjøres ruff med `uvx ruff@0.17.6`, uten å legge det til i prosjektet.
- pytest finnes allerede som dev-avhengighet. Minimum heves til 9.2.0 i tråd med arkitekturen.
- Testen ligger i `backend/tests/test_gitignore.py`. Den finner reporoten med `git rev-parse --show-toplevel` og bruker `git check-ignore --no-index -q`, slik at det er reglene som testes og ikke om fila er sporet. Returkode 0 = ignorert, 1 = ikke ignorert.
- `[project.scripts]` og `main()` i `__init__.py` blir stående. Det er ikke i akseptansekriteriene, og senere stories (web.py) bestemmer oppstarten.
