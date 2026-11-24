---
title: 'Story 4.3: KI-forklaring med tre utfall'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det finnes en godkjent prompt (story 4.2, #23), men ingen kode som fyller den ut og kaller Claude. Story 4.3 (#24) krever at `ki.forklar(...)` alltid gir `Forklaring(tekst)`, `ManglerNøkkel` eller `KiFeil` og aldri kaster videre (FR-20, FR-22, NFR-1, AD-6).

**Approach:** Lag `backend/src/backend/ki.py`, den eneste modulen som importerer `anthropic`. `forklar` fyller ut `prompts/forklaring.md` med utvalget, ukene, regelutslagene og kildehenvisningen. Uten nøkkel kalles ikke Claude. Klienten lages med eksplisitt `api_key=` og modellen fra `Innstillinger` (`claude-haiku-5-5`, kan overstyres med `ANTHROPIC_MODEL`). Alle feil blir `KiFeil`. Testene bruker en falsk klient og tekst fra `tests/fixtures/ki/` og kaller aldri Claude.

Beslutninger fra brukeren (Irene):
- Ukene skrives inn i `{uker}` slik de står i tabellen på siden, for eksempel «uke 50: 1 210 tester, 252 positive, 20,8 %», med «skjult», «mangler» og «kan ikke regnes ut» der tabellen viser det.
- `config.les_innstillinger()` skal behandle tom `ANTHROPIC_MODEL` eller `ANTHROPIC_API_KEY` som ikke satt.

</frozen-after-approval>

## Implementation Notes
