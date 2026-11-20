# Product Brief: FHI Helsedata-utforsker

## Executive Summary

For studenter og andre uten medisinsk eller forskningsbakgrunn som vil forstå smittesituasjonen i Norge – for eksempel fordi de skriver om beredskap – lager vi et KI-assistert verktøy som gjør tall fra et nasjonalt helseregister om til et raskt og ærlig situasjonsbilde over luftveisinfeksjoner. Kilden er laboratoriedatabasen i Meldingssystem for smittsomme sykdommer (MSIS), som Folkehelseinstituttet (FHI) gjør tilgjengelig gjennom et åpent statistikk-API. Brukeren velger et ferdig spørsmål fra en liste med maler – for eksempel «vis andel positive influensatester uke for uke denne sesongen» – og velger virus, sesong og eventuelt aldersgruppe. Appen henter tallene, viser dem som graf og tabell, og lar KI forklare hva de viser med enkle ord og kildehenvisning. Hvis datagrunnlaget er for tynt til en klar konklusjon, sier appen fra og forklarer hvorfor.

I beredskap er et riktig situasjonsbilde like viktig som et raskt et. Tallene i helseregistrene finnes, men de krever kjennskap til API-struktur, statistikk og hvordan dataene samles inn for å bli tolket riktig. Prosjektet kombinerer molekylærmedisinsk fagforståelse med KI-assistert utvikling for å bygge en bro mellom registerdata og innsikt – uten å gå på akkord med personvern eller datakvalitet.

Nå er tidspunktet fordi FHI moderniserer smittevernovervåkingen for å gi et oppdatert og detaljert situasjonsbilde (NORSURV, 2024–2028), og stadig flere registerdata gjøres tilgjengelige gjennom FHIs åpne API. KI-verktøy gjør det samtidig mulig å bygge et enkelt grensesnitt mot åpne data på kort tid – noe som passer godt med læringsmålene i IBE160.

## The Problem

FHI gjør data fra nasjonale helseregistre – blant annet laboratoriefunn av smittsomme sykdommer i MSIS – tilgjengelig gjennom et åpent statistikk-API. Dataene finnes der, men er i praksis vanskelig tilgjengelige: man må kjenne datastrukturen, velge riktige variabler (sykdom, tidsperiode, geografi, alder) og tolke resultatene riktig for å få noe meningsfullt ut av dem.

Det er særlig vanskelig for dem som ikke har medisinsk eller forskningsbakgrunn. Begreper som «andel positive» og «fyrtårnsystem» er ikke selvforklarende, og endringer i hvordan dataene samles inn er ikke synlige i tallene. Et eksempel er at alle norske mikrobiologiske laboratorier kom med i datagrunnlaget fra mars 2025, slik at tall før og etter ikke kan sammenlignes direkte. I dag løses dette gjerne ved manuell nedlasting til Excel, ved å lese FHIs rapporter som er skrevet for fagfolk, eller ved at man rett og slett lar være å bruke dataene.

Kostnaden er et gap mellom data som finnes og innsikt som faktisk brukes – og i beredskapssammenheng en reell risiko for at noen trekker feil konklusjoner fra rå statistikk uten kontekst.

## The Solution

En KI-assistert applikasjon som gjør registerdata fra FHIs åpne statistikk-API forståelige for folk uten fagbakgrunn. Brukeren velger et spørsmål fra en liste med maler, og systemet:

1. Lar brukeren velge virus, sesong og eventuelt aldersgruppe i den valgte malen
2. Henter riktige data fra FHIs API
3. Viser resultatet som graf og tabell, med korte forklaringer av sentrale begreper
4. Lar KI skrive en kort forklaring av hva tallene viser, med enkle ord og kildehenvisning
5. Varsler dersom datagrunnlaget er for tynt til en klar konklusjon, og sier hvilken regel som slo inn

**Hva KI-en gjør i v1:** En språkmodell skriver bare den tekstlige forklaringen i steg 4. Den får de hentede tallene som grunnlag, skal holde seg til dem, skal skrive uten uforklarte faguttrykk og skal ikke gjette på årsaker. Hvilke data som hentes (steg 1–2), begrepsforklaringene (steg 3) og om varselet vises (steg 5) styres av faste regler og faste tekster i koden, ikke av KI. Det gjør appen enklere å teste og kvalitetssikre.

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

Graf, tabell, begrepsforklaringer og varsel fungerer uten KI-nøkkel. Bare forklaringen i steg 4 krever en nøkkel til språkmodellen.

Resultatet er at brukeren går fra et valgt spørsmål til et forklart situasjonsbilde på under ett minutt – uten å måtte forstå API-dokumentasjon, statistiske detaljer eller medisinske faguttrykk selv. Vi spesifiserer bevisst ikke ennå hvilken KI-modell, hvilket rammeverk eller hvilken hosting-løsning som brukes – det er implementasjonsvalg som beskrives i arkitekturen.

## What Makes This Different

| Alternativ i dag | Hvorfor brukere tolererer det | Hvorfor vår tilnærming er bedre |
| --- | --- | --- |
| Manuell nedlasting til Excel/CSV | Det er den eneste veien inn i dataene i dag | Sekunder i stedet for timer, ingen manuell filbehandling |
| Direkte bruk av FHIs API | Fungerer for de som kan programmere | Krever ingen teknisk kompetanse – brukeren velger et spørsmål fra en liste |
| FHIs egne statusrapporter | De er faglig korrekte og oppdateres jevnlig | De er skrevet for fagfolk; vi forklarer de samme tallene med enkle ord og sier tydelig fra når de er usikre |
| Å la være å bruke dataene | Terskelen oppleves for høy til at det er verdt det | Senker terskelen så mye at flere faktisk bruker dataene |

Dette er ingen teknisk «moat» – FHIs data er åpne og tilgjengelige for alle. Fordelen vår er en kombinasjon av god brukeropplevelse for folk uten fagbakgrunn (ferdige spørsmål, forklarte grafer og begreper med enkle ord) og faglig kvalitetssikring: fordi vi har molekylærmedisinsk bakgrunn, kan vi bygge inn en forståelse av hva laboratoriefunn og smittedata faktisk representerer, og dermed fange opp feiltolkninger en rent teknisk løsning ville gått glipp av – for eksempel at utvidelsen av laboratoriedekningen i mars 2025 gjør at tall før og etter ikke kan sammenlignes direkte. Vi er også bevisst ærlige om usikkerhet – systemet er bygget for å si «dette bør undersøkes nærmere» fremfor å gjette på årsaker. I beredskap er det like viktig å vite hva man *ikke* vet.

## Who This Serves

**Primærbruker:** En student uten medisinsk eller forskningsbakgrunn – for eksempel innen beredskap, samfunnssikkerhet eller IT – som skal skrive om smittesituasjonen eller beredskapen for luftveisinfeksjoner i Norge. Studenten har ikke erfaring med API-er eller statistikkprogrammer, og kjenner ikke begreper som «andel positive» eller «fyrtårnsystem». Studenten vil se hvordan tallene har utviklet seg gjennom en sesong, forstå hva grafen viser og vite om tallene er til å stole på. Suksess er å gå fra valgt spørsmål til et korrekt, forklart situasjonsbilde med kildehenvisning på under ett minutt, og å kunne gjengi det riktig med egne ord.

Studenten representerer en større gruppe: folk uten medisinsk eller forskningsbakgrunn som trenger å forstå smittesituasjonen.

**Sekundærbrukere:** Beredskapsrådgivere i kommuner og virksomheter, journalister og kommunikasjonsrådgivere som trenger en rask og korrekt oversikt over smittesituasjonen. Kommuneoverleger og andre med smittevernansvar er målgruppen for neste versjon (se Vision). Appen designes ikke spesielt for sekundærbrukerne i v1.

## Success Criteria

| Signal | Metrikk / evidens | Mål | Når måles |
| --- | --- | --- | --- |
| Korrekte tall | Fast testsett med 10 malspørsmål fordelt på influensa, RSV og SARS-CoV-2, der riktige tall er hentet manuelt fra FHI på forhånd | 10 av 10 gir samme tall som fasiten | Automatiske tester mot lagrede API-svar |
| Kildehenvisning | Andel svar i testsettet med korrekt kildehenvisning | 100 % | Automatiske tester |
| Varsel om tynt datagrunnlag | Testsettet har utvalg som kan velges i appen, der varselet skal vises (f.eks. smale aldersgrupper og perioder over 1. mars 2025) og der det ikke skal vises. De konkrete tilfellene bekreftes når testsettet lages fra ekte tall. Grensetilfellene for hver regel testes med konstruerte testdata i `tests/fixtures/` | Varselet vises riktig, med riktig begrunnelse, i alle tilfeller | Automatiske tester |
| Forklaringens kvalitet | KI-forklaringene vurderes mot en sjekkliste: bruker bare hentede tall, ingen oppdiktede årsaker, ingen uforklarte faguttrykk, nevner usikkerhet når varselet vises | Alle forklaringer i testsettet består | Manuell gjennomgang av lagrede forklaringer |
| Forståelighet | Testbrukere uten medisinsk bakgrunn forklarer med egne ord hva grafen viser, og om tallene er sikre | Minst 4 av 5 testbrukere svarer riktig på begge | Ved brukertesting |
| Brukerutfall | Tid fra valgt mal til forklart situasjonsbilde | Under 1 minutt | Ved brukertesting |

## Scope

**IN – første versjon**

- Laboratoriedata fra MSIS-labdatabasen via FHIs åpne statistikk-API for tre luftveisvirus: influensa, RSV og SARS-CoV-2. Dataene er ukentlige, gjelder hele landet, er fordelt på aldersgrupper og finnes fra uke 40 i 2024.
- Forhåndsdefinert spørsmålsmal 1, utvikling uke for uke: «vis andel positive tester for [virus] i sesongen [sesong]»
- Rekkefølge: mal 1 bygges ferdig og testes for influensa før RSV og SARS-CoV-2 legges til.
- Automatisk henting fra FHIs åpne statistikk-API
- Grafisk visualisering av resultatet, med usikre uker markert. Grafene skal kunne leses uten å skille farger: linjer og søyler skilles også med mønster, form eller etiketter direkte på grafen, og tallene vises i en tabell ved siden av.
- Korte, faste forklaringer av sentrale begreper (for eksempel «andel positive», «sesong» og overvåkingstypen som brukes)
- Kort tekstlig forklaring med enkle ord og kildehenvisning, skrevet av KI
- Varsel etter fast regel når datagrunnlaget er for tynt (se The Solution)
- Graf, tabell, begrepsforklaringer og varsel fungerer uten KI-nøkkel
- Hvilken overvåkingstype som brukes (vanlig klinisk praksis eller fyrtårnsystemet, eller begge), avklares i PRD-en.

**Nøkler, testdata og dokumentasjon**

- KI-nøkkelen ligger i en `.env`-fil som står i `.gitignore` og aldri committes. Repoet har en `.env.example` som viser hva som må fylles inn.
- Testene bruker lagrede svar fra både FHIs API og språkmodellen, i `tests/fixtures/`. Da kjører de uten nett og uten KI-nøkkel, og de koster ingenting.
- Planleggingsdokumentene og KI-loggen ligger i `docs/` og `_bmad-output/planning-artifacts/`.

**Strekkmål – hvis tiden tillater det**

- Mal 2, sammenligning av sesonger: «sammenlign [virus] denne sesongen med forrige»

**OUT – ikke nå**

- Mal 3 (aldersfordeling) og mal 4 (fylker, tabellen «Oversikt luftveisagens»)
- Fri-tekst-tolkning av vilkårlig formulerte spørsmål (se Vision)
- Data eldre enn høsten 2024 (finnes bare på bestilling fra FHI)
- Andre registre enn MSIS, som genomovervåkning, vaksinasjonsdekning og Legemiddelregisteret (se Vision)
- Mage-tarm-virus og andre MSIS-tabeller enn de tre luftveisvirusene
- Data om enkeltpersoner fra helseregistre. Slike data krever søknad og godkjenning; v1 bruker bare åpne, aggregerte tall.
- Støtte for andre datakilder enn FHIs åpne API
- Flerspråklig grensesnitt
- Automatiske varsler/abonnement på nye data
- Integrasjon med FHIs interne systemer

**Scope-test:** Hvis vi fjerner et element og fortsatt kan bevise kjerneverdien – et raskt, korrekt og forklart situasjonsbilde fra åpne registerdata for folk uten fagbakgrunn – hører det ikke hjemme i versjon 1.

## Vision

**Nå:** En prototype der én bruker uten fagbakgrunn velger et spørsmål fra en mal og får et forklart situasjonsbilde over laboratoriedata for influensa, RSV og SARS-CoV-2 fra MSIS, med tydelig varsel når tallene er usikre.

**Neste:** Flere registre i samme situasjonsbilde, med de samme kvalitetsreglene: genomovervåkning (helgenomsekvensering som viser hvilke virusvarianter som sirkulerer, og som allerede finnes i FHIs åpne API) og vaksinasjonsdekning. Deretter et situasjonsbilde for kommuneoverleger og andre som har ansvar for smittevern i kommunene. De får i dag FHIs statusrapporter annenhver uke og må selv tolke hva tallene betyr der de bor. Den versjonen viser smittesituasjonen i deres fylke (tabellen «Oversikt luftveisagens» har fylkestall) sammenlignet med landet. Før dette bygges, testes behovet i samtaler med noen kommuneoverleger. Fritekstspørsmål, der KI oversetter spørsmålet til en av de eksisterende malene og viser hvilken mal som ble brukt, kommer i samme runde.

**2–3 år:** Et beredskapsverktøy kommuner og virksomheter bruker rutinemessig. Det kobler flere helseregistre når de blir åpent tilgjengelige, forklarer tallene for folk uten fagbakgrunn, og varsler aktivt om usikkerhet fremfor å late som om alle svar er sikre. FHIs modernisering av smittevernovervåkingen (NORSURV, 2024–2028) og det europeiske helsedataområdet (EHDS), som gjør flere helsedata tilgjengelige fra 2029, gjør retningen mer realistisk over tid.

## Kilder

- FHI, Åpent API og statistikkbank (hvilke registre som er tilgjengelige): https://www.fhi.no/ta/statistikkalender_og_statistikk/apen-api-og-statistikk/
- FHIs åpne API, MSIS-tabeller: https://statistikk-data.fhi.no/api/open/v1/msis/Table
- Metadata for influensa (tabell 724), RSV (729), SARS-CoV-2 (731) og Oversikt luftveisagens (733): `https://statistikk-data.fhi.no/api/open/v1/msis/Table/{tabell}/metadata`
- FHIs regler for skjuling av små tall, dødsårsakstabellen i Folkehelsestatistikk (tabell 342): https://statistikk-data.fhi.no/api/open/v1/nokkel/Table/342/metadata
- CDC WONDER, regler for små tall: https://wonder.cdc.gov/wonder/help/ucd.html
- NCHS Data Presentation Standards for Proportions: https://wwwn.cdc.gov/nchs/nhanes/tutorials/reliabilityofestimates.aspx
- Helsedirektoratet, Digitalt økosystem for nasjonal smittevernberedskap (NORSURV): https://www.helsedirektoratet.no/digitalisering-og-e-helse/nasjonal-e-helseportefolje/tiltak-i-nasjonal-e-helseportefolje/digitalt-okosystem-for-nasjonal-smittevernberedskap
- FHI, webinar for kommuneoverleger 12.11.2025: https://www.fhi.no/contentassets/7dcd25aa21354860a83b8d0195f0c864/kommuneoverlegewebinar12.11.2025.pdf
- FHI, FHIs rolle og oppdrag i EHDS: https://www.fhi.no/hd/det-europeiske-helsedataomradet/fhis-rolle-og-oppdrag-i-ehds/