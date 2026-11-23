---
title: 'Story 1.5: Enkel README'
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

**Problem:** En medstudent som kloner repoet skal kunne installere, starte og teste appen uten å spørre (issue #5). README i reporoten har kommandoene, men ingen plass for oppstartskommandoen (AD-11), og ingen test sjekker at installering og testkjøring står der.

**Approach:** Skriv README i reporoten slik at den beskriver installering med `uv sync`, testkjøring med `uv run pytest` og ruff-kommandoene (AD-10). Den skal si at `.env` er valgfri og at appen virker uten KI-nøkkel (NFR-1, NFR-9), og ha en plass for oppstartskommandoen som fylles ut i story 3.1. En automatisk test sjekker at README nevner `uv sync` og `uv run pytest`.

</frozen-after-approval>

## Implementation Notes

- README hadde allerede «Kom i gang» med `uv sync`, `uv run pytest`, ruff og `.env`-avsnittet fra story 1.1–1.3. Den mangler en plass for oppstarten, og stegene står i én blokk uten forklaring.
- Ny inndeling: «Installere», «Kjøre testene og ruff», «Starte appen» (plassen for story 3.1), «KI-nøkkel er valgfri». Den planlagte kommandoen (`uv run uvicorn backend.web:app --reload`) skrives ikke inn ennå, siden `backend.web` ikke finnes og kommandoen ville feilet. Plassen sier at den kommer i story 3.1.
- Testen ligger i `backend/tests/test_readme.py` og finner README via git-roten, som `test_gitignore.py` gjør.
- `backend/README.md` er tom, men `pyproject.toml` peker på den (`readme = "README.md"`). Den får én linje som viser til README i reporoten.
- Epic-konteksten ble bygget på nytt: `architecture.md` fikk nyere tidsstempel da PR #45 ble merget.
