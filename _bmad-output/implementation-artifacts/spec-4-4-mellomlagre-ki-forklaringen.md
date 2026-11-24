---
title: 'Story 4.4: Mellomlagre KI-forklaringen'
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

**Problem:** `ki.forklar` (story 4.3) kaller Claude hver gang, så samme tall kan gi ny tekst ved hver sidevisning. Story 4.4 (#25) krever at forklaringen lagres og gjenbrukes når tallene er de samme (FR-25, AD-7).

**Approach:** Nøkkelen er SHA-256 av kanonisk JSON (`sort_keys=True`) med utvalget, de tolkede ukene, regelutslagene, innholdet i promptfila og modellnavnet, men ikke hentetidspunktet. `ki.nøkkel(...)` regner den ut, `mellomlager` leser og skriver `ki/<nøkkel>.json` med `laget`, `modell` og `tekst`, og `Tjeneste.forklaring(...)` bruker den lagrede teksten når den finnes. Ellers kalles `ki.forklar`, og bare `Forklaring` lagres, ikke `ManglerNøkkel` eller `KiFeil`. Testene bruker en falsk klient og kaller aldri Claude.

</frozen-after-approval>

## Implementation Notes
