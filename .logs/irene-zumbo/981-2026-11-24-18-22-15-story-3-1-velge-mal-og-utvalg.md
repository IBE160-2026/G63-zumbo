# Story 3.1: velge mal og utvalg på siden

## 2026-11-24 kl. 18:22 — Irene Zumbo

### Oppgave
Kjøre story 3.1, 3.2 og 3.3 etter hverandre uten å vente på Irene. Dette er 3.1 (issue #15): branchen `story-3.1`, `bmad-build` med små commits, pytest og ruff, `bmad-code-review` med rettelser, status `done`, push til ibe, PR med «Closes #15» og merge. Åpent punkt fra 1.5: oppstartskommandoen i README og endret `test_readme_har_plass_for_oppstart`.

### Plan
- Lage epic 3-konteksten ([epic-3-context](../../_bmad-output/implementation-artifacts/epic-3-context.md)) med en underagent.
- `bmad-build`, enkel rute (oneshot): [spec-3-1](../../_bmad-output/implementation-artifacts/spec-3-1-velge-mal-og-utvalg-pa-siden.md).
- `bmad-code-review` med fire lag på hele branchen, rette funnene, så PR og merge.

### Resultat
- `backend/src/backend/web.py`: `lag_app(les_innstillinger, klient)` og `app = lag_app()`. Innstillingene leses i lifespan (én gang ved oppstart, aldri ved import). `GET /` viser skjemaet: mal 1 som spørsmål, influensa (`tjeneste.KLARE_VIRUS`), sesongene med siste som standard og «Alle aldersgrupper». Ugyldige parametre gir meldingen fra `Utvalg.fra_parametre` uten henting. Et gyldig utvalg kaller `Tjeneste.svar`, men viser foreløpig bare meldingen. Tabellen kommer i 3.2. `nå` lages med `datetime.now(UTC)`.
- Malene `base.html` (`lang="nb"`) og `index.html`, og `static/style.css`.
- `tjeneste`: `KLARE_VIRUS` og `PAUSE_ETTER_FEIL` (60 s uten nytt kall for dimensjonslisten etter at FHI ikke svarte), så én side ikke venter 2 × 10 s.
- README: «Starte appen» med `uv run uvicorn backend.web:app --reload` fra `backend/` og http://127.0.0.1:8000. Testen heter nå `test_readme_har_oppstartskommandoen`.
- Tester: `test_web.py` (nye) og to nye i `test_tjeneste.py`. Totalt 515 tester, og ruff består.
- Kodegjennomgang: ingen alvorlige funn. Rettet: feil valg i skjemaet etter et ugyldig valg, dobbel ventetid når FHI er nede, trimming før valideringen og `fhi`-import i `web`, pluss småting og tester. 2 lave funn er utsatt (meldingstekstene i `domene`, se deferred-work.md) og 7 avvist. Se Review Triage Log i spec-3-1.
- Commits: 726c9c3 (kontekst og spec), 38ba6ba (web), 085d38d (tester), 1364733 (README), 85e62a6 (format), 374a8b4 (pause i tjeneste), 096375c (rettelser), 461c5ce (triage og status). PR #55 (Closes #15).
- Lukket i `issues.md`: punktet fra 1.5 (oppstartskommandoen i README).

### Åpne punkter
- Meldingen for ukjent virus fra `Utvalg.fra_parametre` nevner RSV og SARS-CoV-2, selv om skjemaet bare har influensa. Meldingen for ukjent mal bruker tittelen, ikke spørsmålet. Begge er lave (se deferred-work.md).
