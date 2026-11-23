---
title: 'Story 1.5: Enkel README'
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

**Problem:** En medstudent som kloner repoet skal kunne installere, starte og teste appen uten å spørre (issue #5). README i reporoten har kommandoene, men ingen plass for oppstartskommandoen (AD-11), og ingen test sjekker at installering og testkjøring står der.

**Approach:** Skriv README i reporoten slik at den beskriver installering med `uv sync`, testkjøring med `uv run pytest` og ruff-kommandoene (AD-10). Den skal si at `.env` er valgfri og at appen virker uten KI-nøkkel (NFR-1, NFR-9), og ha en plass for oppstartskommandoen som fylles ut i story 3.1. En automatisk test sjekker at README nevner `uv sync` og `uv run pytest`.

</frozen-after-approval>

## Implementation Notes

- README hadde allerede «Kom i gang» med `uv sync`, `uv run pytest`, ruff og `.env`-avsnittet fra story 1.1–1.3. Den mangler en plass for oppstarten, og stegene står i én blokk uten forklaring.
- Ny inndeling: «Installere», «Kjøre testene og ruff», «Starte appen» (plassen for story 3.1), «KI-nøkkel er valgfri». Den planlagte kommandoen (`uv run uvicorn backend.web:app --reload`) skrives ikke inn ennå, siden `backend.web` ikke finnes og kommandoen ville feilet. Plassen sier at den kommer i story 3.1.
- Testen ligger i `backend/tests/test_readme.py` og finner README via git-roten, som `test_gitignore.py` gjør.
- `backend/README.md` er tom, men `pyproject.toml` peker på den (`readme = "README.md"`). Den får én linje som viser til README i reporoten.
- Epic-konteksten ble bygget på nytt: `architecture.md` fikk nyere tidsstempel da PR #45 ble merget.
- Etter gjennomgangen finner testen README med `Path(__file__).resolve().parents[2]` i stedet for git-roten, så den virker også uten en git-klone.

## Review Triage Log

Diff: `git diff main...HEAD` uten `backend/uv.lock` og `_bmad-output/`. Lag: Blind Hunter (BH), Edge Case Hunter (ECH), Verification Gap (VG), Acceptance Auditor (AA). VG fant ingen mangler. AA fant ingen brudd på akseptansekriteriene. Ingen funn var alvorlige eller krevde endring i PRD-en eller arkitekturen.

### Review Findings

- [x] [Review][Patch] «Alle kommandoene kjøres fra `backend/`» stemte ikke med `.env`-steget, som skjer i reporoten. Kommandoen for å kopiere sto heller ikke der [README.md] — low (BH+ECH+AA). Nå står det at uv-kommandoene kjøres fra `backend/`, og `cp .env.example .env` står med «Fra reporoten» (ed82252).
- [x] [Review][Patch] Installeringen startet med `cd backend`, uten `git clone` [README.md] — low (BH). Klone-steget er lagt til, og at git og uv må være installert (ed82252).
- [x] [Review][Patch] «Appen virker uten KI-nøkkel. Da virker alt unntatt KI-forklaringen.» leses som at to setninger sier imot hverandre [README.md] — low (BH). Slått sammen til én setning (ed82252).
- [x] [Review][Patch] Listen over utviklingsverktøy manglet pytest-socket og respx [README.md] — low (BH). Lagt til (ed82252).
- [x] [Review][Patch] Testen for `.env` sjekket en generell frase (`"uten KI-nøkkel"`), som skiller mellom store og små bokstaver og ville passet på andre setninger [backend/tests/test_readme.py] — low (BH+ECH+AA). Testen sjekker nå selve påstanden «appen virker uten KI-nøkkel», uten å skille mellom store og små bokstaver (d1fd08f).
- [x] [Review][Patch] Testen for oppstarten sjekket bare overskriften, ikke at plassen venter på story 3.1 [backend/tests/test_readme.py] — low (BH+AA). Den sjekker nå at seksjonen nevner story 3.1, så story 3.1 må endre testen med vilje (d1fd08f).
- [x] [Review][Patch] Testen fant README med `git rev-parse` og feilet uten en git-klone, selv om README er en vanlig fil [backend/tests/test_readme.py] — low (VG+ECH+BH+AA). Bruker nå `Path(__file__).resolve().parents[2]` (d1fd08f).
- [x] [Review][Defer] README og AD-10 sier at testene aldri laster `.env`, men ingen test håndhever det [README.md] — low (VG+BH+AA). Det stemmer i dag, fordi ingen kode laster `.env`. Når `config.py` eller `web` begynner å bruke python-dotenv, trengs en test. Ført i deferred-work.md.

**Avvist:**
- low (BH): legg README-oppslaget i en felles `conftest.py`-fixture sammen med `test_gitignore.py`. Etter rettingen trenger README-testen ikke git, så de to oppslagene gjør ikke lenger det samme.
- low (BH): «3.13» står både i README, `.python-version` og `requires-python`. En leser trenger å vite versjonen, og en test for dette ville gitt mer kode enn nytte.
- low (BH): kodeblokkene er innrykket, ikke inngjerdet med ```sh. Det er stilen ellers i README-en, og den vises riktig på GitHub.
- false (ECH): den relative lenken i `backend/README.md` blir brutt i pakkemetadata. Pakken publiseres ikke (den kjøres bare lokalt eller på Vercel, AD-11), så ingen ser metadataene.
