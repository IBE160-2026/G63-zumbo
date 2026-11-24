# Story 4.4: Mellomlagre KI-forklaringen

## 2026-11-24 kl. 23:25 — Irene Zumbo

### Oppgave
Story 4.4 (#25): lagre KI-forklaringen og gjenbruke den når tallene er de samme (AD-7), på branchen `story-4.4`. Etterpå bmad-code-review, sprint-status til done, push til ibe og PR med «Closes #25» uten merge.

### Plan
- Fortsetter [story-4-3](970-2026-11-24-23-13-40-story-4-3-ki-forklaring.md). PR #66 ble merget først.
- bmad-build (oneshot) med spec i `_bmad-output/implementation-artifacts/spec-4-4-mellomlagre-ki-forklaringen.md`.
- bmad-code-review med fire lag. Funnene er rettet eller begrunnet under «Review Triage Log» i spec-en.

### Resultat
- `1422b10` `ki.nøkkel` lager nøkkelen: SHA-256 av utvalg, uker, regelutslag, prompt og modell, uten hentetidspunktet.
- `3f1694d` `mellomlager` leser og skriver `ki/<nøkkel>.json` med `laget`, `modell` og `tekst`.
- `84fc6fc` `Tjeneste.forklaring` bruker en lagret forklaring eller kaller Claude, og lagrer bare `Forklaring`. Samtidige kall deler ett kall til Claude.
- `3989878` README nevner `ki/`.
- `4a492cc` Rettelser fra gjennomgangen: `forklaring` kaster aldri, bruk av lagret forklaring logges, og tom modell avvises. `ny_klient=None` betyr `anthropic.Anthropic`.
- 4.4 står som done i sprint-status. pytest: 751 passed. ruff: OK. PR #67 er ikke merget.

### Åpne punkter
- Irene: prompten har «Hentet <tidspunkt>», men nøkkelen har det ikke. Siterer KI-en tidspunktet, kan en gjenbrukt forklaring vise et eldre tidspunkt enn kilden ved siden av. Valgene er å ta tidspunktet ut av prompten, eller å be KI-en ikke nevne det.
- Nøkkelen tar ikke med `effort`, `max_tokens` eller formateringen av ukene. En endring i `ki.py` gir derfor ikke ny forklaring før `.cache/ki/` slettes (se deferred-work.md).
