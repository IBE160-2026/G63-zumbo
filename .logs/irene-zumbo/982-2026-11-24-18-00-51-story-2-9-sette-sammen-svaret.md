# Story 2.9: sette sammen svaret for et utvalg

## 2026-11-24 kl. 18:00 — Irene Zumbo

### Oppgave
Bygge story 2.9 (issue #14) på branchen `story-2.9` med `bmad-build` og små commits. Ta med de åpne punktene fra 2.3 (FHIs ukeliste skal vinne over reservelisten i `tjeneste.sesonger`) og 2.5 (RSV og SARS-CoV-2 skal gi en norsk melding i stedet for å krasje). Kjøre pytest, ruff og `bmad-code-review`, sette 2.9 og epic 2 til done, pushe til ibe, lage PR med «Closes #14» og merge med `gh pr merge --merge --delete-branch`.

### Plan
- `bmad-build`, enkel rute (oneshot) som 2.7–2.8: [spec-2-9](../../_bmad-output/implementation-artifacts/spec-2-9-sette-sammen-svaret-for-et-utvalg.md).
- Ny modul `tjeneste.py` med klassen `Tjeneste(innstillinger, klient=None)`, metodene `svar(utvalg, nå)` og `sesonger(nå)`, og dataklassen `Resultat`.
- `bmad-code-review` med fire lag på hele branchen, rette funnene, så PR og merge.

### Resultat
- `backend/src/backend/tjeneste.py`: ferske lagrede tall brukes uten kall, ellers hentes og lagres nye. FHI nede gir sist lagrede tall (`sist_lagrede=True` og melding) eller en melding uten tall. Kontrollreglene kjøres alltid. `sesonger` bruker FHIs liste (fersk, ny eller gammel lagret når FHI er nede) og reserven bare uten liste. RSV/SARS-CoV-2 og sesonger uten publiserte uker gir faste norske meldinger før noe kall. Én delt jobb per utvalg og for dimensjonslisten, så samtidige kall gir ett kall til FHI, også når FHI er nede.
- `fhi.Klient` (typenavn for `httpx.Client`), så bare `fhi.py` importerer `httpx`. README-avsnittet om mellomlageret er oppdatert.
- `backend/tests/test_tjeneste.py`: 29 tester med `respx` og `tmp_path`. Totalt 486 tester, og ruff består.
- Kodegjennomgang: ingen alvorlige funn. Retta bl.a. at loggen kunne skrive «None» i stedet for feilen, at samtidige sesongkall kunne gi to kall til FHI, og at samtidighetstesten ikke viste at det andre kallet ventet (testen feiler nå når delingen fjernes). Avvist bl.a. å prøve datakallet når bare dimensjonslisten feiler (det kunne doblet ventetiden til 20 s). Se Review Triage Log i spec-2-9.
- Sprint-status: 2.9 og epic 2 er `done`. `deferred-work.md`: punktet fra 2.5 er løst.
- Commits: c5e40ac (spec), d2f1891 (`fhi.Klient`), a1f6cb3 (tjeneste), 77b19bd (tester), bc4c2f2 (README), 40d7bbb og d88cf23 (rettelser), 9ebd864 (triage og status). PR #54 (Closes #14).
- Lukket i `issues.md`: punktene fra 2.3 (sesonglisten) og 2.5 (RSV/SARS-CoV-2 og sesonger uten publiserte uker).

### Åpne punkter
- Epic 3: `web` må lage `nå` med tidssone, bruke `Resultat.serie is None` (ikke `melding`) for å se om det finnes tall, og vise «Sist lagrede tall, hentet …» fra `kilde.hentet` når `sist_lagrede` er sann.
- Story 4.6: `tjeneste` har ingen tvungen henting uten mellomlager ennå (`POST /hent-nyeste`).
