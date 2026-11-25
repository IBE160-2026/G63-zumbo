---
title: 'Story 6.1: RSV'
type: 'feature'
created: '2026-11-25'
status: 'in-progress'
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
- [ ] `backend/tests/fixtures/fhi/729-dimensjoner.json`, `729-rsv-2025-2026-alle-nonstl.json`, `README.md` -- ekte svar hentet 25.11.2026, forespørselen dokumentert -- AD-10
- [ ] `backend/src/backend/fhi.py` -- `FASTE_FILTRE[729]` -- FR-2, FR-6
- [ ] `backend/src/backend/tjeneste.py` -- dimensjonsliste per tabell for siste publiserte uke; `IKKE_KLART` lister de klare virusene -- AD-3
- [ ] Tester: tolking av 729-fixturen, forespørsel med `respx`, kildehenvisning, RSV i skjemaet, ingen «RS-virus (A+B)» på siden, 729-dimensjonslisten brukes; oppdater testene i Code Map

**Acceptance Criteria:**
- Given skjemaet, when siden vises, then kan RSV velges ved siden av influensa.
- Given et RSV-svar, when siden vises, then står «RESPIaggr RSV antall og andel» og FHIs kildetekst for 729, og ikke «RS-virus (A+B)».
- Given `uv run pytest` og `uv run ruff check`/`ruff format --check`, then er alt grønt uten nett.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Sesonglisten blir på 724 fordi alle tre tabellene har samme uker (sjekket 25.11.2026: `2024-w40` … `2026-w46` i alle tre) og AD-3 bare krever at *siste publiserte uke* kommer fra tabellens egen liste. Én ekstra dimensjonsliste per tabell lagres som `fhi/729-dimensjoner.json` i cachen (AD-4 har allerede formatet).

## Verification

**Commands:**
- `cd backend && uv run pytest` -- expected: alle tester består
- `cd backend && uv run ruff check . && uv run ruff format --check .` -- expected: ingen funn
