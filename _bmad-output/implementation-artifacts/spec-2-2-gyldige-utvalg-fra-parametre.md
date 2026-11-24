---
title: 'Story 2.2: Gyldige utvalg fra parametre'
type: 'feature'
created: '2026-11-24'
status: 'done'
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

- Endrede filer: `backend/src/backend/domene.py` og `backend/tests/test_domene.py`. Testene lå først i en egen fil, men ble flyttet etter gjennomgangen, slik Intent sier.
- `parametre` er en `Mapping[str, str]` (for eksempel `request.query_params` i `web`). Verdiene er nøklene i `MALER` (`"1"`), `VIRUS` (`influensa`, `rsv`, `sars-cov-2`) og `ALDERSGRUPPER` (`alle`, `0-4` …), og sesongen skrevet «2025/2026».
- Mellomrom rundt verdiene fjernes ikke. Bare de eksakte nøklene godtas, slik at ingen variant av en verdi kan gi et annet filnavn.
- Manglende eller tom `alder` gir `alle` (et skjema kan sende et tomt felt). Manglende eller tom `mal`, `virus` og `sesong` er feil.
- Alle feil samles i én `UgyldigUtvalg` med én setning per felt, i rekkefølgen mal, virus, sesong, alder. Meldingen nevner aldri verdien brukeren sendte (en manipulert verdi skal ikke vises på siden) og aldri FHI-koder. Den sier hva som kan velges, for eksempel «Velg et virus: Influensa, RSV eller SARS-CoV-2.» (navnene fra `VIRUS`).
- `mal` tolkes bare som et heltall når teksten er en nøkkel i `MALER` skrevet som tall (`"1"`). `"01"`, `"1.0"` og `" 1"` avvises.
- `nøkkel` er `mal<nr>-<virus>-<sesong>-<alder>` med `/` i sesongen byttet til `-` og `+` byttet til `pluss`, for eksempel `mal1-influensa-2025-2026-80pluss`. Til slutt sjekkes at nøkkelen bare har `[a-z0-9-]`, ellers `ValueError`. Dermed kan heller ikke et `Utvalg` laget direkte med en ugyldig verdi gi et farlig filnavn.
- `nøkkel` sjekker også at `mal`, `virus` og `aldersgruppe` finnes i listene og at sesongen er skrevet `ÅÅÅÅ/ÅÅÅÅ`. Da er nøkkelen ulik for ulike utvalg (for eksempel kan ikke sesongen `2025-2026` gi samme filnavn som `2025/2026`).
- Overraskelse: «Alle» er både FHIs kode og en del av den norske etiketten «Alle aldersgrupper». Testen for FHI-koder i meldingen sjekker derfor bare koder som ikke er vanlige ord.
- Etter gjennomgangen: `fra_parametre` hopper over sesonger i `gyldige_sesonger` som ikke er skrevet `ÅÅÅÅ/ÅÅÅÅ` med andre år = første år + 1, og fjerner dubletter. Da kan ikke et godkjent utvalg få en `nøkkel` som feiler. Én tekst i stedet for en liste gir `TypeError`.

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Ingen brudd på akseptansekriteriene og ingenting som krever endring i PRD eller arkitektur.

- **medium, rettet:** `fra_parametre` sjekket ikke formatet på sesongene. En sesong som `2025-2026` i listen fra story 2.3/2.4 ville gitt et godkjent utvalg der `nøkkel` kaster `ValueError`. Gjelder også tom tekst i listen. Sesongene filtreres nå med samme sjekk som `nøkkel` bruker.
- **medium, rettet:** meldingene for mal og aldersgruppe sa ikke hva som kan velges (FR-5). De lister nå malene og de sju aldersgruppene.
- **low, rettet:** dubletter i sesonglisten ble vist to ganger i meldingen.
- **low, rettet:** docstringen for `Utvalg` sa at `fra_parametre` er det eneste stedet verdiene sjekkes, men `nøkkel` sjekker dem også. Skrevet om.
- **low, rettet:** testene lå i `test_utvalg.py`, mens den frosne Intent sier `test_domene.py`. Flyttet.
- **low, rettet:** ingen test låste rekkefølgen når alder og andre felt er feil samtidig (Verification Gap viste at testene besto med feil rekkefølge). Ny test sammenligner hele meldingen.
- **low, rettet:** testene manglet `mal="1.0"`, `alder=" "` og en tydelig test av at verdien ikke gjentas. Lagt til, med `../ZZQ<script>`.
- **low, rettet:** `nøkkel` godtok sesonger som ikke finnes, som `2026/2025`.
- **low, rettet:** spec-eksempelet skrev «influensa» med liten forbokstav. Koden bruker navnene fra `VIRUS`. Notatet er rettet.
- **low, rettet:** testen for FHI-koder sjekket bare tre meldinger. Den sjekker nå meldingen for hvert felt.
- **avvist (low):** en `str` som `gyldige_sesonger` ble delt opp i tegn. Rettet likevel med en `TypeError`, fordi rettingen er én linje.
- **false:** verdier som ikke er tekst (en liste i `parametre`) gir `TypeError`. `parametre` er `request.query_params`, der `get` alltid gir tekst eller `None`. Ingen kode kan sende noe annet.
- **false:** et `Utvalg` laget direkte med en liste som virus gir `TypeError` i `nøkkel`. Det feiler høyt, og ingen kode lager slike utvalg.
- **avvist (low):** `80+ år` er ikke med i listen over FHI-koder i testen. Det er også den norske etiketten som skal vises, så den kan ikke forbys i meldingen.
- **avvist (low):** ved gjentatte parametre (`?virus=rsv&virus=influensa`) tar `query_params.get` den siste. Begge er gyldige valg, og hører hjemme i `web` (epic 3) hvis det skal håndteres.
