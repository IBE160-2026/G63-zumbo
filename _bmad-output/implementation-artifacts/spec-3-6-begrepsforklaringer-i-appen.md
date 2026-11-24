---
title: 'Story 3.6: Begrepsforklaringer i appen'
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

**Problem:** Sara møter ord som «andel positive», «MSIS» og «for tynt datagrunnlag» uten å få vite hva de betyr (issue #20, FR-13, FR-19). Irene har skrevet de sju forklaringene i issue #19 (story 3.5).

**Approach:** Irenes tekster fra #19 legges ordrett i en ny kjernemodul `begreper.py`. Siden viser dem under overskriften «Hva betyr ordene?» som `<details>`/`<summary>`, som kan åpnes med mus, Enter og mellomrom. Varselet fra story 3.4 får lenken «Hva betyr dette?» til forklaringen av «for tynt datagrunnlag», og lenken åpner den. Tester sjekker at alle sju begrepene finnes, at hver tekst har høyst tre setninger, at siden viser dem og at varselet lenker til riktig forklaring. I samme PR: story 3.5 settes til done i sprint-status, issue #19 lukkes, og punktet i issues.md om «Test og positiv prøve» lukkes, fordi teksten i #19 sier at samme person kan telles flere ganger.

</frozen-after-approval>

## Implementation Notes

- **Tekstene:** `backend/src/backend/begreper.py` (ny, ren kjerne) har `Begrep(nøkkel, navn, tekst)` og `BEGREPER` med de sju tekstene fra #19, ordrett (sjekket maskinelt mot issuekommentaren). `html_id` er «begrep-<nøkkel>», og nøklene er ASCII.
- **Siden:** `index.html` har delen «Hva betyr ordene?» med `<details>`/`<summary>` nederst, under tabell og kilde (PRD §6.0, boks 5). Den vises alltid, også uten utvalg, fordi forklaringene gjelder hele siden. Alle er lukket når siden lastes.
- **Lenken (FR-19):** «Hva betyr dette?» (teksten fra skissen i PRD §6.0) peker på `#begrep-tynt-datagrunnlag`. `app.js` åpner forklaringen og flytter fokus til `<summary>` ved klikk, ved `hashchange` og når siden lastes med adressen. Uten JavaScript fører lenken til forklaringen, som da åpnes med Enter. Sjekket i Chrome uten vindu: `<details id="begrep-tynt-datagrunnlag" open="">`.
- **Skriptene:** `app.js` lastes nå på alle sider, fordi varselet kan vises uten graf. Chart.js lastes fortsatt bare når det finnes en graf, og grafdelen av `app.js` stopper når Chart.js eller grafdata mangler.
- **Tester:** `tests/test_begreper.py` (ny), `tests/test_web_begreper.py` (ny), lenketesten i `test_web_varsel.py`. Tre gamle tester er justert: «For tynt datagrunnlag» og «RSV» står nå i begrepsdelen, og `app.js` lastes alltid.
- **Sprint og issues:** 3.5 og 3.6 er done. Punktet om lenken i deferred-work.md er løst.

## Review Triage Log

Kortere gjennomgang etter Irenes valg: ingen subagenter (Blind Hunter er hoppet over). Jeg sjekket endringene selv mot akseptansekriteriene i #20.

- AK 1, `<details>`/`<summary>` som åpnes med mus, Enter og mellomrom: oppfylt. Nettleserens egen oppførsel, uten JavaScript.
- AK 2, lenken fra varselet åpner forklaringen: oppfylt, testet i HTML og sjekket i Chrome.
- AK 3, test av sju begreper, høyst tre setninger, siden og lenken: oppfylt. Setningstellingen teller ikke «1. mars» som to setninger.
- **low, avvist:** «5 %» og «1 000» i Irenes tekst har vanlig mellomrom, så linjen kan brytes mellom tallet og «%». Tekstene skal stå ordrett, og det skjer bare på smale skjermer.
- **low, avvist:** forklaringen av «Sesong» nevner RSV, som ikke kan velges før epic 6. Det er Irenes tekst og er riktig om sesongen.
