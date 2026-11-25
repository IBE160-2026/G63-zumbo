# Story 3.8: Forside med viruskort

## 2026-11-25 kl. 13:18 — Irene Zumbo

### Oppgave
En testperson sa 25.11.2026, ordrett: «at appen mangler overganger som en forside, at når man trykker så kommer man til en annen side, at den gjør for lite». Irene bestemte at appen skal få en forside med tre viruskort. Jeg skulle:
- opprette issuet;
- legge storyen inn i epics.md og sprint-status;
- legge FR-27 inn i PRD-en og de nye adressene i arkitekturen;
- bygge på branchen `story-3.8` med bmad-build og bmad-code-review;
- sette 3.8 til done, pushe til ibe og lage en PR med «Closes #72». Irene merger selv.

### Plan
- Issue #72 og plandokumentene først: `epics.md`, `sprint-status.yaml`, FR-27 i PRD-en, FR-26 flyttet til forsiden, og AD-9 i arkitekturen med `GET /`, `GET /resultat` og `301` for gamle adresser.
- Epic 3-konteksten ble laget på nytt fordi plandokumentene var endret.
- bmad-build (dispatch) med spec-en i `_bmad-output/implementation-artifacts/spec-3-8-forside-med-viruskort.md`. Irene ba meg kjøre uten å vente, så sjekkpunktet ble godkjent på hennes vegne.
- bmad-code-review med fire lag. Funnene er rettet eller begrunnet i «Review Triage Log» i spec-en.

### Resultat
- Issue #72 er opprettet med tilbakemeldingen ordrett og Irenes beslutning.
- `77f14ac`: plandokumentene. FR-27 er merket «Lagt til 25. november 2026: Irenes beslutning etter tilbakemelding fra testperson».
- `fa213ee`: epic 3-konteksten er laget på nytt.
- `3faaad8`, `4bada9b`, `cd56ef6`, `fc07490`:
  - `GET /` er forsiden med overskrift, introteksten, tre kort, chatbot-teksten og avsenderlinjen.
  - Hvert kort lenker til `/resultat` for sesongen som pågår og alle aldre, og viser andelen og uka. Når den siste uka er usikker, står «usikker uke» i tekst. Når tallene er de sist lagrede, står «Sist lagrede tall, hentet …». Når det ikke finnes tall, står det at de ikke kan vises.
  - Resultatsiden har «← Til forsiden», viruset i `<h1>` og `<title>`, og et skjema med bare sesong og aldersgruppe. Mal og virus følger med som skjulte felt.
  - Gamle `/?…`-adresser får `301` til `/resultat`, og «Hent nyeste tall nå» sender til `/resultat`.
- Kodegjennomgangen: 9 rettet, 0 utsatt, 15 avvist. Ingen alvorlige funn og ingen endring i PRD eller arkitektur utover FR-27 og AD-9.
  - `e9f0191`, `e91de1e`, `d650acd` er rettelsene. Ett av funnene la til en import fra `web` til `sesong`, men den bryter med AD-1. Jeg fjernet den, fordi `tjeneste.sesonger` allerede har en reserve.
- `c5e352a`: 3.8 og epic 3 er satt til done.
- pytest: 905 passed. ruff: OK.
- Prøvd mot ekte FHI på port 8038 med egen cache. Forsiden kom etter 0,7 s med tom cache og viste influensa 7,6 %, RSV 0,3 % og SARS-CoV-2 6,7 %, alle i uke 46. Den gamle adressen gav 301, og resultatsiden for SARS-CoV-2 var riktig.
- Punktet om «[virus]» og «[sesong]» i spørsmålsfeltet er lukket, fordi malvalget ikke vises lenger.

### Åpne punkter
- Irene: sjekke forsiden i nettleseren med Tab (synlig fokus på kortene, Enter åpner resultatsiden) og ved 360 piksler (kortene under hverandre, ingen vannrett rulling).
- Irene: vurdere om SARS-CoV-2-kortet bør si «koronavirus», slik introteksten gjør. Nå står det «SARS-CoV-2», likt resultatsiden.
- Før publisering (story 8.3): forsiden med tom cache gjør opptil seks kall til FHI (724-listen, tre dimensjonslister og tre datakall, der 724-listen deles).
- Mal 2 (epic 8): resultatsiden har ikke lenger noe malvalg. Mal 2 må få et eget valg, for eksempel på forsiden.
