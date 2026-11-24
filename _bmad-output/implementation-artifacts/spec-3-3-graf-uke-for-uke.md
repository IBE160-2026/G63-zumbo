---
title: 'Story 3.3: Graf uke for uke'
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

**Problem:** Sara ser bare en tabell og ikke hovedtrekket i sesongen med en gang (issue #17, FR-9, FR-10, NFR-6, NFR-7). Åpent punkt fra 2.4: uker med flere positive enn tester skal markeres som usikre i grafen, på samme måte som andre usikre uker.

**Approach:** En linjegraf med Chart.js 4.6.1 fra jsDelivr (fast versjon og `integrity`) tegnes av `static/app.js` fra en `<script type="application/json">`-blokk som lages fra samme `Dataserie` som tabellen. Manglende uker er `null`. Usikre uker (`Uke.usikker`, som også gjelder flere positive enn tester) får åpen sirkel. Grafen har en tittel med utvalget, en forklaring av markeringen og en alternativtekst med utvalg og hovedtrekk.

</frozen-after-approval>

## Implementation Notes

- **Grafdata (AD-8):** filteret `grafdata` i `web` lager `{"uker": ["uke 40", …], "andel": [0.9, …, null], "usikker": [false, …], "tekster": {"x": "Uke", "y": "Andel positive (%)"}}`. Andelen er avrundet til én desimal på samme måte som tabellen (halvt opp), så tallene er de samme. Blokken skrives med Jinja2s `tojson`, som gjør `<`, `>` og `&` trygge inne i `<script>`.
- **Tittel og forklaring (FR-9, FR-10):** `<figure>` med tittelen fra `utvalgstekst` og en forklaring i HTML under grafen: «● Sikker uke ○ Usikker uke: færre enn 30 tester, skjult antall tester eller flere positive prøver enn tester.» Alle faste tekster står i malen, ikke i JavaScript.
- **Alternativtekst (NFR-6):** filteret `alternativtekst` lager én tekst med utvalget og hovedtrekkene: ukene grafen dekker, den høyeste andelen og andelen i siste uke med tall. Teksten står i `aria-label` på `<canvas role="img">` og som innhold i `<canvas>` (vises når grafen ikke kan tegnes).
- **Punktform (NFR-7):** fylt sirkel for sikre uker og åpen sirkel (hvit fyll) for usikre uker, ikke bare en annen farge. `spanGaps: false`, så `null` gir brudd i linjen. Fargene er CSS-variabler i `style.css` som `app.js` leser.
- **Skript:** Chart.js og `/static/app.js` lastes med `defer`, bare når det finnes tall. Ingen annen JavaScript på siden.
- **Etter gjennomgangen:** tekstene til aksene og «usikker uke» står i malen som `data-*` på `<canvas>`, og verktøytipset bruker `andel_tekst` fra `grafdata` (samme tekst som tabellen, pluss «usikker uke»). `.grafboks` er `hidden` til `app.js` har Chart.js, og `.grafreserve` viser alternativteksten til da (uten JavaScript eller når CDN-en er blokkert). Grafen og skriptene vises bare når minst én uke har andel (`har_andel`). Uker uten andel (skjult antall tester eller 0 tester) kan ikke ha et punkt. De gir brudd i linjen, og forklaringen og alternativteksten sier det.
- **SRI-hashen** er regnet ut fra fila på jsDelivr 24.11.2026, og SHA-256 for fila stemmer med jsDelivrs eget API.
- Endret: `backend/src/backend/web.py`, `templates/base.html`, `templates/index.html`, `static/app.js` (ny), `static/style.css`, `backend/tests/test_web_graf.py` (ny), `backend/tests/test_web_tabell.py`.
- Ikke med: kontrastsjekk og mobil (3.7), stiplet linje for mal 2 (epic 8).

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Alle akseptansekriteriene i #17 er oppfylt. Ingen alvorlige funn, og ingenting som krever endring i PRD eller arkitektur.

- **medium, rettet:** forklaringen og alternativteksten lovet åpen sirkel også for usikre uker uten andel (skjult antall tester, 0 tester), som ikke kan tegnes. Alternativteksten teller nå bare tegnede sirkler og sier hvor mange uker som gir brudd. Forklaringen sier at uker uten andel gir brudd i linjen. Om dette er greit for FR-10, er lagt som et spørsmål til Irene (deferred-work.md).
- **medium, rettet:** når Chart.js ikke lastes (CDN blokkert, SRI-feil, uten JavaScript), sto en tom boks på 20rem. Nå er boksen skjult til grafen tegnes, og alternativteksten vises i stedet.
- **low, rettet:** verktøytipset og y-aksen formaterte tall i JavaScript (punktum i «2.5 %»). Verktøytipset bruker nå `andel_tekst` fra `web` og sier om uka er usikker. Y-aksen bruker `nb-NO` og hardt mellomrom. Tekstene til aksene står i malen.
- **low, rettet:** grafen ble tegnet med tomme akser når ingen uke hadde andel. Nå vises den ikke da.
- **low, rettet:** manglende tester for flertall og «høyest = siste» i alternativteksten, for brudd og for ingen graf uten andeler. Testen som sammenligner uker brukte et prefiks. Lagt til og rettet. `<figure>` har `aria-labelledby`, og alternativteksten regnes ut én gang.
- **low, rettet:** testen av `app.js` sjekket bare kildetekst. Den sjekker nå også at CSS-variablene og nøklene `app.js` leser, finnes.
- **medium (ikke bekreftet), utsatt:** ingen test kjører `app.js` i en nettleser. Det trengs en Playwright-test (story 3.7).
- **low, avvist:** «høyest» kan være en uke over 100 %. Alternativteksten beskriver det grafen viser, og tabellen har fotnoten.
- **low, avvist:** verktøytipset viser ikke årstallet. Ukene i en sesong (40–53 og 1–20) er unike, og tittelen har sesongen.
- **low, avvist:** grafens tittel er den samme som tabellens tittel. Begge skal gjenta utvalget (FR-9), og `<figure>` og tabellen har hver sin rolle.
- **false:** `JSON.parse` kan feile. Blokken lages alltid med `tojson` fra en ordbok.
- **false:** SRI-hashen er bare sjekket mot en kopi i testen. Hashen ble regnet ut fra fila på jsDelivr, og SHA-256 stemte med jsDelivrs API.
