---
title: 'Story 2.3: Sesonger, uker og utdaterte tall'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det finnes ingen felles kode for sesonger, ISO-uker og levetid for lagrede tall (issue #8). Uten den vil `fhi.tolk`, `tjeneste` og kontrollreglene regne perioder og «utdatert» hver på sin måte (FR-3, FR-7, AD-3, AD-5).

**Approach:** Skriv den rene modulen `backend/src/backend/sesong.py` med `uker(sesong, siste_publiserte_uke=None)` (uke 40 til og med uke 20 året etter, uke 53 som vanlig uke, avkortet ved siste publiserte uke), `sesonger_fra_dato(nå)` (fra 2024/2025 til den som pågår) og `er_utdatert(hentet, nå)` (24 timer eller mer, begge med tidssone). Modulen får «nå» som argument og importerer bare standardbiblioteket og `domene` (AD-1). Tester i `backend/tests/test_sesong.py` dekker uke 53, sesongstart og grensen på 24 timer.

</frozen-after-approval>

## Implementation Notes

- Nye filer: `backend/src/backend/sesong.py` og `backend/tests/test_sesong.py`.
- En uke er en tuple `(år, ukenummer)` i ISO-kalenderen. Tuplene sorteres riktig, så `siste_publiserte_uke` sammenlignes direkte. Ukekodene til FHI (`2025-w40`) tolkes i `fhi.py` (story 2.4), ikke her.
- `uker` gir en tuple med ukene i rekkefølge. Ligger siste publiserte uke før sesongstart, er resultatet tomt. Ligger den etter uke 20, gir det hele sesongen. En sesong som ikke er skrevet `ÅÅÅÅ/ÅÅÅÅ` med andre år = første år + 1, eller en uke som ikke finnes, gir `ValueError`.
- `sesonger_fra_dato(nå)`: en sesong er med når mandag i uke 40 i startåret har kommet, regnet i norsk tid (`Europe/Oslo` fra `zoneinfo`). Mellom sesongene (uke 21–39) er den siste sesongen som har startet, «den som pågår». Dette er en reserve uten nett (AD-3). Den kan vise en ny sesong i uke 40 før FHI har publisert noe for den. Listen starter alltid med 2024/2025, også når `nå` er tidligere.
- `er_utdatert(hentet, nå)` er `nå - hentet >= 24 timer`. Tid uten tidssone gir `ValueError`. Et `hentet` frem i tid gir `False` (ferskt). Det skjer bare hvis klokka er stilt tilbake, og da henter appen igjen når 24 timer har gått.
