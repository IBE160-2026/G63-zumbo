---
status: final
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-fhi-helsedata-2026-11-06/prd.md
  - _bmad-output/planning-artifacts/prds/prd-fhi-helsedata-2026-11-06/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture.md
---

# fhi-helsedata – epics og stories

## Oversikt

Dette dokumentet deler kravene i PRD-en (med addendum) og beslutningene i arkitekturen inn i epics og stories som kan bygges, testes og merges hver for seg. Det finnes ikke noe eget UX-dokument. Skissen av hovedskjermen i PRD kapittel 6.0 og tilgjengelighetskravene NFR-3–NFR-7 og NFR-11 brukes i stedet.

## Kravoversikt

### Funksjonelle krav

- FR-1: Brukeren kan velge en mal fra en liste. Mal 1 vises alltid, mal 2 bare hvis den er bygget. Malene vises som spørsmål på vanlig norsk.
- FR-2: Brukeren kan velge ett virus (influensa, RSV, SARS-CoV-2), og hvert virus hentes fra riktig tabell (724, 729, 731).
- FR-3: Brukeren kan velge én sesong med minst én publisert uke. Standard er siste sesong. Sesongen går fra uke 40 til og med uke 20 (eller siste publiserte uke), og uke 53 er en vanlig uke.
- FR-4: Brukeren kan velge aldersgruppe (frivillig, standard «Alle aldersgrupper»). De seks aldersgruppene tilbys, ikke «Ukjent alder».
- FR-5: Appen godtar bare gyldige utvalg. Mangler et felt eller har det en ugyldig verdi, hentes ingen data, og appen viser en norsk melding om hva som må rettes.
- FR-6: Appen henter positive prøver, tester og andel positive per uke for utvalget (riktig tabell, Non-Sentinel, totalen for virustypen, valgt aldersgruppe), og gir samme tall som fasiten for de 10 testspørsmålene.
- FR-7: Appen mellomlagrer hentede tall med hentetidspunkt. Tall som er 24 timer eller eldre, hentes på nytt neste gang.
- FR-8: Når FHI-API-et ikke svarer, gir feil eller bruker over 10 sekunder, vises en norsk feilmelding uten tekniske koder. Finnes mellomlagrede tall, vises de med «Sist lagrede tall, hentet [dato og klokkeslett]». Ellers vises ingen graf eller tabell. Kontrollregler og begrepsforklaringer gjelder også for mellomlagrede tall.
- FR-9: Appen viser andel positive uke for uke som linjegraf med tittel som gjentar utvalget. Manglende uker er brudd i linjen, ikke 0.
- FR-10: Usikre uker (færre enn 30 tester, skjult antall tester, eller flere positive enn tester, som også får fotnoten «Flere positive prøver enn tester denne uka. Det kan skyldes hvordan prøvene er registrert. Tolk tallet med forsiktighet.» (Endret 24. november 2026: Irenes beslutning i story 2.4). En uke med 0 tester og flere enn 0 positive er usikker og får fotnoten, men ingen andel. Fotnoten og regelen for 0 tester: Endret 24. november 2026: Irenes beslutning) markeres i graf og tabell med form, ikke bare farge, med forklaring i grafen og tegn og fotnote i tabellen.
- FR-11: Appen viser en tabell med uke, tester, positive prøver og andel positive, med de samme tallene som grafen. Skjulte verdier vises som «skjult» eller «mangler», ikke som 0.
- FR-12: Appen viser kildehenvisning (FHIs egen kildetekst for tabellen, tabellnummer, tabellnavn, hentedato) under graf og tabell, også når KI-forklaringen mangler.
- FR-13: Appen har sju faste begrepsforklaringer i koden (andel positive, test og positiv prøve, sesong, aldersgruppe, overvåkingstype, MSIS, «for tynt datagrunnlag»), på høyst tre setninger hver, som kan åpnes med mus og tastatur.
- FR-14: R1 – varsel når summen av positive prøver er under 20 (19 → varsel, 20 → ikke). Skjulte verdier telles ikke.
- FR-15: R2 – varsel når mer enn 20 % av ukene har et kjent antall tester under 30. Uker med skjult antall tester telles under R3, ikke R2.
- FR-16: R3 – varsel når mer enn 20 % av ukene er manglende uker. En uke med to skjulte verdier teller én gang.
- FR-17: R4 – varsel når utvalget har færre enn 3 uker med data.
- FR-18: R5 – varsel når utvalget har uker både før og etter 1. mars 2025 (sesongen 2024/2025 gir alltid varsel).
- FR-19: Varselet vises over grafen når minst én regel slår inn, lister hver regel med en setning og de faktiske tallene, har ikon og overskrift og lenke til forklaringen av «for tynt datagrunnlag». Uten utslag vises ikke varselet.
- FR-20: Appen lager en KI-forklaring på norsk på høyst 120 ord, merket «Skrevet av KI», med kildehenvisning, i et område med `aria-live="polite"` som viser «Forklaringen lages …» mens den hentes. Språkmodellen får bare tall, utvalg og regelutslag.
- FR-21: KI-forklaringen bruker bare tall fra dataene, gjetter ikke på årsaker, forklarer faguttrykk og sier fra om usikkerhet når varselet vises.
- FR-22: Uten KI-nøkkel, ved feil fra språkmodellen eller ved nettverksfeil vises en fast melding i forklaringsfeltet, og resten av siden virker.
- FR-23 (strekkmål): Mal 2 viser denne og forrige sesong i samme graf, uke for uke fra uke 40, med hel og stiplet linje og etiketter, og en tabell med begge sesongene side om side. Uke 53 vises bare for sesongen som har den.
- FR-24 (strekkmål): For mal 2 beregnes R1–R5 per sesong, og varselet sier hvilken sesong det gjelder. Uke 53 som bare finnes i den ene sesongen, teller ikke som manglende i den andre.
- FR-25: Siden viser hentetidspunkt og at FHI publiserer hver torsdag. Knappen «Hent nyeste tall nå» henter på nytt uten mellomlagring, er deaktivert mens hentingen pågår, faller tilbake til FR-8 ved feil, gjenbruker KI-forklaringen når tallene er uendret og kan brukes med tastatur.

### Ikke-funksjonelle krav

- NFR-1: Alt unntatt KI-forklaringen virker uten KI-nøkkel (testes uten `.env` gjennom UJ-4).
- NFR-2: Med mellomlagrede tall vises graf, tabell og varsel på under 5 sekunder. KI-forklaringen kan komme etter.
- NFR-3: Hele grensesnittet er på enkel norsk bokmål, uten engelske FHI-koder. Feilmeldinger sier hva som skjedde og hva brukeren kan gjøre.
- NFR-4: Kontrast minst 4,5:1 for tekst og 3:1 for linjer og symboler i grafen (WCAG 2.1 AA).
- NFR-5: Alt kan brukes med tastatur alene, med synlig fokusmarkering.
- NFR-6: Grafen har alternativtekst med utvalg og hovedtrekk, og tabellen gir de samme tallene som tekst.
- NFR-7: Ingen informasjon formidles bare med farge (sjekkes i gråtoner).
- NFR-8: Bare åpne, aggregerte data fra FHI. Ingen persondata og ingen innlogging.
- NFR-9: KI-nøkkelen ligger i `.env` i `.gitignore`. Repoet har `.env.example`.
- NFR-10: Alle automatiske tester kjører uten nett og uten KI-nøkkel, med lagrede svar i `tests/fixtures/`.
- NFR-11: Hovedskjermen virker på mobil fra 360 piksler og på PC, uten vannrett rulling.

### Suksesskriterier

- SM-1: 10 av 10 testspørsmål (influensa, RSV, SARS-CoV-2) gir samme tall som fasiten hentet manuelt fra FHI. Automatiske tester.
- SM-2: 100 % av svarene i testsettet har korrekt kildehenvisning. Automatiske tester.
- SM-3: Riktig varsel med riktig begrunnelse i alle tilfeller i testsettet, og grensetilfellene for R1–R5 testes med konstruerte data.
- SM-4: Lagrede KI-forklaringer for testsettet består sjekklisten i FR-21 (manuell gjennomgang).
- SM-5: Minst 4 av 5 testbrukere uten medisinsk bakgrunn forklarer riktig hva grafen viser og om tallene er sikre. Fasit skrives før testen. Irene vurderer svarene mot fasiten, og hvis det er mulig vurderer en medstudent de samme svarene uavhengig.
- SM-6: Minst 4 av 5 testbrukere går fra valgt mal til forklart situasjonsbilde på under 1 minutt.
- SM-C1 og SM-C2 (motvekter): Reglene svekkes ikke for å gi færre varsler, og en lengre KI-tekst er ikke bedre.

### Tilleggskrav fra arkitekturen

- Ingen startmal. Det finnes allerede et uv-prosjekt i `backend/` med FastAPI og SQLAlchemy. Første story rydder dette: SQLAlchemy fjernes (AD-4), avhengighetene fra arkitekturens kapittel 5 legges til, og ruff og pytest med pytest-socket settes opp (AD-10).
- AD-1: Ren kjerne (`domene`, `sesong`, `kontrollregler`, `begreper`, tolking i `fhi`) importerer aldri `httpx`, `anthropic`, `mellomlager`, `config` eller `web`, og får «nå» som argument.
- AD-2: `domene.py` eier `Utvalg`, `Uke`, `Dataserie`, `Regelutslag`, `Kildehenvisning` og faste lister. Skjulte verdier er `None`. FHI-koder finnes bare i `domene.py` og `fhi.py`.
- AD-3: `fhi.hent` er eneste kode som kaller FHI (httpx, 10 s, `FhiUtilgjengelig`). `fhi.tolk` lager én `Uke` per forventet uke i sesongen. Siste publiserte uke og sesonglisten kommer fra dimensjonen `dateusedforstatistics`, med reserven `sesong.sesonger_fra_dato(nå)`.
- AD-4: Mellomlagring som JSON-filer i `CACHE_DIR`, `/tmp/fhi-helsedata-cache` på Vercel eller `.cache/` lokalt. `.cache/` i `.gitignore`. Atomisk skriving med `os.replace`. Filnavn bare fra `Utvalg.nøkkel`.
- AD-5: `sesong.er_utdatert(hentet, nå)` gir `True` etter 24 timer. Tid lagres i UTC og vises i norsk tid som «20.11.2026 kl. 14:05».
- AD-6: Bare `ki.py` importerer `anthropic`. Modell `claude-haiku-5-5` (kan overstyres med `ANTHROPIC_MODEL`). `config.les_innstillinger()` kalles bare av `web` ved oppstart. `ki.forklar` gir `Forklaring`, `ManglerNøkkel` eller `KiFeil` og kaster aldri. Prompt i `prompts/forklaring.md`. `.env.example` med `ANTHROPIC_API_KEY=` og `ANTHROPIC_MODEL=`.
- AD-7: KI-forklaringen mellomlagres med SHA-256-nøkkel av utvalg, uker, regelutslag, prompt og modell (uten hentetidspunkt). Bare `Forklaring` lagres.
- AD-8: Server-HTML med Jinja2. Tabell, varsel, kilde og begrepsforklaringer (`<details>`) virker uten JavaScript. Chart.js 4.6.1 fra jsDelivr med `integrity`, data fra en JSON-blokk laget fra samme `Dataserie` som tabellen. Egen JS bare i `static/app.js`.
- AD-9: `GET /` (utvalg som query), `GET /forklaring` (HTML-fragment hentet av `app.js`), `POST /hent-nyeste` (303 til `GET /`, lås per utvalg). Validering bare i `Utvalg.fra_parametre`. Feiltekst for KI i `data-feiltekst`.
- AD-10: pytest med `--disable-socket`, `respx` for FHI, falsk KI-klient, fixtures i `tests/fixtures/fhi/`, `ki/` og `konstruert/`. Testene laster aldri `.env`. `ruff check` og `ruff format --check` skal bestå.
- AD-11: Lokalt med `uv run uvicorn backend.web:app --reload`. Vercel er valgfritt (`[tool.vercel] entrypoint`, `/tmp` er flyktig).
- Konvensjoner (arkitektur kapittel 4): norske navn, `kontrollregler.vurder(serie) -> list[Regelutslag]`, kildehenvisning bare fra `domene.kildehenvisning`, tallformat («20,8 %», tusenskille med mellomrom, «uke 50»), formatering bare i Jinja2-filtre, konfigurasjon bare i `config.py`.
- Addendum: endepunktene for metadata, dimensjoner og data. FHIs kildetekst for tabell 724 er «Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, Folkehelseinstituttet (FHI).» (sjekket 22. november 2026, story 1.4). Etiketten «RS-virus (A+B)» vises ikke for brukeren.

### UX-krav

Det finnes ikke noe eget UX-dokument. Kravene til utseende og oppførsel står i PRD kapittel 6.0 (skisse av hovedskjermen) og i NFR-3–NFR-7 og NFR-11 over.

### Planbeslutninger (20.11.2026)

- Planen er en rekkefølge, ikke en fast datoplan. Datoene er veiledende og justeres etter tempoet. Er en story ferdig tidlig, startes neste med en gang. Planen gjelder fra 21. november 2026.
- Faste frister: mal 1 for influensa virker senest 2. desember (ellers droppes RSV, SARS-CoV-2 og mal 2), appen er ferdig senest 6. desember, og innleveringen er 15. desember.
- Brukertestingen legges til 2.–3. desember og flyttes fram hvis mal 1 blir ferdig tidligere.
- Mal 2 er strekkmål. Vercel er valgfritt, som i AD-11.
- Testspørsmålene bruker i hovedsak avsluttede sesonger (2024/2025 og 2025/2026). For spørsmål om sesongen som pågår, hentes fasit og lagrede svar samme dag, og datoen står i fila.
- README lages i epic 1 og oppdateres i hver story som endrer installering, oppstart, konfigurasjon eller tester. Epic 7 har den endelige README-en, testet fra en ny klone.
- Hver story har sine egne automatiske tester i akseptansekriteriene. Epic 7 er bare det samlede testsettet med 10 spørsmål og fasit (SM-1–SM-4).
- Egne stories for Irene: kildehenvisning for tabell 724, tekstene til begrepsforklaringene, godkjenning av prompten (Claude skriver et utkast), testspørsmål med fasit, brukertesting og gjennomgang av KI-forklaringene (SM-4).

### Dekning av FR

| Krav | Epic | Hva |
| --- | --- | --- |
| FR-1 | 3 | Malliste i skjemaet (mal 2 vises først når epic 8 er bygget) |
| FR-2 | 2, 6 | Virus → tabell i `domene`. Influensa i epic 2, RSV og SARS-CoV-2 i epic 6 |
| FR-3 | 2, 3 | Sesonger og uke 53 i `sesong`, sesongvalg i skjemaet |
| FR-4 | 2, 3 | Aldersgrupper i `domene`, valg i skjemaet |
| FR-5 | 2, 3 | `Utvalg.fra_parametre`, norsk melding på siden |
| FR-6 | 2, 6, 7 | Henting og tolking, nye tabeller, testsettet mot fasit |
| FR-7 | 2 | Mellomlager og `er_utdatert` |
| FR-8 | 2, 3 | Reserve i `tjeneste`, feilmelding på siden |
| FR-9 | 3 | Linjegraf |
| FR-10 | 3 | Usikre uker i graf og tabell |
| FR-11 | 2, 3 | Skjulte verdier som `None`, tabell |
| FR-12 | 1, 3, 6 | Kontroll av FHIs kildetekst for 724, visning, kildetekst for 729 og 731 |
| FR-13 | 3 | Begrepstekster og visning |
| FR-14–FR-18 | 2 | R1–R5 |
| FR-19 | 3 | Varsel over grafen |
| FR-20–FR-22 | 4 | Prompt, `ki.forklar`, `GET /forklaring` |
| FR-23, FR-24 | 8 | Mal 2 (strekkmål) |
| FR-25 | 4 | «Hent nyeste tall nå» |
| NFR-1, NFR-2 | 4 | Uten nøkkel, forklaringen lastes etter siden |
| NFR-3 | 3, 5 | Norske tekster, retting etter brukertesting |
| NFR-4–NFR-7, NFR-11 | 3 | Tilgjengelighet og mobil |
| NFR-8 | alle | Ingen persondata, ingen innlogging |
| NFR-9, NFR-10 | 1 | `.env.example`, pytest-socket (gjelder alle senere tester) |
| SM-1, SM-2 | 7 | Testsettet |
| SM-3 | 2, 7 | Grensetilfeller i epic 2, ekte tilfeller i testsettet |
| SM-4 | 7 | Gjennomgang av KI-forklaringene |
| SM-5, SM-6 | 5 | Brukertesting |

## Epics

### Epic 1: Oppsett
Prosjektet er klart til å bygges: ryddet uv-prosjekt, ruff, pytest uten nett, et ekte svar fra tabell 724 som testene kan bruke, og en enkel README om installering, oppstart og tester. Irene har sjekket FHIs kildehenvisning for tabell 724. Veiledende: 21.–22. november.
**Dekker:** NFR-9, NFR-10, AD-4, AD-6 (`.env.example`), AD-10, FR-12 (kildetekst for 724)

### Epic 2: Riktige influensatall med kontrollregler
Appen kan hente, mellomlagre og tolke influensatall for et utvalg, og avgjør med R1–R5 om datagrunnlaget er for tynt. Alt er testet uten nett. Veiledende: 23.–25. november.
**Dekker:** FR-2–FR-8, FR-11, FR-14–FR-18, SM-3 (grensetilfeller), AD-1–AD-5, AD-9 (lås)

### Epic 3: Influensa på skjermen
Brukeren kan velge utvalg og se graf, tabell, varsel, kildehenvisning og begrepsforklaringer, også på mobil og med tastatur. Veiledende: 26.–28. november.
**Dekker:** FR-1, FR-3–FR-5, FR-8 (melding), FR-9–FR-13, FR-19, NFR-3–NFR-7, NFR-11, AD-8, AD-9

### Epic 4: KI-forklaring og nyeste tall
Brukeren får en kort KI-forklaring med kilde, og kan hente nyeste tall fra FHI. Appen virker uten KI-nøkkel. Etter denne epicen er mal 1 for influensa ferdig. **Fast frist: 2. desember.** Veiledende: 29. november–2. desember.
**Dekker:** FR-20–FR-22, FR-25, NFR-1, NFR-2, AD-6, AD-7, AD-9

### Epic 5: Brukertesting av mal 1
Fem personer uten medisinsk bakgrunn har prøvd mal 1, og ord de ikke forsto, er skrevet om. 2.–3. desember, eller tidligere hvis mal 1 er ferdig før.
**Dekker:** SM-5, SM-6, NFR-3

### Epic 6: RSV og SARS-CoV-2
Brukeren kan velge RSV og SARS-CoV-2 i mal 1. Droppes hvis mal 1 for influensa ikke virker 2. desember. Veiledende: 3.–4. desember.
**Dekker:** FR-2, FR-6, FR-12 (tabell 729 og 731)

### Epic 7: Testsett og README
Testsettet med 10 spørsmål viser at tallene, kildehenvisningene og varslene er riktige. KI-forklaringene er gjennomgått, og den endelige README-en er testet ved å følge den fra en ny klone av repoet. **Fast frist: appen er ferdig 6. desember.** Veiledende: 4.–6. desember. Testspørsmålene (7.1) kan hentes tidligere.
**Dekker:** SM-1–SM-4, FR-6, NFR-1, NFR-9, AD-11 (lokal kjøring)

### Epic 8: Strekkmål og valgfritt
Bare hvis tiden tillater det etter 6. desember, før innleveringen 15. desember. Mal 2 påbegynnes først når mal 1 virker for alle tre virus og testene består (PRD kapittel 5). Vercel er valgfritt (AD-11).
**Dekker:** FR-23, FR-24 (strekkmål), AD-11 (Vercel, valgfritt)

## Felles ferdigkriterier for utviklerstories

Gjelder alle stories som ikke er merket «(Irene)», i tillegg til akseptansekriteriene:

- Storyen har egne automatiske tester for akseptansekriteriene, og `uv run pytest` består uten nett og uten KI-nøkkel (NFR-10, AD-10).
- `ruff check` og `ruff format --check` består (AD-10).
- Ingen import bryter avhengighetsretningen i arkitekturen (AD-1).
- README er oppdatert hvis storyen endrer installering, oppstart, konfigurasjon eller tester.

Stories merket «(Irene)» gjør Irene selv. De har ingen automatiske tester, men resultatet brukes av testene i senere stories.

---

## Epic 1: Oppsett

Prosjektet er klart til å bygges: ryddet uv-prosjekt, ruff, pytest uten nett, et ekte svar fra tabell 724 som testene kan bruke, og en enkel README. Veiledende: 21.–22. november.

### Story 1.1: Rydde uv-prosjektet og holde nøkler og cache utenfor git

Som utvikler
vil jeg ha et uv-prosjekt med bare avhengighetene fra arkitekturen,
slik at appen bygger på riktig stack og ingen nøkler eller cachefiler havner i git.

**Akseptansekriterier:**

**Gitt** `backend/pyproject.toml` med `sqlalchemy`
**Når** storyen er ferdig
**Så** er `sqlalchemy` fjernet, og avhengighetene i arkitekturens kapittel 5 (FastAPI, Uvicorn, Jinja2, python-multipart, httpx, anthropic, python-dotenv, tzdata) står med `>=` og versjonen som minimum (AD-4, arkitektur §5)
**Og** `uv sync` går uten feil, og `uv.lock` er oppdatert
**Og** `.cache/` står i `.gitignore` i reporoten (AD-4)
**Og** `.env.example` i reporoten inneholder `ANTHROPIC_API_KEY=` og `ANTHROPIC_MODEL=`, og `.env` er ignorert av git (NFR-9, AD-6)
**Og** en automatisk test sjekker at `git check-ignore` gjelder for `.env` og `.cache/x.json`, og at `.env.example` ikke er ignorert

### Story 1.2: ruff og pytest uten nett

Som utvikler
vil jeg at testene stopper alle nettverkskall,
slik at ingen test ved et uhell kaller FHI eller Claude (NFR-10).

**Akseptansekriterier:**

**Gitt** prosjektet fra 1.1
**Når** `pytest`, `pytest-socket`, `respx` og `ruff` legges til som utviklingsavhengigheter
**Så** kjører `uv run pytest` med `--disable-socket` som standard (satt i `pyproject.toml`) (AD-10)
**Og** en test som prøver å åpne en socket, feiler med `SocketBlockedError`, og testen viser at sperren virker
**Og** `ruff check` og `ruff format --check` er satt opp i `pyproject.toml` og består (AD-10)
**Og** `tests/fixtures/fhi/`, `tests/fixtures/ki/` og `tests/fixtures/konstruert/` finnes (AD-10)

### Story 1.3: Lagre et ekte svar fra tabell 724 som fixture

Som utvikler
vil jeg ha et ekte svar fra FHI for influensa i `tests/fixtures/fhi/`,
slik at tolkingen kan bygges og testes mot ekte data uten nett.

**Akseptansekriterier:**

**Gitt** FHIs data-endepunkt for tabell 724 (addendum)
**Når** data hentes én gang manuelt for influensa, sesongen 2025/2026, alle aldersgrupper, Non-Sentinel, `A+B`, alle tre måltall
**Så** lagres svaret i `tests/fixtures/fhi/` i samme format som cachen: `{"hentet": <ISO 8601 i UTC>, "svar": <rått svar>}` (AD-4, AD-10)
**Og** dimensjonslisten for tabell 724 lagres på samme måte (`724-dimensjoner.json`) (AD-3)
**Og** valget mellom CSV og JSON fra FHI og hvordan FLAGG-kolonnen ser ut, står i en kort notis i `tests/fixtures/fhi/README.md` (arkitektur §8)
**Og** en automatisk test leser fixturene og sjekker at `hentet` og `svar` finnes, og at uke 2025-w40 er med

### Story 1.4: Sjekke FHIs kildehenvisning for tabell 724 (Irene)

Som Irene
vil jeg ha FHIs egen ordlyd for kildehenvisningen til tabell 724,
slik at appen oppgir kilden slik FHI ber om (FR-12, SM-2).

**Akseptansekriterier:**

**Gitt** metadataene for tabell 724 (`/Table/724/metadata`)
**Når** jeg har lest kildeteksten der
**Så** står den ordrett i addendumet under «Kildehenvisning foreslått av FHI», med datoen jeg sjekket den
**Og** tabellnavnet «RESPIaggr Influensa antall og andel» er bekreftet eller rettet i PRD kapittel 4

### Story 1.5: Enkel README

Som medstudent som kloner repoet
vil jeg lese hvordan appen installeres, startes og testes,
slik at jeg kommer i gang uten å spørre.

**Akseptansekriterier:**

**Gitt** prosjektet fra 1.1–1.3
**Når** README i reporoten er skrevet
**Så** beskriver den installering med `uv sync`, kjøring av tester med `uv run pytest` og ruff-kommandoene (AD-10)
**Og** den sier at `.env` er valgfri, og at appen virker uten KI-nøkkel (NFR-1, NFR-9)
**Og** den har en plass for oppstartskommandoen, som fylles ut i story 3.1 (AD-11)
**Og** en automatisk test sjekker at README nevner `uv sync` og `uv run pytest`

---

## Epic 2: Riktige influensatall med kontrollregler

Appen kan hente, mellomlagre og tolke influensatall for et utvalg, og avgjør med R1–R5 om datagrunnlaget er for tynt. Alt er testet uten nett. Veiledende: 23.–25. november.

### Story 2.1: Domenemodellen

Som utvikler
vil jeg ha ett felles sett dataklasser og faste lister,
slik at alle moduler bruker de samme begrepene som PRD-en (AD-2).

**Akseptansekriterier:**

**Gitt** begrepene i PRD kapittel 3
**Når** `domene.py` er skrevet
**Så** finnes `Utvalg`, `Uke`, `Dataserie`, `Regelutslag` og `Kildehenvisning`, og faste lister for virus → tabell (influensa 724, RSV 729, SARS-CoV-2 731), de sju aldersgruppevalgene og maler (FR-2, FR-4, AD-2)
**Og** `Uke.usikker` er sann ved færre enn 30 tester eller skjult antall tester, og `Uke.manglende` er sann når tester eller positive er `None` (PRD kapittel 3, FR-10, FR-16)
**Og** `Uke.andel` er `None` for manglende uker, aldri 0 (FR-11)
**Og** `domene.kildehenvisning(tabell, hentet)` gir FHIs egen kildetekst for tabellen (ordlyden fra story 1.4), tabellnummer, tabellnavn og hentedato (FR-12, konvensjonen «Kildehenvisning»)
**Og** tester dekker 29 og 30 tester, skjulte verdier og kildehenvisningen for 724
**Og** `domene.py` importerer ingen skallmoduler (AD-1)

### Story 2.2: Gyldige utvalg fra parametre

Som Sara
vil jeg at appen bare godtar valg som finnes,
slik at jeg får en tydelig melding i stedet for feil tall (FR-5).

**Akseptansekriterier:**

**Gitt** query-parametrene `mal`, `virus`, `sesong` og `alder`
**Når** `Utvalg.fra_parametre(parametre, gyldige_sesonger)` kalles, der listen over gyldige sesonger er et argument (den lages i story 2.3–2.4 og 2.9)
**Så** gir gyldige verdier et `Utvalg`, og manglende `alder` gir «Alle aldersgrupper» (FR-4)
**Og** manglende eller ukjente verdier gir en feil med en norsk melding om hva som må rettes, uten FHI-koder (FR-5, NFR-3, AD-9)
**Og** «Ukjent alder» godtas ikke (FR-4)
**Og** `Utvalg.nøkkel` gir et filnavn som bare består av trygge tegn, og er likt for like utvalg (AD-4)
**Og** tester dekker gyldige utvalg, hvert ugyldige felt og en manipulert verdi som `../x`

### Story 2.3: Sesonger, uker og utdaterte tall

Som utvikler
vil jeg ha rene funksjoner for sesonger, ISO-uker og levetid,
slik at alle moduler regner perioder og levetid likt (FR-3, FR-7, AD-5).

**Akseptansekriterier:**

**Gitt** en sesong som «2026/2027»
**Når** ukene i sesongen regnes ut
**Så** er de uke 40 i 2026 til og med uke 20 i 2027, med 2026-w53 som en vanlig uke (FR-3)
**Og** for sesongen som pågår, stopper perioden ved en oppgitt siste publisert uke (FR-3, AD-3)
**Og** `sesong.sesonger_fra_dato(nå)` gir sesongene fra 2024/2025 til den som pågår (reserve i AD-3)
**Og** `sesong.er_utdatert(hentet, nå)` gir `False` ved 23 t 59 min og `True` ved 24 t og mer, og begge tidspunktene må ha tidssone (FR-7, AD-5)
**Og** modulen tar «nå» som argument og bruker ikke klokka selv (AD-1)
**Og** tester dekker uke 53, sesongstart og grensen på 24 timer

### Story 2.4: Tolke FHI-svar til en komplett dataserie

Som utvikler
vil jeg gjøre et rått FHI-svar om til en `Dataserie` med én uke for hver forventet uke,
slik at graf, tabell og kontrollregler bruker de samme ukene (AD-3).

**Akseptansekriterier:**

**Gitt** fixturen for tabell 724 fra story 1.3
**Når** `fhi.tolk(rått_svar, utvalg)` kalles
**Så** gir den én `Uke` per forventet uke i sesongen frem til siste publiserte uke, med tester, positive og andel (FR-6, AD-3)
**Og** tallene for tre utvalgte uker stemmer med fixturen (FR-6)
**Og** `..`, `.`, `:`, tom verdi og uker FHI ikke sendte, blir `None`, aldri 0 (FR-11, FR-16, AD-2)
**Og** siste publiserte uke og sesonglisten lages fra dimensjonslisten `dateusedforstatistics` (FR-3, AD-3)
**Og** tolkefunksjonene er rene og importerer ikke `httpx` (AD-1)
**Og** tester dekker fixturen og et konstruert svar med skjulte verdier og en manglende uke

### Story 2.5: Hente fra FHI med tidsgrense

Som Sara
vil jeg at appen gir opp etter 10 sekunder hvis FHI ikke svarer,
slik at jeg ikke venter på en side som har hengt seg (FR-8).

**Akseptansekriterier:**

**Gitt** et utvalg
**Når** `fhi.hent(...)` kaller FHIs data-endepunkt
**Så** brukes riktig tabell, `NONSTL`, `A+B` for influensa, valgt aldersgruppe og ukene i sesongen (FR-2, FR-6)
**Og** tidsavbrudd etter 10 sekunder, HTTP-feil og ugyldig svar gir alltid `FhiUtilgjengelig` (FR-8, AD-3)
**Og** dimensjonslisten kan hentes med en egen funksjon (AD-3)
**Og** `fhi.py` er den eneste modulen som kaller `statistikk-data.fhi.no` (AD-3)
**Og** tester med `respx` dekker vellykket svar (fixturen fra 1.3), tidsavbrudd, status 500 og ugyldig svar

### Story 2.6: Mellomlagre FHI-svar

Som Sara
vil jeg at tall jeg har sett før, vises uten nytt kall til FHI,
slik at siden kommer raskt og virker selv om FHI er nede (FR-7, FR-8, NFR-2).

**Akseptansekriterier:**

**Gitt** `config.les_innstillinger()` med cachemappen fra `CACHE_DIR`, ellers `/tmp/fhi-helsedata-cache` når `VERCEL` finnes, ellers `.cache/` i reporoten (AD-4, AD-6)
**Når** `mellomlager` lagrer et rått svar for et utvalg
**Så** skrives `fhi/<Utvalg.nøkkel>.json` med `{"hentet": ..., "svar": ...}` via en midlertidig fil og `os.replace` (AD-4)
**Og** en lagret fil kan leses tilbake med hentetidspunktet (FR-7)
**Og** en fil som ikke kan leses, behandles som om den ikke finnes (AD-4)
**Og** `config` laster ikke `.env` ved import (AD-6)
**Og** tester med `tmp_path` dekker lagring, lesing, ødelagt fil og valg av cachemappe

### Story 2.7: Kontrollregler R1–R3

Som Sara
vil jeg få vite når det er for få positive prøver, for få tester eller for mange manglende uker,
slik at jeg ikke trekker konklusjoner av tynne tall (FR-14–FR-16).

**Akseptansekriterier:**

**Gitt** en `Dataserie`
**Når** `kontrollregler.vurder(serie)` kalles
**Så** gir R1 utslag ved 19 positive og ikke ved 20, og skjulte verdier telles ikke (FR-14)
**Og** R2 gir ikke utslag ved 4 av 20 uker under 30 tester (20 %), men ved 5 av 20 (25 %). En uke med 29 tester teller, en med 30 teller ikke, og uker med skjult antall tester telles ikke i R2 (FR-15)
**Og** R3 gir ikke utslag ved 2 av 10 manglende uker, men ved 3 av 10, og en uke med to skjulte verdier teller én gang (FR-16)
**Og** hvert `Regelutslag` har en setning på enkel norsk med de faktiske tallene, for eksempel «6 av 20 uker har færre enn 30 tester» (FR-19, konvensjonen «Regelutslag»)
**Og** grensetilfellene ligger som konstruerte data i `tests/fixtures/konstruert/` og testes (SM-3, AD-10)
**Og** modulen er ren (AD-1)

### Story 2.8: Kontrollregler R4–R5

Som Sara
vil jeg få vite når en sesong nettopp har startet eller går over 1. mars 2025,
slik at jeg ikke sammenligner tall som ikke kan sammenlignes (FR-17, FR-18).

**Akseptansekriterier:**

**Gitt** en `Dataserie`
**Når** `kontrollregler.vurder(serie)` kalles
**Så** gir R4 utslag ved 2 uker med data og ikke ved 3, og manglende uker telles ikke som uker med data (FR-17)
**Og** R5 gir utslag når serien har en uke som starter før 1. mars 2025 og en som slutter 1. mars 2025 eller senere, slik at 2024/2025 alltid gir utslag og 2025/2026 og 2026/2027 aldri gjør det (FR-18)
**Og** setningene følger konvensjonen «Regelutslag» (FR-19)
**Og** grensetilfellene ligger i `tests/fixtures/konstruert/` og testes, og ingen regel er svekket for å gi færre varsler (SM-3, SM-C1)

### Story 2.9: Sette sammen svaret for et utvalg

Som Sara
vil jeg få tall, varsel og kilde for utvalget mitt, også når FHI er nede,
slik at jeg alltid vet hva jeg ser på (FR-7, FR-8).

**Akseptansekriterier:**

**Gitt** et utvalg og «nå»
**Når** `tjeneste.svar(utvalg, nå)` kalles
**Så** brukes lagrede tall når de ikke er utdaterte, og ellers hentes nye fra FHI og lagres (FR-7, AD-5)
**Og** svaret inneholder `Dataserie`, `Regelutslag` og `Kildehenvisning` med hentetidspunktet (FR-12, FR-14–FR-18)
**Og** ved `FhiUtilgjengelig` brukes lagrede tall merket som «sist lagrede», eller så gir svaret beskjed om at det ikke finnes tall (FR-8)
**Og** kontrollreglene gjelder også for lagrede tall (FR-8)
**Og** `tjeneste.sesonger(nå)` gir sesonglisten fra den lagrede eller hentede dimensjonslisten, og bruker `sesong.sesonger_fra_dato(nå)` når FHI er nede og ingen liste er lagret (FR-3, AD-3)
**Og** samtidige kall for samme utvalg deler ett kall til FHI (AD-9)
**Og** tester med `respx` og `tmp_path` dekker ferske tall, utdaterte tall, FHI nede med og uten lagrede tall, sesonglisten med og uten FHI, og to samtidige kall

---

## Epic 3: Influensa på skjermen

Brukeren kan velge utvalg og se graf, tabell, varsel, kildehenvisning og begrepsforklaringer, også på mobil og med tastatur. Veiledende: 26.–28. november.

### Story 3.1: Velge mal og utvalg på siden

Som Sara
vil jeg velge mal, virus, sesong og aldersgruppe i et enkelt skjema,
slik at jeg kan stille spørsmålet mitt uten å kjenne FHIs tabeller (FR-1–FR-5).

**Akseptansekriterier:**

**Gitt** at appen startes med `uv run uvicorn backend.web:app --reload` uten `.env` (AD-11, NFR-1)
**Når** Sara åpner `GET /` uten parametre
**Så** vises bare skjemaet, med mal 1 som spørsmål på vanlig norsk, influensa som eneste virus foreløpig, sesongene med siste sesong som standard og «Alle aldersgrupper» som standard (FR-1–FR-4)
**Og** ugyldige parametre gir den norske meldingen fra `Utvalg.fra_parametre` og ingen henting (FR-5, AD-9)
**Og** siden har `lang="nb"`, og ingen FHI-koder vises (NFR-3, AD-2)
**Og** `config.les_innstillinger()` kalles bare én gang, ved oppstart i `web` (AD-6)
**Og** README har oppstartskommandoen (AD-11)
**Og** tester med FastAPIs testklient dekker skjemaet uten parametre og et ugyldig utvalg

### Story 3.2: Tabell, kildehenvisning og feilmelding

Som Sara
vil jeg se tallene uke for uke i en tabell med kilde,
slik at jeg kan bruke dem og oppgi riktig kilde i oppgaven min (FR-11, FR-12).

**Akseptansekriterier:**

**Gitt** et gyldig utvalg og lagrede tall
**Når** siden vises
**Så** har tabellen kolonnene uke, tester, positive prøver og andel positive, med «uke 50», «20,8 %» og mellomrom som tusenskille, laget av Jinja2-filtre (FR-11, arkitektur §4)
**Og** skjulte verdier vises som «skjult» eller «mangler», ikke som 0 (FR-11)
**Og** usikre uker har tegn og fotnote (FR-10)
**Og** kildehenvisningen og hentetidspunktet («20.11.2026 kl. 14:05», norsk tid) vises under tabellen (FR-12, AD-5)
**Og** når FHI er nede, vises FR-8-meldingen med «Sist lagrede tall, hentet …», eller ingen tabell og forslag om å prøve igjen senere (FR-8)
**Og** tabellen virker uten JavaScript (AD-8)
**Og** tester dekker formatering, skjult verdi, usikker uke, kildehenvisning og begge FR-8-tilfellene

### Story 3.3: Graf uke for uke

Som Sara
vil jeg se utviklingen som en linjegraf,
slik at jeg ser hovedtrekket i sesongen med en gang (FR-9).

**Akseptansekriterier:**

**Gitt** samme `Dataserie` som tabellen
**Når** siden vises
**Så** tegner Chart.js 4.6.1 fra jsDelivr (fast versjon og `integrity`) en linjegraf med uker langs x-aksen og andel positive langs y-aksen (FR-9, AD-8)
**Og** dataene ligger i en `<script type="application/json">`-blokk, der manglende uker er `null` og gir brudd i linjen (FR-9, AD-8)
**Og** grafen har en tittel som gjentar utvalget, for eksempel «Influensa, sesongen 2025/2026, alle aldersgrupper» (FR-9)
**Og** usikre uker har en annen punktform, og forklaringen sier hva markeringen betyr (FR-10, NFR-7)
**Og** grafen har en alternativtekst med utvalg og hovedtrekk (NFR-6)
**Og** egen JavaScript ligger bare i `static/app.js` (AD-8)
**Og** tester sjekker at JSON-blokken har samme tall som tabellen, `null` for manglende uker og riktig tittel og alternativtekst

### Story 3.4: Varsel om tynt datagrunnlag

Som Sara
vil jeg se et tydelig varsel før tallene når de er usikre,
slik at jeg tolker dem med forsiktighet (FR-19).

**Akseptansekriterier:**

**Gitt** et svar med minst ett regelutslag
**Når** siden vises
**Så** står varselet over grafen, med ikon og overskrift og ikke bare farge, og lister hver regel med setningen fra `Regelutslag` (FR-19, NFR-7)
**Og** uten regelutslag vises ikke varselet (FR-19)
**Og** tester dekker et utvalg med R1 og R5 samtidig og et utvalg uten utslag

### Story 3.5: Skrive tekstene til de sju begrepsforklaringene (Irene)

Som Irene
vil jeg skrive forklaringene selv,
slik at de er korrekte og enkle nok for en student uten medisinsk bakgrunn (FR-13, PRD åpent spørsmål 2).

**Akseptansekriterier:**

**Gitt** de sju begrepene i FR-13
**Når** tekstene er skrevet
**Så** har hvert begrep en forklaring på høyst tre setninger uten faguttrykk som ikke er forklart (FR-13)
**Og** forklaringen av overvåkingstype sier at appen bruker vanlig klinisk praksis, og nevner kort hva fyrtårnsystemet er (FR-13)
**Og** tekstene er levert som en liste (for eksempel i issuet), klare for story 3.6

### Story 3.6: Begrepsforklaringer i appen

Som Sara
vil jeg kunne åpne korte forklaringer av ordene på siden,
slik at jeg forstår grafen uten å slå opp faguttrykk (FR-13).

**Akseptansekriterier:**

**Gitt** tekstene fra story 3.5
**Når** de ligger i `begreper.py` og vises på siden
**Så** vises de som `<details>`/`<summary>` som kan åpnes med mus, Enter og mellomrom (FR-13, NFR-5, AD-8)
**Og** varselet fra story 3.4 får en lenke til forklaringen av «for tynt datagrunnlag», og lenken åpner den (FR-19)
**Og** en test sjekker at alle sju begrepene finnes, at hver tekst har høyst tre setninger, at siden viser dem, og at varselet lenker til riktig forklaring

### Story 3.7: Tilgjengelighet og mobil

Som Sara
vil jeg kunne bruke siden på mobilen og med tastatur,
slik at jeg kan bruke appen der jeg er (NFR-4, NFR-5, NFR-11).

**Akseptansekriterier:**

**Gitt** hovedskjermen med skjema, varsel, graf, tabell og begrepsforklaringer
**Når** `static/style.css` er ferdig
**Så** har vanlig tekst kontrast på minst 4,5:1, og linjer og symboler i grafen minst 3:1 (NFR-4)
**Og** alle valg, knapper og forklaringer har synlig fokusmarkering (NFR-5)
**Og** siden kan brukes ved 360 piksler bredde uten vannrett rulling, og tabellen kan rulle inni sin egen boks (NFR-11)
**Og** fargene for tekst og graf er CSS-variabler i `style.css`, som `app.js` leser, og en automatisk test regner ut kontrasten og sjekker grensene, og en test sjekker at alle skjemafelt har en `<label>`
**Og** en manuell sjekk i gråtoner, med tastatur og ved 360 piksler er notert i issuet (NFR-5, NFR-7, NFR-11)

---

## Epic 4: KI-forklaring og nyeste tall

Brukeren får en kort KI-forklaring med kilde, og kan hente nyeste tall fra FHI. Appen virker uten KI-nøkkel. Etter denne epicen er mal 1 for influensa ferdig. **Fast frist: 2. desember.** Veiledende: 29. november–2. desember.

### Story 4.1: Utkast til prompt

Som utvikler
vil jeg ha et utkast til prompten for KI-forklaringen,
slik at Irene kan rette og godkjenne den før koden skrives (FR-20, FR-21).

**Akseptansekriterier:**

**Gitt** kravene i FR-20 og FR-21
**Når** `prompts/forklaring.md` er skrevet
**Så** ber prompten om en forklaring på norsk på høyst 120 ord, med enkle ord (FR-20)
**Og** den sier at bare tall fra dataene skal brukes, at årsaker ikke skal gjettes, at faguttrykk skal forklares, og at usikkerhet skal nevnes når det er regelutslag (FR-21)
**Og** den har plassholdere for utvalg, tolkede uker, regelutslag og kildehenvisning, og ingenting annet (FR-20, AD-6)
**Og** en test sjekker at alle plassholderne finnes

### Story 4.2: Rette og godkjenne prompten (Irene)

Som Irene
vil jeg lese og rette prompten,
slik at KI-forklaringen sier det jeg vil, før FR-20 bygges.

**Akseptansekriterier:**

**Gitt** utkastet fra story 4.1
**Når** jeg har lest det mot FR-20 og FR-21
**Så** er rettelsene mine committet i `prompts/forklaring.md`
**Og** issuet sier at prompten er godkjent

### Story 4.3: KI-forklaring med tre utfall

Som Sara
vil jeg få en kort forklaring av tallene, eller en tydelig melding hvis den ikke kan lages,
slik at resten av siden alltid virker (FR-20, FR-22, NFR-1).

**Akseptansekriterier:**

**Gitt** den godkjente prompten
**Når** `ki.forklar(...)` kalles
**Så** gir den alltid `Forklaring(tekst)`, `ManglerNøkkel` eller `KiFeil`, og kaster aldri videre (AD-6)
**Og** uten nøkkel kalles ikke Claude, og utfallet er `ManglerNøkkel` (FR-22, NFR-1)
**Og** klienten lages med eksplisitt `api_key=`, modellen er `claude-haiku-5-5` og kan overstyres med `ANTHROPIC_MODEL` (AD-6)
**Og** `config.les_innstillinger()` leser `ANTHROPIC_API_KEY` og `ANTHROPIC_MODEL`, og `.env` vinner over skallet (AD-6)
**Og** bare `ki.py` importerer `anthropic` (AD-6)
**Og** README forklarer hvordan nøkkelen settes i `.env` (NFR-9)
**Og** tester med en falsk klient og tekst fra `tests/fixtures/ki/` dekker alle tre utfallene

### Story 4.4: Mellomlagre KI-forklaringen

Som Sara
vil jeg få samme forklaring når tallene er de samme,
slik at teksten ikke endrer seg hver gang jeg åpner siden (FR-25, AD-7).

**Akseptansekriterier:**

**Gitt** et utvalg med tolkede uker og regelutslag
**Når** en forklaring lages
**Så** lagres den i `ki/<nøkkel>.json` med `laget`, `modell` og `tekst`, der nøkkelen er SHA-256 av kanonisk JSON med utvalg, uker, regelutslag, promptinnhold og modell, uten hentetidspunkt (AD-7)
**Og** neste kall med de samme tallene bruker den lagrede teksten uten å kalle Claude (AD-7)
**Og** endrede tall, endret prompt eller endret modell gir ny nøkkel (AD-7)
**Og** `ManglerNøkkel` og `KiFeil` lagres ikke (AD-7)
**Og** tester dekker gjenbruk, ny nøkkel ved endret prompt og at feil ikke lagres

### Story 4.5: Forklaringen på siden

Som Sara
vil jeg se graf og tabell med en gang og få forklaringen når den er klar,
slik at jeg ikke venter på KI-en (FR-20, NFR-2).

**Akseptansekriterier:**

**Gitt** siden for et gyldig utvalg
**Når** den vises
**Så** står «Forklaringen lages …» i et område med `aria-live="polite"`, og `app.js` henter `GET /forklaring` med samme parametre og setter inn fragmentet (FR-20, AD-9)
**Og** fragmentet er merket «Skrevet av KI» og har kildehenvisningen fra `domene.kildehenvisning` (FR-12, FR-20)
**Og** uten nøkkel sier fragmentet at forklaringen krever en KI-nøkkel, og at graf, tabell og varsel er komplette uten den (FR-22)
**Og** ved `KiFeil`, nettverksfeil eller annen status enn 200 vises teksten fra `data-feiltekst` (FR-22, AD-9)
**Og** med lagrede tall vises graf, tabell og varsel på under 5 sekunder uten å vente på KI (NFR-2)
**Og** tester med testklienten dekker fragmentet for alle tre utfallene, og at `GET /` ikke kaller `ki`

### Story 4.6: Hente nyeste tall nå

Som Sara
vil jeg kunne hente tallene på nytt med en gang,
slik at jeg ser de nye tallene FHI publiserer på torsdag (FR-25).

**Akseptansekriterier:**

**Gitt** siden for et gyldig utvalg
**Når** siden vises
**Så** står hentetidspunktet og at FHI publiserer nye tall hver torsdag (FR-25)
**Og** knappen «Hent nyeste tall nå» sender `POST /hent-nyeste`, som henter uten mellomlagring, lagrer med nytt hentetidspunkt og svarer `303` til `GET /` for samme utvalg (FR-25, AD-9)
**Og** `app.js` deaktiverer knappen når skjemaet sendes, og knappen kan brukes med tastatur (FR-25, NFR-5)
**Og** når FHI ikke svarer, vises sist lagrede tall med dato (FR-8)
**Og** når tallene er uendret, gjenbrukes den lagrede KI-forklaringen (FR-25, AD-7)
**Og** tester dekker omdirigeringen, ny lagring, FHI nede og at uendrede tall ikke gir nytt KI-kall

---

## Epic 5: Brukertesting av mal 1

Fem personer uten medisinsk bakgrunn har prøvd mal 1, og ord de ikke forsto, er skrevet om. 2.–3. desember, eller tidligere hvis mal 1 er ferdig før.

### Story 5.1: Brukertesting med fem personer (Irene)

Som Irene
vil jeg teste appen med fem personer uten medisinsk bakgrunn,
slik at jeg vet om de forstår grafen og varselet (SM-5, SM-6).

**Akseptansekriterier:**

**Gitt** at mal 1 for influensa virker
**Når** jeg har skrevet to oppgaver med mal 1, én der varselet ikke vises og én der det vises (for eksempel sesongen 2024/2025, som alltid gir R5), med fasit skrevet før testen (hovedtrekket i grafen, og om varselet vises og hvorfor)
**Så** har fem personer prøvd appen én og én, og tiden fra valgt mal til forklart situasjonsbilde er målt (SM-6)
**Og** jeg har vurdert svarene mot fasiten, og hvis det var mulig har en medstudent vurdert de samme svarene uavhengig (SM-5)
**Og** resultatet er notert: hvor mange som svarte riktig på begge, hvor mange som brukte under 1 minutt, og hvilke ord de ikke forsto (SM-5, SM-6, NFR-3)

### Story 5.2: Skrive om ord etter brukertestingen

Som Sara
vil jeg at ordene på siden er ord jeg forstår,
slik at jeg kan forklare tallene med egne ord (NFR-3).

**Akseptansekriterier:**

**Gitt** listen over ord fra story 5.1
**Når** tekstene i malene, varslene og begrepsforklaringene er skrevet om
**Så** er hvert ord på listen skrevet om eller forklart, og endringene er notert i issuet (NFR-3)
**Og** begrepsforklaringer som endres, er godkjent av Irene og har fortsatt høyst tre setninger (FR-13)
**Og** testene som sjekker tekstene, er oppdatert, og en test sjekker at ingen FHI-koder (`NONSTL`, `pos_rate`, `Non-Sentinel`, `A+B`) finnes på siden (NFR-3)

---

## Epic 6: RSV og SARS-CoV-2

Brukeren kan velge RSV og SARS-CoV-2 i mal 1. Droppes hvis mal 1 for influensa ikke virker 2. desember. Veiledende: 3.–4. desember.

### Story 6.1: RSV

Som Sara
vil jeg kunne velge RSV,
slik at jeg kan se situasjonen for RSV på samme måte som for influensa (FR-2).

**Akseptansekriterier:**

**Gitt** mal 1 for influensa
**Når** RSV legges til
**Så** hentes RSV fra tabell 729 med `rsvtype` `A+B` (totalen, inkludert ukjent type) (FR-2, FR-6, addendum)
**Og** etiketten «RS-virus (A+B)» vises ikke for brukeren (NFR-3, addendum)
**Og** kildehenvisningen bruker FHIs ordlyd for 729 og tabellnavnet «RESPIaggr RSV antall og andel» (FR-12, addendum)
**Og** et ekte svar og dimensjonslisten for 729 er lagret i `tests/fixtures/fhi/` med hentedato i fila (AD-10)
**Og** tester dekker tolking av fixturen, riktig forespørsel med `respx`, kildehenvisningen og at RSV kan velges i skjemaet

### Story 6.2: SARS-CoV-2

Som Sara
vil jeg kunne velge SARS-CoV-2,
slik at jeg kan se alle tre luftveisvirusene (FR-2).

**Akseptansekriterier:**

**Gitt** mal 1 for influensa og RSV
**Når** SARS-CoV-2 legges til
**Så** hentes SARS-CoV-2 fra tabell 731 uten typedimensjon (FR-2, FR-6, addendum)
**Og** kildehenvisningen bruker FHIs ordlyd for 731 og tabellnavnet «RESPIaggr SARS-CoV-2 antall og andel» (FR-12, addendum)
**Og** et ekte svar og dimensjonslisten for 731 er lagret i `tests/fixtures/fhi/` med hentedato i fila (AD-10)
**Og** tester dekker tolking av fixturen, riktig forespørsel med `respx`, kildehenvisningen og at SARS-CoV-2 kan velges i skjemaet

---

## Epic 7: Testsett og README

Testsettet med 10 spørsmål viser at tallene, kildehenvisningene og varslene er riktige. KI-forklaringene er gjennomgått, og den endelige README-en er testet ved å følge den fra en ny klone av repoet. **Fast frist: appen er ferdig 6. desember.** Veiledende: 4.–6. desember. Testspørsmålene (7.1) kan hentes tidligere.

### Story 7.1: Velge de 10 testspørsmålene og hente fasit (Irene)

Som Irene
vil jeg ha et fast testsett med fasit hentet manuelt fra FHI,
slik at jeg kan vise at appen gir riktige tall (SM-1, PRD åpent spørsmål 3).

**Akseptansekriterier:**

**Gitt** malen og virusene som er bygget
**Når** testsettet er valgt
**Så** har det 10 utvalg fordelt på influensa, RSV og SARS-CoV-2, eller bare influensa hvis RSV og SARS-CoV-2 er droppet (SM-1)
**Og** spørsmålene bruker i hovedsak de avsluttede sesongene 2024/2025 og 2025/2026
**Og** testsettet har både utvalg med varsel (for eksempel 2024/2025 med R5) og uten varsel (SM-3)
**Og** for hvert utvalg står fasiten (tester, positive og andel per uke, og forventet varsel med regel) i `tests/fixtures/testsett/`, hentet manuelt fra FHIs nettsider, med hentedato i fila
**Og** for et spørsmål om sesongen som pågår, er fasiten og det lagrede API-svaret hentet samme dag, og datoen står i begge filene

### Story 7.2: Testsettet for tall og kildehenvisning

Som Irene
vil jeg at testsettet kjøres automatisk,
slik at jeg kan vise at 10 av 10 svar har riktige tall og riktig kilde (SM-1, SM-2).

**Akseptansekriterier:**

**Gitt** fasiten fra story 7.1
**Når** API-svarene for de 10 utvalgene er lagret i `tests/fixtures/fhi/`
**Så** gir en parametrisert test for hvert utvalg samme tall som fasiten (SM-1, FR-6)
**Og** kildehenvisningen er riktig i alle 10 (SM-2, FR-12)
**Og** for utvalg i sesongen som pågår, er API-svaret hentet samme dag som fasiten, og testen sjekker at datoene i de to filene er like
**Og** testene kjører uten nett (NFR-10)

### Story 7.3: Testsettet for varsel

Som Irene
vil jeg at varslene i testsettet testes automatisk,
slik at jeg kan vise at riktig varsel vises med riktig begrunnelse (SM-3).

**Akseptansekriterier:**

**Gitt** forventet varsel i fasiten fra story 7.1
**Når** `tjeneste` kjøres for hvert utvalg i testsettet
**Så** gir R1–R5 riktig resultat og riktig regel for alle utvalg, med og uten varsel (SM-3, FR-19)
**Og** testen viser at siden har varsel for utvalgene som skal ha det, og ikke for de andre

### Story 7.4: Lagre KI-forklaringer for testsettet

Som Irene
vil jeg ha lagret KI-forklaringene for testsettet,
slik at jeg kan gå gjennom dem mot sjekklisten (SM-4).

**Akseptansekriterier:**

**Gitt** en KI-nøkkel i `.env` hos den som kjører skriptet
**Når** et skript i `backend/scripts/` kjøres manuelt
**Så** lages forklaringer for de 10 utvalgene og lagres i `tests/fixtures/ki/` med modell og dato (SM-4, AD-7)
**Og** skriptet kjøres ikke av pytest, og testene virker uten nøkkel (NFR-10)
**Og** en test sjekker at alle 10 filene finnes, er på høyst 120 ord og har riktig modellnavn (FR-20)

### Story 7.5: Gå gjennom KI-forklaringene (Irene)

Som Irene
vil jeg vurdere hver lagret forklaring mot sjekklisten,
slik at jeg vet at KI-en ikke finner på tall eller årsaker (SM-4, FR-21).

**Akseptansekriterier:**

**Gitt** de 10 forklaringene fra story 7.4
**Når** jeg har gått gjennom dem
**Så** er hver forklaring vurdert mot de fire punktene i FR-21: bare tall fra dataene, ingen gjetting på årsaker, faguttrykk forklart, og usikkerhet nevnt når varselet vises
**Og** resultatet er notert per forklaring, og målet er at alle består (SM-4)
**Og** en forklaring som feiler, fører til en rettelse i prompten (ny godkjenning som i 4.2) og nye forklaringer, ikke til at teksten rettes for hånd (SM-C2)

### Story 7.6: Endelig README testet fra en ny klone

Som medstudent eller sensor
vil jeg kunne følge README fra en ny klone og få appen og testene til å virke,
slik at jeg kan prøve appen selv (NFR-1, NFR-9).

**Akseptansekriterier:**

**Gitt** en ny klone av repoet i en tom mappe, uten `.env`
**Når** README følges steg for steg
**Så** installeres appen, testene består, og appen starter og viser graf, tabell og varsel (NFR-1, NFR-10, AD-11)
**Og** README beskriver hva appen gjør, hvordan KI-nøkkelen settes, hvilke data som brukes med kilde, og hvilke begrensninger som finnes (for eksempel at Vercel er valgfritt) (NFR-8, NFR-9, AD-11)
**Og** testen fra en ny klone er notert i issuet med dato og eventuelle rettelser
**Og** en automatisk test sjekker at kommandoene i README finnes i `pyproject.toml` eller er standard uv-kommandoer

---

## Epic 8: Strekkmål og valgfritt

Bare hvis tiden tillater det etter 6. desember, før innleveringen 15. desember. Mal 2 påbegynnes først når mal 1 virker for alle tre virus og testene består (PRD kapittel 5). Vercel er valgfritt (AD-11).

### Story 8.1: Mal 2 – to sesonger og kontrollregler per sesong (strekkmål)

Som Sara
vil jeg sammenligne denne sesongen med forrige,
slik at jeg ser om smitten er høyere eller lavere enn i fjor (FR-23, FR-24).

**Akseptansekriterier:**

**Gitt** mal 1 for alle tre virus
**Når** `tjeneste` lager svar for mal 2
**Så** hentes «denne sesongen» (siste sesong med data) og «forrige» som to serier, ordnet etter uke i sesongen fra uke 40 (FR-23)
**Og** uke 53 som bare finnes i den ene sesongen, har ingen verdi i den andre og telles ikke som manglende i R3 (FR-23, FR-24)
**Og** `kontrollregler.vurder` kalles én gang per sesong, og varselet sier hvilken sesong det gjelder (FR-24)
**Og** tester dekker 2026/2027 mot 2025/2026 (ingen R5) og uke 53

### Story 8.2: Mal 2 – graf og tabell (strekkmål)

Som Sara
vil jeg se begge sesongene i samme graf og tabell,
slik at jeg kan sammenligne dem uke for uke (FR-23).

**Akseptansekriterier:**

**Gitt** svaret fra story 8.1
**Når** mal 2 velges i skjemaet
**Så** vises mal 2 i mallisten som et spørsmål på vanlig norsk (FR-1)
**Og** grafen har hel og stiplet linje med etiketter direkte på grafen, ikke bare farge (FR-23, NFR-7, AD-8)
**Og** tabellen viser begge sesongene side om side (FR-23)
**Og** tester dekker mallisten, JSON-blokken med to serier og tabellen

### Story 8.3: Publisere på Vercel (valgfritt)

Som medstudent
vil jeg kunne åpne appen i nettleseren uten å klone repoet,
slik at jeg kan prøve den raskt (AD-11).

**Akseptansekriterier:**

**Gitt** at appen er ferdig
**Når** den publiseres på Vercel
**Så** er FastAPI-appen pekt ut med `[tool.vercel] entrypoint` i `pyproject.toml`, og `ANTHROPIC_API_KEY` er satt i prosjektets miljøvariabler (AD-11, NFR-9)
**Og** cachen ligger i `/tmp/fhi-helsedata-cache`, og README sier at den er flyktig og bare gjelder én instans (AD-4, AD-11)
**Og** en test sjekker at `VERCEL` i miljøet gir cachemappen i `/tmp`
**Og** lenken og datoen for publiseringen står i README
