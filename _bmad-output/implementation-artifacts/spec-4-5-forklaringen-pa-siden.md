---
title: 'Story 4.5: Forklaringen på siden'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `Tjeneste.forklaring` (story 4.3 og 4.4) gir KI-forklaringen, men siden viser den ikke. Story 4.5 (#26) krever at graf, tabell og varsel vises med en gang, og at forklaringen settes inn når den er klar, uten at siden venter på KI-en (FR-20, FR-22, NFR-2, AD-9).

**Approach:** Siden får et forklaringsområde med `aria-live="polite"`, «Forklaringen lages …» og `data-feiltekst`. `app.js` henter `GET /forklaring` med de samme parametrene og setter inn HTML-fragmentet. Fragmentet har tre utfall: forklaringen merket «Skrevet av KI» med kildehenvisningen, teksten om at forklaringen krever en KI-nøkkel, og feilteksten. `GET /` kaller aldri `ki`. Testene bruker en falsk klient og kaller aldri Claude.

</frozen-after-approval>

## Implementation Notes

- **Plassering:** boks 6 i skissen i PRD §6.0, etter «Hva betyr ordene?» og før «Hvorfor ikke bare spørre en chatbot?». Området vises bare når det finnes tall (`resultat.serie is not none`).
- **`web.lag_app`:** får `ny_ki_klient` og sender den til `Tjeneste`, slik at testene og demoen kan bruke en falsk Claude.
- **`GET /forklaring`:** samme parametre som `/`, sjekket i `Utvalg.fra_parametre`. Ugyldig eller tomt utvalg gir `400` med feilteksten, og `app.js` viser da `data-feiltekst`. Ellers `tjeneste.svar` og så `tjeneste.forklaring`, og fragmentet `_forklaring.html` med status `200`. Svaret har `Cache-Control: no-store`.
- **Tekstene** står i malene (AD-9): `MANGLER_NØKKEL` og `KI_FEIL` sendes fra `web` til begge malene, så `data-feiltekst` og `KiFeil`-fragmentet har samme tekst.
  - Uten nøkkel: «KI-forklaringen krever en KI-nøkkel. Graf, tabell og varsel er komplette uten den.»
  - Feil: «Forklaringen kunne ikke lages akkurat nå.»
- **Forklaringen:** avsnitt delt på tomme linjer, Jinja2 escaper teksten. Kildehenvisningen er `kildetekst(resultat.kilde)`, den samme som under tabellen (FR-12).
- **`app.js`:** finner `#forklaring[data-adresse]`, henter med `fetch`, og setter inn fragmentet bare ved status 200. Nettverksfeil eller annen status gir `data-feiltekst`. Uten JavaScript sier en `<noscript>` at forklaringen krever JavaScript.
- **Demo uten nøkkel:** `backend/scripts/vis_forklaring.py <forklaring|ingen-nokkel|feil>` starter appen med en falsk Claude og en midlertidig cache, så en falsk forklaring aldri havner i `.cache/ki/`.
- **README:** forklaringen vises på siden, og hvordan demoen startes.
- **Tester:** `test_web_forklaring.py` med `TestClient`: området på siden, at `GET /` ikke kaller `ki`, fragmentet for alle tre utfallene, kildehenvisningen, escaping, ugyldige parametre og at Claude aldri kalles uten nøkkel.
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">cat /Users/irenezumbo/fhi-helsedata/_bmad/render/bmad-build/fhi-helsedata-649fa7292272/9c01d9d21cfc49029950/step-oneshot.md