# Forsidenavn, CI og brukertest-manus

## 2026-11-25 kl. 23:44 — Irene Zumbo

### Oppgave
Tre ting: (1) gi SARS-CoV-2-kortet på forsiden navnet «Koronavirus (SARS-CoV-2)», kommentere og merge PR #73; (2) sette opp GitHub Actions som kjører pytest og ruff på hver PR, og merge bare hvis sjekken er grønn; (3) skrive et utkast til manus for brukertestingen i story 5.1, uten å merge.

### Plan
- Kortnavnet i `web.py` (egen tabell `KORTNAVN`), så resten av appen beholder «SARS-CoV-2».
- Kjøre pytest og ruff, pushe, kommentere ordrett på PR #73, merge med `--merge --delete-branch`.
- Issue for CI, workflow på egen branch, PR med «Closes», vente på sjekken.
- Manus i `docs/brukertest-manus.md` på egen branch, PR med «Refs #28».

### Resultat
- **Del 1:** `KORTNAVN` i `backend/src/backend/web.py` og test i `test_web_forside.py` som leser kortoverskriftene (commit 0753545). 905 tester bestod, ruff check og format bestod. Kommentaren står på PR #73, og PR-en er merget til main (b9cf000). Ingen PR-er var stablet på story-3.8.
- **Del 2:** Issue #74 opprettet. Branch `ci-pytest-ruff` med `.github/workflows/tester.yml` (`uv sync --locked`, `pytest`, `ruff check`, `ruff format --check` i `backend/`, på PR og push til main), og oppdatert punkt i `deferred-work.md`, `issues.md` og README. PR #75. **Sjekken ble rød** etter 3 sekunder, før testene startet: `Unable to resolve action astral-sh/setup-uv@v10, unable to find version v10`. Stoppet som avtalt, ikke rettet og ikke merget. CI-punktet i issues.md på main står derfor fortsatt åpent.
- **Del 3:** `docs/brukertest-manus.md` på branch `brukertest-manus`, PR #76 (Refs #28), ikke merget. Manuset har introduksjon, fem oppgaver (influensa uten varsel, influensa 2024/2025 med varsel, RSV 0–4 år, «andel positive», kilde), notater per oppgave, tre spørsmål til slutt, notatark og resultattabell for SM-5, SM-6 og NFR-3. Fasiten står med «…» og skal fylles inn før testen.
- Lukket to punkter fra story 3.8 i issues.md (Tab-sjekken og navnet «koronavirus»).

### Åpne punkter
- CI-sjekken i PR #75 er rød fordi `astral-sh/setup-uv@v10` ikke fins (siste er `v10.4.0`). Irene avgjør rettingen.
- Irene retter manuset i PR #76 og skriver fasit før første testperson.
