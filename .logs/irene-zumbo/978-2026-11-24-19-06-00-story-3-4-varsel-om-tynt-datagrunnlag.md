# Story 3.4: Varsel om tynt datagrunnlag

## 2026-11-24 kl. 19:06 — Irene Zumbo

### Oppgave
Legge inn Irenes tre gjennomgangskommentarer ordrett på PR #55, #56 og #57. Deretter bygge story 3.4 (#18): et varsel over grafen når minst én kontrollregel slår inn. I samme PR skal Irenes beslutninger fra gjennomgangen av 3.1–3.3 tas med og føres inn i PRD-en. Til slutt kjøre kodegjennomgang og merge.

### Plan
- Kommentarer med `gh pr comment` på #55–#57.
- Branch `story-3.4` fra oppdatert `main`. Bygget med `bmad-build` (oneshot): [spec-3-4-varsel-om-tynt-datagrunnlag.md](../../_bmad-output/implementation-artifacts/spec-3-4-varsel-om-tynt-datagrunnlag.md).
- Små commits: beslutningen om 0 tester, varselet, PRD-en, gjennomgangen.
- `bmad-code-review` med fire lag (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Rette funnene eller begrunne dem.

### Resultat
- Kommentarene er lagt inn på #55, #56 og #57.
- `ba56dcf`: ny `web.andelstekst`. En uke med 0 tester viser «kan ikke regnes ut», og «mangler» brukes bare for skjulte tall. Tabellen og verktøytipset i grafen bruker den. Ny test for at forklaringen under grafen vises også uten usikre uker.
- `d71ee74`: varselet i `index.html` står over grafen. Det har ikon (⚠︎), overskriften «For tynt datagrunnlag», innledningen «Tallene bør tolkes med forsiktighet fordi:» og ett punkt per `Regelutslag`, med ramme i `style.css`. Det vises ikke uten utslag. Ny `tests/test_web_varsel.py` dekker R1 og R5 samtidig, R1 og R5 hver for seg fra lagrede tall, sist lagrede tall og utvalg uten utslag.
- `d284760`: PRD FR-9, FR-10 og FR-11 er oppdatert med beslutningene, merket «Endret 24. november 2026: Irenes beslutning». `epic-3-context.md` følger med, og de to spørsmålene fra 3.2 og 3.3 i `deferred-work.md` er markert som løst.
- `a3e7282`: rettelser etter gjennomgangen. PRD FR-9 sa feil om tabellen. FR-10 sier nå at forklaringen ikke vises uten graf. Ikonet vises i tekstform, det er lagt til en test for rekkefølgen melding → varsel, og en utdatert setning i epic-konteksten er fjernet. Ingen alvorlige funn. Triage-loggen står i specen. Sprint-status for 3.4 er done.
- `uv run pytest`: 588 bestått. `ruff check` og `ruff format --check` er grønne.

### Åpne punkter
- Story 3.6: varselet må få lenken til begrepsforklaringen «for tynt datagrunnlag» (FR-19), med en test (se deferred-work.md).
- Irene: vurdere om overskriften «For tynt datagrunnlag» passer når bare R5 slår inn, siden R5 gjelder sammenlignbarhet. Kan tas med i brukertestingen (se deferred-work.md).
