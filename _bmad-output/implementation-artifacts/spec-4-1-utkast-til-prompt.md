---
title: 'Story 4.1: Utkast til prompt'
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

**Problem:** KI-forklaringen (FR-20, FR-21) kan ikke bygges før Irene har rettet og godkjent prompten (story 4.2, issue #22), og det finnes ennå ingen prompt. AD-6 sier at prompten ligger i `prompts/forklaring.md` og bare får utvalg, tolkede tall, regelutslag og kildehenvisning.

**Approach:** Skriv et utkast i `backend/src/backend/prompts/forklaring.md` på norsk. Det ber om en forklaring på norsk på høyst 120 ord med enkle ord, sier at bare tall fra dataene skal brukes, at årsaker ikke skal gjettes, at faguttrykk skal forklares, og at usikkerhet skal nevnes når det er regelutslag. Det har plassholderne `{utvalg}`, `{uker}`, `{regelutslag}` og `{kildehenvisning}` og ingen andre. En test sjekker at plassholderne er nøyaktig disse fire. Ikke start på 4.2 eller 4.3.

</frozen-after-approval>

## Implementation Notes

