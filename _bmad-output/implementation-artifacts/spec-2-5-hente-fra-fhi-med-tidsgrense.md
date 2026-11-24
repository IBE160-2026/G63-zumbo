---
title: 'Story 2.5: Hente fra FHI med tidsgrense'
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

**Problem:** Appen kan ikke hente tall fra FHI (issue #10). Uten en tidsgrense og én feiltype vil en treg eller nede FHI kunne henge siden eller gi en ukontrollert feil (FR-8, AD-3).

**Approach:** Legg `fhi.hent(utvalg, siste_publiserte_uke)` og `fhi.hent_dimensjoner(tabell)` i `backend/src/backend/fhi.py`. De bruker `httpx` med 10 sekunders tidsgrense mot `statistikk-data.fhi.no`, og alle feil (tidsavbrudd, nettverksfeil, HTTP-feil, ugyldig svar) blir `FhiUtilgjengelig`. Forespørselen bruker tabellen for viruset, `NONSTL`, `A+B`, valgt aldersgruppe og ukene i sesongen frem til siste publiserte uke. `fhi.py` er den eneste modulen som kaller FHI. Tester i `backend/tests/test_fhi_hent.py` bruker `respx` med fixturen fra 1.3, tidsavbrudd, status 500 og ugyldig svar.

</frozen-after-approval>

## Implementation Notes

- Endrede filer: `backend/src/backend/fhi.py`, ny `backend/tests/test_fhi_hent.py`, og AD-1-testen i `backend/tests/test_fhi_tolk.py`. Den forbød `httpx` i hele `fhi.py`. Nå sjekker den at tolkefunksjonene ikke bruker `httpx`, mens hentefunksjonene får lov.
- Adressene og kroppen står i `tests/fixtures/fhi/README.md`: `GET {BASE}/Table/{tabell}/dimension` og `POST {BASE}/Table/{tabell}/data`, der `BASE = https://statistikk-data.fhi.no/api/open/v1/msis`. Kroppen har alle fem dimensjonene med `"filter": "item"` og `"response": {"format": "json-stat2"}`.
- `hent` returnerer det rå svaret (`dict`) slik det skal lagres i cachen (AD-4). Før det sjekkes svaret med `tolk(svar, utvalg, siste_publiserte_uke)`. Et svar `tolk` ikke godtar, er et ugyldig svar og gir `FhiUtilgjengelig`. `hent_dimensjoner` sjekker på samme måte med `siste_publiserte_uke(svar)` og `sesonger(svar)`.
- Ukene er `sesong.uker(utvalg.sesong, siste_publiserte_uke)` skrevet som `ÅÅÅÅ-wUU`. En sesong som ikke har startet ennå (ingen uker), gir `ValueError`. Det er en programmeringsfeil, ikke en feil hos FHI.
- Tidsgrensen er `httpx.Timeout(10.0)`. Den gjelder hvert steg (tilkobling, sending, hver lesing), ikke hele kallet. En server som sender ett tegn hvert 9. sekund, kan derfor holde lenger enn 10 s. Det skjer ikke med FHI i praksis. En grense for hele kallet ville krevd en egen tråd.
- `FhiUtilgjengelig` arver fra `Exception` og har den opprinnelige feilen som `__cause__`, slik at `tjeneste` kan logge detaljene (AD-3). Meldingen er teknisk og vises ikke til brukeren.
- En `httpx.Client` kan sendes inn (`klient=`) for tester og for gjenbruk. Ellers lages en ny klient per kall og lukkes etterpå.
