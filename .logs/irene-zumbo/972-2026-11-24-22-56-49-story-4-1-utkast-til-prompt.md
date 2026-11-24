# Story 4.1: utkast til prompt

## 2026-11-24 kl. 22:56 — Irene Zumbo

### Oppgave
Story 4.1 (#22): skrive et utkast til prompten for KI-forklaringen i `prompts/forklaring.md` etter akseptansekriteriene, med bmad-build og små commits, slik at Irene kan rette og godkjenne den i story 4.2. 4.2 og 4.3 ble ikke startet.

### Plan
- Branch `story-4.1` fra oppdatert main (etter at PR #63 med lenkefargen var merget, se [lenkefarge](973-2026-11-24-22-54-01-lenkefarge.md)).
- bmad-build, enkel rute: epic 4-konteksten kompilert, spec [spec-4-1-utkast-til-prompt.md](../../_bmad-output/implementation-artifacts/spec-4-1-utkast-til-prompt.md).
- Kort gjennomgang mot akseptansekriteriene i stedet for Blind Hunter-underagent.

### Resultat
- `d1d15fb` `epic-4-context.md`, spec, og sprint-status satt til in-progress for 4.1 og epic 4.
- `5ffd80c` `backend/src/backend/prompts/forklaring.md`: prompten ber om norsk bokmål, høyst 120 ord og enkle ord. Reglene: bare tall fra dataene, ingen gjetting på årsaker, faguttrykk forklares, og usikkerheten og årsaken til den nevnes ved regelutslag. Plassholderne er bare `{utvalg}`, `{uker}`, `{regelutslag}` og `{kildehenvisning}`.
- `c31e92c` `backend/tests/test_prompt.py`: tester at de fire plassholderne finnes, én gang hver, at prompten kan fylles ut med `str.format`, og at «norsk» og «høyst 120 ord» står i teksten.
- `c195717` Specen er ferdig, og 4.1 står som done i sprint-status.
- pytest: 642 passed. ruff check og format: OK. Prompten kommer med i wheelen (`uv build`).

### Åpne punkter
- Story 4.2: Irene retter og godkjenner prompten, også de to ekstra reglene (tester og ikke personer, kildehenvisningen trenger ikke gjentas).
- Story 4.3: avgjøre hvordan `{uker}` formateres (prosent med komma, «skjult»/«mangler»), så modellen kan sitere tallene riktig.
