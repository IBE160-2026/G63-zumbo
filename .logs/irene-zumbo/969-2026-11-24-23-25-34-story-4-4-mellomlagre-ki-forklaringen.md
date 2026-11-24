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

## 2026-11-24 kl. 23:42 — Irene Zumbo

### Oppgave
Irenes beslutninger før merge av PR #67: en regel i prompten om at KI-en ikke skal nevne når tallene ble hentet, og et versjonsnummer for ukeformatet i nøkkelen. Så kommentar på PR #67, merge og oppdatert main.

### Plan
- Endre `prompts/forklaring.md` og `ki.nøkkel` på `story-4.4`, med tester. Kjøre pytest og ruff og pushe til ibe.
- Kommentere ordrett på PR #67 og merge med `gh pr merge 67 --merge --delete-branch`.

### Resultat
- `72a3488` Prompten har regelen «Ikke nevn når tallene ble hentet. Det står ved siden av forklaringen.» `ki.UKEFORMAT = 1` er med i nøkkelen, så et nytt ukeformat gir ny forklaring når tallet økes. Nye tester i `test_ki.py` og `test_prompt.py`. README og deferred-work.md er oppdatert. pytest: 753 passed. ruff: OK.
- Begge åpne punktene fra 4.4 er lukket i issues.md.
- Kommentaren står på PR #67, og PR-en er merget (`a5668a6`). Branchen `story-4.4` er slettet, og main er hentet.

### Åpne punkter
Ingen.
