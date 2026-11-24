---
title: 'Story 4.5: Forklaringen på siden'
type: 'feature'
created: '2026-11-24'
status: 'done'
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
- **`GET /forklaring`:** samme parametre som `/`, sjekket i `Utvalg.fra_parametre`. Ugyldig eller tomt utvalg gir `400` («Ugyldig utvalg.»), og `app.js` viser da `data-feiltekst`. Ellers `tjeneste.svar` og så `tjeneste.forklaring`, og fragmentet `_forklaring.html` med status `200`. Svaret har `Cache-Control: no-store`.
- **Tekstene** står i malene (AD-6, AD-9): `templates/_ki_tekster.html` har `ki_feil` og `mangler_nøkkel`, og både `index.html` (`data-feiltekst`) og `_forklaring.html` importerer dem, så feilteksten er den samme.
  - Uten nøkkel: «KI-forklaringen krever en KI-nøkkel. Graf, tabell og varsel er komplette uten den.»
  - Feil: «Forklaringen kunne ikke lages akkurat nå.»
- **`web` importerer ikke `ki`** (diagrammet i arkitektur §2). `tjeneste` gir videre `Forklaring`, `ManglerNøkkel` og `KiFeil`, og `web` bruker dem derfra.
- **Forklaringen:** avsnitt delt på tomme linjer, Jinja2 escaper teksten. Kildehenvisningen er `kildetekst(resultat.kilde)`, den samme som under tabellen (FR-12).
- **`app.js`:** finner `#forklaring[data-adresse]`, henter med `fetch`, og setter inn fragmentet bare ved status 200. Nettverksfeil eller annen status gir `data-feiltekst`. Uten JavaScript sier en `<noscript>` at forklaringen krever JavaScript.
- **Demo uten nøkkel:** `backend/scripts/vis_forklaring.py <forklaring|uten-nokkel|feil>` starter appen på port 8001 med en falsk Claude (to sekunders pause, så ventetekst synes) og en midlertidig cache, så en falsk forklaring aldri havner i `.cache/ki/`. Port 8001 fordi den vanlige appen ofte kjører på 8000. Prøvd mot ekte FHI i alle tre utfallene.
- **README:** forklaringen vises på siden, og hvordan demoen startes.
- **Tester:** `test_web_forklaring.py` med `TestClient`: området på siden, at `GET /` ikke kaller `ki`, fragmentet for alle tre utfallene, kildehenvisningen, escaping, ugyldige parametre og at Claude aldri kalles uten nøkkel. `test_vis_forklaring.py` for demoskriptet. Ingen test kaller Claude.
- pytest: 790 passed etter rettelsene fra kodegjennomgangen. ruff check og ruff format: OK.
- **Ikke testet automatisk:** at `app.js` faktisk setter inn fragmentet i en nettleser (ingen nettlesertest, se story 3.7). Testene leser JavaScript-teksten.

## Review Triage Log

bmad-code-review med fire lag (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Acceptance Auditor fant ingen brudd på akseptansekriteriene. 4 rettet, 1 utsatt, 13 avvist.

- low, rettet: ingen test viste at området er borte når utvalget er gyldig, men FHI ikke gir tall. Ny test med FHI 503 og tom cache.
- low, rettet: AC5 (NFR-2) manglet en egen test for «med lagrede tall». Ny test: andre visning av siden kaller verken FHI eller `Tjeneste.forklaring`, og viser graf, tabell og ventetekst.
- low, rettet: demoen skrev `8001` i stedet for `PORT`, og `main()` var ikke testet. Nå brukes `PORT`, `Innstillinger` får navngitte felt, og en test sjekker alle tre utfallene, porten og at den midlertidige mappen slettes og ikke er `.cache/`.
- low, rettet: teksten i `<noscript>` sto ikke i `_ki_tekster.html` med de andre faste tekstene.
- defer: `app.js` testes bare ved å lese kildeteksten. En nettlesertest trengs for å vise at fragmentet settes inn og at feilteksten vises (samme hull som grafen, story 3.7).
- false: en ny ventetid på FHI i `/forklaring` når FHI er nede. `Tjeneste._dimensjonsliste` prøver ikke FHI igjen i 60 sekunder etter en feil (`PAUSE_ETTER_FEIL`), så `/forklaring` bruker de lagrede tallene med en gang.
- false: en omdirigering kan sette inn feil side. `/forklaring` omdirigerer aldri.
- false: fragmentet for `KiFeil` bruker ikke `data-feiltekst`. Begge kommer fra `ki_feil` i `_ki_tekster.html`, og en test viser at de er like.
- false: demoskriptet importerer `anthropic` (AD-6). Regelen gjelder modulene i pakken `backend`. Testene gjør det samme.
- false: sprint-status og spec står som `in-progress`. De settes til `done` i dette steget.
- avvist (low): `/forklaring` kaller `tjeneste.svar` på nytt, så kildehenvisningen kan i sjeldne tilfeller vise et annet hentetidspunkt enn under tabellen. Det skjer bare når tallene blir utdatert akkurat mellom de to forespørslene, eller når lagringen feiler. Å sende tidspunktet i adressen ville gi en ny parameter.
- avvist (low): ingen tidsgrense i `fetch`. Serveren svarer alltid til slutt (Claude 2 × 15 s, FHI 10 s), og nettleseren har sin egen tidsgrense.
- avvist (low): ingen `aria-busy` mens forklaringen lages. Ventetekst står i området, og `aria-live` leser opp svaret.
- avvist (low): feil i `fetch` logges ikke i konsollen. Brukeren ser feilteksten, og serveren logger feilen.
- avvist (low): et tomt eller ugyldig utvalg kan hente sesonglisten fra FHI før svaret blir 400. `app.js` sender alltid et gyldig utvalg, og `GET /` gjør det samme.
- avvist (low): et gyldig utvalg uten tall gir 200 med feilteksten, ikke 400. Siden viser ikke området da, så `app.js` spør aldri.
- avvist (low): synkrone ruter deler trådbassenget, så mange samtidige forklaringer kan forsinke `GET /`. Appen har få brukere, og like forklaringer deler ett kall (`_én_gang`).
- avvist (low): et 500-svar har ikke `Cache-Control: no-store`. Ingen mellomtjener ligger foran appen.
