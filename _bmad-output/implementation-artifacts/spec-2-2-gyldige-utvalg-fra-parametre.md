---
title: 'Story 2.2: Gyldige utvalg fra parametre'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen har ingen kode som gjør query-parametrene `mal`, `virus`, `sesong` og `alder` om til et `Utvalg` (issue #7). Uten den kan en manipulert URL gi feil tall eller et farlig filnavn i cachen (FR-5, AD-4, AD-9).

**Approach:** Legg til `Utvalg.fra_parametre(parametre, gyldige_sesonger)` og egenskapen `Utvalg.nøkkel` i `backend/src/backend/domene.py`, og et nytt unntak `UgyldigUtvalg(ValueError)` med en norsk melding uten FHI-koder. Manglende `alder` gir «Alle aldersgrupper», «Ukjent alder» godtas ikke, og listen over gyldige sesonger er et argument. `nøkkel` gir et filnavn med bare trygge tegn som er likt for like utvalg. Tester i `backend/tests/test_domene.py` dekker gyldige utvalg, hvert ugyldige felt og `../x`.

</frozen-after-approval>

## Implementation Notes

- Endrede filer: `backend/src/backend/domene.py` og `backend/tests/test_domene.py`.
- `parametre` er en `Mapping[str, str]` (for eksempel `request.query_params` i `web`). Verdiene er nøklene i `MALER` (`"1"`), `VIRUS` (`influensa`, `rsv`, `sars-cov-2`) og `ALDERSGRUPPER` (`alle`, `0-4` …), og sesongen skrevet «2025/2026».
- Mellomrom rundt verdiene fjernes ikke. Bare de eksakte nøklene godtas, slik at ingen variant av en verdi kan gi et annet filnavn.
- Manglende eller tom `alder` gir `alle` (et skjema kan sende et tomt felt). Manglende eller tom `mal`, `virus` og `sesong` er feil.
- Alle feil samles i én `UgyldigUtvalg` med én setning per felt, i rekkefølgen mal, virus, sesong, alder. Meldingen nevner aldri verdien brukeren sendte (en manipulert verdi skal ikke vises på siden) og aldri FHI-koder. Den sier hva som kan velges, for eksempel «Velg et virus: influensa, RSV eller SARS-CoV-2.».
- `mal` tolkes bare som et heltall når teksten er en nøkkel i `MALER` skrevet som tall (`"1"`). `"01"`, `"1.0"` og `" 1"` avvises.
- `nøkkel` er `mal<nr>-<virus>-<sesong>-<alder>` med `/` i sesongen byttet til `-` og `+` byttet til `pluss`, for eksempel `mal1-influensa-2025-2026-80pluss`. Til slutt sjekkes at nøkkelen bare har `[a-z0-9-]`, ellers `ValueError`. Dermed kan heller ikke et `Utvalg` laget direkte med en ugyldig verdi gi et farlig filnavn.
