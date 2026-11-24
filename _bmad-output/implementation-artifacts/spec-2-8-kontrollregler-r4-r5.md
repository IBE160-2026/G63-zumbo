---
title: 'Story 2.8: Kontrollregler R4–R5'
type: 'feature'
created: '2026-11-24'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen sier ikke fra når en sesong nettopp har startet eller går over 1. mars 2025 (issue #13). Da kan Sara sammenligne tall som ikke kan sammenlignes (FR-17, FR-18, FR-19).

**Approach:** Legg R4 og R5 til `kontrollregler.vurder` fra story 2.7, som rene funksjoner (AD-1). R4 gir utslag når serien har færre enn 3 uker med data (manglende uker teller ikke). R5 gir utslag når serien har en uke som starter før 1. mars 2025 og en uke som slutter 1. mars 2025 eller senere. Grensetilfellene ligger som konstruerte FHI-svar i `backend/tests/fixtures/konstruert/` og testes i `backend/tests/test_kontrollregler.py`. Ingen regel svekkes.

</frozen-after-approval>

## Implementation Notes

- R4 teller uker der `Uke.manglende` er usann. En tom serie gir R4 (0 uker med data).
- R5 ser på alle uker i serien, også manglende uker, fordi perioden i utvalget går over datoen uansett. En ISO-uke starter mandag og slutter søndag. Uke 9 i 2025 (24. februar–2. mars) starter før og slutter etter 1. mars, så den alene gir utslag. En serie som slutter med uke 8 i 2025 gir ikke utslag. Det kan ikke skje i appen, fordi 2024/2025 er ferdig, men det viser grensen.
- Setningene: R4 «Utvalget har bare 2 uker med tall. Det trengs minst 3 for å se en retning.» (entall og «ingen» håndteres). R5 «Perioden går over 1. mars 2025. Fra den datoen er alle norske laboratorier med i tallene, så tall før og etter kan ikke sammenlignes direkte.»
- Endret: `backend/src/backend/kontrollregler.py` (R4, R5, `MINSTE_ANTALL_UKER`, `ALLE_LABORATORIER_FRA`) og `backend/tests/test_kontrollregler.py`. Nye fixturer: `724-r4-2-uker-med-data.json`, `724-r4-3-uker-med-data.json` og `724-r5-2024-2025.json`, beskrevet i README-en i `konstruert/`.
- For 2025/2026 brukes den ekte fixturen fra story 1.3. Den gir ingen varsel i det hele tatt, som PRD kapittel 6.5 sier om ekte tall for alle aldre.

## Review Triage Log

Se specen for story 2.7, der funnene fra den felles gjennomgangen står. **low, rettet:** grensen for R5 (uke 8/9 i 2025) var bare testet med data laget i testkoden. Den ligger nå også i `724-r5-til-uke-8-2025.json` og `724-r5-til-uke-9-2025.json`, slik AK-en krever.
