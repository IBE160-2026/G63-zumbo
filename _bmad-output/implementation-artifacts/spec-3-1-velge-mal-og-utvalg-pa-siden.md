---
title: 'Story 3.1: Velge mal og utvalg på siden'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen har ingen nettside ennå, så Sara kan ikke velge mal, virus, sesong og aldersgruppe uten å kjenne FHIs tabeller (issue #15, FR-1–FR-5). README sier fortsatt at oppstartskommandoen kommer i story 3.1 (åpent punkt fra 1.5).

**Approach:** Ny modul `web.py` med FastAPI-appen og `GET /`, Jinja2-malene `base.html` og `index.html` og en tom `static/`. Uten parametre vises bare skjemaet. Ugyldige parametre gir meldingen fra `Utvalg.fra_parametre` og ingen henting. `config.les_innstillinger()` kalles én gang ved oppstart. README får oppstartskommandoen, og `test_readme_har_plass_for_oppstart` endres. Tester med FastAPIs testklient.

</frozen-after-approval>

## Implementation Notes

- **App:** `web.lag_app(les_innstillinger=config.les_innstillinger, klient=None)` lager appen. `app = lag_app()` på modulnivå. Innstillingene leses i `lifespan` ved oppstart (ikke ved import, så testene aldri laster `.env`), og `Tjeneste` lages én gang og legges i `app.state`. Testene lager appen med egne innstillinger (`CACHE_DIR` = `tmp_path`) og `respx`.
- **Skjema (FR-1–FR-4):** `GET` mot `/`, knappen «Vis tallene», `<label>` på alle felt. Mal 1 vises som spørsmålet «Vis andel positive tester for [virus] i sesongen [sesong]» (PRD tabell 5). Virus: bare de som er klare (`tjeneste.KLARE_VIRUS`, laget fra `fhi.FASTE_FILTRE`), altså influensa til epic 6. Sesonger fra `Tjeneste.sesonger(nå)`, siste valgt som standard. Aldersgrupper fra `domene.ALDERSGRUPPER` med «Alle aldersgrupper» som standard. Verdiene i skjemaet er nøklene i `domene`, aldri FHI-koder (AD-2). Etter innsending er brukerens valg forhåndsvalgt.
- **Utvalg (FR-5, AD-9):** alle parametre tomme eller mangler → bare skjemaet. Ellers `Utvalg.fra_parametre(request.query_params, sesonger)`. `UgyldigUtvalg` → meldingen vises (`role="alert"`) og `Tjeneste.svar` kalles ikke. «Ingen henting» betyr ingen henting av tall for utvalget. Sesonglisten (dimensjonslisten) trengs for å sjekke sesongen og hentes eller leses fra cachen som før.
- **Gyldig utvalg:** `Tjeneste.svar(utvalg, nå)` kalles, og siden viser foreløpig bare `melding` hvis den finnes (RSV, FHI nede). Tabellen kommer i 3.2, grafen i 3.3.
- **`nå`:** `datetime.now(UTC)` i `web` (åpent punkt fra 2.9).
- **Siden:** `lang="nb"`, enkel norsk. `static/` monteres på `/static` (tom `style.css` nå, `app.js` kommer i 3.3).
- **README:** «Starte appen» får `uv run uvicorn backend.web:app --reload` fra `backend/` og adressen `http://127.0.0.1:8000`.
- Endret: `backend/src/backend/web.py` (ny), `backend/src/backend/templates/` (ny), `backend/src/backend/static/style.css` (ny), `backend/src/backend/tjeneste.py` (`KLARE_VIRUS`), `backend/tests/test_web.py` (ny), `backend/tests/test_readme.py`, `README.md`.
