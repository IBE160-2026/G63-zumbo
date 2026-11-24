---
title: "PRD: FHI Helsedata-utforsker"
status: final
created: 2026-11-06
updated: 2026-11-20
---

# PRD: FHI Helsedata-utforsker

## 0. Om dokumentet

Denne PRD-en bygger på `docs/product-brief.md` slik den ble endret 20. november 2026: retningen er beredskap og helseregister, og hovedbrukeren er en student uten medisinsk bakgrunn. Der briefen og de tidligere notatene i `.memlog.md` er uenige, følger PRD-en briefen.

Dokumentet er skrevet for gruppen, faglærer og sensor, og er grunnlaget for arkitektur, epics og stories. Begrepene i kapittel 3 brukes likt i hele dokumentet. Kravene har faste ID-er (FR-1, NFR-1, SM-1 osv.) som stories og tester kan vise til. Antakelser er merket `[ANTAKELSE]` og samlet i kapittel 13. Tekniske detaljer om FHI-API-et ligger i `addendum.md` i samme mappe.

## 1. Visjon

FHI Helsedata-utforsker gjør laboratoriedata fra Meldingssystem for smittsomme sykdommer (MSIS) forståelige for folk uten medisinsk bakgrunn. Brukeren velger et ferdig spørsmål, for eksempel «vis andel positive tester for influensa i sesongen 2025/2026», og får graf, tabell, korte begrepsforklaringer og en kort forklaring skrevet av KI med enkle ord og kildehenvisning.

I beredskap er et riktig situasjonsbilde like viktig som et raskt et. Derfor sier appen tydelig fra når datagrunnlaget er for tynt til en klar konklusjon, og forklarer hvilken regel som slo inn. Reglene er faste og står i koden, ikke i KI-en, slik at de kan testes.

## 2. Målbruker

**Hovedbruker:** En student uten medisinsk eller forskningsbakgrunn, for eksempel innen beredskap, samfunnssikkerhet eller IT, som skal skrive om smittesituasjonen for luftveisinfeksjoner i Norge. Studenten har ikke brukt API-er eller statistikkprogrammer, og kjenner ikke begreper som «andel positive» eller «fyrtårnsystem».

### 2.1 Oppgaver brukeren vil få gjort

- Se hvordan smitten har utviklet seg uke for uke gjennom en sesong.
- Forstå hva grafen viser, uten å slå opp faguttrykk.
- Vite om tallene er til å stole på før hen bruker dem i en oppgave.
- Kunne gjengi situasjonsbildet riktig med egne ord og med korrekt kilde.

### 2.2 Ikke målbrukere i v1

Beredskapsrådgivere, journalister og kommunikasjonsrådgivere kan ha nytte av appen, men den designes ikke spesielt for dem. Kommuneoverleger er målgruppen for en senere versjon (se briefens Vision).

### 2.3 Brukerreiser

Personen «Sara» er laget for denne PRD-en ut fra hovedbrukeren i briefen, og er bekreftet av gruppen 20. november 2026. Hun kan justeres etter brukertestingen.

- **UJ-1. Sara ser influensasesongen uke for uke.**
  Sara studerer samfunnssikkerhet og skriver om beredskap for luftveisinfeksjoner. Hun åpner appen i nettleseren, uten innlogging. Hun velger mal 1, influensa, sesongen 2025/2026 og «alle aldersgrupper». Appen viser en graf over andel positive tester uke for uke, en tabell med tallene, korte forklaringer av begrepene og en KI-skrevet forklaring med kilde. Ingen varsel vises. Sara kopierer kildehenvisningen og forklarer utviklingen med egne ord i oppgaven sin.

- **UJ-2. Sara får beskjed om at tallene er for usikre.**
  Sara velger RSV, aldersgruppen 80+ år og sesongen 2026/2027, som nettopp har startet. Appen viser graf og tabell, men øverst står et varsel om for tynt datagrunnlag: det er bare 6 positive prøver så langt i sesongen, og grensen er 20. KI-forklaringen nevner usikkerheten. Sara bytter til sesongen 2024/2025 og får et nytt varsel: perioden går over 1. mars 2025, så tallene før og etter kan ikke sammenlignes direkte. Sara skriver i oppgaven at tallene må tolkes med forsiktighet. (Tallene er fra FHI per 20.11.2026.)

- **UJ-3. FHI-API-et svarer ikke.**
  Sara åpner appen mens FHI-API-et er nede. Appen viser en feilmelding på norsk om at tallene ikke kunne hentes nå. Hvis appen har lagret tall for det samme utvalget tidligere, vises de med dato for når de ble hentet.

- **UJ-4. Appen kjører uten KI-nøkkel.**
  En medstudent kloner repoet og starter appen uten å legge inn KI-nøkkel. Graf, tabell, begrepsforklaringer og varsel virker. Der KI-forklaringen skulle stått, står det at forklaringen krever en KI-nøkkel.

## 3. Begreper

Disse begrepene brukes likt i hele PRD-en og i stories og kode.

- **Mal** — Et ferdig spørsmål med faste felt brukeren fyller ut (virus, sesong, aldersgruppe). v1 har mal 1. Mal 2 er strekkmål.
- **Utvalg** — Kombinasjonen brukeren har valgt: mal, virus, sesong og aldersgruppe. Overvåkingstypen er alltid vanlig klinisk praksis i v1.
- **Virus** — Influensa, RSV eller SARS-CoV-2. Hvert virus har én FHI-tabell (se kapittel 4).
- **Sesong** — Uke 40 ett år til og med uke 20 året etter, skrevet som «2025/2026». For sesongen som pågår, slutter perioden ved siste publiserte uke.
- **Uke** — ISO-uke, slik FHI bruker den (for eksempel `2025-w50`).
- **Test** — Én PCR-analyse for viruset, telt i uka prøven ble tatt (prøvedato) (FHIs måltall «Testede»). Tallene teller analyser, ikke personer, og samme person kan telles flere ganger. Kilde: FHIs statusrapport for luftveisinfeksjoner, metodebeskrivelsen. *Endret 24. november 2026: Irenes kontroll mot FHIs metodebeskrivelse.*
- **Positiv prøve** — En påvisning av viruset (FHIs måltall «Påvisninger»).
- **Andel positive** — Positive prøver delt på tester, ganget med 100, for én uke.
- **Aldersgruppe** — Alle, 0–4, 5–14, 15–29, 30–64, 65–79 eller 80+ år.
- **Overvåkingstype** — Hvordan prøvene er samlet inn. *Vanlig klinisk praksis* (FHI: Non-Sentinel) er prøver tatt når folk oppsøker lege eller sykehus. *Fyrtårnsystemet* (FHI: Sentinel) er prøver tatt bare for overvåking hos utvalgte fastleger.
- **MSIS** — Meldingssystem for smittsomme sykdommer. Laboratoriedatabasen i MSIS er kilden til alle tallene.
- **Skjult verdi** — En verdi FHI har skjult eller som mangler. I API-et vises den som `..`, `.` eller `:`, eller som tom verdi.
- **Manglende uke** — En uke der antall tester eller antall positive prøver er en skjult verdi, slik at andelen positive ikke kan regnes ut.
- **Usikker uke** — En uke med færre enn 30 tester, der antall tester er en skjult verdi, eller der antall positive prøver er større enn antall tester (Endret 24. november 2026: Irenes beslutning i story 2.4).
- **Kontrollregel** — En av de fem faste reglene R1–R5 i kapittel 6.5.
- **Varsel om tynt datagrunnlag** — Melding som vises når minst én kontrollregel slår inn.
- **KI-forklaring** — Kort tekst skrevet av en språkmodell ut fra de hentede tallene.
- **Kildehenvisning** — Henvisning til FHI-tabellen tallene kommer fra: FHIs egen kildetekst for tabellen, tabellnummer, tabellnavn og dato for hentingen. For tabell 724 er kildeteksten «Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, Folkehelseinstituttet (FHI).»
- **Mellomlagrede data** — Tall appen har hentet fra FHI tidligere og lagret, med tidspunkt for hentingen.

## 4. Datasett

Alle tre tabellene ligger i FHIs åpne statistikk-API under MSIS. De har ukentlige tall for hele landet fra uke 40 i 2024, og oppdateres hver torsdag.

| Tabell | Navn hos FHI | Virus | Virustype som brukes | Måltall |
| --- | --- | --- | --- | --- |
| 724 | RESPIaggr Influensa antall og andel | Influensa | Influensa (A+B) | Påvisninger, Testede, Andel (%) |
| 729 | RESPIaggr RSV antall og andel | RSV | RS-virus (A+B) | Påvisninger, Testede, Andel (%) |
| 731 | RESPIaggr SARS-CoV-2 antall og andel | SARS-CoV-2 | (ingen typeinndeling) | Påvisninger, Testede, Andel (%) |

Tabellnavnet for 724 er bekreftet mot metadataene 23. november 2026.

Felles valg for alle tre tabellene i v1:

- **Overvåkingstype:** vanlig klinisk praksis (Non-Sentinel). Det gir flest prøver og dermed færre usikre uker. Fyrtårnsystemet er en mulig utvidelse.
- **Virustype:** totalen. For RSV har vi sjekket at «RS-virus (A+B)» også tar med prøver med ukjent type (se `addendum.md`).
- **Aldersgruppe:** «Alle» er standard. Brukeren kan velge én av de seks aldersgruppene. «Ukjent alder» tilbys ikke.

**Sesong.** PRD-en bruker uke 40 til uke 20 året etter. Vi har sjekket dette mot metadataene for tabell 724: tabellen har ingen egen sesongdimensjon, bare år og uke. Metadataene sier at influensaepidemiene kommer fra desember til april, at en sesong navngis med to årstall («2024/2025»), og at dataene starter i uke 40 i 2024. Uke 40–20 dekker desember–april og stemmer med datastarten, men sluttuken (uke 20) står ikke i metadataene. Valget er derfor vårt eget, i tråd med vanlig praksis for overvåking av luftveisvirus.

Tilgjengelige sesonger per 20. november 2026: 2024/2025, 2025/2026 og 2026/2027 (pågår).

Tabell 733 («Oversikt luftveisagens», fylkestall) er ikke med i v1. Det tidligere notatet om 733 som strekkmål gjelder ikke lenger.

## 5. Maler

| Mal | Spørsmål | Felt brukeren velger | Status |
| --- | --- | --- | --- |
| Mal 1 – utvikling uke for uke | «Vis andel positive tester for [virus] i sesongen [sesong]» | Virus, sesong, aldersgruppe (valgfri) | v1 |
| Mal 2 – sammenligning av sesonger | «Sammenlign [virus] denne sesongen med forrige» | Virus, aldersgruppe (valgfri) | Strekkmål |

Rekkefølge: Mal 1 bygges ferdig og testes for influensa før RSV og SARS-CoV-2 legges til. Mal 2 påbegynnes først når mal 1 virker for alle tre virusene og testene består.

Mal 3 (aldersfordeling) og mal 4 (fylker) er ikke med (se kapittel 9).

## 6. Funksjoner og krav

### 6.0 Skisse av hovedskjermen

Hovedskjermen er én side. På mobil ligger delene under hverandre i samme rekkefølge.

```
┌────────────────────────────────────────────────────────────────────┐
│ FHI Helsedata-utforsker                                            │
├────────────────────────────────────────────────────────────────────┤
│ 1  VELG SPØRSMÅL                                                   │
│    Mal:          [ Andel positive tester uke for uke         ▾ ]   │
│    Virus:        ( ) Influensa  ( ) RSV  ( ) SARS-CoV-2            │
│    Sesong:       [ 2026/2027 ▾ ]                                   │
│    Aldersgruppe: [ Alle aldersgrupper ▾ ]        [ Vis tallene ]   │
├────────────────────────────────────────────────────────────────────┤
│ ⚠ 2  VARSEL: For tynt datagrunnlag                                 │
│    Tallene bør tolkes med forsiktighet fordi:                      │
│    • Bare 6 positive prøver så langt i sesongen (grensen er 20)    │
│    [ Hva betyr dette? ]                                            │
├──────────────────────────────────────────┬─────────────────────────┤
│ 3  GRAF                                  │ 4  TABELL               │
│ Andel positive (%)                       │ Uke  Tester Pos. Andel  │
│  20 ┤            ●──●                    │ 40   1 210   12  1,0 %  │
│  10 ┤      ●──●─╯    ╲●                  │ 41   1 305   15  1,1 %  │
│   0 ┼──●──●            ○ ← usikker uke   │ ...                     │
│     40  44  48  52  4   8                │ 7       24    5 20,8 %* │
│  ● = sikker uke  ○ = usikker uke         │ * færre enn 30 tester   │
├──────────────────────────────────────────┴─────────────────────────┤
│ Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa,    │
│ Folkehelseinstituttet (FHI). Tabell 724 «RESPIaggr Influensa       │
│ antall og andel». Hentet 20.11.2026 kl. 14:05.                     │
│ FHI publiserer nye tall hver torsdag.   [ Hent nyeste tall nå ]    │
├────────────────────────────────────────────────────────────────────┤
│ 5  HVA BETYR ORDENE?                                               │
│    ▸ Andel positive  ▸ Test og positiv prøve  ▸ Sesong             │
│    ▸ Aldersgruppe  ▸ Overvåkingstype  ▸ MSIS                       │
│    ▸ For tynt datagrunnlag                                         │
├────────────────────────────────────────────────────────────────────┤
│ 6  FORKLARING (skrevet av KI)                                      │
│    «Andelen positive influensatester steg fra 1 % i uke 40 til     │
│    ...»                                                            │
│    Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, │
│    Folkehelseinstituttet (FHI), tabell 724. Hentet 20.11.2026.     │
└────────────────────────────────────────────────────────────────────┘
```

Tallene i skissen er bare illustrasjon. Varselet (2) ligger over grafen, slik at brukeren ser det før tallene. Uten varsel vises ikke boks 2. Uten KI-nøkkel står det i boks 6 at forklaringen krever en nøkkel, mens resten virker.

### 6.1 Velge mal og utvalg

Brukeren velger mal og fyller ut feltene i malen. Realiserer UJ-1 og UJ-2.

#### FR-1: Velge mal

Brukeren kan velge en mal fra en liste.

- Listen viser mal 1. Mal 2 vises bare hvis den er bygget.
- Hver mal vises som et spørsmål på vanlig norsk, ikke som tabellnavn eller kode.

#### FR-2: Velge virus

Brukeren kan velge ett virus: influensa, RSV eller SARS-CoV-2.

- Hvert virus hentes fra riktig tabell: influensa → 724, RSV → 729, SARS-CoV-2 → 731.

#### FR-3: Velge sesong

Brukeren kan velge én sesong blant dem FHI har data for.

- Listen viser bare sesonger med minst én publisert uke (per 20.11.2026: 2024/2025, 2025/2026, 2026/2027).
- Standardvalget er siste sesong.
- Sesongen gjelder fra uke 40 til og med uke 20 året etter. For sesongen som pågår, slutter perioden ved siste publiserte uke.
- I år med uke 53 (for eksempel 2026) er uke 53 en vanlig uke i sesongen.

#### FR-4: Velge aldersgruppe

Brukeren kan velge aldersgruppe. Valget er frivillig.

- Standardvalget er «Alle aldersgrupper».
- Valgene er de seks aldersgruppene i kapittel 3. «Ukjent alder» tilbys ikke.

#### FR-5: Hindre ugyldige valg

Appen godtar bare utvalg som finnes i listene.

- Hvis et felt mangler eller har en verdi som ikke finnes (for eksempel i en manipulert URL), hentes ingen data, og appen viser en melding på norsk om hva som må rettes.

### 6.2 Hente data

Appen henter tallene fra FHIs åpne API eller fra mellomlagrede data. Hvilke data som hentes, styres av faste regler i koden, ikke av KI.

#### FR-6: Hente riktige tall

Appen henter positive prøver, tester og andel positive per uke for utvalget.

- Henting bruker tabellen fra FR-2, overvåkingstypen vanlig klinisk praksis, totalen for virustypen og valgt aldersgruppe.
- For de 10 spørsmålene i testsettet (SM-1) gir appen de samme tallene som fasiten, som er hentet manuelt fra FHI.

#### FR-7: Mellomlagre data

Appen lagrer hentede tall sammen med tidspunktet for hentingen.

- Et utvalg som er hentet tidligere, kan vises uten nytt kall til FHI.
- Mellomlagrede data som ble hentet for 24 timer siden eller mer, regnes som utdaterte og hentes på nytt neste gang utvalget vises.
- Begrunnelse: Fast levetid virker uansett når på torsdagen FHI publiserer. En regel knyttet til et klokkeslett torsdag ville regnet gamle tall som ferske i en hel uke hvis tallene ble hentet etter klokkeslettet, men før FHI faktisk hadde publisert. Ett døgns forsinkelse er greit for ukentlige tall, og FR-25 lar brukeren hente nye tall med en gang.

#### FR-8: Håndtere at FHI-API-et ikke svarer

Når FHI-API-et ikke svarer, gir feil eller ikke har svart innen 10 sekunder, sier appen tydelig fra. Realiserer UJ-3.

Begrunnelse for 10 sekunder: Brukeren venter neppe lenger før hen tror appen har hengt seg. Mellomlagrede tall vises uansett innen 5 sekunder (NFR-2).

- Appen viser en feilmelding på norsk, uten tekniske feilkoder, som sier at tallene ikke kunne hentes fra FHI akkurat nå.
- Hvis det finnes mellomlagrede data for utvalget, vises de med teksten «Sist lagrede tall, hentet [dato og klokkeslett]».
- Hvis det ikke finnes mellomlagrede data, vises ingen graf eller tabell. Feilmeldingen foreslår å prøve igjen senere.
- Kontrollreglene og begrepsforklaringene gjelder også for mellomlagrede data.

#### FR-25: Hente nyeste tall nå

*Lagt til 20. november 2026, etter at PRD-en var ferdig.*

Brukeren kan be appen hente tallene fra FHI på nytt, uten å vente på at de mellomlagrede tallene blir utdaterte (FR-7).

- Siden viser når tallene ble hentet (dato og klokkeslett), og at FHI publiserer nye tall hver torsdag.
- En knapp «Hent nyeste tall nå» henter tallene for utvalget fra FHI på nytt uten å bruke mellomlagringen, og lagrer de nye tallene med nytt hentetidspunkt.
- Mens hentingen pågår, er knappen deaktivert, slik at gjentatte trykk ikke starter nye kall.
- Hvis FHI ikke svarer, gjelder FR-8: sist lagrede tall vises med dato.
- Hvis tallene ikke har endret seg, gjenbrukes den lagrede KI-forklaringen.
- Knappen kan brukes med tastatur (NFR-5).

### 6.3 Graf og tabell

#### FR-9: Vise graf

Appen viser andel positive uke for uke som en linjegraf. Realiserer UJ-1.

- Én verdi per uke i sesongen, med uker langs den vannrette aksen og andel positive (%) langs den loddrette.
- Grafen har en tittel som gjentar utvalget, for eksempel «Influensa, sesongen 2025/2026, alle aldersgrupper».
- Manglende uker vises som brudd i linjen, ikke som 0. Det gjelder alle uker uten andel, også uker med skjult antall tester og uker med 0 tester. De har ikke noe punkt i grafen. I tabellen står tallene som «skjult», «mangler» eller «kan ikke regnes ut» (FR-11). *Endret 24. november 2026: Irenes beslutning.*
- Punktene blir mindre jo smalere grafen er, slik at de ikke overlapper på smale skjermer. *Endret 24. november 2026: Irenes beslutning.*
- Når brukeren holder musa over et punkt, viser den lille boksen (verktøytipset) uka, antall tester, antall positive prøver og andelen, med de samme tallene som i tabellen. *Endret 24. november 2026: Irenes beslutning.*
- Grafen og tabellen henger sammen. Peker brukeren på en uke i grafen, markeres samme rad i tabellen. Peker brukeren på eller går med tastaturet til en rad i tabellen, markeres punktet i grafen. Markeringen er ikke bare farge: raden får fet skrift og strek over og under, og punktet blir større og får verktøytipset. *Endret 24. november 2026: Irenes beslutning.*

#### FR-10: Markere usikre uker

Appen markerer usikre uker (færre enn 30 tester, skjult antall tester, eller flere positive prøver enn tester) i grafen og tabellen.

- Uker der antall tester er skjult, markeres som usikre selv om de ikke telles i R2 (se FR-15).
- Uker med flere positive prøver enn tester viser andelen som den er (over 100 %). De markeres som usikre og får en egen fotnote på enkel norsk: «Flere positive prøver enn tester denne uka. Det kan skyldes hvordan prøvene er registrert. Tolk tallet med forsiktighet.» De telles ikke i R2, som bare teller uker med færre enn 30 tester (FR-15). *Endret 24. november 2026: Irenes beslutning i story 2.4. Fotnoten: Endret 24. november 2026: Irenes beslutning.*
- En uke med 0 tester og flere enn 0 positive er usikker og får fotnoten, men ingen andel, fordi andelen ikke kan regnes ut. *Endret 24. november 2026: Irenes beslutning.*
- Usikre uker skilles fra andre uker med form (for eksempel åpen sirkel i stedet for fylt), ikke bare med farge.
- Grafen har en forklaring som sier hva markeringen betyr. Forklaringen av fylt og åpen sirkel vises alltid under grafen, også når ingen uke er usikker. Når ingen uke har en andel, vises ingen graf og heller ingen forklaring. *Endret 24. november 2026: Irenes beslutning.*
- I tabellen er usikre uker merket med tegn og fotnote.

#### FR-11: Vise tabell

Appen viser tallene i en tabell ved siden av eller under grafen.

- Kolonner: uke, tester, positive prøver og andel positive.
- Tallene i tabellen er de samme som i grafen.
- Skjulte verdier vises som «skjult» eller «mangler», ikke som 0. «mangler» brukes bare når et tall er skjult. En uke med 0 tester viser «kan ikke regnes ut» i kolonnen for andel positive. *Endret 24. november 2026: Irenes beslutning.*
- Andelen vises med én desimal og komma, for eksempel «20,8 %». *Endret 24. november 2026: Irenes beslutning.*

#### FR-12: Vise kildehenvisning

Appen viser kildehenvisning under graf og tabell.

- Kildehenvisningen begynner med FHIs egen kildetekst for tabellen, ordrett slik den står i metadataene (se `addendum.md`). For tabell 724: «Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, Folkehelseinstituttet (FHI).»
- Deretter kommer tabellnummer, tabellnavn og dato for hentingen.
- Kildehenvisningen vises også når KI-forklaringen mangler.

Endret 23. november 2026: bruker FHIs ordlyd fra story 1.4.

### 6.4 Begrepsforklaringer

#### FR-13: Vise faste begrepsforklaringer

Appen har faste, korte forklaringer på enkel norsk for disse begrepene: andel positive, test og positiv prøve, sesong, aldersgruppe, overvåkingstype, MSIS og «for tynt datagrunnlag».

- Tekstene er skrevet på forhånd og ligger i koden, ikke laget av KI.
- Hver forklaring er på høyst tre setninger og bruker ingen andre faguttrykk uten å forklare dem.
- Forklaringen av overvåkingstype sier at v1 bruker vanlig klinisk praksis, og nevner kort hva fyrtårnsystemet er.
- Forklaringene kan åpnes med både mus og tastatur.

### 6.5 Varsel om tynt datagrunnlag

Appen sjekker hvert utvalg mot fem faste kontrollregler. Hvis minst én slår inn, vises et varsel om tynt datagrunnlag. Reglene beregnes i koden, ikke av KI, og gir samme svar hver gang for de samme tallene. Realiserer UJ-2.

Alle reglene beregnes over **ukene i utvalget**: ukene i valgt sesong (uke 40 til uke 20, eller til siste publiserte uke) for valgt virus og aldersgruppe.

**Hvilke regler slår inn i ekte data?** Vi sjekket tallene 20.11.2026 for SARS-CoV-2 (alle aldersgrupper) og RSV (0–4 og 80+ år) med vanlig klinisk praksis. Alle uker hadde minst 129 tester, og ingen verdier var skjult. R2 og R3 slo derfor ikke inn for noen av disse utvalgene. Varsler i ekte data kommer fra R1 (smale aldersgrupper tidlig i sesongen som pågår, for eksempel RSV 80+ år i 2026/2027 med 6 positive prøver), R4 (de første ukene av en ny sesong) og R5 (sesongen 2024/2025). R2 og R3 beholdes som sikring, for eksempel hvis FHI endrer dataene eller fyrtårnsystemet tas med senere, og testes med konstruerte testdata.

#### FR-14: R1 – få positive prøver

Appen viser varsel når summen av positive prøver i utvalget er mindre enn 20.

- 19 positive prøver → varsel. 20 positive prøver → ikke varsel etter R1.
- Skjulte verdier telles ikke med i summen.
- Begrunnelse: CDC/NCHS regner rater basert på færre enn 20 tilfeller som upålitelige (relativ usikkerhet over ca. 22 %).

#### FR-15: R2 – mange uker med få tester

Appen viser varsel når mer enn 20 % av ukene i utvalget har et kjent antall tester som er mindre enn 30.

- 20 uker der 4 har færre enn 30 tester (20 %) → ikke varsel. 20 uker der 5 har færre enn 30 tester (25 %) → varsel.
- En uke med 29 tester teller. En uke med 30 tester teller ikke.
- Uker der antall tester er skjult, telles ikke i R2, men under R3, slik at samme uke ikke teller to ganger. De regnes likevel som usikre uker i grafen og tabellen (FR-10).
- Begrunnelse: NCHS krever minst 30 observasjoner for andeler. 20 % er samme grense som FHI bruker for å skjule hele tidsserier.

#### FR-16: R3 – mange manglende uker

Appen viser varsel når mer enn 20 % av ukene i utvalget er manglende uker.

- En uke er manglende når antall tester eller antall positive prøver (minst én av de to) er en skjult verdi (`..`, `.`, `:`) eller mangler, fordi andelen positive da ikke kan regnes ut.
- 10 uker der 2 er manglende (20 %) → ikke varsel. 10 uker der 3 er manglende (30 %) → varsel.
- En uke der begge verdiene er skjult, teller som én manglende uke, ikke to.
- Begrunnelse: FHI skjuler hele tidsserier når mer enn 20 % av verdiene er skjult.

#### FR-17: R4 – for få uker

Appen viser varsel når utvalget har færre enn 3 uker med data.

- 2 uker → varsel. 3 uker → ikke varsel etter R4.
- Det betyr at varselet alltid vises i de to første ukene av en ny sesong (uke 40 og 41).
- En uke har data når den ikke er en manglende uke.
- Begrunnelse: To datapunkter viser bare én endring. Tre er minimum for å se en retning (opp, ned eller flat).

#### FR-18: R5 – perioden går over 1. mars 2025

Appen viser varsel når utvalget har minst én uke som starter før 1. mars 2025, og minst én uke som slutter 1. mars 2025 eller senere.

- Sesongen 2024/2025 gir alltid varsel etter R5. Sesongene 2025/2026 og 2026/2027 gir aldri varsel etter R5.
- Begrunnelse: Fra 1. mars 2025 er alle norske mikrobiologiske laboratorier med i MSIS-labdatabasen, så tall før og etter kan ikke sammenlignes direkte (FHI, metadata for tabell 724, 729 og 731).

#### FR-19: Vise varselet

Når minst én kontrollregel slår inn, viser appen varselet over grafen. Varselet sier hvilke regler som slo inn.

- Varselet lister hver regel som slo inn, med en setning på enkel norsk og de faktiske tallene, for eksempel «6 av 20 uker har færre enn 30 tester».
- Når ingen regel slår inn, vises ikke varselet.
- Varselet skilles fra resten av siden med ikon og overskrift, ikke bare med farge.
- Varselet har FHIs Rød 3 (#FBD1CD) som bakgrunn, slik at det er tydelig rosa. Rammen og ikonet har Rød 1 (#D14641), og ikonet har minst 3:1 kontrast mot bakgrunnen. *Endret 24. november 2026: Irenes beslutning.*
- Varselet har en lenke til begrepsforklaringen for «for tynt datagrunnlag».
- For hvert tilfelle i testsettet (SM-3) gir R1–R5 riktig resultat og riktig begrunnelse.

### 6.6 KI-forklaring

En språkmodell skriver en kort forklaring av tallene. Dette er det eneste KI-en gjør i v1.

#### FR-20: Skrive KI-forklaring

Appen lager en kort forklaring av hva tallene i utvalget viser, med enkle ord. Realiserer UJ-1.

- Språkmodellen får bare de hentede tallene, utvalget og resultatet av kontrollreglene.
- Forklaringen er merket «Skrevet av KI».
- Forklaringen er på norsk og høyst 120 ord.
- Kildehenvisningen fra FR-12 vises sammen med forklaringen.
- Forklaringen settes inn i et område med `aria-live="polite"`, slik at skjermlesere leser den opp når den kommer.
- Mens forklaringen hentes, står det «Forklaringen lages …» i området.

#### FR-21: Krav til innholdet i KI-forklaringen

KI-forklaringen må følge disse reglene. De sjekkes med sjekklisten i SM-4.

- Den bruker bare tall som finnes i de hentede dataene.
- Den gjetter ikke på årsaker, for eksempel vær, vaksiner eller tiltak.
- Den bruker ingen faguttrykk uten å forklare dem.
- Når varselet vises, sier forklaringen at tallene er usikre, og hvorfor.

#### FR-22: Uten KI-nøkkel eller ved feil fra språkmodellen

Når KI-nøkkelen mangler, eller språkmodellen gir feil, virker resten av appen. Realiserer UJ-4.

- Uten nøkkel står det i forklaringsfeltet at KI-forklaringen krever en nøkkel, og at graf, tabell og varsel er komplette uten den.
- Ved feil fra språkmodellen står det at forklaringen ikke kunne lages akkurat nå.
- Hvis selve hentingen av forklaringen feiler, for eksempel ved nettverksfeil, vises den samme meldingen.
- Graf, tabell, begrepsforklaringer, varsel og kildehenvisning vises i begge tilfellene.

### 6.7 Mal 2 – sammenligning av sesonger (strekkmål)

Bygges bare hvis tiden tillater det (se kapittel 5).

#### FR-23: Sammenligne to sesonger

Brukeren kan velge mal 2, virus og eventuelt aldersgruppe, og se denne sesongen og forrige sesong i samme graf.

- «Denne sesongen» er siste sesong med data. «Forrige» er sesongen før.
- Begge sesongene vises uke for uke fra uke 40, slik at samme uke i sesongen ligger på samme sted.
- 2026 har uke 53. Når bare den ene sesongen har uke 53, vises den uken bare for den sesongen, og den andre sesongen har ikke noe punkt der.
- De to linjene skilles med linjetype (hel og stiplet) og etiketter direkte på grafen, ikke bare med farge.
- Tabellen viser begge sesongene side om side.

#### FR-24: Kontrollregler for mal 2

Kontrollreglene R1–R5 beregnes for hver sesong for seg. Varselet vises hvis minst én regel slår inn for én av sesongene, og sier hvilken sesong det gjelder.

- Per 20.11.2026 sammenligner mal 2 sesongen 2026/2027 med 2025/2026. Ingen av dem går over 1. mars 2025, så R5 slår ikke inn. R5 slår bare inn hvis forrige sesong er 2024/2025.
- Tidlig i sesongen som pågår kan R1 og R4 slå inn for «denne sesongen».
- En uke 53 som bare finnes i den ene sesongen, telles ikke som manglende uke i R3 for den andre sesongen.

### 6.8 Om appen

#### FR-26: Hvorfor ikke bare spørre en chatbot?

*Lagt til 24. november 2026: Irenes beslutning.*

Nederst på siden står en kort tekst med overskriften «Hvorfor ikke bare spørre en chatbot?» og denne teksten:

«En chatbot kan finne på tall eller bruke gamle tall, og den sier sjelden hvor tallene kommer fra. Denne appen henter tallene direkte fra Folkehelseinstituttet, viser når de ble hentet, og sier fra når det er for lite data til å konkludere. KI brukes bare til å forklare tallene med enkle ord, aldri til å lage dem.»

- Teksten er fast og står i koden, ikke laget av KI.
- Den vises på hele siden, også uten valgt utvalg og uten KI-nøkkel.

## 7. Ikke-funksjonelle krav

#### NFR-1: Virker uten KI-nøkkel

Alt unntatt KI-forklaringen virker uten KI-nøkkel: valg av mal, henting, graf, tabell, begrepsforklaringer, varsel og kildehenvisning.

- Testes ved å starte appen uten `.env` og kjøre gjennom UJ-4.

#### NFR-2: Svartid

Med mellomlagrede data vises graf, tabell og varsel på under 5 sekunder fra brukeren trykker «Vis tallene».

- KI-forklaringen kan komme etter, uten at resten av siden venter på den.
- Første henting fra FHI er ikke omfattet, fordi den avhenger av FHIs API.

#### NFR-3: Norsk og enkelt språk

Hele grensesnittet er på norsk bokmål med enkle ord.

- Ingen engelske FHI-koder (for eksempel «Non-Sentinel», «pos_rate») vises for brukeren.
- Feilmeldinger, varsler og tomme tilstander sier hva som skjedde og hva brukeren kan gjøre.
- Om språket er enkelt nok, prøves i brukertestingen (SM-5): ord testbrukerne ikke forstår, skrives om.

#### NFR-4: Kontrast

Tekst og viktige grafelementer har god kontrast mot bakgrunnen.

- Vanlig tekst har kontrastforhold på minst 4,5:1, og linjer og symboler i grafen minst 3:1 (WCAG 2.1 AA).

#### NFR-5: Tastatur

Alle funksjoner kan brukes med tastatur alene.

- Alle valg, knapper og begrepsforklaringer kan nås med Tab og brukes med Enter eller mellomrom, og har synlig fokusmarkering.

#### NFR-6: Alternativtekst på grafer

Hver graf har en alternativtekst som beskriver utvalget og hovedtrekket, og tabellen gir de samme tallene i tekstform.

#### NFR-7: Ikke bare farge

Ingen informasjon formidles bare med farge.

- Usikre uker, varsel og linjene i mal 2 skilles også med form, linjetype, ikon eller tekst.
- Testes ved å se på siden i gråtoner: all informasjon skal fortsatt kunne leses.

#### NFR-8: Bare åpne, aggregerte data

Appen bruker bare åpne, aggregerte tall fra FHIs åpne statistikk-API. Den henter, lagrer og viser ingen opplysninger om enkeltpersoner, og har ingen innlogging.

#### NFR-9: Nøkler holdes utenfor repoet

KI-nøkkelen ligger i en `.env`-fil som står i `.gitignore` og aldri committes. Repoet har en `.env.example` som viser hva som må fylles inn.

#### NFR-10: Tester uten nett og nøkkel

Alle automatiske tester kjører uten nett og uten KI-nøkkel. De bruker lagrede svar fra FHI-API-et og språkmodellen i `tests/fixtures/`.

#### NFR-11: Mobil og PC

Hentet fra `docs/sjekkliste.md` og bekreftet av gruppen 20. november 2026. Hovedskjermen kan brukes på mobil (fra 360 piksler bredde) og PC uten vannrett rulling.

## 8. Ikke-mål

- Appen tolker ikke tallene selv utover KI-forklaringen, og gir ingen råd om smittevern.
- Appen spår ikke hvordan smitten vil utvikle seg.
- Appen erstatter ikke FHIs egne rapporter og er ikke en offisiell kilde.
- KI-en bestemmer ikke hvilke data som hentes, og om varselet vises.

## 9. Omfang

**Med i v1**
- Mal 1 for influensa (tabell 724), RSV (729) og SARS-CoV-2 (731), bygget i den rekkefølgen.
- Overvåkingstype: vanlig klinisk praksis.
- Graf, tabell, usikre uker, begrepsforklaringer, kildehenvisning, varsel (R1–R5) og KI-forklaring.
- Mellomlagring og feilmelding når FHI-API-et ikke svarer.
- Knappen «Hent nyeste tall nå» (FR-25, lagt til 20. november 2026).
- Teksten «Hvorfor ikke bare spørre en chatbot?» nederst på siden (FR-26, lagt til 24. november 2026).

**Strekkmål**
- Mal 2, sammenligning av sesonger (FR-23, FR-24).

**Ikke med nå**
- Fyrtårnsystemet som eget valg. Mulig utvidelse: gir prøver som er tatt bare for overvåking, men færre prøver og flere usikre uker.
- Mal 3 (aldersfordeling) og mal 4 (fylker, tabell 733).
- Fritekstspørsmål (se briefens Vision).
- Data fra før uke 40 i 2024 (finnes bare på bestilling fra FHI).
- Andre registre enn MSIS, andre MSIS-tabeller og mage-tarm-virus.
- Data om enkeltpersoner.
- Andre språk enn norsk, abonnement på nye data og integrasjon med FHIs interne systemer.

## 10. Suksesskriterier

**Hovedkriterier**

- **SM-1: Korrekte tall.** Et fast testsett med 10 malspørsmål fordelt på influensa, RSV og SARS-CoV-2, med fasit hentet manuelt fra FHI. Mål: 10 av 10 gir samme tall som fasiten. Automatiske tester mot lagrede API-svar. Validerer FR-2, FR-3, FR-4, FR-6.
- **SM-2: Kildehenvisning.** Mål: 100 % av svarene i testsettet har korrekt kildehenvisning. Automatiske tester. Validerer FR-12.
- **SM-3: Riktig varsel.** Testsettet har utvalg som kan velges i appen, både der varselet skal vises og der det ikke skal vises. Eksempler på utvalg som kan gi varsel er smale aldersgrupper tidlig i sesongen som pågår (R1, for eksempel RSV 80+ år i 2026/2027) og sesongen 2024/2025, som alltid gir varsel etter R5. De konkrete tilfellene bekreftes når testsettet lages fra ekte tall. R2 og R3 slår ikke inn i ekte data per 20.11.2026 (se kapittel 6.5), så de testes bare med konstruerte data. Grensetilfellene for hver regel (19/20 positive, 20 %/25 % uker med færre enn 30 tester, 20 %/30 % manglende uker, 2/3 uker) testes med konstruerte testdata i `tests/fixtures/`. Mål: riktig varsel med riktig begrunnelse i alle tilfeller. Automatiske tester. Validerer FR-14–FR-19.
- **SM-4: Forklaringens kvalitet.** KI-forklaringene i testsettet vurderes mot sjekklisten i FR-21. Mål: alle består. Manuell gjennomgang av lagrede forklaringer. Validerer FR-20, FR-21.

**Brukertesting**

Fem personer uten medisinsk bakgrunn, for eksempel medstudenter, prøver appen én og én. Hver får én oppgave med mal 1 der varselet ikke vises, og én der det vises.

- **SM-5: Forståelighet.** Testbrukeren forklarer med egne ord hva grafen viser, og om tallene er sikre. Før testen skrives en fasit for hver oppgave (hovedtrekket i grafen og om varselet vises, og hvorfor). Jeg vurderer svarene mot fasiten. Hvis det er mulig, vurderer en medstudent de samme svarene uavhengig av meg. Mål: minst 4 av 5 svarer riktig på begge. Validerer FR-9, FR-13, FR-19, FR-20.
- **SM-6: Tid.** Tid fra valgt mal til forklart situasjonsbilde. Mål: under 1 minutt for minst 4 av 5. Validerer FR-1–FR-4, NFR-2.

**Motvekter (skal ikke optimaliseres)**

- **SM-C1: Antall varsler.** Færre varsler er ikke et mål i seg selv. Reglene skal ikke svekkes for at appen skal virke sikrere. Motvekt til SM-5 og SM-6.
- **SM-C2: Lengde og flyt i KI-forklaringen.** En lengre eller mer selvsikker tekst er ikke bedre. Motvekt til SM-4.

## 11. Avvik fra planen

PRD-en skulle vært ferdig 8. november 2026. Den ble skrevet 20. november, fordi økten med `bmad-prd` 6. november stoppet etter at bare et tomt skjelett var laget (commit `353556c`). I mellomtiden ble product brief endret med ny retning: beredskap og helseregister, og en hovedbruker uten medisinsk bakgrunn. PRD-en bygger derfor på den nye briefen, og noen tidligere notater gjelder ikke lenger, blant annet at tabell 733 var strekkmål.

FR-25 («Hente nyeste tall nå») ble lagt til 20. november 2026, etter at PRD-en var ferdig, og før arkitekturen ble skrevet.

FR-26 («Hvorfor ikke bare spørre en chatbot?») ble lagt til 24. november 2026 etter Irenes beslutning, under arbeidet med story 3.7.

## 12. Åpne spørsmål

1. Hvilken språkmodell, hvilket rammeverk og hvilken hosting som brukes, og hvordan mellomlagringen lagres. Avgjøres i arkitekturen.
2. Nøyaktige tekster for de sju begrepsforklaringene. Skrives før FR-13 bygges, og prøves ut i brukertestingen.
3. Hvilke 10 spørsmål testsettet består av, og fasiten. Hentes manuelt fra FHI før testene skrives.

## 13. Antakelser

Ingen antakelser står åpne per 20. november 2026. Personen «Sara» (§2.3), fornyingen av mellomlagrede tall (FR-7) og kravet om mobil og PC (NFR-11) er bekreftet.
