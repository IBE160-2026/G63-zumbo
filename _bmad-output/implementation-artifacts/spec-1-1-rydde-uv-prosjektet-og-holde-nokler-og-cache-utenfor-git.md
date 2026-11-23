---
title: 'Story 1.1: Rydde uv-prosjektet og holde nøkler og cache utenfor git'
type: 'chore'
created: '2026-11-22'
status: 'done'
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
- Ruff ble kjørt med `uvx ruff@0.17.6` og fant PLW1510 (`subprocess.run` uten `check`) i den første versjonen av testen. Rettet før commit.
- Oneshot-stegets egen Blind Hunter ble erstattet av en full `bmad-code-review` (fire lag) etter ønske fra brukeren.

## Review Triage Log

Diff: `git diff main...HEAD` uten `backend/uv.lock` og `_bmad-output/`. Lag: Blind Hunter (BH), Edge Case Hunter (ECH), Verification Gap (VG), Acceptance Auditor (AA). VG fant ingen hull i verifiseringen.

### Review Findings

- [x] [Review][Patch] README sa at KI-forklaringen «trenger en nøkkel», ikke at `.env` er valgfri, og nevnte ikke `ANTHROPIC_MODEL` [README.md] — medium (VG+AA+BH). Strider mot NFR-1 og mot epic-konteksten («README skal si at `.env` er valgfri»). Rettet i 334c011.
- [x] [Review][Patch] Standardmodellen sto i kommentaren i `.env.example`, i tillegg til i arkitekturen (og senere i `config`) [.env.example:4] — low (AA+BH). To kilder for samme verdi blir fort ulike. Rettet ved å fjerne navnet (334c011).
- [x] [Review][Patch] Testen hoppet stille over seg selv uten git, så akseptansekriteriet ble ikke sjekket [backend/tests/test_gitignore.py] — low (AA+ECH+BH). `skipif` er fjernet. Uten git eller repo feiler testen nå med en tydelig melding, og reporoten finnes én gang i en fixture (860f8df).
- [x] [Review][Patch] `--no-index` sjekker bare reglene, ikke om `.env` eller `.cache` allerede er sjekket inn. Mønsteret `.env.*` var heller ikke dekket [backend/tests/test_gitignore.py] — low (BH). Lagt til en sjekk med `git ls-files` og parameteren `.env.local` (860f8df).
- [x] [Review][Patch] Plassholderen «Add your description here» fra `uv init` sto fortsatt [backend/pyproject.toml:4] — low (BH). Rettet i 94ec040.
- [x] [Review][Defer] `ANTHROPIC_MODEL=` kopiert uendret til `.env` gir tom streng via python-dotenv (`override=True`). Da overstyrer `os.environ.get(..., standard)` standardmodellen med `""` [.env.example] — medium (ECH+BH). Linja må stå tom etter AC-en. Kravet gjelder `config.les_innstillinger()`, som ikke finnes ennå. Ført i deferred-work.md.

**Avvist:**
- false (BH): «`uv.lock` mangler i diffen» — fila ble holdt utenfor diffen med vilje. AA kjørte `uv lock --check` og `uv sync` uten feil, og lockfila inneholder ikke sqlalchemy.
- false (ECH): BOM eller mellomrom i `.env.example` — fila er vår egen og har ingen av delene. En manglende fil gir en tydelig FileNotFoundError, som er ønsket.
- false (BH): ø i testnavn bryter ruff (PLC2401) — `ruff check` består med 0.17.6. Arkitekturen krever norske navn.
- low (BH): `_reporot()` kjøres flere ganger — løst som en bieffekt av fixture-rettelsen.
- low (BH): stderr fra `_reporot()` forsvant — løst som en bieffekt av samme rettelse (`assert` med stderr).
