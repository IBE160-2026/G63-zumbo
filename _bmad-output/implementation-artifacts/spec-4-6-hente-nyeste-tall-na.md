---
title: 'Story 4.6: Hente nyeste tall nå'
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

**Problem:** Tallene fornyes først når de er 24 timer gamle (FR-7), så brukeren kan ikke se nye tall fra FHI med en gang de publiseres på torsdag. `tjeneste` mangler en henting som hopper over mellomlageret, og siden sier ikke at FHI publiserer nye tall hver torsdag (FR-25, #27).

**Approach:** `Tjeneste.svar` får en tvungen henting som hopper over ferske lagrede tall og dimensjonslisten, og lagrer med nytt hentetidspunkt. Siden får teksten «FHI publiserer nye tall hver torsdag.» og knappen «Hent nyeste tall nå», som sender `POST /hent-nyeste` og får `303` til `GET /` for samme utvalg. `app.js` deaktiverer knappen når skjemaet sendes. Når FHI ikke svarer, vises sist lagrede tall med dato (FR-8). Uendrede tall gir samme nøkkel, så den lagrede KI-forklaringen gjenbrukes (AD-7). Testene kaller aldri FHI eller Claude på ekte.

</frozen-after-approval>

## Implementation Notes
