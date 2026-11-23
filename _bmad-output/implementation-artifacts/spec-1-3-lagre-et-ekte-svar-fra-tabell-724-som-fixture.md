---
title: 'Story 1.3: Lagre et ekte svar fra tabell 724 som fixture'
type: 'chore'
created: '2026-11-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Tolkingen i epic 2 skal bygges og testes mot ekte FHI-data uten nett, men `tests/fixtures/fhi/` er tom. Det er heller ikke bestemt om FHI-svaret skal hentes som CSV eller JSON, eller hvordan FLAGG-kolonnen ser ut (issue #3, arkitektur §8).

**Approach:** Hent én gang manuelt fra tabell 724: dataene for sesongen 2025/2026 (`2025-w40` til `2026-w20`), `Alle`, `NONSTL`, `A+B` og de tre måltallene, og dimensjonslisten. Lagre begge i cacheformatet `{"hentet": <ISO 8601 i UTC>, "svar": <rått svar>}`, dimensjonslisten som `724-dimensjoner.json`. Skriv valget av format og hvordan FLAGG ser ut i `tests/fixtures/fhi/README.md`. En test leser fixturene og sjekker `hentet`, `svar` og uke `2025-w40`.

</frozen-after-approval>

## Implementation Notes

- `tests/` er `backend/tests/`, som i 1.2.
- **API-et (fra FHIs swagger, `https://statistikk-data.fhi.no/swagger/OpenApi_v1/swagger.json`):** `POST …/msis/Table/724/data` med `{"dimensions": [{"code", "filter": "item", "values": [...]}, ...], "response": {"format": ...}}`. Alle dimensjoner må være med. Formatene er `json-stat2`, `csv2` (etiketter), `csv3` (koder) og `parquet`.
- **Valg: `json-stat2`.** Svaret er JSON, så `svar` blir et vanlig JSON-objekt i fixturen og ikke en CSV-streng med escaping. Tallene har riktig type, kodene (`NONSTL`, `pos_rate`) og de norske etikettene står begge i `dimension`, og `updated` sier når FHI sist endret tabellen. CSV ville krevd egen tolking av semikolon, anførselstegn og desimaler.
- **FLAGG (sjekket 23.11.2026):** `GET …/Table/724/flag` gir bare flagg 0 («Verdi finnes i tabellen»). I `csv3` er FLAGG `"0"` på hver rad, i `csv2` er den tom. I `json-stat2` ligger flaggene i `status` (tom streng her) og `extension.flags` (tom). En bredere spørring (alle aldersgrupper, `NONSTL`+`STL`, `A+B`/`A`/`B`, hele sesongen: 4 752 verdier) hadde ingen `null` og ingen andre flagg. Ekte data viser altså ikke skjulte verdier; de må testes med konstruerte data i epic 2.
- Ukene i forespørselen tas fra dimensjonslisten (33 uker; ISO-året 2025 har ikke uke 53).
- Filnavn for dataene: `724-influensa-2025-2026-alle-nonstl.json`. `Utvalg.nøkkel` finnes ikke før story 2.1, så navnet er bare for lesbarhet. Testene leser filene med navn.
- Hentingen gjøres med et lite engangsskript i scratchpad, ikke i repoet. Forespørselskroppen står i README-notisen, så den kan gjentas.
- Hentet 23.11.2026 kl. 21:20 UTC med `httpx` fra et engangsskript i scratchpad. Svaret har 33 uker × 3 måltall = 99 verdier. FHI oppdaterte tabellen sist 19.11.2026 (`updated`).
- `.gitkeep` i `fixtures/fhi/` er fjernet, siden mappen nå har filer. `test_fixturemapper.py` består fortsatt.
- Testen (`backend/tests/test_fhi_fixturer.py`) sjekker mer enn AC-en krever: at `hentet` er i UTC, at utvalget er det storyen ber om, og at dimensjonslisten har sesongens første og siste uke. Da oppdager vi det hvis noen bytter fixturen mot et annet utvalg.
- Rot-README-en sa at det første lagrede svaret kom i 1.3. Den peker nå til `fixtures/fhi/README.md`.
- Som i 1.1 og 1.2 ble oneshot-stegets Blind Hunter erstattet av en full `bmad-code-review`.

## Review Triage Log

Diff: `git diff main...HEAD` uten `backend/uv.lock` og `_bmad-output/`. Lag: Blind Hunter (BH), Edge Case Hunter (ECH), Verification Gap (VG), Acceptance Auditor (AA). VG fant ingen mangler. AA fant ingen brudd på akseptansekriteriene.

### Review Findings

- [x] [Review][Patch] Ingen test viste at fixturen har alle ukene i sesongen. En fixtur med en uke borte i midten ville bestått [backend/tests/test_fhi_fixturer.py] — low (BH+ECH+AA). Ukene sammenlignes nå med utsnittet `2025-w40`–`2026-w20` av dimensjonslisten, og det skal være 33 (243d21d).
- [x] [Review][Patch] README beskriver rekkefølgen i `value` (følger `id` og `size`), men ingen test sjekket den, og verdiene for uke 40 var ikke låst [backend/tests/test_fhi_fixturer.py] — low (BH+ECH+AA). Testen sjekker nå `id`, `size`, `len(value)` og de tre første tallene (243d21d).
- [x] [Review][Patch] README sier at svaret ikke har `null`, men ingen test sjekket det [backend/tests/test_fhi_fixturer.py] — low (ECH). Alle verdier må være tall (243d21d).
- [x] [Review][Patch] `assert innhold["svar"]` godtok også en CSV-tekst eller en feilmelding fra FHI [backend/tests/test_fhi_fixturer.py] — low (BH+ECH). `svar` må være et JSON-objekt, og dataene må ha `class: dataset` og `version: 2.0` (243d21d).
- [x] [Review][Patch] Forespørselen i README kunne ikke gjentas som den sto: `…` i ukelisten og ingen `Content-Type` [backend/tests/fixtures/fhi/README.md] — low (BH). Det står nå hva `…` betyr, og hvilken header som brukes (3bb2b8d).
- [x] [Review][Patch] README sa ikke hvordan en skjult verdi vil se ut i `json-stat2`, eller hvilke særheter tolkingen må passe på (`role.time` er `null`, `children: null` for `MEASURE_TYPE`, aldersgruppene ligger under `Alle`, liten `w` i ukekodene) [backend/tests/fixtures/fhi/README.md] — low (BH+ECH). Lagt til, og det står tydelig at formen på skjulte verdier er en antakelse (3bb2b8d).
- [x] [Review][Patch] Notisen skrev `tests/fixtures/konstruert/`, mens rot-README-en bruker `backend/tests/…` [backend/tests/fixtures/fhi/README.md] — low (BH+AA). Endret til full sti (3bb2b8d).
- [x] [Review][Defer] Arkitekturen §8 og epic-konteksten sier fortsatt at CSV eller JSON ikke er bestemt, og beskriver CSV-kolonnene [_bmad-output/planning-artifacts/architecture/architecture.md] — low (BH). Rettingen endrer planleggingsdokumentene, så den er ført i deferred-work.md.

**Avvist:**
- false (BH): sprint-status og specen var ikke satt til done. Det gjøres i dette steget, etter gjennomgangen.
- false (ECH): ukelisten for sesongen 2026/27 kan mangle uke 53. Ukene tas fra dimensjonslisten, ikke ved å telle 1–52, og fixturen gjelder bare 2025/2026.
- false (ECH): andre som kopierer den flate lesingen av kategoriene, går glipp av aldersgruppene. Ingen kode leser dimensjonslisten ennå, og testen trenger bare ukene. Hierarkiet står nå i README.
- low (ECH): `next(...)` gir `StopIteration` i stedet for en tydelig assert hvis ukedimensjonen mangler. Testen feiler uansett med en traceback som peker på linjen.
- low (BH): den bredere spørringen (4 752 verdier) er ikke lagret. Utvalget står i README, og en tredje fixtur ville gitt mer å vedlikeholde uten å teste noe nytt, siden svaret ikke har skjulte verdier.
- low (AA): `hentet` sjekkes ikke mot datoen i README-tabellen. En slik test ville låst to kopier av samme dato mot hverandre for liten nytte.
