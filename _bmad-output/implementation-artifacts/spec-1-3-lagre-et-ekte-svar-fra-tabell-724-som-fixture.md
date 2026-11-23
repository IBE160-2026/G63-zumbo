---
title: 'Story 1.3: Lagre et ekte svar fra tabell 724 som fixture'
type: 'chore'
created: '2026-11-23'
status: 'in-progress'
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
