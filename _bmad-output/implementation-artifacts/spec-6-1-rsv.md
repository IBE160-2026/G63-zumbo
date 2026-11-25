---
title: 'Story 6.1: RSV'
type: 'feature'
created: '2026-11-25'
status: 'done'
baseline_commit: 'bf97c165f46072ed8ff6960932e0d8f6fd815a89'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-6-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Brukeren kan bare velge influensa. RSV står i `domene.VIRUS`, men `fhi` kan ikke hente eller tolke tabell 729, og skjemaet viser bare influensa (FR-2, issue #30).

**Approach:** Legg til de faste filtrene for 729 (`rsvtype` `A+B`, `NONSTL`) i `fhi`. Da blir RSV et «klart» virus og vises i skjemaet. `tjeneste` finner siste publiserte uke i dimensjonslisten for utvalgets egen tabell (AD-3), mens sesonglisten fortsatt lages fra 724. Lagre et ekte svar og dimensjonslisten for 729 som fixtures.

## Boundaries & Constraints

**Always:** Tabellnavn og kildetekst kommer fra `domene.TABELLER` (Irene sjekket dem mot FHIs metadata 25.11.2026). FHI-koder finnes bare i `domene` og `fhi` (NFR-3). Etiketten «RS-virus (A+B)» vises aldri. Tester kaller aldri FHI (AD-10). Influensa virker som før.

**Never:** Ingen endring i kontrollreglene, KI-prompten, PRD-en eller arkitekturen. SARS-CoV-2 (731) tas i story 6.2.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| RSV hentes | `GET /?mal=1&virus=rsv&sesong=2025/2026` | `POST …/Table/729/data` med `rsvtype` `A+B` og `NONSTL`; tabell og kilde for 729 | N/A |
| Siste uke per tabell | RSV-utvalg uten lagret 729-liste | `GET …/Table/729/dimension` gir siste publiserte uke; sesonglisten kommer fra 724 | FHI nede: FR-8 som for influensa |
| SARS-CoV-2 via URL | `virus=sars-cov-2` | «Tall for SARS-CoV-2 kan ikke vises i appen ennå. Velg influensa eller RSV.» uten kall | N/A |
| Svar fra feil tabell | 724-svar tolket som RSV-utvalg | `ValueError` (mangler `rsvtype`) | `fhi.hent` gir `FhiUtilgjengelig` |

</frozen-after-approval>

## Code Map

- `backend/src/backend/fhi.py` -- `FASTE_FILTRE` styrer både `forespørsel` og `_sjekk_filtre`; legg til 729.
- `backend/src/backend/tjeneste.py` -- `KLARE_VIRUS` avledes av `FASTE_FILTRE`; `IKKE_KLART` har fast «Velg influensa»; `_dimensjonsliste`/`_lagret_dimensjonsliste` bruker alltid `SESONGTABELL`. `sesonger()` skal fortsatt bruke 724. `_feilet`-pausen er felles for FHI.
- `backend/src/backend/mellomlager.py` -- `les_dimensjoner`/`lagre_dimensjoner` tar allerede tabellnummer; ingen endring.
- `backend/src/backend/web.py` -- skjemaet bruker `KLARE_VIRUS`; ingen endring ventet.
- `backend/tests/fixtures/fhi/` -- `724-*`-filene og `README.md` er mønsteret (cacheformat `{"hentet", "svar"}`).
- Tester som forventer at RSV ikke er klart: `test_fhi_hent.py:93`, `test_tjeneste.py:222-235`, `test_web.py:97-100,205,242-246`, `test_web_hent_nyeste.py:314`, `test_web_forklaring.py:373`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/tests/fixtures/fhi/729-dimensjoner.json`, `729-rsv-2025-2026-alle-nonstl.json`, `README.md` -- ekte svar hentet 25.11.2026, forespørselen dokumentert -- AD-10
- [x] `backend/src/backend/fhi.py` -- `FASTE_FILTRE[729]` -- FR-2, FR-6
- [x] `backend/src/backend/tjeneste.py` -- dimensjonsliste per tabell for siste publiserte uke; `IKKE_KLART` lister de klare virusene -- AD-3
- [x] Tester: tolking av 729-fixturen, forespørsel med `respx`, kildehenvisning, RSV i skjemaet, ingen «RS-virus (A+B)» på siden, 729-dimensjonslisten brukes; oppdater testene i Code Map

**Acceptance Criteria:**
- Given skjemaet, when siden vises, then kan RSV velges ved siden av influensa.
- Given et RSV-svar, when siden vises, then står «RESPIaggr RSV antall og andel» og FHIs kildetekst for 729, og ikke «RS-virus (A+B)».
- Given `uv run pytest` og `uv run ruff check`/`ruff format --check`, then er alt grønt uten nett.

## Implementation Notes

- Fixturene for 729 og README-teksten er lagt inn i commit 01f7e33. De skal ikke endres eller hentes på nytt. Ikke commit; hovedøkten committer.

## Spec Change Log

## Review Triage Log

Kodegjennomgang 25.11.2026 med fire lag: blind-hunter (BH), edge-case-hunter (EC), verification-gap (VG) og acceptance-auditor (AA). Ingen alvorlige funn, ingen som krever endring i PRD eller arkitektur. 3 rettet, 0 utsatt, 17 avvist.

| # | Lag | Funn | Vurdering | Begrunnelse / rettelse |
|---|-----|------|-----------|------------------------|
| 1 | VG | Ingen test for at jobbnøkkelen for dimensjonslisten er per tabell ved samtidige kall | medium, patch | Rettet: `test_rsv_venter_ikke_på_724_listen_som_hentes_samtidig`. Feiler hvis nøkkelen blir `dimensjoner-724` igjen (sjekket). |
| 2 | AA+BH | «Hent nyeste tall nå» for RSV har ingen test | low, patch | Rettet: `test_tvungen_henting_for_rsv_henter_729_selv_om_alt_er_ferskt`. |
| 3 | BH | Docstringen til `FASTE_FILTRE` viser til testdokumentasjon for et faglig faktum | low, patch | Rettet: viser nå til PRD-ens addendum. |
| 4 | EC+BH | En vellykket henting av 729-listen nullstiller pausen etter en feil på 724 | false | Uten `tving` stopper `_stopp_hvis_nylig_feil` kallet før det går til FHI. En vellykket henting betyr at FHI svarer, og da er det riktig å nullstille pausen. Slik var det også før, mellom listen og datakallet for 724. |
| 5 | EC | Lagret 729-liste brukes ikke når FHI er nede | false | Listen brukes bare til å bestemme ukene for datakallet. Når FHI er nede, feiler også datakallet. De lagrede tallene vises uansett, slik som for influensa (FR-8). |
| 6 | EC+BH | Sesonglisten kommer fra 724, og 729 kan mangle den nyeste sesongen | low, avvist | Alle tre tabellene har de samme ukene og ble publisert samtidig (19.11.2026). Hvis listene likevel skiller seg, får brukeren meldingen `IKKE_PUBLISERT`, ikke feil tall. Står i Design Notes. |
| 7 | EC+BH | `_i_setning`/`KLARE_VIRUS` kan gi `IndexError` med tomt navn eller tom liste | false | Navnene og listene er faste i `domene`/`fhi`. Influensa er alltid klart. |
| 8 | VG | `_klare_virus_som_tekst` gjentar `domene._liste` | low, avvist | `IKKE_KLART` blir uaktuell i 6.2, når alle virusene er klare. Ryddes da. |
| 9 | BH | `IKKE_KLART` mangler tester for tilfellene med ett og tre navn | low, avvist | Samme grunn som #8. |
| 10 | BH | Ingen test for KI-forklaringen med RSV / at etiketten ikke havner i prompten | false | `Dataserie` og `Kildehenvisning` har ingen FHI-etiketter. Prompten får virusnavnet fra `domene.VIRUS` («RSV») og tabellnavnet fra `TABELLER`. |
| 11 | AA | «RS-virus (A+B)» sjekkes bare på hovedsiden | false | Samme grunn som #10. Etiketten kan ikke nå andre sider. |
| 12 | AA | Testen for RSV i skjemaet sjekker hele siden | low, avvist | `_verdier(html, "virus") == ["influensa", "rsv"]` sjekker valgene i skjemaet. |
| 13 | BH | `test_siste_publiserte_uke_for_rsv_kommer_fra_729` er svak | false | 724-listen har uke 46 og 729-listen uke 44. Testen krever uke 44, og det viser at 724 ikke ble brukt. Ukekodene har alltid to sifre. |
| 14 | BH | Pausen etter feil er bare testet i én retning | low, avvist | Pausen er felles og symmetrisk (`_feilet`). Én retning er testet, og koden er den samme. |
| 15 | BH | Tvungen henting for RSV fornyer ikke sesonglisten fra 724 | low, avvist | Den valgte sesongen står allerede i listen. Listen fornyes uansett når den er utdatert (AD-5). |
| 16 | BH | Ingen sjekk mens appen kjører av at tabellene har de samme ukene | low, avvist | Samme som #6. |
| 17 | AA+BH | `sprint-status` sier `in-progress`, spec-en `in-review` | false | Settes til `done` etter gjennomgangen. |
| 18 | AA | Spec-en sier «Ikke commit», men branchen har commits | false | Notatet gjaldt implementasjonsagenten. Hovedøkten committet. |
| 19 | BH | Ingen test for at knappen vises for RSV | low, avvist | Knappen vises for alle virus i `KLARE_VIRUS`, og det er allerede testet for influensa. RSV er med i `KLARE_VIRUS`. |
| 20 | EC | Brukeren kan velge en sesong som 729 ikke har publisert, og får bare en melding | low, avvist | Samme som #6. |

## Design Notes

Sesonglisten blir på 724 fordi alle tre tabellene har samme uker (sjekket 25.11.2026: `2024-w40` … `2026-w46` i alle tre) og AD-3 bare krever at *siste publiserte uke* kommer fra tabellens egen liste. Én ekstra dimensjonsliste per tabell lagres som `fhi/729-dimensjoner.json` i cachen (AD-4 har allerede formatet).

## Verification

**Commands:**
- `cd backend && uv run pytest` -- expected: alle tester består
- `cd backend && uv run ruff check . && uv run ruff format --check .` -- expected: ingen funn
