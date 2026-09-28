# Product Brief: FHI Helsedata-utforsker

## Executive Summary

For studenter, forskere og kommunehelsetjenester som trenger raske svar fra norske helsedata, lager vi en KI-assistert utforsker for Folkehelseinstituttets (FHI) åpne statistikk-API. Brukeren stiller et spørsmål på vanlig språk – for eksempel «hvordan har influensatilfeller utviklet seg de siste fem årene?» – og systemet finner riktig datakilde, henter tallene, lager en visualisering og forklarer hva den viser, med kildehenvisning.

I dag krever FHIs data god kjennskap til API-struktur og statistikk.for å bli brukt riktig, noe som gjør at mye verdifull informasjon om smittsomme sykdommer og laboratoriefunn forblir utilgjengelig for de som trenger den raskt. Prosjektet kombinerer molekylærmedisinsk fagforståelse med KI-assistert utvikling for å bygge en bro mellom rådata og innsikt – uten å gå på akkord med personvern eller datakvalitet.

Nå er tidspunktet fordi FHI selv jobber aktivt med å gjøre helsedata raskere og sikrere tilgjengelig, og fordi KI-verktøy nå gjør det mulig å bygge denne typen naturlig-språk-grensesnitt mot åpne data på kort tid – noe som passer godt med læringsmålene i IBE160.

## The Problem

FHI gjør store mengder helsedata – blant annet om smittsomme sykdommer og laboratoriefunn – tilgjengelig gjennom et åpent statistikk-API. Dataene finnes der, men er i praksis vanskelig tilgjengelige: man må kjenne datastrukturen, velge riktige variabler (sykdom, tidsperiode, geografi, alder, kjønn) og tolke resultatene riktig for å få noe meningsfullt ut av dem.

Dette rammer flere grupper: studenter og forskere som vil utforske trender uten å bruke timer på API-dokumentasjon, journalister og kommunikasjonsrådgivere som trenger raske og korrekte oppsummeringer, og kommunehelsetjenesten som ønsker oversikt uten eget analysemiljø. I dag løses dette gjerne ved manuell nedlasting til Excel, eller ved at man rett og slett lar være å bruke dataene.

Kostnaden er et gap mellom data som finnes og innsikt som faktisk brukes – og risikoen for at de som prøver å tolke tallene selv, trekker feil konklusjoner fra rå statistikk uten kontekst.

## The Solution

En KI-assistert applikasjon som fungerer som et naturlig-språk-grensesnitt mot FHIs åpne statistikk-API. Brukeren stiller et spørsmål i vanlig tekst, og systemet:

1. Tolker spørsmålet og identifiserer sykdom, tidsperiode, geografi og andre relevante variabler
2. Finner og henter riktig data fra FHIs API
3. Genererer en visualisering (graf/tabell)
4. Forklarer i tekst hva dataene viser, med kildehenvisning
5. Varsler dersom datagrunnlaget er for tynt eller usikkert til å støtte en klar konklusjon

Resultatet er at brukeren går fra et spørsmål til en forklart, visualisert innsikt på sekunder – uten å måtte forstå API-dokumentasjon eller statistiske detaljer selv. Vi spesifiserer bevisst ikke ennå hvilken KI-modell, hvilket rammeverk eller hvilken hosting-løsning som brukes – det er implementasjonsvalg som kommer senere.

## What Makes This Different

| Alternativ i dag | Hvorfor brukere tolererer det | Hvorfor vår tilnærming er bedre |
| --- | --- | --- |
| Manuell nedlasting til Excel/CSV | Det er den eneste veien inn i dataene i dag | Sekunder i stedet for timer, ingen manuell filbehandling |
| Direkte bruk av FHIs API | Fungerer for de som kan programmere | Krever ingen teknisk kompetanse – vanlig språk holder |
| Å la være å bruke dataene | Terskelen oppleves for høy til at det er verdt det | Senker terskelen så mye at flere faktisk bruker dataene |

Dette er ingen teknisk «moat» – FHIs data er åpne og tilgjengelige for alle. Fordelen vår er en kombinasjon av god brukeropplevelse (naturlig språk mot data) og faglig kvalitetssikring: fordi vi har molekylærmedisinsk bakgrunn, kan vi bygge inn en forståelse av hva laboratoriefunn og smittedata faktisk representerer biologisk, og dermed fange opp feiltolkninger en rent teknisk løsning ville gått glipp av. Vi er også bevisst ærlige om usikkerhet – systemet er bygget for å si «dette bør undersøkes nærmere» fremfor å gjette på årsaker.

## Who This Serves

**Primærbruker:** Studenter, forskere og fagpersoner i kommunehelsetjenesten som trenger å utforske trender i smitte- og laboratoriedata raskt, uten egen dataanalysekompetanse. De vil forstå «hva skjer og hvorfor» uten å bruke tid på å lære seg et API. Suksess for dem er å gå fra spørsmål til korrekt, forklart svar på under ett minutt, med tillit til at kilden og tolkningen er riktig.

**Sekundærbrukere:** Journalister og kommunikasjonsrådgivere som trenger raske, korrekte oppsummeringer av folkehelsetall til publisering.

## Success Criteria

| Signal | Metrikk / evidens | Mål | Når måles |
| --- | --- | --- | --- |
| Brukerutfall | Tid fra spørsmål til forklart svar | Under 1 minutt | Ved brukertesting |
| Adopsjon/atferd | Andel testbrukere som stiller et oppfølgingsspørsmål | Over 50 % | Ved brukertesting |
| Kvalitet/tillit | Andel svar med korrekt kildehenvisning og riktig tolket datagrunnlag | 100 % | Manuell gjennomgang av testkjøringer |
| Faglig/oppgave | Godkjent leveranse i IBE160 med dokumentert kodekvalitet, testing og refleksjon rundt KI-hallusinasjon og personvern | Bestått vurdering | Ved innlevering/muntlig eksamen |

## Scope

**IN – første versjon**

- Forhåndsdefinerte spørsmålsmaler (f.eks. «vis utvikling for \[sykdom\] siste \[X\] år») for smittsomme sykdommer og laboratoriedata
- Automatisk henting fra FHIs åpne statistikk-API
- Grafisk visualisering av resultatet
- Kort tekstlig forklaring med kildehenvisning
- Varsel når datagrunnlaget er for tynt eller usikkert til en klar konklusjon

**OUT – ikke nå**

- Fri-tekst-tolkning av vilkårlig formulerte spørsmål (mulig strekkmål hvis tiden tillater det)
- Bruk av personidentifiserbare eller sensitive helsedata
- Støtte for andre datakilder enn FHIs åpne API
- Flerspråklig grensesnitt
- Automatiske varsler/abonnement på nye data
- Integrasjon med FHIs interne systemer

**Scope-test:** Hvis vi fjerner et element og fortsatt kan bevise kjerneverdien – rask, korrekt og forklart innsikt fra åpne helsedata – hører det ikke hjemme i versjon 1.

## Vision

**Nå:** En prototype som lar én bruker stille spørsmål om smitte- og laboratoriedata og få et forklart, visualisert svar fra FHIs åpne API.

**Neste:** Utvidet til flere FHI-datasett (f.eks. vaksinasjonsdekning, helseregistre), med sammenligning over tid og geografi, og tilbakemeldingsløkke som forbedrer tolkningene.

**2–3 år:** En generell «KI-tolk» for norske offentlige helsedata som kommunehelsetjenester, forskere og journalister bruker rutinemessig – et verktøy som gjør åpne helsedata reelt tilgjengelige for folk uten dataanalysebakgrunn, samtidig som det aktivt varsler om usikkerhet fremfor å late som om alle svar er sikre.
