---
title: 'Story 2.9: Sette sammen svaret for et utvalg'
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

**Problem:** Delene fra story 2.3–2.8 (sesong, tolking, henting, mellomlager og kontrollregler) er ikke satt sammen, så web (epic 3) har ikke ett svar å vise for et utvalg (issue #14, FR-7, FR-8, AD-9). To åpne punkter må også løses: sesonglisten må la FHIs ukeliste vinne over reservelisten (fra 2.3), og et utvalg med RSV eller SARS-CoV-2 skal gi en norsk melding i stedet for å krasje (fra 2.5).

**Approach:** Ny modul `tjeneste.py` med klassen `Tjeneste(innstillinger, klient=None)` og metodene `svar(utvalg, nå)` og `sesonger(nå)`. `svar` bruker ferske lagrede tall, ellers henter den nye fra FHI og lagrer dem. Når FHI er nede, brukes lagrede tall merket «sist lagrede», ellers gir svaret en norsk melding. Kontrollreglene kjøres alltid. Samtidige kall for samme utvalg deler ett kall til FHI. Tester med `respx` og `tmp_path`.

</frozen-after-approval>

## Implementation Notes

- **Resultat:** dataklassen `tjeneste.Resultat` har `utvalg`, `serie` (`Dataserie | None`), `regelutslag` (tuple), `kilde` (`Kildehenvisning | None`, med hentetidspunktet), `sist_lagrede` (bool) og `melding` (norsk tekst eller `None`). Ingen tall gir `serie=None` og en melding. `web` formaterer «Sist lagrede tall, hentet …» fra `kilde.hentet` (FR-8, AD-5).
- **Meldinger (faste, uten FHI-koder):** virus som ikke er klart: «Tall for RSV kan ikke vises i appen ennå. Velg influensa.» FHI nede med lagrede tall: «Tallene kunne ikke hentes fra FHI akkurat nå. Du ser de sist lagrede tallene.» FHI nede uten lagrede tall: «Tallene kunne ikke hentes fra FHI akkurat nå, og det finnes ingen lagrede tall for dette utvalget. Prøv igjen senere.» Sesong uten publiserte uker: «FHI har ikke publisert tall for sesongen 2026/2027 ennå. Prøv igjen senere.»
- **RSV/SARS-CoV-2:** stoppes før cache og FHI når tabellen ikke finnes i `fhi.FASTE_FILTRE` (åpnes i epic 6 uten endring i `tjeneste`).
- **svar:** fersk lagret fil (`sesong.er_utdatert`) som kan tolkes → brukes uten kall. Ellers hentes dimensjonslisten (fersk lagret eller ny), siste publiserte uke finnes, og `fhi.hent` kalles. Lagret svar tolkes med `fhi.tolk(svar, utvalg)` uten siste uke (svaret har ukene som ble bedt om). En lagret fil som ikke kan tolkes, regnes som manglende. `OSError` ved lagring logges, og tallene vises likevel.
- **sesonger:** fersk lagret dimensjonsliste, ellers ny fra FHI (lagres). FHI nede: lagret liste selv om den er gammel. Bare uten gyldig lagret liste brukes `sesong.sesonger_fra_dato(nå)`. Listene blandes aldri, så FHIs liste vinner (åpent punkt fra 2.3). Sesonglisten hentes fra tabell 724 til epic 6.
- **Samtidighet:** én pågående jobb per nøkkel (`Utvalg.nøkkel` og en egen nøkkel for dimensjonslisten). Andre kall venter på samme resultat, også ved feil, slik at to kall gir ett kall til FHI. Tråder, fordi `fhi.hent` er synkron.
- **Logging:** `FhiUtilgjengelig` og lagringsfeil logges på nivå INFO med årsaken (AD-9, kapittel 5).
- Ikke med: tvungen henting for `POST /hent-nyeste` (story 4.6).
- Feiler dimensjonslisten, prøves ikke datakallet i tillegg, slik at brukeren venter høyst én tidsgrense (10 s) før lagrede tall vises. `sesonger` bruker en gammel lagret liste når FHI er nede.
- Endret: `backend/src/backend/tjeneste.py` (ny), `backend/tests/test_tjeneste.py` (ny), `backend/src/backend/fhi.py` (typenavnet `fhi.Klient = httpx.Client`, fordi en test krever at bare `fhi.py` importerer `httpx`, AD-3) og `README.md` (avsnittet om mellomlageret).

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Alle akseptansekriteriene i #14 er oppfylt. Ingen alvorlige funn, og ingenting som krever endring i PRD eller arkitektur.

- **medium, rettet:** loggen skrev bare `feil.__cause__`, som er `None` for «svaret er ikke et JSON-objekt» og en tom `TimeoutError` ved tidsavbrudd. Nå logges hele `FhiUtilgjengelig` med metode, URL og årsak.
- **medium, rettet:** sjekken av om den lagrede dimensjonslisten er fersk lå utenfor den delte jobben, så to samtidige `sesonger`-kall (eller kall for ulike utvalg) kunne gi to kall til FHI. Sjekken ligger nå inne i jobben. Testet med samtidige sesongkall, både med FHI oppe og nede.
- **medium, rettet:** samtidighetstesten viste ikke at det andre kallet ventet. Det kunne ha lest den ferske cachen i stedet. Testen bruker nå en `Future` som sier fra når noen venter, sjekker at trådene er ferdige og har en variant med FHI nede. Begge testene feiler når delingen fjernes.
- **medium, rettet:** ingen test viste at en gammel dimensjonsliste hentes på nytt når FHI svarer, og valideringen i `_lagret_dimensjonsliste` ble aldri nådd. Nye tester for begge.
- **low, rettet:** docstringen til `Resultat` sa at `melding` betyr ingen tall (gjelder ikke «sist lagrede»), meldingstesten sjekket malene og ikke ferdig tekst, en lagret dimensjonsliste som ikke kunne brukes ble forkastet uten logg, og testen for lagringsfeil sjekket ikke loggen.
- **low, avvist:** når bare dimensjonslisten feiler, kunne en gammel lagret liste brukes til å prøve datakallet. Det kan doble ventetiden til 20 s når FHI er helt nede (FR-8, NFR-2). Valget står i Implementation Notes.
- **low, avvist:** `nå` uten tidssone gir `ValueError` etter et vellykket kall til FHI. Feilen er høylytt, og `sesong` krever allerede tidssone, så `web` (epic 3) må lage `nå` med tidssone.
- **low, avvist:** de som venter, har ingen egen tidsgrense, får eierens «nå» og deler samme unntaksobjekt. Ventetiden er begrenset av `fhi` (10 s), «nå» er millisekunder unna, og delt unntak er vanlig oppførsel for `concurrent.futures`. Står i docstringen.
- **low, avvist:** et vellykket svar tolkes to ganger (`fhi.hent` sjekker med `tolk`). Å endre det krever ny returtype i `fhi.hent`.
- **low, avvist:** README sier ikke noe om sesongliste og RSV-melding. README beskriver oppsett, ikke oppførsel i appen.
- **false:** `ValueError` fra `fhi.hent` eller `Utvalg.nøkkel` og `KeyError` for ukjent virus. Tabellen og ukene sjekkes før `fhi.hent`, og utvalg fra brukeren lages bare med `Utvalg.fra_parametre`.
- **false:** spec og sprint-status står som `in-progress`. De settes til `done` etter gjennomgangen.
