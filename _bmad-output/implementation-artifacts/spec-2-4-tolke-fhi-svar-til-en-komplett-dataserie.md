---
title: 'Story 2.4: Tolke FHI-svar til en komplett dataserie'
type: 'feature'
created: '2026-11-24'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/backend/tests/fixtures/fhi/README.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det finnes ingen kode som gjør et rått `json-stat2`-svar fra FHI om til en `Dataserie` (issue #9). Uten den vil graf, tabell og kontrollregler kunne se ulike uker, og skjulte verdier kunne bli 0 (AD-3, FR-11, FR-16).

**Approach:** Lag de rene tolkefunksjonene i `backend/src/backend/fhi.py`: `tolk(rått_svar, utvalg)` gir én `Uke` per forventet uke i sesongen (fra `sesong.uker`) frem til siste publiserte uke. Skjulte verdier (`..`, `.`, `:`, tom, `null`) og uker FHI ikke sendte blir `None`. `siste_publiserte_uke(dimensjoner)` og `sesonger(dimensjoner)` lages fra dimensjonslisten `dateusedforstatistics`. Modulen importerer ikke `httpx` ennå (henting kommer i 2.5). Tester i `backend/tests/test_fhi_tolk.py` bruker fixturen fra 1.3 og et konstruert svar i `backend/tests/fixtures/konstruert/`.

**Irenes beslutning (24.11.2026):** Har en uke flere positive enn tester, vises andelen som den er (over 100 %), og uka er usikker med en fotnote på enkel norsk. R2 teller fortsatt bare uker med færre enn 30 tester. FR-10 i PRD-en og `Uke.usikker` i `domene.py` oppdateres med regelen, merket «Endret 24. november 2026: Irenes beslutning i story 2.4». Fixturen har ingen slike uker (sjekket: laveste antall tester er 3 987, og ingen uke har flere positive enn tester).

</frozen-after-approval>

## Implementation Notes

- Endrede filer: ny `backend/src/backend/fhi.py`, `backend/src/backend/domene.py` (`Uke.usikker`, ny `Uke.flere_positive_enn_tester`), `backend/src/backend/sesong.py` (`sjekk_uke` er gjort offentlig), ny `backend/tests/test_fhi_tolk.py`, `backend/tests/test_domene.py`, ny `backend/tests/fixtures/konstruert/724-skjulte-verdier.json` med README, PRD kapittel 3 og FR-10, FR-10 i `epics.md`, `epic-2-context.md` og `deferred-work.md`.
- `tolk(rått_svar, utvalg, siste_publiserte_uke=None)`: den tredje parameteren er valgfri. `tjeneste` (2.9) sender inn uka fra dimensjonslisten (AD-3). Uten den brukes den høyeste uka i svarets egen ukedimensjon. Da kan `tolk` fortsatt kalles som i akseptansekriteriet. Har svaret en høyere uke enn den som sendes inn, brukes svarets uke, slik at publiserte tall ikke forsvinner. Et svar med uker utenfor sesongen gir `ValueError`.
- `rått_svar` er innholdet i `svar` (ikke hele cachefila med `hentet`).
- Tolkingen følger `id` og `size` i `json-stat2`. Den finner ikke plassene ved å anta rekkefølge. `category.index` kan være en liste eller et objekt, og `value` kan være en liste eller et objekt med plass → verdi. En plass som mangler, blir `None`.
- Svaret må gjelde utvalget: aldersgruppen er `ALDERSGRUPPER[...].fhi_kode`, og for tabell 724 er influensatypen `A+B` og overvåkingstypen `NONSTL`. Andre dimensjoner enn uke og måltall må ha nøyaktig én kategori. Ellers gir `tolk` `ValueError` (et ugyldig svar, som `fhi.hent` i 2.5 gjør om til `FhiUtilgjengelig`).
- Tall: et heltall, eller et desimaltall uten desimaler (`64.0`), godtas. Tekst som er en skjult verdi, blir `None`. Annen tekst, `bool` og negative tall gir `ValueError`. FHIs `pos_rate` brukes ikke (andelen regnes i `Uke`), men testen sjekker at den stemmer med den utregnede innen 0,0001 prosentpoeng.
- Ukekoder har formen `ÅÅÅÅ-wUU` med liten `w`. En kode som ikke har den formen, gir `ValueError`.
- `sesonger(dimensjoner)` gir hver sesong som har minst én uke mellom uke 40 og uke 20 i dimensjonslisten, eldste først, fra 2024/2025. Uker 21–39 hører ikke til noen sesong.
- FHI-kodene (`dateusedforstatistics`, `MEASURE_TYPE`, `Detections`, `Tests`, `A+B`, `NONSTL`) finnes bare i `fhi.py` og `domene.py` (AD-2).
- Med 0 tester og positive over 0 er `andel` `None` (kan ikke dele på 0, samme regel som i story 2.1). Uka er usikker og har `flere_positive_enn_tester`, men er ikke manglende. Irene bør bekrefte dette tilfellet (åpent punkt).

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Ingen brudd på akseptansekriteriene. Ingenting krever endring i PRD eller arkitektur utover Irenes beslutning.

- **medium, rettet:** et svar for feil sesong ga en tom serie (to argumenter) eller 33 manglende uker (tre argumenter) uten feil. Bekreftet. Uker utenfor sesongen gir nå `ValueError`, som `fhi.hent` i 2.5 kan gjøre om til `FhiUtilgjengelig`.
- **medium, rettet:** uker i svaret etter `siste_publiserte_uke` forsvant uten varsel hvis dimensjonslisten var eldre enn svaret. Den høyeste uka i svaret brukes nå som nedre grense.
- **medium, rettet:** `category.index` som objekt ble ikke sjekket for hull eller dubletter, og dobbelte ukekoder ble slått sammen. Begge gir nå `ValueError`.
- **medium, rettet (Verification Gap):** tre kontroller hadde ingen test. Hver av dem kunne fjernes uten at noen test feilet: sortering etter plass i `index`, «nøyaktig én kategori» og manglende fast filter. Alle har nå tester.
- **low, rettet:** svært store tall (`10**400`) ga `OverflowError` i stedet for `ValueError`.
- **low, rettet:** `sesonger()` returnerte `()` for en liste uten sesonger, mens `siste_publiserte_uke()` feilet. Begge feiler nå, slik at `tjeneste` kan bruke reserven.
- **low, rettet:** regelen om flere positive enn tester var ikke testet gjennom `tolk`.
- **low, rettet:** `# type: ignore` i `Uke.flere_positive_enn_tester` er byttet ut med eksplisitte sjekker.
- **low, rettet:** testen for tre uker sammenlignet én andel med seg selv, og testen for `pos_rate` antok rekkefølgen i fixturen uten å sjekke den.
- **low, rettet:** FR-10 i `epics.md` hadde den gamle regelen. Specens liste over filer var ufullstendig, og den konstruerte fila manglet linjeskift til slutt.
- **utsatt:** fotnoten for flere positive enn tester har ingen eier i koden. Den lages i story 3.2/3.3, se deferred-work.md.
- **utsatt:** R2 (story 2.7) må ha en test som viser at slike uker ikke telles. Se deferred-work.md.
- **avvist (low):** forklaringen under skissen i PRD-en (`* færre enn 30 tester`) er ikke oppdatert. Skissen er bare en illustrasjon.
- **avvist:** `tolk` uten tredje argument tar siste uke fra svaret, ikke fra dimensjonslisten. Dette er bevisst og står i notatene. `tjeneste` sender alltid inn uka, og svar for feil sesong stoppes nå.
- **false:** et svar der `id` mangler uke eller måltall, men `dimension` har dem. Det ga `KeyError` → `ValueError` allerede. Nå er det en egen sjekk.
- **avvist (low):** `sesong.sjekk_uke` har ingen egen test. Den testes gjennom `sesong.uker` og `fhi.les_ukekode`.
