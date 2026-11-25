# Kommentarsjekk, tidslinje, testoversikt og mappestruktur

## 2026-11-26 kl. 00:36 — Irene Zumbo

### Oppgave
Seks punkter uten nye stories og uten merge: en tabell over mergede PR-er og om Irene har kommentert etter merge, en privat tidslinje fra 6.11 som grunnlag for KI-loggen (ikke i git), en testoversikt med én setning per test, et tomt fasitskjema for 10 utvalg, to PR-er (dokumentene og en oppdatert mappestruktur i arkitekturen) og en oppsummering med forklaring av gh-kommandoene.

### Plan
- Hente mergede PR-er med `gh pr list` og Irenes kommentarer, kommentarer på kodelinjer og reviews per PR med `gh api`, og sammenligne med `mergedAt`.
- Lage tidslinjen fra PR-er, issues og commits på `main` (norsk tid) og legge `notater/` i `.gitignore`.
- Lese alle 529 testfunksjonene (navn og assert-linjer via `ast`) og skrive én setning per test, med merking av tester som ikke kan feile.
- Oppdatere §6 i arkitekturen etter filene i git, uten å endre AD-3.

### Resultat
- PR #82 (branch `dokumentasjon-sjekker`, commit 8ee1672): `docs/kommentar-sjekk.md` (33 mergede PR-er, alle merget av `irzum8624`, 19 merket MANGLER), `docs/testoversikt.md` (529 tester; 2 merket ⚠️ fordi de bare tester hjelpefunksjoner i testfila, 28 merket ◦ fordi de bare sjekker fixturer, README, testoppsett eller faste verdier), `fasit-inn/skjema.md` og `notater/` i `.gitignore`. `uv run pytest`: 905 bestått.
- PR #83 (branch `arkitektur-mappestruktur`): §6 i `architecture.md` stemmer med koden. AD-3 er ikke endret. PR-teksten nevner konflikten med #79.
- `notater/tidslinje.md` ligger bare lokalt og er ikke committet. Siden `.gitignore`-endringen bare ligger i PR #82, vises `notater/` som usporet på `main` til PR-en er merget.
- Ingen PR er merget.

### Åpne punkter
- Irene: se gjennom PR #82 og #83 (ikke merget).
- Fasitskjemaet har ikke egne kolonner for sesong og aldersgruppe; Irene avgjør om de trengs.
- Testene merket ⚠️ og ◦ i testoversikten: Irene avgjør om noen skal skrives om eller fjernes.
