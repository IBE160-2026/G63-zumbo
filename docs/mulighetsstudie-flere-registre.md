# Mulighetsstudie: genomovervåkning og vaksinasjonsdekning i appen

*26. november 2026. Bare en undersøkelse: appen er ikke endret.*

Product briefens Vision sier at neste steg er «flere registre i samme situasjonsbilde, med de samme kvalitetsreglene: genomovervåkning … og vaksinasjonsdekning» (`docs/product-brief.md`, «Vision»). Studien svarer på om dataene finnes i FHIs åpne API, hvordan de ser ut og hva det ville kreve å ta dem inn i appen.

## Kort svar

| | Genomovervåkning (NGS) | Vaksinasjon (SYSVAK) |
|---|---|---|
| I det åpne API-et? | **Ja**, kilde `ngs` | **Ja**, kilde `sysvak` |
| Tidsoppløsning | **Måned** | **Uke** (antall vaksinasjoner) og **sesong** (dekning i %) |
| Aldersgrupper | Ingen | Ukestabeller: 4 grupper + alle. Dekning: bare 65+ og 75+ |
| Geografi | Bare hele landet | Land, fylke, kommune og bydeler i Oslo |
| Skjulte verdier | Ingen flagg brukt i utvalget vårt, men svært små tall | `:` for små tall, som i MSIS |
| Største særhet | Ny tabell og nye kategorier hver sesong; svært få prøver i siste måned | Ukestabellene viser **antall stikk, ikke dekning** |
| Omtrentlig arbeid | Stort (en epic, 6–8 stories) | Middels (en epic, 5–7 stories) hvis vi holder oss til dekning 65+ |
| Anbefaling | Vent, eller vis bare «hovedvariant» uten graf over tid | Best egnet å begynne med: dekning 65+ per sesong |

## Hvordan undersøkelsen ble gjort

Jeg gjorde 12 kall mot `https://statistikk-data.fhi.no/api/open/v1/` 26. november 2026: kildelisten, tabellisten for `ngs` og `sysvak`, `dimension` for tabellene 980, 964, 928, 955 og 753, `metadata` for 980 og 928, og `data` (json-stat2) for 980, 753 og 928 (fylkene Oslo og Finnmark samt hele landet). Statistikkbanken (statistikk.fhi.no) åpnet jeg ikke. Den bygger på de samme tabellene, men jeg har ikke undersøkt om den har noe API-et mangler.

Kilder:

- Kildeliste: <https://statistikk-data.fhi.no/api/open/v1/Common/source>
- Tabeller i NGS: <https://statistikk-data.fhi.no/api/open/v1/ngs/Table>
- Tabeller i SYSVAK: <https://statistikk-data.fhi.no/api/open/v1/sysvak/Table>
- Dimensjoner, for eksempel: <https://statistikk-data.fhi.no/api/open/v1/sysvak/Table/928/dimension>
- Metadata, for eksempel: <https://statistikk-data.fhi.no/api/open/v1/ngs/Table/980/metadata>
- FHI om genomovervåkning: <https://www.fhi.no/hd/laboratorie-analyser>
- FHI om SYSVAK: <https://www.fhi.no/va/sysvak/>
- FHIs statusrapporter om luftveisinfeksjoner (der FHI tolker variantdataene): <https://www.fhi.no/publ/statusrapporter/luftveisinfeksjoner/>
- ECDCs variantdefinisjoner (VOI/VUM): <https://www.ecdc.europa.eu/en/covid-19/variants-concern>
- Statistikkbanken (ikke åpnet): <https://statistikk.fhi.no/>

Kallene bruker de samme endepunktene som appen allerede bruker for MSIS (`…/Table/<id>/dimension` og `POST …/Table/<id>/data`, se `backend/src/backend/fhi.py`). Selve hentingen kan derfor gjenbrukes.

## 1. Genomovervåkning (kilde `ngs`)

### Tabeller

Kilden heter «Mikrobiologisk genomovervåkning» og har 18 tabeller. De relevante:

| Tabell | Tittel | Sist publisert |
|---|---|---|
| 980 | Sesong 2026/27 SARS-CoV-2 hovedvariant fordeling i Norge | 25.11.2026 |
| 981 | Sesong 2026/27: Fordeling av SARS-CoV-2 Pangolin-linjer i Norge | 25.11.2026 |
| 982 | Sesong 2026/27: SARS-CoV-2-varianter under overvåking (VUM) | 25.11.2026 |
| 983 | Sesong 2026/27: SARS-CoV-2-varianter av interesse (VOI) | 25.11.2026 |
| 962 | Sesong 2026/27 – influensa A(H1N1)pdm09 | 17.11.2026 |
| 964 | Sesong 2026/27 – influensa A(H3N2) fordeling i Norge | 17.11.2026 |
| 965 | Sesong 2026/27 – influensa B(Victoria) fordeling i Norge | 17.11.2026 |
| 914–916 | Samme tre influensatabeller for sesong 2025/26 | 7.10.2026 |
| 832, 842, 844, 845, 911 | Eldre SARS-CoV-2-tabeller (per måned, siste to måneder, VOI, VUM, over tid) | 30.9.2026 |
| 917, 918 | RSV-A og RSV-B | 14.9.2026 |

Kilden har også en hepatitt C-tabell (665), som ikke er relevant her.

### Dimensjoner

**Tabell 980 (SARS-CoV-2 hovedvariant):**

- `my` (Måned): `2026 aug`, `2026 sep`, `2026 okt`, `2026 nov`
- `Collapsed_pango` (variant): `Andre SARS CoV 2`, `BA.2.86`, `NB.1.8.1`, `PQ.16.1.1`, `XFG`, `PJ.2.1`
- `MEASURE_TYPE`: `Antall`, `Prosent`

**Tabell 964 (influensa A(H3N2)):**

- `my` (Måned): `2026 aug`, `2026 sep`, `2026 okt`. November mangler ennå.
- `Rapporteringskategori`: 7 genetiske klader, for eksempel «A(H3) klade 2a.3a.1 (K +S144D) representativ A/Norway/8765/2025»
- `MEASURE_TYPE`: `Antall`, `Prosent`

Det finnes ingen aldersgrupper, ingen geografi og ingen ukedimensjon.

### Hvordan tallene ser ut

Fra tabell 980, hentet 26.11.2026:

| Måned | Sekvenserte prøver | Største variant |
|---|---|---|
| August | 39 | XFG 16 (41 %) |
| September | 60 | XFG 38 (63 %) |
| Oktober | 48 | XFG 27 (56 %), PJ.2.1 11 (23 %) |
| November | **7** | XFG 3 (43 %), PQ.16.1.1 2 (29 %), PJ.2.1 2 (29 %) |

### Oppdatering

Tabellene publiseres på nytt når FHI oppdaterer, ikke på et fast tidspunkt vi kan lese ut av API-et. SARS-CoV-2-tabellene ble publisert 25.11, influensatabellene 17.11. Det passer med at FHI gir ut statusrapporter om luftveisinfeksjoner jevnlig. Hvor ofte tallene oppdateres er en slutning ut fra publiseringsdatoene, ikke noe FHI oppgir i metadataene.

### Særheter

1. **Svært få prøver.** Det er noen titalls sekvenser i måneden, og 7 i november så langt. Prosentene ser sikre ut («43 %»), men 43 % er 3 prøver. FHIs egne metadata sier: «Det tas forbehold for tidvis lavt antall sekvenser i datagrunnlaget. Siste måneds data kan være ufullstendige.»
2. **Ny tabell for hver sesong.** Sesongen 2026/27 har egne tabell-ID-er (962–965, 980–983), og 2025/26 har andre (914–916). Appen kan ikke ha faste tabellnumre slik den har for MSIS (724, 729, 731). Den må finne riktig tabell ut fra tittelen i tabellisten, og titlene skrives ikke helt likt («fordeling I Norge», «Sesong 2026/27:» med og uten kolon).
3. **Kategoriene endres.** Hvilke varianter og klader som finnes, endres fra tabell til tabell og over tid. FHI skriver at VOI/VUM-listen «vil kunne utvides eller forkortes». Appen kan ikke ha faste kategorier.
4. **Prosent er avrundet til hele tall**, og summen blir ikke alltid 100 (november: 29 + 43 + 29 = 101).
5. **Dimensjonene har tekniske navn**, for eksempel `Collapsed_pango` (både som kode og etikett), og kladenavnene er lange og bare forståelige for fagfolk.
6. **Ingen skjulte verdier i utvalget vi hentet** (json-stat-flaggene var tomme). Måneder uten funn står som 0.
7. **Ikke offisiell statistikk** (`isOfficialStatistics: false` i metadataene).

### Hva det ville gi en bruker uten fagbakgrunn

- Et svar på «hvilken variant er vanligst nå?», som media ofte spør om når en ny variant dukker opp.
- En mulighet til å koble varianter til tallene appen allerede viser: «Andelen positive steg i oktober, samtidig som PJ.2.1 ble vanligere.» Det er likevel ikke en årsak, og PRD-en sier at KI-forklaringen ikke skal gjette på årsaker (FR-21).

### Hva som er vanskelig å forklare

- Hva en variant, en Pango-linje og en klade er, og hvorfor navnene ser ut som koder.
- At «andel» her er andel av **sekvenserte prøver**, ikke av syke eller av positive prøver. Det er lett å blande sammen med «andel positive» i appen i dag.
- At de som får prøven sin sekvensert, er et lite og ikke tilfeldig utvalg.
- Forskjellen på VOI («variant av interesse») og VUM («variant under overvåking»), og at det ikke sier noe om hvor farlig varianten er.
- At en variant som er «vanligst» med 3 av 7 prøver, ikke sier stort.

## 2. Vaksinasjon (kilde `sysvak`)

### Tabeller

Kilden heter «Nasjonalt vaksinasjonsregister (SYSVAK)» og har 14 tabeller. De relevante:

| Tabell | Tittel | Hva den viser | Sist publisert |
|---|---|---|---|
| 928 | SYSVAK influensavaksinasjon 26/27 | Antall vaksinasjoner per uke | 25.11.2026 |
| 955 | SYSVAK koronavaksinasjon 26/27 | Antall vaksinasjoner per uke | 25.11.2026 |
| 716 / 717 | Samme for 25/26 | | 31.8.2026 |
| 324 / 484 | Samme for 24/25 | | 27.5.2025 |
| 753 | SYSVAK influensa årlig 65+ | **Dekning i %** per sesong | 30.9.2026 |
| 751 | SYSVAK covid-19 årlig 65+ | **Dekning i %** per sesong | 30.9.2026 |
| 750 | SYSVAK covid-19 årlig 75+ | **Dekning i %** per sesong | 30.9.2026 |

Kilden har også pneumokokk, barnevaksinasjonsprogrammet og kikhostevaksine til gravide (648, 882, 936–938).

### Dimensjoner

**Tabell 928 (influensa, per uke):**

- `Geografi`: 410 verdier: hele landet (`0`), 15 fylker, kommuner, bydeler i Oslo og `9999` (Ukjent)
- `Aldersgruppe`: `5` 0–8 år, `6` 9–17 år, `7` 18–64 år, `8` 65 år og over, `Alle`
- `Kjonn`: `Begge`, `Female`, `Male`
- `Uke`: `2026.36` til `2026.48` (13 uker så langt)
- `MEASURE_TYPE`: bare `Antall` («Antall vaksinasjoner»)

**Tabell 955 (covid-19, per uke)** har samme oppsett, men **andre aldersgrupper**: `1` 0–17 år, `2` 18–64 år, `3` 65–74 år, `4` 75 år og eldre, `Alle`.

**Tabell 753 (influensa, dekning 65+):**

- `geo`: hele landet, fylker og kommuner (409 verdier)
- `year`: sesongene 2015/2016 til 2025/2026, kodet med sluttåret (`2026` = 2025/2026)
- `MEASURE_TYPE`: bare `dekning` («Vaksinasjonsdekning»)

### Hvordan tallene ser ut

- Dekning mot influensa blant 65+ for hele landet (tabell 753): 23,8 % i 2015/16, 59,7 % i 2020/21 og 69,4 % i 2025/26. Tallene har mange desimaler (`69.43080139160156`).
- Antall influensavaksinasjoner per uke for hele landet og alle aldre (tabell 928): stiger fra 11 i uke 36 til rundt 200 000–230 000 i ukene 44–47. Uke 48 har 55 380 fordi uka ikke er ferdig.

### Oppdatering

Ukestabellene for inneværende sesong ble publisert natt til 25.11 og tar med uka som pågår, så de oppdateres trolig daglig eller flere ganger i uka. Dekningstabellene for 65+ og 75+ ble publisert 30.9, én gang etter at sesongen var over. Også dette er slutninger ut fra publiseringsdatoene.

### Særheter

1. **Ukestabellene viser ikke dekning.** De viser antall vaksiner satt. For å regne ut dekning trenger vi folketall per aldersgruppe og fylke, som ikke er i disse tabellene. Å regne ut dekning selv blir en ny metode som FHI ikke har kontrollert. Den ferdige dekningen finnes bare per sesong og bare for 65+ (influensa og covid-19) og 75+ (covid-19).
2. **Uka som pågår, er med**, og den ser ut som et kraftig fall. Det er det motsatte av MSIS-tabellene, der appen bruker «siste publiserte uke».
3. **Skjulte verdier.** Små tall vises som `:` («Anonymisert eller skjult av andre årsaker»). Flaggene `..` og `.` finnes også. Det er de samme verdiene som i MSIS, så `SKJULTE_VERDIER` i `fhi.py` dekker dem. I tabell 753 var 92 av 4 499 verdier skjult. I tabell 928 er de små aldersgruppene i fylkene ofte skjult tidlig i sesongen.
4. **Ulike aldersgrupper i influensa- og covid-tabellene**, og ingen av dem er like aldersgruppene i MSIS-tabellene som appen bruker nå. Brukeren kan ikke velge «samme aldersgruppe» på tvers.
5. **Ny tabell for hver sesong** (928, 716, 324 for influensa), slik som i NGS.
6. **Nytt ukeformat**: `2026.36`, mot `2026-w36` i MSIS. `les_ukekode` i `fhi.py` godtar bare MSIS-formatet.
7. **Sesongkoden i dekningstabellene er sluttåret** (`2026` betyr 2025/2026).
8. **Lav dekning de første årene kan skyldes registrering.** Dekningen for 65+ stiger fra 24 % til 60 % fra 2015/16 til 2020/21. Det kan delvis skyldes at færre vaksinasjoner ble registrert i SYSVAK før, ikke bare at færre ble vaksinert. Det må sjekkes med FHI før appen viser en slik graf uten forbehold.
9. **Geografien har rariteter**: Samiske navn i fylkesetiketten («Trøndelag Trööndelage»), en egen kategori «Ukjent» (`9999`), og i tabell 955 ligger en bydelskode (`110302`) løst på øverste nivå uten navn.
10. **Ikke offisiell statistikk** (`isOfficialStatistics: false`).

### Hva det ville gi en bruker uten fagbakgrunn

- Et enkelt og nyttig tall: «Hvor mange over 65 tok influensavaksinen i fjor, i mitt fylke og i landet?» Det passer godt til kommuneoverlegene, som er neste målgruppe i Vision.
- En kurve som viser når vaksinesesongen er i gang («de fleste vaksinerer seg i oktober og november»), vist ved siden av andelen positive prøver.

### Hva som er vanskelig å forklare

- Forskjellen på **antall vaksinasjoner** og **dekning**: høye ukestall betyr ikke at mange er beskyttet.
- At dekningen bare finnes for de eldste, og at det er fordi de er målgruppen for vaksineprogrammet.
- At vaksinasjon og andelen positive prøver ikke kan sammenlignes rett fram. Det er fristende å lese «flere vaksinert, færre syke», men det kan appen ikke vise. KI-forklaringen må ikke gjette på årsaker (FR-21), og det må gjelde også her.
- At tall fra de første årene kan være for lave på grunn av registreringen (særhet 8).

## 3. Hva det ville kreve å legge det til i appen

Appen er bygd rundt én type tabell: MSIS-tabeller med uker, aldersgrupper, antall tester, antall positive og andel positive (`domene.py`, `fhi.py`, `kontrollregler.py`). Begge de nye kildene har en annen form, så dette er mer enn å legge til nye tabellnumre.

| Del | Vaksinasjonsdekning 65+ (SYSVAK 753/751) | Varianter (NGS 980 + influensa) |
|---|---|---|
| **Henting** | Gjenbruk `hent`/`hent_dimensjoner`. Faste tabellnumre fungerer, fordi dekningstabellene ikke byttes hver sesong. | Ny funksjon som finner riktig tabell for sesongen ut fra titler i `…/ngs/Table`. Det er sårbart når titlene endres. |
| **Mellomlager** | Kan gjenbrukes. | Kan gjenbrukes, men nøkkelen må ta med tabell-ID-en, fordi den endres. |
| **Tolking** | Ny tolker: én verdi per sesong og geografi, ikke uker. Sesongkoden er sluttåret. | Ny tolker: måned × variant × (antall, prosent). Kategoriene er dynamiske. |
| **Domenemodell** | Ny type serie («dekning per sesong»). Geografi er ny. | Ny type serie («fordeling per måned»). |
| **Kontrollregler** | R1–R5 passer ikke. Nye regler: varsel om skjulte kommuner, og forbehold om registrering før ca. 2020. | Nye regler: varsel når en måned har få sekvenser (for eksempel under 30), og at siste måned kan være ufullstendig. |
| **Visning** | Søylediagram eller linje per sesong. Ny mal med valg av fylke. | Stablet søyle per måned, eller bare «vanligste variant nå» med antall. Lange kladenavn må forkortes eller forklares. |
| **KI-forklaring** | Ny prompt. Må ikke koble dekning til smitte. | Ny prompt. Må ikke si noe om hvor farlig en variant er. |
| **Begrepsforklaringer** (FR-13) | Vaksinasjonsdekning, SYSVAK, «antall vaksinasjoner er ikke dekning», målgruppe 65+. | Genomovervåkning/sekvensering, variant, Pango-linje, klade, VOI/VUM, «andel av sekvenserte prøver». |
| **Kildehenvisning** (FR-12) | Ny kildetekst fra SYSVAKs metadata. | Ny kildetekst: «Referanselaboratoriet for koronavirus …» (fra metadataene for 980). |

### Nye krav i PRD-en

- Kapittel 4 (Datasett): to nye datasett med tabellnumre, dimensjoner, oppdatering og særheter. Se seksjon 1 og 2 her.
- Kapittel 3 (Begreper): begrepene i tabellen over.
- Kapittel 5 (Maler): nye maler, for eksempel «Mal 5: Vaksinasjonsdekning 65+ per sesong» og «Mal 6: Vanligste SARS-CoV-2-varianter de siste månedene».
- Nye FR-er for valg av fylke, ny graf, nye kontrollregler og KI-regler (ikke koble vaksine til smitte, ikke vurdere hvor farlig en variant er).
- En beslutning om hvorvidt appen skal regne ut dekning selv fra ukestallene. Anbefaling: nei, ikke i første omgang.
- «Utenfor omfang» i briefen (linje 109) må endres når dette tas inn.

### Nye tester

Med samme oppskrift som for MSIS (stories 1.3 og 2.4):

- Fixturer med ekte svar fra 753, 751 og 980 (og 928 hvis ukestall tas med), lagret uten nett, slik `tests/fixtures` gjør i dag.
- Tolkertester: skjulte verdier (`:`), sesongkode som sluttår, dynamiske kategorier, prosent som ikke summerer til 100, uke som pågår.
- Test av tabelloppslaget for NGS: finner riktig tabell for sesongen og feiler tydelig når ingen tittel passer.
- Tester av nye kontrollregler og begrepsforklaringer, og webtester for nye maler (som `test_web_*.py`).
- `test_nettsperre.py` sørger allerede for at testene ikke går mot FHI.

### Omtrentlig arbeid

Anslaget er i stories av samme størrelse som i epic 2 og 3.

- **Vaksinasjonsdekning 65+ (tabell 753 og 751):** 5–7 stories. Fixtur, tolker, domenetype for serie per sesong og geografi, kontrollregler, mal med fylkesvalg og graf, begreper og KI-prompt. Middels stort. Den største nye tingen er geografi, som også er neste steg i Vision.
- **Ukestall for vaksinasjoner (928 og 955) i tillegg:** +2–3 stories, særlig hvis de skal vises sammen med MSIS-grafen. Det krever også klare regler for uka som pågår og for skjulte celler.
- **Varianter (NGS):** 6–8 stories. Oppslag av tabell per sesong, tolker med dynamiske kategorier, ny graftype, nye kontrollregler for få sekvenser, mange nye begreper og KI-regler. Stort, og det mest krevende å forklare godt.

## Anbefaling

1. Begynn med **vaksinasjonsdekning 65+ per sesong** (tabell 753 for influensa og 751 for covid-19). Tallene er ferdig beregnet av FHI, tabellnumrene er stabile, skjulte verdier håndteres som i dag, og fylkestallene passer med neste målgruppe i Vision (kommuneoverleger).
2. Vent med **genomovervåkning**, eller begrens det til en liten boks med «vanligste SARS-CoV-2-variant siste måned», alltid sammen med antall sekvenser. Datagrunnlaget er lite, tabellene og kategoriene endres hver sesong, og begrepene er vanskelige for målbrukeren.
3. Før noe av dette bygges: spør FHI om registreringen i SYSVAK før 2020 og om det finnes en stabil måte å finne sesongtabellene i NGS på.
