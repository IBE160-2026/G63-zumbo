---
title: 'Story 3.4: Varsel om tynt datagrunnlag'
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

**Problem:** Sara ser tallene uten å få vite at de er usikre når en kontrollregel slår inn (issue #18, FR-19, NFR-7). I tillegg har Irene tatt fire beslutninger i gjennomgangen av 3.1–3.3 som skal inn i samme PR: en uke med 0 tester viser «kan ikke regnes ut» i andelskolonnen («mangler» bare for skjulte tall), brudd i linjen for uker uten andel er godkjent, forklaringen av fylt og åpen sirkel under grafen vises alltid, og andelen vises fortsatt med én desimal. Beslutningene føres inn i PRD-en der de endrer noe, merket «Endret 24. november 2026: Irenes beslutning».

**Approach:** Når `Resultat.regelutslag` ikke er tomt, viser `index.html` et varsel over grafen med ikon (⚠, skjult for skjermlesere) og overskriften «For tynt datagrunnlag», innledningen «Tallene bør tolkes med forsiktighet fordi:» og én punktliste med setningen fra hvert `Regelutslag` (som skissen i PRD §6.0). Uten utslag vises det ikke. Varselet er avgrenset med ramme og ikon, ikke bare farge. Tester dekker et utvalg med R1 og R5 samtidig og et utvalg uten utslag. Andelsteksten for 0 tester endres i `web`.

</frozen-after-approval>

## Implementation Notes

- **Varsel (FR-19, NFR-7):** `<section class="varsel" aria-labelledby="varseltittel">` rett etter skjemaet, feilmeldingen og meldingen om sist lagrede tall, og før `<figure>`. Det vises bare når `resultat.serie` finnes og `resultat.regelutslag` ikke er tomt, også med sist lagrede tall. Teksten i hvert punkt er `Regelutslag.tekst` som den er. Faste tekster står i malen. Ingen JavaScript.
- **Lenken til «for tynt datagrunnlag» (FR-19)** kommer i story 3.6, når begrepsforklaringene finnes (epic-3-context, avhengigheter). Den er ikke med her.
- **«kan ikke regnes ut»:** nytt filter `andelstekst(uke)` i `web`: andel når den finnes, «mangler» når uka er manglende (skjult eller manglende tall), ellers «kan ikke regnes ut» (0 tester). Tabellen og `grafdata["andel_tekst"]` bruker det. `andel(None)` er fortsatt «mangler».
- **PRD:** FR-9 (brudd også for uker uten andel), FR-10 (forklaringen vises alltid) og FR-11 («kan ikke regnes ut», én desimal), merket «Endret 24. november 2026: Irenes beslutning». De to spørsmålene i deferred-work.md (3.2 og 3.3) markeres som løst.
- **Etter gjennomgangen:** ikonet er `⚠︎` (U+FE0E), så det vises som tekst og ikke som fargeemoji. En uke med 0 tester og skjult antall positive viser «mangler», fordi et tall er skjult. Teksten i PRD FR-9 sier nå hva tabellen viser for uker uten andel. FR-10 sier at forklaringen ikke vises når det ikke finnes noen graf.
- Endret: `backend/src/backend/web.py`, `templates/index.html`, `static/style.css`, `backend/tests/test_web_varsel.py` (ny), `test_web_tabell.py`, `test_web_graf.py`, PRD (FR-9–FR-11), `epic-3-context.md`, `deferred-work.md`.

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Alle akseptansekriteriene i #18 og alle fire beslutningene er oppfylt. Ingen alvorlige funn, og ingenting som krever endring i PRD eller arkitektur utover beslutningene. Verification Gap fant ingen hull i testene.

- **medium, rettet:** den nye teksten i PRD FR-9 sa at alle uker uten andel er «markert som usikre i tabellen». En uke med minst 30 tester og skjult antall positive er ikke usikker (`Uke.usikker`). Teksten sier nå hva tabellen viser.
- **low, rettet:** `epic-3-context.md` sa fortsatt at fotnoten «finnes ikke i koden ennå». Setningen er fjernet.
- **low, rettet:** «forklaringen vises alltid» gjaldt ikke når ingen uke har andel. Da vises ingen graf. FR-10 sier det nå.
- **low, rettet:** ingen test av at meldingen om sist lagrede tall står over varselet. Lagt til.
- **low, rettet:** ⚠ kan vises som fargeemoji. Nå `⚠︎` (tekstform).
- **low, utsatt:** lenken fra varselet til «for tynt datagrunnlag» (FR-19) kommer i story 3.6. Ført i deferred-work.md, så den ikke glemmes.
- **low, utsatt (spørsmål til Irene):** overskriften «For tynt datagrunnlag» når bare R5 slår inn. Følger PRD-ens skisse og begrep. Ført i deferred-work.md.
- **low, avvist:** `(0 tester, skjulte positive)` gir «mangler». Det er i tråd med «mangler bare for skjulte tall», fordi et tall er skjult. Står nå i docstringen.
- **low, avvist:** R1+R5 testes med en stubbet tjeneste. Setningene kommer fra de ekte `kontrollregler.vurder`, og R1 og R5 testes hver for seg gjennom cachen. Ingen fixtur har begge, og å lage en gir lite ekstra.
- **low, avvist:** ingen test av R2–R4 på siden og av rekkefølgen R1–R5. Malen lister `regelutslag` i rekkefølgen den får. Rekkefølgen testes i `test_kontrollregler.py`.
- **low, avvist:** ingen test av escaping. Jinja2Templates har autoescape for `.html`, og tekstene er faste i koden.
- **low, avvist:** parameternavnet `verdi` i `andelstekst`. Samme navn som i `uke(verdi: Uke)`.
- **low, avvist:** R5-setningen har ingen tall (FR-19). Setningen hører til kontrollreglene i epic 2 og vises som den er.
- **false:** «specen mangler akseptansekriterier». Specen er `oneshot` og har bare Intent og Implementation Notes, som malen tillater. Status settes til done her.
- **false (kosmetisk):** beslutningen om forklaringen står under FR-10, ikke FR-9 som notatet sa. FR-10 er der kravet om forklaringen står. Notatet over er rettet.
