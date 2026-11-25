# Epic 6 Context: RSV og SARS-CoV-2

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Brukeren kan velge RSV og SARS-CoV-2 i mal 1, i tillegg til influensa, og får graf, tabell, varsel, kildehenvisning og KI-forklaring på samme måte for alle tre luftveisvirusene. Epicen bygger videre på den ferdige mal 1 for influensa og legger bare til de to nye FHI-tabellene (729 og 731). Den droppes hvis mal 1 for influensa ikke virker 2. desember 2026. Veiledende: 3.–4. desember.

## Stories

- Story 6.1: RSV
- Story 6.2: SARS-CoV-2

## Requirements & Constraints

- **Virus → tabell:** influensa → 724, RSV → 729, SARS-CoV-2 → 731. Brukeren velger ett virus i skjemaet (radioknapper: Influensa, RSV, SARS-CoV-2).
- **Felles utvalg for alle tabeller:** vanlig klinisk praksis (`surveillancetype` `NONSTL`), totalen for virustypen og valgt aldersgruppe (`Alle` som standard, «Ukjent alder» tilbys ikke). Måltallene er de samme: positive prøver, tester og andel positive per uke.
- **RSV (729):** bruk `rsvtype` `A+B`. Det er totalen, inkludert prøver med ukjent type (sjekket mot ekte tall: A + B + ukjent = «A+B»). Etiketten «RS-virus (A+B)» er misvisende og skal aldri vises for brukeren.
- **SARS-CoV-2 (731):** har ingen typedimensjon. Forespørselen skal ikke ha noen typeparameter.
- **Kildehenvisning:** FHIs egen kildetekst ordrett, deretter tabellnummer, tabellnavn og hentedato.
  - 729: «Kilde: MSIS-labdatabase og Referanselaboratoriet for RS-virus, Folkehelseinstituttet (FHI).» Tabellnavn «RESPIaggr RSV antall og andel».
  - 731: «Kilde: MSIS-labdatabase og Referanselaboratoriet for koronavirus med utbruddspotensiale, Folkehelseinstituttet (FHI).» Tabellnavn «RESPIaggr SARS-CoV-2 antall og andel».
- **Kontrollregler og sesonger** gjelder uendret for alle virus. R5 (bruddet 1. mars 2025) gjelder også 729 og 731. I ekte data per 20.11.2026 hadde RSV og SARS-CoV-2 minst 129 tester per uke og ingen skjulte verdier, så varsler kommer fra R1 (for eksempel RSV 80+ år i 2026/2027), R4 og R5.
- **Ingen FHI-koder i grensesnittet** (`NONSTL`, `A+B`, `pos_rate` osv.). Alt er på enkel norsk bokmål.
- **Ferdigkriterier for hver story:** egne tester for akseptansekriteriene (tolking av fixturen, riktig forespørsel med `respx`, kildehenvisningen, at viruset kan velges i skjemaet), `uv run pytest` består uten nett og uten nøkkel, `ruff check` og `ruff format --check` består, ingen import bryter avhengighetsretningen, og README oppdateres ved behov.

## Technical Decisions

- **FHI-koder bare i `domene.py` og `fhi.py`.** Den faste listen virus → tabell og typedimensjonen per tabell hører hjemme der. Maler og KI-prompt får bare norske etiketter.
- **`fhi.hent` er eneste kode som kaller FHI** (httpx, 10 s, `FhiUtilgjengelig`). Endepunktene er de samme for alle tabeller: `.../msis/Table/{tabell}/data` (POST), `/dimension` og `/metadata`. Formatet er JSON (`json-stat2`).
- **Dimensjonslisten per tabell:** siste publiserte uke og sesonglisten kommer fra `dateusedforstatistics` for den aktuelle tabellen, mellomlagret som `fhi/<tabell>-dimensjoner.json`. Reserven er `sesong.sesonger_fra_dato(nå)`.
- **Mellomlagring:** filnavn bare fra `Utvalg.nøkkel`, som må skille virusene.
- **Kildehenvisning** lages bare av `domene.kildehenvisning(tabell, hentet)`, og den samme brukes under grafen og ved KI-forklaringen.
- **Fixtures:** et ekte svar og dimensjonslisten for 729 og for 731 lagres i `tests/fixtures/fhi/` i samme format som cachen, med hentedato i fila. Testene bruker `respx` og trenger ikke nett.

## Cross-Story Dependencies

- Hele epicen forutsetter at mal 1 for influensa er ferdig (epic 2–4). Ellers droppes den.
- 6.2 bygger på 6.1: når RSV er lagt til, skal SARS-CoV-2 følge samme mønster, men uten typedimensjon.
- Epic 7 (testsettet med 10 spørsmål for alle tre virus, SM-1–SM-3) og mal 2 i epic 8 forutsetter at begge storyene er ferdige.
