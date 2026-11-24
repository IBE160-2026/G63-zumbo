---
title: 'Story 2.3: Sesonger, uker og utdaterte tall'
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

**Problem:** Det finnes ingen felles kode for sesonger, ISO-uker og levetid for lagrede tall (issue #8). Uten den vil `fhi.tolk`, `tjeneste` og kontrollreglene regne perioder og «utdatert» hver på sin måte (FR-3, FR-7, AD-3, AD-5).

**Approach:** Skriv den rene modulen `backend/src/backend/sesong.py` med `uker(sesong, siste_publiserte_uke=None)` (uke 40 til og med uke 20 året etter, uke 53 som vanlig uke, avkortet ved siste publiserte uke), `sesonger_fra_dato(nå)` (fra 2024/2025 til den som pågår) og `er_utdatert(hentet, nå)` (24 timer eller mer, begge med tidssone). Modulen får «nå» som argument og importerer bare standardbiblioteket og `domene` (AD-1). Tester i `backend/tests/test_sesong.py` dekker uke 53, sesongstart og grensen på 24 timer.

</frozen-after-approval>

## Implementation Notes

- Nye filer: `backend/src/backend/sesong.py` og `backend/tests/test_sesong.py`.
- En uke er en tuple `(år, ukenummer)` i ISO-kalenderen, med typenavnet `IsoUke` (ikke `Uke`, som er dataklassen i `domene`). Tuplene sorteres riktig, så `siste_publiserte_uke` sammenlignes direkte. Ukekodene til FHI (`2025-w40`) tolkes i `fhi.py` (story 2.4), ikke her.
- `uker` gir en tuple med ukene i rekkefølge. Ligger siste publiserte uke før sesongstart, er resultatet tomt. Ligger den etter uke 20, gir det hele sesongen. En sesong som ikke er skrevet `ÅÅÅÅ/ÅÅÅÅ` med andre år = første år + 1, eller en uke som ikke finnes, gir `ValueError`.
- `sesonger_fra_dato(nå)`: en sesong er med når mandag i uke 40 i startåret har kommet, regnet i norsk tid (`Europe/Oslo` fra `zoneinfo`). Mellom sesongene (uke 21–39) er den siste sesongen som har startet, «den som pågår». Dette er en reserve uten nett (AD-3). Den kan vise en ny sesong i uke 40 før FHI har publisert noe for den. Listen starter alltid med 2024/2025, også når `nå` er tidligere.
- `er_utdatert(hentet, nå)` regner `nå - hentet` i UTC og gir `True` ved 24 timer eller mer. Tid uten tidssone gir `ValueError`. Ligger `hentet` mer enn fem minutter frem i tid, har klokka vært feil, og tallene regnes som utdaterte. Først sto det her at et `hentet` frem i tid var ferskt, men da kunne tallene bli stående i X + 24 timer (endret etter gjennomgangen).
- Sesongformatet (`ÅÅÅÅ/ÅÅÅÅ`, andre år = første år + 1) sjekkes med `domene.er_sesong` (gjort offentlig i denne storyen), slik at `Utvalg.fra_parametre` og `sesong` godtar de samme sesongene. `domene` kan ikke importere `sesong` (AD-1), så regelen bor i `domene`.
- I uke 40 kan reserven si at en ny sesong har startet før FHIs dimensjonsliste har den. FHIs liste vinner når den finnes (AD-3). Det avgjøres i `tjeneste.sesonger` (story 2.9).

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Ett brudd på akseptansekriteriene (sommertid), rettet. Ingenting krever endring i PRD eller arkitektur.

- **high, rettet:** `er_utdatert` trakk fra veggklokketid når begge tidspunktene hadde samme `ZoneInfo`. Bekreftet: Oslo 24.10. kl. 12:00 til 25.10. kl. 11:00 (24 ekte timer) ga `False`. Over skiftet til sommertid ble tall utdaterte en time for tidlig. Regner nå i UTC, med tester over begge skiftene.
- **medium, rettet:** et `hentet` X timer frem i tid ga ferske tall i X + 24 timer. Mer enn fem minutter frem i tid gir nå `True`.
- **medium, rettet:** sesongregelen var kopiert fra `domene`. `startår` bruker nå `domene.er_sesong`, og en test sjekker at de er enige.
- **low, rettet:** `sesong.Uke` hadde samme navn som `domene.Uke`. Heter nå `IsoUke`.
- **low, rettet:** `siste_publiserte_uke` som tall, feil lengde eller `bool` ga `TypeError` eller ble godtatt. En liste ga `TypeError` i løkka. Gir nå `ValueError` eller blir gjort om til en tuple.
- **low, rettet:** AD-1-testen godtok hele standardbiblioteket og så bare etter attributter. Den har nå en fast liste over importer og sjekker også navn som `open` og `time`.
- **low, rettet:** testene manglet uke 53 i 2020/2021, sesongen 2024/2025, uke 21, 1. januar i ISO-uke 53, og sesonger som `None`, med linjeskift eller med andre siffertegn.
- **false:** `OverflowError` for `nå` nær `datetime.min`/`max`. Ingen kode sender slike tider.
- **false:** specen mangler akseptkriterier og testkommando. Det er en oneshot-spec. Akseptkriteriene står i issue #8, og ferdigkriteriene i epic-konteksten.
- **avvist (low):** `navn()` sjekker ikke typen. Den får bare `int` fra `startår` og `sesonger_fra_dato`.
