# Story 4.5: Forklaringen på siden

## 2026-11-24 kl. 23:42 — Irene Zumbo

### Oppgave
Story 4.5 (#26): vise KI-forklaringen på siden uten at graf, tabell og varsel venter på KI-en (FR-20, FR-22, NFR-2, AD-9). Branchen er `story-4.5` fra oppdatert main. Etterpå kommer bmad-code-review, status done, push til ibe og en PR med «Closes #26» uten merge. Irene har ingen API-nøkkel, så det trengs en måte å se utfallene uten nøkkel.

### Plan
- Fortsetter [story-4-4](969-2026-11-24-23-25-34-story-4-4-mellomlagre-ki-forklaringen.md). PR #67 ble merget først.
- bmad-build (oneshot) med spec i `_bmad-output/implementation-artifacts/spec-4-5-forklaringen-pa-siden.md`.
- bmad-code-review med fire lag. Funnene er rettet eller begrunnet under «Review Triage Log» i spec-en.

### Resultat
- `a6b9fa2` Ny rute `GET /forklaring` gir et HTML-fragment med tre utfall:
  - forklaringen, merket «Skrevet av KI», med kildehenvisningen
  - «krever en KI-nøkkel»
  - «kunne ikke lages akkurat nå»

  Tekstene står i `templates/_ki_tekster.html`. `web` importerer ikke `ki`: `tjeneste` gir utfallene videre.
- `1ccd0e7` Forklaringsområdet ligger nederst på siden (boks 6 i skissen) og har `aria-live="polite"`, «Forklaringen lages …» og `data-feiltekst`. `app.js` henter fragmentet etter at siden er vist.
- `ddddc72` Tester i `test_web_forklaring.py` med en falsk Claude.
- `3d5a5b7` Demoskriptet `backend/scripts/vis_forklaring.py` bruker en falsk Claude, port 8001 og en midlertidig cache. Det er prøvd mot ekte FHI med alle tre utfallene.
- `10efdd6` README forklarer forklaringen og demoen.
- `6c566c8` Rettelser fra kodegjennomgangen:
  - nye tester for side uten tall, for NFR-2 med lagrede tall og for `main()` i demoen
  - teksten for `<noscript>` er flyttet til `_ki_tekster.html`
- `0fc576a` Triage er skrevet i spec-en, og 4.5 er done i sprint-status. Gjennomgangen ga 4 rettet, 1 utsatt og 13 avvist.
- pytest: 790 passed. ruff: OK. Ingen test kaller Claude.

### Åpne punkter
- Ingen automatisk test viser at `app.js` setter inn fragmentet, eller at feilteksten vises ved 400 og nettverksfeil. Det må sjekkes for hånd med demoen, og en nettlesertest bør komme sammen med den for grafen (se deferred-work.md).
