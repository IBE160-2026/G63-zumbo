---
title: 'Story 3.1: Velge mal og utvalg på siden'
type: 'feature'
created: '2026-11-24'
status: 'done'
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
- **Siden:** `lang="nb"`, enkel norsk. `static/` monteres på `/static` (`style.css` med noen få grunnregler nå, bygges ut i 3.7; `app.js` kommer i 3.3).
- **README:** «Starte appen» får `uv run uvicorn backend.web:app --reload` fra `backend/` og adressen `http://127.0.0.1:8000`.
- **Valgt i skjemaet:** brukerens valg når det finnes i listen, ellers standardvalget (siste sesong, «Alle aldersgrupper», influensa). Slik viser skjemaet aldri et annet valg enn det som står, også etter et ugyldig valg eller RSV.
- **Pause etter feil:** `tjeneste` prøver ikke dimensjonslisten på nytt i 60 s (`PAUSE_ETTER_FEIL`) etter at FHI ikke svarte. Ellers kunne én side vente to tidsgrenser (sesonglisten og tallene, 20 s) når FHI er nede.
- Endret: `backend/src/backend/web.py` (ny), `backend/src/backend/templates/` (ny), `backend/src/backend/static/style.css` (ny), `backend/src/backend/tjeneste.py` (`KLARE_VIRUS`), `backend/tests/test_web.py` (ny), `backend/tests/test_readme.py`, `README.md`.

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Alle akseptansekriteriene i #15 er oppfylt. Ingen alvorlige funn, og ingenting som krever endring i PRD eller arkitektur.

- **medium, rettet:** etter et ugyldig valg eller RSV hadde ingen `<option>` `selected`, så nettleseren viste første valg (eldste sesong, influensa ved RSV-meldingen). Nå brukes standardvalget når verdien ikke finnes i listen. Testet.
- **medium, rettet:** med FHI nede og gammel sesongliste hentet `sesonger` og `svar` hver sin dimensjonsliste, så siden kunne vente 2 × 10 s. `tjeneste` venter nå 60 s før et nytt forsøk. Testet i `test_web` og `test_tjeneste`.
- **medium, rettet:** `web` trimmet parametrene før `fra_parametre`, så «influensa » ble godtatt. Validering skjer nå bare i `domene` (AD-9). Bare sjekken av om noe er fylt ut trimmer.
- **low, rettet:** `web` importerte `fhi` bare for typen til testklienten (AD-1). Nå bare under `TYPE_CHECKING`. `config` importeres fortsatt, fordi AD-6 sier at `web` kaller `les_innstillinger`.
- **low, rettet:** manglende tester for forhåndsvalg (ikke-standard aldersgruppe), tomme parametre og FHI nede. Lagt til.
- **low, rettet:** ulik `<title>` og overskrift, ufullstendig type på `klient`-fixturen, `glob` i stedet for `rglob` og `import inspect` inne i en test.
- **low, utsatt:** meldingen for ukjent virus nevner RSV og SARS-CoV-2, og meldingen for ukjent mal bruker tittelen. Begge lages i `domene` (fra før). Se deferred-work.md.
- **low, avvist:** gyldig utvalg uten melding viser ingen tall. Tabellen kommer i 3.2, som bygges rett etter.
- **low, avvist:** sesonglisten hentes også uten parametre (opptil 10 s med kald cache og FHI nede). Spec-en tillater det, FR-8 godtar 10 s, og pausen gjør neste visning rask.
- **low, avvist:** gjentatte parametre (`?mal=1&mal=9`) og ukjente nøkler. Det siste valget fra Starlette brukes, og ukjente nøkler ignoreres. Ingen skade.
- **low, avvist:** ingen 3.1-test starter appen gjennom ekte `les_innstillinger` uten `.env`. Det dekkes av `test_config`, og testene skal aldri laste `.env` (AD-10).
- **false:** sesongtesten avhenger av klokka. Sesongene kommer fra dimensjonslisten i fixturen, ikke fra `nå`.
- **false:** `/` gir 500 når FHI er nede. `Tjeneste.sesonger` fanger `FhiUtilgjengelig` og bruker reserven. Nå testet.
- **false:** `AttributeError` uten lifespan og `IndexError` ved tom `KLARE_VIRUS`. Begge feiler høylytt i tilstander appen ikke kommer i (uvicorn kjører lifespan, og influensa er alltid klar).
