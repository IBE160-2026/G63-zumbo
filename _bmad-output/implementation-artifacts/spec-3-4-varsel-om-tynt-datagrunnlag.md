---
title: 'Story 3.4: Varsel om tynt datagrunnlag'
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

**Problem:** Sara ser tallene uten å få vite at de er usikre når en kontrollregel slår inn (issue #18, FR-19, NFR-7). I tillegg har Irene tatt fire beslutninger i gjennomgangen av 3.1–3.3 som skal inn i samme PR: en uke med 0 tester viser «kan ikke regnes ut» i andelskolonnen («mangler» bare for skjulte tall), brudd i linjen for uker uten andel er godkjent, forklaringen av fylt og åpen sirkel under grafen vises alltid, og andelen vises fortsatt med én desimal. Beslutningene føres inn i PRD-en der de endrer noe, merket «Endret 24. november 2026: Irenes beslutning».

**Approach:** Når `Resultat.regelutslag` ikke er tomt, viser `index.html` et varsel over grafen med ikon (⚠, skjult for skjermlesere) og overskriften «For tynt datagrunnlag», innledningen «Tallene bør tolkes med forsiktighet fordi:» og én punktliste med setningen fra hvert `Regelutslag` (som skissen i PRD §6.0). Uten utslag vises det ikke. Varselet er avgrenset med ramme og ikon, ikke bare farge. Tester dekker et utvalg med R1 og R5 samtidig og et utvalg uten utslag. Andelsteksten for 0 tester endres i `web`.

</frozen-after-approval>

## Implementation Notes

- **Varsel (FR-19, NFR-7):** `<section class="varsel" aria-labelledby="varseltittel">` rett etter skjemaet, feilmeldingen og meldingen om sist lagrede tall, og før `<figure>`. Det vises bare når `resultat.serie` finnes og `resultat.regelutslag` ikke er tomt, også med sist lagrede tall. Teksten i hvert punkt er `Regelutslag.tekst` som den er. Faste tekster står i malen. Ingen JavaScript.
- **Lenken til «for tynt datagrunnlag» (FR-19)** kommer i story 3.6, når begrepsforklaringene finnes (epic-3-context, avhengigheter). Den er ikke med her.
- **«kan ikke regnes ut»:** nytt filter `andelstekst(uke)` i `web`: andel når den finnes, «mangler» når uka er manglende (skjult eller manglende tall), ellers «kan ikke regnes ut» (0 tester). Tabellen og `grafdata["andel_tekst"]` bruker det. `andel(None)` er fortsatt «mangler».
- **PRD:** FR-9 (brudd også for uker uten andel, forklaringen vises alltid), FR-10 (0 tester) og FR-11 («kan ikke regnes ut», én desimal), merket «Endret 24. november 2026: Irenes beslutning». De to spørsmålene i deferred-work.md (3.2 og 3.3) markeres som løst.
