---
title: 'Story 2.5: Hente fra FHI med tidsgrense'
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

**Problem:** Appen kan ikke hente tall fra FHI (issue #10). Uten en tidsgrense og én feiltype vil en treg eller nede FHI kunne henge siden eller gi en ukontrollert feil (FR-8, AD-3).

**Approach:** Legg `fhi.hent(utvalg, siste_publiserte_uke)` og `fhi.hent_dimensjoner(tabell)` i `backend/src/backend/fhi.py`. De bruker `httpx` med 10 sekunders tidsgrense mot `statistikk-data.fhi.no`, og alle feil (tidsavbrudd, nettverksfeil, HTTP-feil, ugyldig svar) blir `FhiUtilgjengelig`. Forespørselen bruker tabellen for viruset, `NONSTL`, `A+B`, valgt aldersgruppe og ukene i sesongen frem til siste publiserte uke. `fhi.py` er den eneste modulen som kaller FHI. Tester i `backend/tests/test_fhi_hent.py` bruker `respx` med fixturen fra 1.3, tidsavbrudd, status 500 og ugyldig svar.

</frozen-after-approval>

## Implementation Notes

- Endrede filer: `backend/src/backend/fhi.py`, ny `backend/tests/test_fhi_hent.py`, og AD-1-testen i `backend/tests/test_fhi_tolk.py`. Den forbød `httpx` i hele `fhi.py`. Nå sjekker den at alle funksjoner unntatt skallet (`_kall`, `_kall_i_tråd`, `hent`, `hent_dimensjoner`) er rene. `fhi.py` importerer `httpx` øverst, slik arkitekturen legger opp til (`fhi.hent` bor i `fhi.py`, AD-3). AD-1 gjelder tolkefunksjonene.
- Adressene og kroppen står i `tests/fixtures/fhi/README.md`: `GET {BASE}/Table/{tabell}/dimension` og `POST {BASE}/Table/{tabell}/data`, der `BASE = https://statistikk-data.fhi.no/api/open/v1/msis`. Kroppen har alle fem dimensjonene med `"filter": "item"` og `"response": {"format": "json-stat2"}`.
- `hent` returnerer det rå svaret (`dict`) slik det skal lagres i cachen (AD-4). Før det sjekkes svaret med `tolk(svar, utvalg, siste_publiserte_uke)`. Et svar `tolk` ikke godtar, er et ugyldig svar og gir `FhiUtilgjengelig`. `hent_dimensjoner` sjekker på samme måte med `siste_publiserte_uke(svar)` og `sesonger(svar)`.
- Ukene er `sesong.uker(utvalg.sesong, siste_publiserte_uke)` skrevet som `ÅÅÅÅ-wUU`. En sesong som ikke har startet ennå (ingen uker), gir `ValueError`. Det er en programmeringsfeil, ikke en feil hos FHI.
- Tidsgrensen: hele kallet kjøres i en egen tråd og gir opp etter 10 sekunder (`TOTAL_TIDSGRENSE`), også navneoppslaget og et svar som drypper inn. `httpx.Timeout(10.0)` gjelder i tillegg hvert steg, slik at tråden bak et kall som har gitt opp, stopper av seg selv. Først var det bare grensen per steg. Det ble endret etter gjennomgangen, fordi et kall da kunne vare mye lenger enn 10 s (FR-8).
- Ingen nye forsøk ved 429/503. `tjeneste` bruker lagrede tall i stedet (FR-8).
- Hodene er `Accept: application/json` og `User-Agent: fhi-helsedata/0.1`, uten personopplysninger.
- `FhiUtilgjengelig` arver fra `Exception` og har den opprinnelige feilen som `__cause__`, slik at `tjeneste` kan logge detaljene (AD-3). Meldingen er teknisk og vises ikke til brukeren.
- En `httpx.Client` kan sendes inn (`klient=`) for tester og for gjenbruk. Ellers lages en ny klient per kall og lukkes etterpå.

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Ingen alvorlige funn og ingenting som krever endring i PRD eller arkitektur.

- **medium, rettet:** grensen på 10 sekunder gjaldt hvert steg, ikke hele kallet. Navneoppslaget hadde ingen grense, og et svar som dryppet inn kunne holde kallet åpent lenge (FR-8). Hele kallet kjøres nå i en egen tråd med 10 sekunders grense. Det er testet med et kall som henger.
- **low, rettet:** `RecursionError` (dypt nøstet JSON), `httpx.StreamError`, `httpx.InvalidURL` og en lukket klient slapp ut som andre feil enn `FhiUtilgjengelig`. Bekreftet for nøstet JSON.
- **low, rettet (Verification Gap):** sjekken med `sesonger(svar)` i `hent_dimensjoner` hadde ingen test. Den kunne fjernes uten at noe feilet.
- **low, rettet:** testene for at bare `fhi.py` importerer `httpx` og kaller FHI, lette etter tekst og sammenlignet filnavn. De bruker nå AST og relative stier.
- **low, rettet:** AD-1-testen sjekket en fast liste over tolkefunksjoner. Nå sjekkes alle funksjoner unntatt skallet.
- **low, rettet:** testene sjekket ikke `__cause__` for ugyldige svar, og manglet 3xx og hodene. `Accept` og `User-Agent` er lagt til.
- **utsatt:** `hent` gir `ValueError` for RSV og SARS-CoV-2 og for en sesong uten publiserte uker. `tjeneste` (2.9) må håndtere det, se deferred-work.md.
- **avvist:** `fhi.py` importerer `httpx` øverst. Arkitekturen legger `fhi.hent` i `fhi.py` (AD-3), og AD-1 gjelder tolkefunksjonene. Det er nå testet funksjon for funksjon.
- **avvist (low):** ingen grense for hvor stort svaret kan være. FHI er den eneste verten, og svarene er små (fixturen er 7 kB). En grense ville krevd strømming.
- **avvist:** færre uker i svaret enn i forespørselen godtas. En uke FHI ikke sendte, skal bli en manglende uke (FR-16, AD-3).
- **avvist (low):** `forespørsel` gir `KeyError` for et `Utvalg` med ukjent virus eller aldersgruppe. Alle utvalg fra brukeren går gjennom `Utvalg.fra_parametre`.
- **avvist (low):** en dimensjonsliste med en uke langt frem i tid (`9999-w52`) godtas. Ingen grunn til å tro at FHI sender det, og `sesong.uker` takler det.
