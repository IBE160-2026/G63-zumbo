# Manus for brukertestingen (story 5.1)

**Utkast.** Irene retter manuset før testen. Se issue #28.

Manuset måler det PRD-en sier om brukertestingen (kapittel 12):

- **SM-5, forståelighet:** testpersonen forklarer med egne ord hva grafen viser og om tallene er sikre. Mål: minst 4 av 5 svarer riktig på begge oppgavene med mal 1 (oppgave 1 og 2).
- **SM-6, tid:** tid fra valgt mal til forklart situasjonsbilde. Mål: under 1 minutt for minst 4 av 5.
- **NFR-3, enkelt språk:** ord testpersonen ikke forstår, noteres og skrives om.

Fem personer uten medisinsk bakgrunn prøver appen én og én. Hver får én oppgave med mal 1 der varselet ikke vises (oppgave 1), og én der det vises (oppgave 2).

## Før testen

- [ ] Skriv fasit for hver oppgave i tabellen under, med tallene slik de er den dagen. Fasiten skal være skrevet før første testperson.
- [ ] Sjekk at appen virker og at forsiden viser tre kort.
- [ ] Ha klar stoppeklokke og ett notatark per testperson (se «Notatark» nederst).
- [ ] Spør hvis det er mulig en medstudent om å vurdere svarene mot fasiten uavhengig av meg (SM-5).

| Oppgave | Fasit (skrives før testen) |
|---|---|
| 1. Influensa 2025/2026, alle aldre | Hovedtrekk: … Varsel: nei. |
| 2. Influensa 2024/2025, alle aldre | Hovedtrekk: … Varsel: ja, fordi perioden går over 1. mars 2025 (R5), så tallene før og etter kan ikke sammenlignes direkte. |
| 3. RSV, 0–4 år, sesongen som pågår | Andel i siste uke med tall: … % (uke …). Varsel: … |
| 4. «Andel positive» | Hvor mange av testene som var positive, regnet i prosent av alle testene. |
| 5. Kilde og tidspunkt | Folkehelseinstituttet, hentet … |

## Introduksjon (les høyt)

> Takk for at du vil være med. Jeg lager en app som viser tall fra Folkehelseinstituttet om influensa, RSV og koronavirus. Nå vil jeg se om appen er lett å forstå.
>
> Det er appen som testes, ikke deg. Det fins ingen gale svar. Hvis noe er vanskelig, er det appen som må bli bedre.
>
> Jeg gir deg fem små oppgaver. Si gjerne høyt hva du tenker mens du leter. Jeg hjelper deg ikke underveis, for jeg vil se hvordan appen fungerer uten meg. Hvis du står fast, kan du si «jeg gir opp», og så går vi videre.
>
> Jeg tar tiden på noen av oppgavene og skriver ned hva du gjør. Jeg skriver ikke ned navnet ditt. Det tar omtrent 15 minutter, og du kan stoppe når du vil.
>
> Har du noen spørsmål før vi begynner?

## Oppgaver

Les oppgaven høyt og gi testpersonen den på en lapp. Start klokka når testpersonen har trykket på kortet, altså når malen er valgt (SM-6). Stopp klokka når testpersonen er ferdig med å forklare.

### Oppgave 1: Influensa uten varsel (SM-5, SM-6)

> Du skriver en oppgave om influensa. Finn tallene for influensa i sesongen 2025/2026 for alle aldre. Fortell meg med egne ord hva grafen viser, og om du mener tallene er sikre.

### Oppgave 2: Influensa med varsel (SM-5, SM-6)

> Bytt til sesongen 2024/2025. Fortell meg hva grafen viser, og om tallene er sikre. Hvis appen viser et varsel, hvorfor vises det?

### Oppgave 3: RSV hos de minste barna

> Finn andelen positive tester for RSV hos de minste barna i den siste uka det finnes tall for. Hvilken uke er det?

### Oppgave 4: Hva betyr «andel positive»?

> Forklar med egne ord hva «andel positive» betyr. Du kan bruke appen for å finne ut av det.

### Oppgave 5: Hvor kommer tallene fra?

> Hvor kommer tallene fra, og når ble de hentet?

## Hva jeg noterer for hver oppgave

| | Hva |
|---|---|
| Tid | Sekunder fra valgt mal til ferdig forklaring. Mål: under 60 (SM-6). |
| Lyktes | Ja, delvis eller nei, vurdert mot fasiten. For oppgave 1 og 2: riktig hovedtrekk **og** riktig om tallene er sikre (SM-5). |
| Hva testpersonen sa | Stikkord, helst med testpersonens egne ord. |
| Ord | Ord testpersonen ikke forsto eller spurte om (NFR-3). |
| Hvor testpersonen stoppet opp | For eksempel at hen lette etter sesongvalget, eller ikke så varselet. |

## Spørsmål til slutt

1. Hva var vanskeligst å forstå eller å finne i appen?
2. Var det noen ord eller forklaringer du ikke skjønte?
3. Savnet du noe i appen, eller er det noe du ville ha gjort annerledes?

> Takk for hjelpen!

## Notatark (ett per testperson)

Testperson nr.: ___ Dato: ___ Medisinsk bakgrunn: nei

| Oppgave | Tid (sek) | Lyktes (ja/delvis/nei) | Hva testpersonen sa | Ord testpersonen ikke forsto | Hvor testpersonen stoppet opp |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

Svar på spørsmålene til slutt:

1.
2.
3.

## Resultat etter fem personer

| Mål | Resultat |
|---|---|
| SM-5: riktig på både oppgave 1 og 2 | ___ av 5 (mål: minst 4) |
| SM-6: under 1 minutt på oppgave 1 og 2 | ___ av 5 (mål: minst 4) |
| SM-5: vurdert uavhengig av medstudent | ja / nei, ___ av 5 |
| NFR-3: ord som skal skrives om | … |
