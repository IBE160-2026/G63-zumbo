# Story 3.7: tilgjengelighet og mobil

## 2026-11-24 kl. 20:12 — Irene Zumbo

### Oppgave
Bygge story 3.7 (#21) med Irenes designvalg: FHI-farger som CSS-variabler, Fraunces og Poppins lagret lokalt med OFL-lisens, avsenderlinjen uten FHI-logo, justeringsteksten under hentetidspunktet, varseloverskriften uendret og det nye kravet FR-26 «Hvorfor ikke bare spørre en chatbot?». Kortere gjennomgang mot akseptansekriteriene (Irenes valg).

### Plan
- `bmad-build`, oneshot: [spec-3-7](../../_bmad-output/implementation-artifacts/spec-3-7-tilgjengelighet-og-mobil.md).
- Skrive `style.css` ferdig, legge tekstene i malene, FR-26 i PRD-en og epics, og tester for kontrast, fokus, `<label>`, skrift og tekster. Manuell sjekk i Chrome uten vindu, notert på #21.

### Resultat
- Commits `9a5a842`, `9be2056`, `837b0d1`, `e65e247`, `5c31da6`, `8549639`, `ed45493` på branchen `story-3.7`.
- Kontrast mot hvitt: tekst 15,9:1, hovedfarge 5,6:1, varselfarge 4,50:1 (bare ramme og ikon). Alle farger står bare i `:root`.
- Skriftene ligger i `backend/src/backend/static/fonts/` (Fraunces variabel med SOFT og WONK, Poppins 400 og 600, tegnsettet latin) med OFL-filene.
- FR-26 er lagt i PRD-en (§6.8, §9, §11), `epics.md` og `epic-3-context.md`, merket «Lagt til 24. november 2026: Irenes beslutning». Arkitekturen er ikke endret.
- 631 tester består, ruff består. Sjekket i Chrome: ingen vannrett rulling ved 360 piksler, tabellen ruller i egen boks, gråtoner leselige, fokusmarkering synlig. Notert på #21.
- Sprint-status: 3.7 og epic 3 er done. Lukket i issues.md: spørsmålet om varseloverskriften (Irene: den beholdes).

### Åpne punkter
- Irene: gå gjennom siden med ekte Tab, Enter og mellomrom (NFR-5), og noter det på #21.
