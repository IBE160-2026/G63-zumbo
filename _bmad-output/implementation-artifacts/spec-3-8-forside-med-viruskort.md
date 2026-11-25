---
title: 'Story 3.8: Forside med viruskort'
type: 'feature'
created: '2026-11-25'
status: 'done'
baseline_commit: '792b655549ff05cf6702f3fa905855eb12617d0f'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** En testperson sa 25.11.2026: «at appen mangler overganger som en forside, at når man trykker så kommer man til en annen side, at den gjør for lite». I dag er `GET /` ett skjema uten tall før brukeren har valgt (FR-27, issue #72).

**Approach:** Irenes beslutning: `GET /` blir en forside med tre viruskort, og hovedskjermen flyttes til `GET /resultat` (AD-9, endret 25.11.2026). Forsiden har:
- overskriften «Tall fra FHI om luftveisvirus»;
- introteksten ordrett: «Se hvordan influensa, RSV og koronavirus utvikler seg uke for uke i Norge, med tall fra Folkehelseinstituttet. Appen sier fra når tallene er for usikre til å trekke konklusjoner, og forklarer ordene underveis.»;
- tre kort;
- FR-26-teksten, som flyttes hit fra resultatsiden;
- avsenderlinjen.

Hvert kort er en lenke til resultatsiden for viruset, med sesongen som pågår og alle aldre. Kortet viser virusnavnet, andelen positive i siste uke med tall og hvilken uke det gjelder. Resultatsiden har en tydelig lenke tilbake til forsiden, og der kan sesong og aldersgruppe endres som før. Gamle `/?…`-adresser sendes videre med `301`. README og testene oppdateres. Alt skal virke med tastatur og på mobil, med de samme fargene og skriftene som før.

## Boundaries & Constraints

**Always:**
- Valg sjekkes bare i `Utvalg.fra_parametre` (AD-9).
- Kortene bruker `tjeneste.svar` og samme mellomlager som resultatsiden, så ingen ny henting fra FHI legges til.
- Brukeren ser ingen FHI-koder (NFR-3).
- Farger finnes bare som variabler i `:root` (test_stil).
- Testene kaller aldri FHI eller Claude (AD-10).
- `GET /forklaring` og skjemafeltene i `POST /hent-nyeste` er uendret.

**Never:**
- Ingen KI-forklaring på forsiden.
- Ingen nye farger eller skrifter.
- Ingen endring i kontrollreglene, `fhi` eller `domene`.
- Ingen endring i PRD-en eller arkitekturen utover det som allerede er committet.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Forside med tall | `GET /` når tallene er lagret eller FHI svarer | Tre kort i rekkefølgen influensa, RSV, SARS-CoV-2. Hvert kort har en `href` til `/resultat?mal=1&virus=…&sesong=<nyeste>&alder=alle`, andelen i den siste uka med andel (for eksempel «20,8 %») og «uke 50» | N/A |
| Siste uke er usikker | Den siste uka med andel er usikker | Kortet viser andelen og «usikker uke» i tekst | N/A |
| FHI nede, lagrede tall | `sist_lagrede` | Kortet viser andelen og «Sist lagrede tall, hentet …» | N/A |
| Ingen tall | `serie is None`, eller ingen uke har andel | Kortet viser en kort norsk tekst om at tallene ikke kan vises nå. Lenken virker fortsatt | Uventet unntak for ett kort logges, og det kortet viser samme tekst. Siden gir aldri 500 |
| Gammel adresse | `GET /?mal=1&virus=rsv&sesong=2025/2026&alder=alle` (også med `nyeste_feilet`) | `301` til `/resultat?` med samme query-streng | N/A |
| Resultatside uten valg | `GET /resultat` uten parametre eller med bare tomme parametre | `303` til `/` | N/A |
| Ugyldig valg | `/resultat?virus=ebola…` | Feilmeldingen fra `fra_parametre` og lenken til forsiden. Ingen henting | N/A |
| Hent nyeste | `POST /hent-nyeste` | `303` til `/resultat?…` | Som før (FR-8) |

</frozen-after-approval>

## Code Map

- `backend/src/backend/web.py`:
  - Ruten `forside` (`GET /`) deles i tre: forsiden med kort, `resultat` (`GET /resultat`, dagens logikk) og `301` for gamle adresser når minst ett av `PARAMETRE` eller `NYESTE` har en verdi.
  - `hent_nyeste` sender videre til `/resultat?`.
  - Sesongen som pågår er `tjeneste.sesonger(nå)[-1]`. Lag en `Utvalg` per virus i `VIRUS` (mal 1, alder `STANDARD_ALDERSGRUPPE`), kall `tjeneste.svar` for hvert av dem, og legg et `try/except Exception` med logging rundt hvert kort.
  - Kortdataene, «siste uke med andel», lages i en liten ren hjelper som kan testes. Gjenbruk filtrene `andel`, `uke` og `tidspunkt` fra `formatering`.
- `backend/src/backend/templates/index.html`:
  - Fil som skal deles: lag `forside.html` (nytt) og `resultat.html` (dagens innhold).
  - På resultatsiden:
    - Overskriften viser viruset (for eksempel «Influensa»).
    - Over den står lenken «← Til forsiden» (`href="/"`).
    - Skjemaet har `action="/resultat"`, `mal` og `virus` som `<input type="hidden">`, og bare sesong og aldersgruppe som synlige `<select>`.
    - Seksjonen `om-appen` (FR-26) flyttes til forsiden.
  - Ved ugyldig virus vises feilmeldingen og lenken, uten skjema.
- `backend/src/backend/templates/base.html` -- avsenderlinjen og blokkene, uendret.
- `backend/src/backend/static/style.css`:
  - Kortene står i et rutenett: tre kolonner på brede skjermer og én kolonne ved 360 piksler.
  - Hele kortet er én `<a>` med synlig `:focus-visible`. Bruk bare de eksisterende variablene.
- `backend/src/backend/static/app.js` -- trenger trolig ingen endring. Sjekk at ingenting peker på `/`.
- `README.md`:
  - «Starte appen»: forsiden på `/` og resultatsiden på `/resultat`.
  - Avsnittet om `vis_forklaring.py` sier «velg et utvalg og trykk «Vis tallene»». Det må passe forsiden, for eksempel «trykk på et viruskort».
- Tester som bruker `klient.get("/?…")` eller sjekker skjemaet på `/`:
  - `test_web.py`, `test_web_tabell.py`, `test_web_hent_nyeste.py` (Location `/?` → `/resultat?`), `test_web_varsel.py`, `test_web_graf.py`, `test_web_forklaring.py`, `test_web_begreper.py` og `test_stil.py` (chatbot-teksten står nå på `/`, og `<label>` sjekkes på `/resultat`).
  - Mønsteret for fixtures og mocking står øverst i `test_web.py`. Fixtures for 729 og 731 finnes i `tests/fixtures/fhi/`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/src/backend/web.py` -- rutene `/`, `/resultat`, omdirigeringen og kortdataene -- FR-27, AD-9
- [x] `backend/src/backend/templates/forside.html`, `resultat.html` (erstatter `index.html`) -- forsiden og resultatsiden -- FR-26, FR-27
- [x] `backend/src/backend/static/style.css` -- kort og rutenett, fokus, 360 piksler -- NFR-4, NFR-5, NFR-11
- [x] `README.md` -- adressene og forsiden
- [x] Tester:
  - Ny `backend/tests/test_web_forside.py` med hele matrisen over, at introteksten står ordrett, at kortene står i riktig rekkefølge med riktige lenker, at sesongen som pågår er valgt, at det ikke finnes FHI-koder, at FR-26 står på forsiden og ikke på resultatsiden, og lenken tilbake.
  - Oppdater de eksisterende testene i Code Map.

**Acceptance Criteria:**
- Given forsiden, when Sara bruker Tab, then kan hvert kort nås, og fokus er synlig. Enter åpner resultatsiden.
- Given resultatsiden, when Sara endrer sesong eller aldersgruppe og trykker «Vis tallene», then vises det nye utvalget for samme virus på `/resultat`.
- Given `uv run pytest` og `uv run ruff check`/`ruff format --check`, then er alt grønt uten nett.

## Implementation Notes

- Ikke commit; hovedøkten committer.
- Gjennomgangen er rettet etter `Review Triage Log`. 905 tester består, og ruff er grønn.
- Prøvd mot ekte FHI med egen cache: tre kort med tall i uke 46, kortlenken åpner resultatsiden, og gamle adresser gir `301`.

## Spec Change Log

## Review Triage Log

Kodegjennomgang 25.11.2026 med fire lag: blind-hunter (BH), edge-case-hunter (EC), verification-gap (VG) og acceptance-auditor (AA). Ingen alvorlige funn, ingen som krever endring i PRD eller arkitektur. 9 rettet, 0 utsatt, 15 avvist.

| # | Lag | Funn | Vurdering | Begrunnelse / rettelse |
|---|-----|------|-----------|------------------------|
| 1 | AA | `try/except` i `forside` dekker bare `tjeneste.svar`, ikke `Utvalg(...)` og `viruskort(...)` | low, patch | Rettet: hele kortet lages inne i `try`, med test. |
| 2 | VG+AA+BH | Når sesonglisten feiler, lenker kortene til `sesong=` (tom), og grenen er ikke testet | low, patch | Rettet: `try` rundt sesonglisten er fjernet. `tjeneste.sesonger` har allerede reserven `sesonger_fra_dato` når FHI er nede (AD-3), så sesongen er aldri tom. En reserve i `web` ville gitt en import fra `web` til `sesong`, som diagrammet i AD-1 ikke tillater. Testen for FHI nede sjekker nå den faktiske sesongen i lenken. |
| 3 | BH | Ingen test for antall kall til FHI på forsiden når FHI er nede | low, patch | Rettet: test for nøyaktig ett kall. Pausen i `tjeneste` gjør at kortene ikke venter på hvert sitt tidsavbrudd. |
| 4 | VG+BH | `<title>` med virusnavn er ikke testet | low, patch | Rettet. |
| 5 | VG+BH | Tre tester ber fortsatt om `/`, som nå er forsiden, og sjekker derfor ingenting | low, patch | Rettet: tilfellene bruker en ugyldig `/resultat`-adresse. |
| 6 | BH | Like tester i `test_web.py` og `test_web_forside.py` | low, patch | Rettet: én av hver er beholdt. |
| 7 | VG | Docstringen i `scripts/vis_forklaring.py` sier «Vis tallene» | low, patch | Rettet. |
| 8 | EC | Docstringen i `hent_nyeste` lover feilmelding også for et helt tomt utvalg, som havner på forsiden | low, patch | Rettet. |
| 9 | BH | README nevner ikke at gamle adresser sendes videre | low, patch | Rettet. |
| 10 | BH+EC | Forsiden bruker sesongen fra 724 for alle tre virus | false | Alle tre tabellene har samme uker (sjekket 25.11.2026, `SESONGTABELL`), og sesonglisten har bare sesonger med publiserte uker. |
| 11 | EC | Kortet viser samme tekst for «ikke publisert» og «FHI nede» | low, avvist | Sesongen som pågår har alltid publiserte uker (#10), så «ikke publisert» skjer nesten ikke. Resultatsiden viser den presise meldingen. |
| 12 | BH | Kortene viser ikke hentetidspunkt når FHI svarer | low, avvist | Resultatsiden viser kilde og hentetidspunkt. Kortet viser tidspunktet når tallene er de sist lagrede, slik FR-8 krever. |
| 13 | BH | «usikker uke» på kortet forklares ikke | low, avvist | Resultatsiden har varsel, fotnote og begrepsforklaring. Kortet sier fra i tekst. |
| 14 | BH | Skjermleseren leser hele kortet som lenketekst | low, avvist | Teksten er kort og gir virus, andel og uke, som er nyttig. Ingen feil. |
| 15 | BH | Introteksten sier «koronavirus», kortet «SARS-CoV-2» | low, avvist | Valg i Design Notes (`Virus.navn`). Nevnt for Irene i oppsummeringen. |
| 16 | BH+EC | `301` er varig, og `/?nyeste_feilet=…` alene gir to omdirigeringer | low, avvist | `/` med valg blir aldri forsiden igjen (AD-9). Bare `nyeste_feilet` kommer ikke fra appen. |
| 17 | BH+AA | Mal og virus kan ikke endres på resultatsiden, og malspørsmålet vises ikke | false | Slik er intensjonen: «Der kan sesong og aldersgruppe endres som før». Mal 2 (epic 8) må få et eget valg. |
| 18 | EC+AA | Ugyldig `mal` med gyldig virus gir «Velg en mal» uten malvalg, og det skjulte feltet blir 1 | low, avvist | Kan bare skje med en adresse som er endret for hånd. Skjemaet gir da mal 1, som er den eneste. |
| 19 | EC | Et helt tomt `POST /hent-nyeste` havner på forsiden uten melding | low, avvist | Kan bare skje med et skjema som er laget for hånd. Docstringen er rettet (#8). |
| 20 | EC | Gamle adresser med bare tomme valg sendes ikke videre | false | Villet og testet. Tomme valg er ingen valg. |
| 21 | EC | Gyldig virus med andre ugyldige valg viser overskrift uten tall | false | Skjemaet og feilmeldingen vises, slik det skal. |
| 22 | BH | `Viruskort` hører hjemme i `formatering` | low, avvist | Ingen skade å peke på. `formatering` har bare filtre. |
| 23 | AA | Ingen automatisk test av synlig fokus på kortene | low, avvist | Kortene er `<a>`, og `a:focus-visible` er testet i `test_stil`. Tastatur og 360 piksler sjekkes for hånd av Irene. |
| 24 | AA | Epic-konteksten nevner malspørsmålet i skjemaet | false | Endringen følger intensjonen (#17). |

## Design Notes

Valg som er tatt i planleggingen:
- Kortet bruker `Virus.navn`, så SARS-CoV-2-kortet heter «SARS-CoV-2», likt resultatsiden.
- Forsiden kaller `tjeneste.svar` én gang per virus, etter hverandre. Med tomt mellomlager blir det opptil seks kall til FHI. Når FHI er nede, stopper pausen i `tjeneste` de neste kallene etter det første tidsavbruddet. Dette tas med i punktet for story 8.3.

## Verification

**Commands:**
- `cd backend && uv run pytest` -- expected: alle tester består
- `cd backend && uv run ruff check . && uv run ruff format --check .` -- expected: ingen funn

**Manual checks:**
- Start appen på en ledig port med egen `CACHE_DIR`. Sjekk at `/` viser tre kort med tall, at et klikk åpner resultatsiden, og at `/?mal=1&virus=rsv&sesong=2025/2026&alder=alle` blir sendt videre.
