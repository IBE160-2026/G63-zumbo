---
title: 'Story 2.1: Domenemodellen'
type: 'feature'
created: '2026-11-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det finnes ingen felles dataklasser eller faste lister ennå (issue #6). Uten `domene.py` vil fhi-tolking, kontrollregler, web og KI-prompt lage hver sin variant av «uke», «skjult verdi», «aldersgruppe» og kildehenvisning (AD-2).

**Approach:** Skriv `backend/src/backend/domene.py` med de frosne dataklassene `Utvalg`, `Uke`, `Dataserie`, `Regelutslag` og `Kildehenvisning`, faste lister for virus → tabell (724/729/731), de sju aldersgruppevalgene og mal 1, og funksjonen `kildehenvisning(tabell, hentet)` med FHIs kildetekster fra addendumet. `Uke.usikker` (færre enn 30 tester eller skjult antall tester) og `Uke.manglende` (tester eller positive er `None`) regnes ut i `Uke`, og `Uke.andel` er `None` for manglende uker, aldri 0. Modulen importerer bare standardbiblioteket (AD-1). Tester i `backend/tests/test_domene.py` dekker 29 og 30 tester, skjulte verdier, kildehenvisningen for 724 og at ingen skallmoduler importeres.

</frozen-after-approval>

## Implementation Notes

- Nye filer: `backend/src/backend/domene.py` og `backend/tests/test_domene.py`.
- Faste lister er `MappingProxyType` (kan ikke endres): `TABELLER` (nummer, navn, kildetekst), `VIRUS` (nøkkel → tabell), `ALDERSGRUPPER` (sju valg med nøkkel, norsk etikett og FHI-kode) og `MALER`. Nøklene (`influensa`, `rsv`, `sars-cov-2`, `alle`, `0-4` …) er tenkt som verdier i query-parametrene i story 2.2.
- Bare mal 1 er med i `MALER`. Mal 2 er strekkmål og legges til i epic 8, slik at story 2.2 ikke godtar den før den finnes.
- Kildetekstene for 729 og 731 står i addendumet og er tatt med nå. Tabellnavnene for 729 og 731 er fra PRD kapittel 4 og ikke sjekket mot metadataene (gjøres i epic 6).
- `Uke.andel` er en egenskap som alltid regnes ut som `positive * 100 / tester` (PRD kapittel 3). Den er `None` for en manglende uke og ved 0 tester (kan ikke dele på 0). 0 positive av 100 gir `0.0`, fordi det er en ekte null. Først var `andel` et felt der FHIs `pos_rate` kunne sendes inn. Det ble endret etter gjennomgangen (se under). `fhi.tolk` i story 2.4 trenger derfor ikke lese `pos_rate`. Den kan heller sjekke at FHIs andel stemmer med den utregnede.
- `Uke` avviser uker som ikke finnes i ISO-året (for eksempel 2025-w53, sjekket med `date.fromisocalendar`) og negative tall. `Regelutslag` avviser andre regler enn R1–R5 og tom tekst. `kildehenvisning` avviser ukjent tabell og tid uten tidssone (AD-5).
- `Kildehenvisning` har ingen ferdig tekst for visning. Formatering av dato skjer i Jinja2-filtre i `web` (arkitekturen kapittel 4).
- `Utvalg` validerer ikke verdiene selv. Det gjør `Utvalg.fra_parametre` i story 2.2. `Utvalg.tabell` slår opp i `VIRUS`.
- Importtesten leser `domene.py` med `ast` og sjekker at alle importer er fra standardbiblioteket (AD-1).


## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Ingen brudd på akseptansekriteriene.

- **medium, rettet:** `dataclasses.replace(uke, positive=…)` beholdt den gamle andelen. Bekreftet: ga 5.0 i stedet for 10.0. `andel` er nå en egenskap.
- **medium, rettet:** en oppgitt andel ble beholdt ved 0 tester og kunne avvike fra tallene. Rettet med samme endring.
- **medium, rettet:** kildeteksten for 729 og 731 ble bare sjekket på begynnelse og slutt. Testen sammenligner nå hele `Kildehenvisning` ordrett for alle tre tabellene.
- **low, rettet:** uke 53 ble godtatt i år uten uke 53. Bekreftet: `Uke(2025, 53, …)` ble godtatt.
- **low, rettet:** ingen test for negative `positive`.
- **low, rettet:** ingen test av FHI-kodene for aldersgruppene. Testen sjekker dem nå mot `724-dimensjoner.json`.
- **low, rettet:** docstringene for `Dataserie` og `kildehenvisning` lovet mer enn koden sjekker. De er skrevet om. Uker med 0 tester (usikker, ikke manglende, andel `None`) er nå beskrevet.
- **maybe-false, utsatt:** flere positive enn tester gir andel over 100 %. Vi vet ikke om FHI kan sende slike tall, se deferred-work.md.
- **avvist:** `Utvalg` sjekker ikke verdiene, og `Utvalg.tabell` gir `KeyError`. Dette er bevisst, fordi valideringen kommer i story 2.2 (`fra_parametre`).
- **avvist (low):** `Regelutslag(…, None)` og `kildehenvisning(…, date)` gir `AttributeError` i stedet for `ValueError`. Det feiler høyt, og ingen kode sender slike verdier.
- **avvist (low):** `bool`, `float` og `str` godtas som antall, og andel kontrolleres ikke for NaN eller grenser. Ingen kode sender slike verdier, og andelen kommer ikke lenger utenfra.
- **avvist (low):** en `Kildehenvisning` kan lages direkte. Docstringen sier nå at `kildehenvisning()` skal brukes. En sperre ville gjort dataklassen vanskeligere å bruke i tester.
- **avvist (low):** testen sjekker ikke kall til `datetime.now()` eller `open`, at alle listene ikke kan endres, plassholderne i `Mal.spørsmål`, eller at 30 står fast i en docstring. AD-1-testen dekker akseptansekriteriet (importer).
- **avvist:** AD-1-testen er strengere enn AD-1 (bare standardbiblioteket). Det er greit nå. Den må endres hvis `domene` en gang skal importere en annen kjernemodul.
