# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G63 – G63-zumbo |
| **Product brief** | `docs/product-brief.md` (commit `2c50b61`). `product-brief-fhi-helsedata.md` i rotmappen har identisk innhold. Vi har vurdert fila i `docs/`, som README viser til. |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Godt utgangspunkt med justeringer.** Gruppen kan gå videre og innarbeide punktene under.

**Det som er bra:**

1. Godt valgt problem med åpne data. FHIs åpne statistikk-API er en reell datakilde uten personopplysninger, og dere har fagbakgrunn (molekylærmedisin) som gjør at dere kan vurdere om tolkningen av smitte- og laboratoriedata er riktig. Det er et stort pluss for kvalitetssikringen.
2. Tydelig og fornuftig avgrensning i Scope. V1 bruker forhåndsdefinerte spørsmålsmaler i stedet for fri tekst, og bare FHIs åpne API. Scope-testen («hvis vi fjerner et element og fortsatt kan bevise kjerneverdien …») er et godt verktøy.
3. Bevisst holdning til usikkerhet. Appen skal varsle når datagrunnlaget er for tynt, og si «dette bør undersøkes nærmere» i stedet for å gjette på årsaker.

**De viktigste endringene:**

1. **Executive Summary og Solution stemmer ikke med Scope.** De beskriver fritekstspørsmål («hvordan har influensatilfeller utviklet seg de siste fem årene?») som tolkes av KI, mens Scope sier at v1 bruker maler og at fri tekst er et strekkmål. Oppdater de første delene, slik at de beskriver malbasert v1, og sett fritekst under Vision.
2. **Definer hva KI-en faktisk gjør i v1, og hvordan «for tynt datagrunnlag» avgjøres.** Med maler er det mest naturlige at KI skriver den tekstlige forklaringen. Bestem om varselet om tynt datagrunnlag skal være en fast regel (for eksempel færre enn N tilfeller eller manglende perioder) eller en KI-vurdering. En fast regel kan testes. En KI-vurdering er vanskeligere å kvalitetssikre.
3. **Gjør suksesskriteriene testbare i emnet.** «100 % korrekt kildehenvisning og riktig tolket datagrunnlag» er et godt mål. Gjør det konkret med et fast sett testspørsmål med fasit, for eksempel 10 malspørsmål der dere på forhånd har hentet riktige tall manuelt. Kriteriet «bestått vurdering … ved innlevering/muntlig eksamen» bør erstattes. Emnet har ingen muntlig eksamen, og et produktkriterium bør handle om appen.

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Middels**

**Sammenlignbart med:** 7) Kurs-FAQ-chatbot (middels). Begge henter informasjon fra en kilde og lar KI forklare den med kildehenvisning og håndtering av usikkerhet. Her er kilden et statistikk-API i stedet for en kunnskapsbase, og visualisering kommer i tillegg.

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | middels | Riktig valg av tabell, variabler (sykdom, periode, geografi, alder, kjønn) og riktig tolkning av tallene. Dere har fagkunnskapen til å vurdere dette. |
| Datamodell – antall entiteter og relasjoner mellom dem | lav | Spørsmålsmaler, datasett og eventuelt mellomlagrede API-svar. Ingen brukerkontoer i v1. |
| Brukere, roller og innlogging | lav | Én bruker uten innlogging. Det er et godt valg. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | middels | KI-en skriver forklaringen. Den må holde seg til tallene som er hentet, og ikke finne på årsaker. Det krever gode prompts og testing. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | middels | FHIs statistikk-API (åpent) og et LLM-API. API-strukturen må forstås godt før malene kan bygges. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | lav | Ingen. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | lav | Ingen opplasting. Grafer genereres i appen. |
| Sikkerhet og personvern | lav | Bare åpne, aggregerte data. Personidentifiserbare data er eksplisitt utelatt. |

**Hva vanskelighetsgraden betyr for dere:**

- _Middels:_ Et godt balansert valg. Pass på at kjerneflyten blir ferdig og stabil før dere legger til mer. For dere betyr det at noen få maler som henter, viser og forklarer riktige tall bør være ferdige og testet før dere går videre til fritekst.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | OK | Malbasert v1 med henting, graf, forklaring og varsel er realistisk for én person. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | risiko | Motsetningen mellom fritekst og maler må løses først. Oppgi også hvilke konkrete datasett og maler v1 skal ha. BMAD er ikke satt opp i repoet ennå. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | OK | Python-backend (FastAPI er alt satt opp med uv) med et kjent grafbibliotek passer godt. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | OK | Dere har fagkunnskap og kan kontrollere tallene manuelt mot FHIs egne visninger. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | risiko | Henting og graf kan testes mot lagrede API-svar med kjente tall. KI-forklaringene må testes mot en sjekkliste. Regelen for «for tynt datagrunnlag» må defineres først. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | risiko | FHIs API er åpent, men LLM-forklaringen krever en nøkkel. Planlegg at graf og tall vises uten nøkkel, og at forklaringen kan kjøres med egen nøkkel via `.env.example`. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | risiko | LLM-kall koster litt. Lagre eksempelsvar fra både FHI og LLM til testene, slik at testene ikke er avhengige av nett eller nøkkel. |

**Konklusjon om gjennomførbarhet:**

- **Gjennomførbart som beskrevet.**

Det gjelder Scope-delen slik den står. Fritekst-tolkning bør forbli et strekkmål.

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. Start med 3–5 maler for et lite antall sykdommer eller laboratoriefunn, med valg av periode og eventuelt fylke. Utvid antall datasett før dere går over til fritekst.
2. Hvis dere når fritekst, la KI-en bare oversette spørsmålet til en av de eksisterende malene (og vise hvilken), i stedet for å bygge vilkårlige API-kall. Det er lettere å kontrollere og teste.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | Juster | Tydelig problem, men beskriver fritekstspørsmål, som ikke er med i v1. Oppdater til malbasert v1. |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | OK | Godt beskrevet: dataene finnes, men krever kjennskap til API og statistikk. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | Juster | De fem stegene beskriver brukeropplevelsen godt, men steg 1 (tolke spørsmålet) stemmer ikke med malbasert v1. |
| What Makes This Different – er vurderingen ærlig og realistisk? | OK | Ærlig: ingen teknisk vollgrav, fordelen er brukeropplevelse og faglig kvalitetssikring. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | Juster | Primærbrukeren samler tre grupper (studenter, forskere, kommunehelsetjenesten). Velg én konkret bruker å designe for, for eksempel en student som skal skrive om influensatrender. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | Juster | Gode signaler, men trenger et fast testsett med fasit. Kriteriet om bestått vurdering bør erstattes med et produktkriterium. |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | OK | Tydelig IN/OUT-liste og en nyttig scope-test. |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | OK | Trinnvis visjon som ikke blander seg inn i v1. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | Juster | Briefen er et godt grunnlag når motsetningen er løst. Sett opp BMAD i repoet og lag PRD før dere bygger videre på backenden. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | OK | Velg mal → hent → graf → forklaring → varsel. Kjerneflyten er tydelig og har passe omfang. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | Juster | Lag et testsett med kjente tall og forventet varsel. Pytest er alt satt opp, så det ligger godt til rette. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | Juster | Skisser hovedskjermen: valg av mal, graf, forklaring og varsel. Tenk på lesbare grafer og tekst for dem som ikke ser fargeforskjeller. |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | Juster | FastAPI og SQLAlchemy er lagt til før arkitekturen er beskrevet. Begrunn i arkitekturdokumentet om det trengs en database, eller om mellomlagring holder. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Juster | README har alt oppstart med uv, og det er bra. Utvid med LLM-nøkkel via `.env.example` og hva som virker uten. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | Juster | Fjern duplikatet `product-brief-fhi-helsedata.md` i rotmappen, slik at det bare finnes én gjeldende brief. Legg lagrede API-svar til testene i en egen mappe. |

## 3. Neste steg for gruppen

1. Oppdater Executive Summary og Solution, slik at de beskriver malbasert v1, og fjern duplikatbriefen i rotmappen.
2. Bestem regelen for «for tynt datagrunnlag», og lag et testsett med 10 malspørsmål med manuelt kontrollerte tall.
3. Sett opp BMAD i repoet og lag PRD, der hver mal og hvert datasett i v1 er listet opp.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
