---
title: 'Story 6.2: SARS-CoV-2'
type: 'feature'
created: '2026-11-25'
status: 'in-progress'
baseline_commit: '50232036aaeeee2ae2b2937beed846a6dd454f44'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-6-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** SARS-CoV-2 kan ikke velges. `fhi` kan ikke hente eller tolke tabell 731, og en URL med `virus=sars-cov-2` gir «kan ikke vises i appen ennå» (FR-2, issue #31).

**Approach:** Legg til de faste filtrene for 731 (bare `NONSTL`, ingen typedimensjon) i `fhi`. Når alle tre virusene er klare, fjernes veien for virus som ikke er klare (`IKKE_KLART` og hjelperne). Lagre et ekte svar og dimensjonslisten for 731 som fixtures. Irenes krav (25.11.2026): meldingen for ugyldig virus skal nevne nøyaktig de virusene som kan velges i skjemaet.

## Boundaries & Constraints

**Always:** Tabellnavn og kildetekst kommer fra `domene.TABELLER` (Irene sjekket dem mot FHIs metadata 25.11.2026). FHI-koder finnes bare i `domene` og `fhi` (NFR-3). Tester kaller aldri FHI (AD-10). Influensa og RSV virker som før. Siste publiserte uke kommer fra tabellens egen dimensjonsliste, slik det ble gjort i story 6.1.

**Never:** Ingen endring i kontrollreglene, KI-prompten, PRD-en eller arkitekturen. Meldingen for ukjent *mal* endres ikke her.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| SARS-CoV-2 hentes | `GET /?mal=1&virus=sars-cov-2&sesong=2025/2026` | `POST …/Table/731/data` med `aldersgruppe`, uker, `surveillancetype` `NONSTL`, måltall, og ingen typedimensjon; tabell og kilde for 731 | N/A |
| Ugyldig virus | `virus=ebola` | «Velg et virus: Influensa, RSV eller SARS-CoV-2.», nøyaktig de virusene som står i skjemaet | N/A |
| Svar med ekstra dimensjon | 724- eller 729-svar tolket som SARS-CoV-2 | `ValueError` | `fhi.hent` gir `FhiUtilgjengelig` |
| Dimensjonsrekkefølge | 731-svaret har `aldersgruppe` før ukene i `id` | Tolkes riktig (uke 2025-w40 = 471 positive av 7109 tester) | N/A |

</frozen-after-approval>

## Code Map

- `backend/src/backend/fhi.py` -- `FASTE_FILTRE` styrer både `forespørsel` og `_sjekk_filtre`; legg til `731: {"surveillancetype": "NONSTL"}`. `_sjekk_filtre` krever at alle dimensjoner utenom uke og måltall har én kategori, så en typedimensjon i et 724/729-svar vil bli avvist bare hvis den ikke finnes i 731. Sjekk at et svar med en dimensjon 731 ikke har, gir `ValueError`. Hvis ikke, må `_sjekk_filtre` kreve at svaret ikke har andre dimensjoner enn de forventede.
- `backend/src/backend/tjeneste.py` -- `KLARE_VIRUS`, `_i_setning`, `_klare_virus_som_tekst`, `IKKE_KLART` og grenen i `svar` som bruker dem (rundt linje 254) fjernes, sammen med testene for dem.
- `backend/src/backend/web.py` -- bruker `KLARE_VIRUS` (linje 54, 258, 262, 279). Bruk `VIRUS` direkte. `klare_virus` i malen faller bort.
- `backend/src/backend/templates/index.html:66` -- vilkåret `resultat.utvalg.virus in klare_virus` blir bare `resultat.serie is none`.
- `backend/src/backend/domene.py` -- `Utvalg.fra_parametre` lister allerede alle virusene i `VIRUS`; ingen endring ventet.
- `backend/tests/fixtures/fhi/731-*.json` og `README.md` -- allerede lagt inn (commit 5023203). Ikke endre eller hent på nytt.
- Tester som forventer at SARS-CoV-2 ikke er klart: `test_fhi_hent.py:102`, `test_tjeneste.py:198,222-235`, `test_web.py:97-100,203,242-246`, `test_web_hent_nyeste.py:314`, `test_web_forklaring.py:377`. Mønster for RSV-testene fra 6.1 står i de samme filene.

## Tasks & Acceptance

**Execution:**
- [x] `backend/tests/fixtures/fhi/731-dimensjoner.json`, `731-sars-cov-2-2025-2026-alle-nonstl.json`, `README.md` -- ekte svar hentet 25.11.2026 -- AD-10
- [ ] `backend/src/backend/fhi.py` -- `FASTE_FILTRE[731]`, og at et svar med en ekstra dimensjon avvises -- FR-2, FR-6
- [ ] `backend/src/backend/tjeneste.py`, `web.py`, `templates/index.html` -- fjern veien for virus som ikke er klare -- død kode etter 6.2
- [ ] Tester: tolking av 731-fixturen (også rekkefølgen i `id`), forespørsel med `respx` uten typedimensjon, kildehenvisning for 731, at SARS-CoV-2 kan velges, at alle tabellene i `VIRUS` har faste filtre, at meldingen for ugyldig virus nevner nøyaktig valgene i skjemaet, og at siden for SARS-CoV-2 ikke viser FHI-koder. Oppdater testene i Code Map.

**Acceptance Criteria:**
- Given skjemaet, when siden vises, then kan influensa, RSV og SARS-CoV-2 velges, i den rekkefølgen.
- Given et SARS-CoV-2-svar, when siden vises, then står «RESPIaggr SARS-CoV-2 antall og andel» og FHIs kildetekst for 731.
- Given `uv run pytest` og `uv run ruff check`/`ruff format --check`, then er alt grønt uten nett.

## Implementation Notes

- Ikke commit; hovedøkten committer.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `cd backend && uv run pytest` -- expected: alle tester består
- `cd backend && uv run ruff check . && uv run ruff format --check .` -- expected: ingen funn
