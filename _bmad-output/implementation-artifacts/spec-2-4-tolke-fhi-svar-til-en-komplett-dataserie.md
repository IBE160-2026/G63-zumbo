---
title: 'Story 2.4: Tolke FHI-svar til en komplett dataserie'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
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

- Endrede filer: ny `backend/src/backend/fhi.py`, `backend/src/backend/domene.py` (`Uke.usikker`, ny `Uke.flere_positive_enn_tester`), ny `backend/tests/test_fhi_tolk.py`, ny `backend/tests/fixtures/konstruert/724-skjulte-verdier.json`, PRD kapittel 3 og FR-10, `epic-2-context.md` og `deferred-work.md`.
- `tolk(rått_svar, utvalg, siste_publiserte_uke=None)`: den tredje parameteren er valgfri. `tjeneste` (2.9) sender inn uka fra dimensjonslisten (AD-3). Uten den brukes den høyeste uka i svarets egen ukedimensjon. Da kan `tolk` fortsatt kalles som i akseptansekriteriet.
- `rått_svar` er innholdet i `svar` (ikke hele cachefila med `hentet`).
- Tolkingen følger `id` og `size` i `json-stat2`. Den finner ikke plassene ved å anta rekkefølge. `category.index` kan være en liste eller et objekt, og `value` kan være en liste eller et objekt med plass → verdi. En plass som mangler, blir `None`.
- Svaret må gjelde utvalget: aldersgruppen er `ALDERSGRUPPER[...].fhi_kode`, og for tabell 724 er influensatypen `A+B` og overvåkingstypen `NONSTL`. Andre dimensjoner enn uke og måltall må ha nøyaktig én kategori. Ellers gir `tolk` `ValueError` (et ugyldig svar, som `fhi.hent` i 2.5 gjør om til `FhiUtilgjengelig`).
- Tall: et heltall, eller et desimaltall uten desimaler (`64.0`), godtas. Tekst som er en skjult verdi, blir `None`. Annen tekst, `bool` og negative tall gir `ValueError`. FHIs `pos_rate` brukes ikke (andelen regnes i `Uke`), men testen sjekker at den stemmer med den utregnede innen 0,0001 prosentpoeng.
- Ukekoder har formen `ÅÅÅÅ-wUU` med liten `w`. En kode som ikke har den formen, gir `ValueError`.
- `sesonger(dimensjoner)` gir hver sesong som har minst én uke mellom uke 40 og uke 20 i dimensjonslisten, eldste først, fra 2024/2025. Uker 21–39 hører ikke til noen sesong.
- FHI-kodene (`dateusedforstatistics`, `MEASURE_TYPE`, `Detections`, `Tests`, `A+B`, `NONSTL`) finnes bare i `fhi.py` og `domene.py` (AD-2).
