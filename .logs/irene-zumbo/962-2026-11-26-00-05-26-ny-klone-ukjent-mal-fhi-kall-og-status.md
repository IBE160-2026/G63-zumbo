# Ny klone, ukjent mal, færre FHI-kall og status mot sensorveiledningen

## 2026-11-26 kl. 00:05 — Irene Zumbo

### Oppgave
Fire ting uten å vente på Irene, og ingenting skal merges: (A) følge README-en fra en ny klone som sensor og rette den, (B) rette meldingen for ukjent mal og sjekke punktet om «[virus]»/«[sesong]», (C) redusere antall FHI-kall med tomt mellomlager uten å endre det brukeren ser, med `bmad-code-review`, (D) statusrapport mot sensorveiledningen.

### Plan
- A: klone til scratchpad, følge README ordrett, notere uklarheter, rette på egen branch (Refs #37).
- B: meldingen viser malens spørsmål med gyldige valg satt inn.
- C: datakallet ber om hele sesongen (FHI sender bare publiserte uker, sjekket live), dimensjonslisten bare for 724, og ved 400 sjekkes tabellens egen liste.
- D: rapport per kriterium fra `tilbakemelding-product-brief.md` §2 og `sjekkliste.md`, i en egen arbeidskopi mens gjennomgangen av C kjørte.

### Resultat
- **A, PR #77** (`readme-fra-ny-klone`): alle steg virket fra en ny klone (uv sync, 905 tester, ruff, appen, forklaring uten nøkkel, vis_forklaring). Rettet: hva appen gjør, data og kilde, begrensninger, installering av uv, forventet utdata, port og nett, hvor nøkkelen hentes, Windows-kommando, dokumentlenker og struktur.
- **B, PR #78** (`melding-ukjent-mal`): `domene._spørsmål` lager «Velg en mal: «Vis andel positive tester for influensa i sesongen 2025/2026».», med «viruset du velger»/«du velger» for ugyldige verdier. 910 tester. Punktet i deferred-work og issues.md er lukket. Punktet om «[virus]»/«[sesong]» var alt lukket, og er sjekket på nytt: teksten fins ikke i koden.
- **C, PR #79** (`faerre-fhi-kall`, e571f06 + ee99b4e): forsiden går fra 6 til 4 kall, RSV/SARS-CoV-2 fra 3 til 2 (testet, og sjekket mot ekte FHI). `fhi.ForespørselAvvist` for 400. `bmad-code-review` med tre lag (ingen spec): 4 retninger rettet, 2 utsatt til deferred-work, 5 avvist. 915 tester. AD-3 er ikke endret, forslaget står i PR-en.
- **D, PR #80** (`status-mot-sensorveiledning`): `docs/status-mot-sensorveiledning.md`. Sensorveiledningen selv ligger ikke i repoet. Sjekklisten er ikke endret.
- CI er grønn på #77–#80. #76 har ingen sjekk, fordi den ble laget før workflowen fantes.

### Åpne punkter
- Hvis PR #79 merges: oppdatere AD-3 og epics.md.
- Sjekke FHI-oppførselen (hele sesongen gir bare publiserte uker, 400 når ingen) på nytt mot ekte FHI.
- KI-loggen har bare to oppføringer (kriterium 1).
- Arkitektur §6 er utdatert.
- Story 7.6: automatisk test av README-kommandoene, og notat i #37.
