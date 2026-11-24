---
title: 'Story 3.2: Tabell, kildehenvisning og feilmelding'
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

**Problem:** Siden viser ingen tall etter at Sara har valgt et gyldig utvalg, og ingen kilde hun kan oppgi (issue #16, FR-8, FR-10–FR-12). To åpne punkter skal med: når FHI er nede og det finnes lagrede tall, skal siden vise «Sist lagrede tall, hentet …» (fra 2.9), og uker med flere positive enn tester skal få fotnoten «Flere positive prøver enn tester denne uka. Det kan skyldes hvordan prøvene er registrert. Tolk tallet med forsiktighet.» (fra 2.4).

**Approach:** Tabellen (uke, tester, positive prøver, andel positive) lages i `index.html` fra `Resultat.serie`, formatert med Jinja2-filtre i `web`. Usikre uker får tegn og fotnote, og kildehenvisningen med hentetidspunkt i norsk tid står under tabellen. Når FHI er nede, vises FR-8-meldingen med «Sist lagrede tall, hentet …» og tabellen, eller bare meldingen uten tabell. Tester med testklienten og konstruerte data.

</frozen-after-approval>

## Implementation Notes

- **Filtre (arkitektur §4):** `tall` (mellomrom som tusenskille, `None` → «skjult»), `andel` (én desimal, komma og « %», avrundet halvt opp, `None` → «mangler»), `uke` («uke 50») og `tidspunkt` (norsk tid, «20.11.2026 kl. 14:05»). Mellomrommene er harde mellomrom (U+00A0), så tall og prosent ikke brytes over to linjer. Filtrene registreres på `maler.env` i `web`.
- **Tabell (FR-11):** én rad per `Uke` i `serie.uker`, i samme rekkefølge. Kolonneoverskrifter med `<th scope="col">`, ukene som `<th scope="row">`. Tabellen ligger i en boks som kan rulle vannrett (mobil i 3.7). Andelen over 100 % vises som den er.
- **Usikre uker (FR-10):** `*` etter uka når `Uke.usikker`, med fotnoten «* Usikker uke: færre enn 30 tester, skjult antall tester eller flere positive prøver enn tester.» Når `Uke.flere_positive_enn_tester`, også `†` og fotnoten «† Flere positive prøver enn tester denne uka. Det kan skyldes hvordan prøvene er registrert. Tolk tallet med forsiktighet.» Hver fotnote vises bare når minst én uke har tegnet. Tegnet har en skjult tekst for skjermlesere.
- **Kildehenvisning (FR-12):** «Kilde: … (FHI). Tabell 724 «RESPIaggr Influensa antall og andel». Hentet 20.11.2026 kl. 14:05.» fra `Resultat.kilde`.
- **FR-8:** `Resultat.serie is None` → bare `melding` (FHI nede uten lagrede tall gir «… Prøv igjen senere.»). `sist_lagrede` → meldingen og «Sist lagrede tall, hentet 20.11.2026 kl. 14:05.» over tabellen, og tabellen vises.
- **Uten JavaScript (AD-8):** alt står i HTML fra serveren.
- Ikke med: «FHI publiserer nye tall hver torsdag» og knappen (FR-25, story 4.6), varsel (3.4), graf (3.3).
