---
title: 'Story 4.1: Utkast til prompt'
type: 'feature'
created: '2026-11-24'
status: 'done'
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

- Prompten ligger i `backend/src/backend/prompts/forklaring.md`, slik arkitekturen viser filstrukturen (under pakken, ved siden av `templates/`). Fila kommer med i wheelen (sjekket med `uv build --wheel`).
- Plassholderne er `{utvalg}`, `{uker}`, `{regelutslag}` og `{kildehenvisning}`, slik at story 4.3 kan bruke `str.format`. Derfor står det ingen andre krøllparenteser i teksten, og testen sjekker at utfylling med `format` virker.
- Utkastet har to regler utover akseptansekriteriene, som Irene kan beholde eller stryke i 4.2: tallene teller tester, ikke personer (som i begrepsforklaringen), og kildehenvisningen trenger ikke gjentas fordi den vises ved siden av.
- `backend/tests/test_prompt.py`: nøyaktig de fire plassholderne, én gang hver; utfylling med `format`; «norsk» og «høyst 120 ord» står i teksten.
- pytest: 642 passed. ruff check og ruff format: OK.

## Review Triage Log

- Kort gjennomgang mot akseptansekriteriene i #22 (etter brukerens ønske i stedet for Blind Hunter-underagent): norsk, høyst 120 ord og enkle ord – OK; bare tall fra dataene, ingen gjetting på årsaker, faguttrykk forklares, usikkerhet og hvorfor ved regelutslag – OK; bare de fire plassholderne – OK; test – OK.
- low (ikke rettet, hører til 4.3): hvordan `{uker}` formateres (prosent med komma, «skjult»/«mangler») avgjør om modellen kan sitere tallene riktig. Avgjøres når `ki.py` bygges.

