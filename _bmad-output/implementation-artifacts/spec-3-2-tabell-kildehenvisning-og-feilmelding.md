---
title: 'Story 3.2: Tabell, kildehenvisning og feilmelding'
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
- **Tabelltittel:** `<caption>` med utvalget («Influensa, sesongen 2025/2026, alle aldersgrupper») fra filteret `utvalgstekst`, som grafen kan bruke i 3.3. Rulleboksen har `role="region"`, `tabindex="0"` og navn fra tittelen, så den kan rulles med tastatur.
- **Klokke:** `lag_app` tar en `klokke` (standard `datetime.now(UTC)`), så testene får faste tidspunkter.
- Endret: `backend/src/backend/web.py`, `templates/index.html`, `static/style.css`, `backend/tests/test_web_tabell.py` (ny).
- Ikke med: «FHI publiserer nye tall hver torsdag» og knappen (FR-25, story 4.6), varsel (3.4), graf (3.3).

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Alle akseptansekriteriene i #16 er oppfylt. Ingen alvorlige funn, og ingenting som krever endring i PRD eller arkitektur.

- **medium, rettet:** tabellen hadde ikke noe tilgjengelig navn som sier hvilket utvalg tallene gjelder. Den har nå `<caption>` med utvalget.
- **medium, rettet:** rulleboksen kunne ikke nås med tastatur. Den har nå `tabindex="0"`, `role="region"` og et navn.
- **low, rettet:** ingen test for `*` uten `†`, for en uke med 0 tester og flere enn 0 positive, for `aria-hidden`/`scope="row"`, eller for at «Sist lagrede tall» står over tabellen og bare når FHI er nede. Testene er lagt til.
- **low, rettet:** testen for «uten JavaScript» krevde at siden ikke hadde noe `<script>` og ville feilet i 3.3. Den sjekker nå at tallene står i tabellen i HTML-en.
- **low, rettet:** klassen `usikker` på `<tr>` ble ikke brukt. Den er fjernet. `last_updated` i sprint-status gikk bakover. Den er rettet.
- **low, utsatt:** «mangler» som andel for en uke med 0 tester kan leses som skjult. Ordvalget er Irenes (se deferred-work.md).
- **low, avvist:** fotnoten sier «denne uka» under hele tabellen. Teksten er Irenes ordrett (PRD FR-10), og `†` står ved uka.
- **low, avvist:** hentetidspunktet står både i «Sist lagrede tall, hentet …» og i kilden. FR-8 og FR-12 krever begge.
- **low, avvist:** kilden forutsetter punktum på slutten av `kildetekst`. Alle tre tekstene i `domene.TABELLER` slutter med punktum (ordrett fra FHI).
- **false:** «skjult» for verdier som mangler. PRD kapittel 3 definerer skjult verdi som en verdi FHI har skjult eller som mangler.
- **false:** NaN eller uendelig i `andel`. `Uke.andel` regnes fra heltall og er `None` ved 0 tester.
- **false:** naiv tid i `tidspunkt` eller `klokke`. `kildehenvisning` krever tidssone, og `sesong` kaster en feil for naiv `nå`.
- **false:** tom `serie.uker` og `sist_lagrede` uten `kilde` eller `melding`. `fhi.tolk` gir alltid minst én uke for en publisert sesong, og `tjeneste` setter alltid `kilde` og `melding` sammen med `sist_lagrede`.
