---
title: 'Story 3.3: Graf uke for uke'
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

**Problem:** Sara ser bare en tabell og ikke hovedtrekket i sesongen med en gang (issue #17, FR-9, FR-10, NFR-6, NFR-7). Åpent punkt fra 2.4: uker med flere positive enn tester skal markeres som usikre i grafen, på samme måte som andre usikre uker.

**Approach:** En linjegraf med Chart.js 4.6.1 fra jsDelivr (fast versjon og `integrity`) tegnes av `static/app.js` fra en `<script type="application/json">`-blokk som lages fra samme `Dataserie` som tabellen. Manglende uker er `null`. Usikre uker (`Uke.usikker`, som også gjelder flere positive enn tester) får åpen sirkel. Grafen har en tittel med utvalget, en forklaring av markeringen og en alternativtekst med utvalg og hovedtrekk.

</frozen-after-approval>

## Implementation Notes

- **Grafdata (AD-8):** filteret `grafdata` i `web` lager `{"uker": ["uke 40", …], "andel": [0.9, …, null], "usikker": [false, …], "tekster": {"x": "Uke", "y": "Andel positive (%)"}}`. Andelen er avrundet til én desimal på samme måte som tabellen (halvt opp), så tallene er de samme. Blokken skrives med Jinja2s `tojson`, som gjør `<`, `>` og `&` trygge inne i `<script>`.
- **Tittel og forklaring (FR-9, FR-10):** `<figure>` med tittelen fra `utvalgstekst` og en forklaring i HTML under grafen: «● Sikker uke ○ Usikker uke: færre enn 30 tester, skjult antall tester eller flere positive prøver enn tester.» Alle faste tekster står i malen, ikke i JavaScript.
- **Alternativtekst (NFR-6):** filteret `alternativtekst` lager én tekst med utvalget og hovedtrekkene: ukene grafen dekker, den høyeste andelen og andelen i siste uke med tall. Teksten står i `aria-label` på `<canvas role="img">` og som innhold i `<canvas>` (vises når grafen ikke kan tegnes).
- **Punktform (NFR-7):** fylt sirkel for sikre uker og åpen sirkel (hvit fyll) for usikre uker, ikke bare en annen farge. `spanGaps: false`, så `null` gir brudd i linjen. Fargene er CSS-variabler i `style.css` som `app.js` leser.
- **Skript:** Chart.js og `/static/app.js` lastes med `defer`, bare når det finnes tall. Ingen annen JavaScript på siden.
- Ikke med: kontrastsjekk og mobil (3.7), stiplet linje for mal 2 (epic 8).
