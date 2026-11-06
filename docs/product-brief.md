# Product Brief: FHI Helsedata-utforsker

## Executive Summary

For studenter som skal skrive om luftveisinfeksjoner i Norge, lager vi en KI-assistert utforsker for laboratoriedata fra Folkehelseinstituttets (FHI) åpne statistikk-API. Brukeren velger et ferdig spørsmål fra en liste med maler – for eksempel «vis andel positive influensatester uke for uke denne sesongen» – og velger virus, sesong og eventuelt aldersgruppe. Appen henter tallene, viser dem som graf og lar KI forklare hva grafen viser, med kildehenvisning. Hvis datagrunnlaget er for tynt til en klar konklusjon, sier appen fra og forklarer hvorfor.

I dag krever FHIs data god kjennskap til API-struktur og statistikk for å bli brukt riktig, noe som gjør at mye verdifull informasjon om smittsomme sykdommer og laboratoriefunn forblir utilgjengelig for de som trenger den raskt. Prosjektet kombinerer molekylærmedisinsk fagforståelse med KI-assistert utvikling for å bygge en bro mellom rådata og innsikt – uten å gå på akkord med personvern eller datakvalitet.

Nå er tidspunktet fordi FHI selv jobber aktivt med å gjøre helsedata raskere og sikrere tilgjengelig, blant annet gjennom et åpent API, og fordi KI-verktøy nå gjør det mulig å bygge et enkelt grensesnitt mot åpne data på kort tid – noe som passer godt med læringsmålene i IBE160.

## The Problem

FHI gjør store mengder helsedata – blant annet om smittsomme sykdommer og laboratoriefunn – tilgjengelig gjennom et åpent statistikk-API. Dataene finnes der, men er i praksis vanskelig tilgjengelige: man må kjenne datastrukturen, velge riktige variabler (sykdom, tidsperiode, geografi, alder, kjønn) og tolke resultatene riktig for å få noe meningsfullt ut av dem.

Dette rammer flere grupper: studenter og forskere som vil utforske trender uten å bruke timer på API-dokumentasjon, journalister og kommunikasjonsrådgivere som trenger raske og korrekte oppsummeringer, og kommunehelsetjenesten som ønsker oversikt uten eget analysemiljø. I dag løses dette gjerne ved manuell nedlasting til Excel, eller ved at man rett og slett lar være å bruke dataene.

Kostnaden er et gap mellom data som finnes og innsikt som faktisk brukes – og risikoen for at de som prøver å tolke tallene selv, trekker feil konklusjoner fra rå statistikk uten kontekst.

## The Solution

En KI-assistert applikasjon som gjør laboratoriedata fra FHIs åpne statistikk-API enkle å bruke. Brukeren velger et spørsmål fra en liste med maler, og systemet:

1. Lar brukeren velge virus, sesong og eventuelt aldersgruppe i den valgte malen
2. Henter riktige data fra FHIs API
3. Viser resultatet som graf og tabell
4. Lar KI skrive en kort forklaring av hva tallene viser, med kildehenvisning
5. Varsler dersom datagrunnlaget er for tynt til en klar konklusjon, og sier hvilken regel som slo inn

**Hva KI-en gjør i v1:** En språkmodell skriver bare den tekstlige forklaringen i steg 4. Den får de hentede tallene som grunnlag, skal holde seg til dem og skal ikke gjette på årsaker. Hvilke data som hentes (steg 1–2) og om varselet vises (steg 5), styres av faste regler i koden, ikke av KI. Det gjør appen enklere å teste og kvalitetssikre.

**Regel for for tynt datagrunnlag:** Varselet vises når minst én av disse gjelder for utvalget brukeren har valgt:

| Kontrollspørsmål | Varsel hvis | Begrunnelse |
| --- | --- | --- |
| Hvor mange positive prøver er det totalt? | færre enn 20 | CDC/NCHS regner rater basert på færre enn 20 tilfeller som upålitelige (relativ usikkerhet over ca. 22 %) |
| Hvor mange tester bygger andelen positive på? | mer enn 20 % av ukene har færre enn 30 tester | NCHS-standarden for andeler krever minst 30 observasjoner; 20 % er samme grense som FHI bruker for å skjule hele tidsserier |
| Hvor stor andel av verdiene mangler eller er skjult (API-symbolene `..`, `.` og `:`)? | mer enn 20 % | FHI skjuler hele tidsserier når mer enn 20 % av verdiene er skjult |
| Hvor mange uker er det å vise utvikling over? | færre enn 3 | Eget faglig valg, begrunnes i PRD |
| Går perioden over 1. mars 2025? | ja | Fra denne datoen er alle norske mikrobiologiske laboratorier med i datagrunnlaget, så tall før og etter er ikke direkte sammenlignbare (FHI) |

Uker med færre enn 30 tester markeres også som usikre i grafen.

FHIs egne grenser (færre enn 4 tilfeller, 6 eller færre tilfeller) gjelder når tall skal *skjules* av personvern- og stabilitetshensyn. Appen skal *advare* om usikkerhet før det, og bruker derfor den høyere grensen på 20.

Graf og tall fungerer uten KI-nøkkel. Bare forklaringen i steg 4 krever en nøkkel til språkmodellen.

Resultatet er at brukeren går fra et valgt spørsmål til en forklart graf på under ett minutt – uten å måtte forstå API-dokumentasjon eller statistiske detaljer selv. Vi spesifiserer bevisst ikke ennå hvilken KI-modell, hvilket rammeverk eller hvilken hosting-løsning som brukes – det er implementasjonsvalg som beskrives i arkitekturen.

## What Makes This Different

| Alternativ i dag | Hvorfor brukere tolererer det | Hvorfor vår tilnærming er bedre |
| --- | --- | --- |
| Manuell nedlasting til Excel/CSV | Det er den eneste veien inn i dataene i dag | Sekunder i stedet for timer, ingen manuell filbehandling |
| Direkte bruk av FHIs API | Fungerer for de som kan programmere | Krever ingen teknisk kompetanse – brukeren velger et spørsmål fra en liste |
| Å la være å bruke dataene | Terskelen oppleves for høy til at det er verdt det | Senker terskelen så mye at flere faktisk bruker dataene |

Dette er ingen teknisk «moat» – FHIs data er åpne og tilgjengelige for alle. Fordelen vår er en kombinasjon av god brukeropplevelse (ferdige spørsmål og forklarte grafer i stedet for API-kall) og faglig kvalitetssikring: fordi vi har molekylærmedisinsk bakgrunn, kan vi bygge inn en forståelse av hva laboratoriefunn og smittedata faktisk representerer, og dermed fange opp feiltolkninger en rent teknisk løsning ville gått glipp av – for eksempel at utvidelsen av laboratoriedekningen i mars 2025 gjør at tall før og etter ikke kan sammenlignes direkte. Vi er også bevisst ærlige om usikkerhet – systemet er bygget for å si «dette bør undersøkes nærmere» fremfor å gjette på årsaker.

## Who This Serves

**Primærbruker:** En student som skal skrive en oppgave om luftveisinfeksjoner i Norge, for eksempel influensa, og som ikke har erfaring med API-er eller statistikkprogrammer. Studenten vil se hvordan tallene har utviklet seg gjennom en sesong og få en forklaring av hva grafen viser, uten å bruke tid på å lære seg FHIs API. Suksess er å gå fra valgt spørsmål til en korrekt, forklart graf med kildehenvisning på under ett minutt, og å kunne stole på at tallene stemmer med FHIs egne.

**Sekundærbrukere:** Forskere, fagpersoner i kommunehelsetjenesten, journalister og kommunikasjonsrådgivere som trenger en rask og korrekt oversikt over folkehelsetall. Appen designes ikke spesielt for dem i v1.

## Success Criteria

| Signal | Metrikk / evidens | Mål | Når måles |
| --- | --- | --- | --- |
| Korrekte tall | Fast testsett med 10 malspørsmål fordelt på influensa, RSV og SARS-CoV-2, der riktige tall er hentet manuelt fra FHI på forhånd | 10 av 10 gir samme tall som fasiten | Automatiske tester mot lagrede API-svar |
| Kildehenvisning | Andel svar i testsettet med korrekt kildehenvisning | 100 % | Automatiske tester |
| Varsel om tynt datagrunnlag | Testsettet har tilfeller der varselet skal vises (f.eks. RSV og SARS-CoV-2 utenom sesong, perioder over 1. mars 2025) og der det ikke skal vises | Varselet vises riktig, med riktig begrunnelse, i alle tilfeller | Automatiske tester |
| Forklaringens kvalitet | KI-forklaringene vurderes mot en sjekkliste: bruker bare hentede tall, ingen oppdiktede årsaker, nevner usikkerhet når varselet vises | Alle forklaringer i testsettet består | Manuell gjennomgang av lagrede forklaringer |
| Brukerutfall | Tid fra valgt mal til forklart graf | Under 1 minutt | Ved brukertesting |
| Adopsjon/atferd | Andel testbrukere som utforsker en mal til etter første svar | Over 50 % | Ved brukertesting |

## Scope

**IN – første versjon**

- Laboratoriedata fra MSIS-labdatabasen via FHIs åpne statistikk-API for tre luftveisvirus: influensa, RSV og SARS-CoV-2. Dataene er ukentlige, gjelder hele landet, er fordelt på aldersgrupper og finnes fra uke 40 i 2024.
- Forhåndsdefinerte spørsmålsmaler:
  1. Utvikling uke for uke: «vis andel positive tester for [virus] i sesongen [sesong]»
  2. Sammenligning av sesonger: «sammenlign [virus] denne sesongen med forrige»
  3. Aldersfordeling: «hvilke aldersgrupper har flest positive prøver for [virus] i [sesong]»
- Rekkefølge: mal 1 bygges ferdig og testes for influensa før RSV, SARS-CoV-2 og de andre malene legges til.
- Automatisk henting fra FHIs åpne statistikk-API
- Grafisk visualisering av resultatet, med usikre uker markert. Grafene skal kunne leses uten å skille farger: linjer og søyler skilles også med mønster, form eller etiketter direkte på grafen, og tallene vises i en tabell ved siden av.
- Kort tekstlig forklaring med kildehenvisning, skrevet av KI
- Varsel etter fast regel når datagrunnlaget er for tynt (se The Solution)
- Graf og tall fungerer uten KI-nøkkel
- Hvilken overvåkingstype som brukes (vanlig klinisk praksis eller fyrtårnsystemet, eller begge), avklares i PRD-en.

**Nøkler, testdata og dokumentasjon**

- KI-nøkkelen ligger i en `.env`-fil som står i `.gitignore` og aldri committes. Repoet har en `.env.example` som viser hva som må fylles inn.
- Testene bruker lagrede svar fra både FHIs API og språkmodellen, i `tests/fixtures/`. Da kjører de uten nett og uten KI-nøkkel, og de koster ingenting.
- Planleggingsdokumentene og KI-loggen ligger i `docs/`.

**Strekkmål – hvis tiden tillater det**

- Mal 4, fylker: «sammenlign fylkene for [luftveisagens]» (tabellen «Oversikt luftveisagens» har tall per fylke)

**OUT – ikke nå**

- Fri-tekst-tolkning av vilkårlig formulerte spørsmål (se Vision)
- Data eldre enn høsten 2024 (finnes bare på bestilling fra FHI)
- Mage-tarm-virus og andre MSIS-tabeller enn de tre luftveisvirusene
- Bruk av personidentifiserbare eller sensitive helsedata
- Støtte for andre datakilder enn FHIs åpne API
- Flerspråklig grensesnitt
- Automatiske varsler/abonnement på nye data
- Integrasjon med FHIs interne systemer

**Scope-test:** Hvis vi fjerner et element og fortsatt kan bevise kjerneverdien – rask, korrekt og forklart innsikt fra åpne helsedata – hører det ikke hjemme i versjon 1.

## Vision

**Nå:** En prototype der én bruker velger et spørsmål fra en mal og får en forklart graf over laboratoriedata for influensa, RSV og SARS-CoV-2 fra FHIs åpne API.

**Neste:** Et situasjonsbilde for kommuneoverleger og andre som har ansvar for smittevern i kommunene. De får i dag FHIs statusrapporter annenhver uke og må selv tolke hva tallene betyr der de bor. Neste versjon viser smittesituasjonen i deres fylke (tabellen «Oversikt luftveisagens» har fylkestall) sammenlignet med landet, med de samme kvalitetsreglene, slik at de raskt ser hva som skjer og hvor sikre tallene er. Før dette bygges, testes behovet i samtaler med noen kommuneoverleger. Fritekstspørsmål, der KI oversetter spørsmålet til en av de eksisterende malene og viser hvilken mal som ble brukt, kommer i samme runde.

**2–3 år:** Et verktøy kommunene bruker rutinemessig i smittevernarbeidet. Det kobler flere datakilder når de blir åpent tilgjengelige, og varsler aktivt om usikkerhet fremfor å late som om alle svar er sikre. FHI moderniserer smittevernovervåkingen for å gi et oppdatert og detaljert situasjonsbilde (NORSURV, 2024–2028), og det europeiske helsedataområdet (EHDS) gjør flere helsedata tilgjengelige fra 2029. Begge deler gjør retningen mer realistisk over tid.

## Kilder

- FHIs åpne API, MSIS-tabeller: https://statistikk-data.fhi.no/api/open/v1/msis/Table
- Metadata for influensa (tabell 724), RSV (729), SARS-CoV-2 (731) og Oversikt luftveisagens (733): `https://statistikk-data.fhi.no/api/open/v1/msis/Table/{tabell}/metadata`
- FHIs regler for skjuling av små tall, dødsårsakstabellen i Folkehelsestatistikk (tabell 342): https://statistikk-data.fhi.no/api/open/v1/nokkel/Table/342/metadata
- CDC WONDER, regler for små tall: https://wonder.cdc.gov/wonder/help/ucd.html
- NCHS Data Presentation Standards for Proportions: https://wwwn.cdc.gov/nchs/nhanes/tutorials/reliabilityofestimates.aspx
- Helsedirektoratet, Digitalt økosystem for nasjonal smittevernberedskap (NORSURV): https://www.helsedirektoratet.no/digitalisering-og-e-helse/nasjonal-e-helseportefolje/tiltak-i-nasjonal-e-helseportefolje/digitalt-okosystem-for-nasjonal-smittevernberedskap
- FHI, webinar for kommuneoverleger 12.11.2025: https://www.fhi.no/contentassets/7dcd25aa21354860a83b8d0195f0c864/kommuneoverlegewebinar12.11.2025.pdf
- FHI, FHIs rolle og oppdrag i EHDS: https://www.fhi.no/hd/det-europeiske-helsedataomradet/fhis-rolle-og-oppdrag-i-ehds/
