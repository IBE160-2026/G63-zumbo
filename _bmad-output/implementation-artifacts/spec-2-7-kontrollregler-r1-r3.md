---
title: 'Story 2.7: Kontrollregler R1–R3'
type: 'feature'
created: '2026-11-24'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen kan ikke si fra når datagrunnlaget er for tynt (issue #12). Uten R1–R3 kan Sara trekke konklusjoner av for få positive prøver, for få tester eller for mange manglende uker (FR-14–FR-16, FR-19).

**Approach:** Lag `backend/src/backend/kontrollregler.py` med `vurder(serie) -> list[Regelutslag]` og R1–R3 som rene funksjoner (AD-1). Hvert utslag har en setning på enkel norsk med de faktiske tallene. Grensetilfellene ligger som konstruerte FHI-svar i `backend/tests/fixtures/konstruert/` (samme format som cachen, AD-4/AD-10), og `backend/tests/test_kontrollregler.py` tolker dem med `fhi.tolk` og tester reglene. Testen fra story 2.4 er med: en uke med flere positive enn tester og minst 30 tester telles ikke i R2.

**Irenes beslutninger (24.11.2026, samme PR):** Fotnoten for uker med flere positive enn tester blir «Flere positive prøver enn tester denne uka. Det kan skyldes hvordan prøvene er registrert. Tolk tallet med forsiktighet.» i PRD-en og alle andre dokumenter den står i. FR-10 sier at en uke med 0 tester og flere enn 0 positive er usikker og får fotnoten, men ingen andel. Begge merkes «Endret 24. november 2026: Irenes beslutning».

</frozen-after-approval>

## Implementation Notes

- Reglene regnes over alle uker i `serie.uker`, altså alle forventede uker (AD-3). «Mer enn 20 %» regnes med heltall (`antall * 100 > GRENSE_PROSENT_UKER * uker`), slik at 4/20 ikke gir utslag og 5/20 gir det, uten avrundingsfeil. En tom serie gir ikke utslag i R2 eller R3 (0 av 0 er ikke over 20 %), men R1 slår inn (0 positive).
- R1 summerer alle kjente `positive`, også i en uke der bare antall tester er skjult. Bare skjulte verdier (`None`) holdes utenfor, slik akseptansekriteriet sier.
- R2 teller uker med `tester is not None and tester < GRENSE_USIKKER_UKE`. Den bruker ikke `Uke.usikker`, som også er sann for skjult antall tester og for flere positive enn tester (deferred-work fra story 2.4). En uke med 0 tester teller i R2.
- R3 teller uker med `Uke.manglende`. En uke med to skjulte verdier er én uke.
- Setningene: R1 «Utvalget har bare 19 positive prøver. Det trengs minst 20 for et sikkert tall.» (entall og «ingen» håndteres). R2 «5 av 20 uker har færre enn 30 tester.» R3 «3 av 10 uker mangler tall eller har skjulte tall.»
- Fixturene lages med en liten generator i scratchpad og lagres som vanlig JSON. README-en i `konstruert/` beskriver hver fil.
- Nye filer: `backend/src/backend/kontrollregler.py`, `backend/tests/test_kontrollregler.py` og seks fixturer `724-r1-*`, `724-r2-*`, `724-r3-*` i `backend/tests/fixtures/konstruert/` (beskrevet i README-en der). Fixturene er laget med et engangsskript og ikke sjekket inn som kode. Fixturen for R2 har både en uke med 30 tester, en med skjult antall tester og en med flere positive enn tester, slik at testen feiler hvis noen av dem telles.
- `vurder` gir R1–R3 i denne storyen. R4 og R5 kommer i story 2.8.

## Review Triage Log

Gjennomgang av 2.7 og 2.8 samlet med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Ingen alvorlige funn, og ingenting som krever endring i PRD eller arkitektur utover Irenes beslutninger.

- **medium, rettet:** R1 sa «ingen positive prøver» når tallene bare var skjult. Setningen sier nå «kjente» når noen tall er skjult.
- **low, rettet:** feil datoformat på `last_updated` i sprint-status, `deferred-work.md` var ikke oppdatert, fotnoten var feilmerket i epic-2-konteksten, FR-10 i epics var tung å lese, formelen i specen stemte ikke med koden, testene krasjet med `AttributeError` i stedet for å feile tydelig, testene sjekket ikke hvilken uke som manglet, og fixtur-README-en forklarte ikke `pos_rate`.
- **false:** en uke med kjent antall tester under 30 og skjult antall positive telles i både R2 og R3. Det følger akseptansekriteriet (R2 teller kjent antall tester under 30). Å fjerne den fra R2 ville svekket regelen.
- **false:** R1 og R4 gir begge utslag for en tom serie. Reglene er uavhengige, og FR-19 sier at varselet lister hver regel som slo inn.
- **avvist:** ordlisten i PRD dekker allerede 0 tester (0 er færre enn 30, og positive er flere enn tester). Tegnforklaringen i skissen er et eksempel. AK-en i story 2.1 er historisk.
- **utsatt:** fotnoteteksten finnes ikke i koden ennå. Den lages i story 3.2/3.3, se deferred-work.md.
