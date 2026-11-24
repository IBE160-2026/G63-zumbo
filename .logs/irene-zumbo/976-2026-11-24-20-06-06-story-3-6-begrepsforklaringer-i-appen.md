# Story 3.6: begrepsforklaringer i appen

## 2026-11-24 kl. 20:06 — Irene Zumbo

### Oppgave
Bygge story 3.6 (#20) med Irenes sju begrepsforklaringer fra issue #19, ordrett, og lenken fra varselet til forklaringen av «for tynt datagrunnlag». Sette 3.5 til done, lukke #19 og lukke punktet om at «Test og positiv prøve» må si at tallene teller analyser. Kortere gjennomgang mot akseptansekriteriene i stedet for fire gjennomgangsagenter (Irenes valg).

### Plan
- `bmad-build`, oneshot: [spec-3-6](../../_bmad-output/implementation-artifacts/spec-3-6-begrepsforklaringer-i-appen.md).
- Ny kjernemodul `begreper.py`, delen «Hva betyr ordene?» med `<details>`/`<summary>`, lenken «Hva betyr dette?» i varselet, og `app.js` som åpner forklaringen.

### Resultat
- Commits `f737523`, `56c2751`, `df47a4f`, `2674f41`, `7b0dcbd` på branchen `story-3.6`.
- Tekstene er sjekket maskinelt mot kommentaren i #19 og er like. Hver har tre setninger.
- Forklaringene vises nederst på alle sider, lukket. Lenken i varselet peker på `#begrep-tynt-datagrunnlag`. `app.js` åpner den ved klikk og når adressen peker dit, og lastes nå på alle sider (Chart.js bare når det finnes en graf). Sjekket i Chrome uten vindu: forklaringen får `open`.
- Tester: `test_begreper.py` og `test_web_begreper.py` (nye), lenketest i `test_web_varsel.py`, tre gamle tester justert. 607 tester består, ruff består.
- Epic-konteksten er oppdatert med den nye definisjonen av «Test». Sprint-status: 3.5 og 3.6 done. Punktet om lenken i deferred-work.md er løst.
- Lukket i issues.md: tekstene til begrepsforklaringene (3.5), lenken fra varselet (3.6) og «Test og positiv prøve» (teksten i #19 sier at samme person kan telles flere ganger).

### Åpne punkter
Ingen.
