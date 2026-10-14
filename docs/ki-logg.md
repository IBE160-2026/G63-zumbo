# KI-logg

Her logger jeg de viktigste gangene jeg har brukt KI i prosjektet: hva jeg ba om, hva KI-en svarte, hva jeg gjorde med svaret, og hvilken commit det førte til. Nyeste oppføring står nederst.

## Mal

Kopier denne for hver ny oppføring:

```markdown
### ÅÅÅÅ-MM-DD – kort tittel
- **Verktøy:** Claude (chat) / Claude Code
- **Type:** beslutning / rettet feil / avvist forslag / planlegging
- **Story:** hvilken story eller hvilket krav (– hvis ingen ennå)
- **Prompt:** det jeg skrev
- **Svar (kort):** hva KI-en foreslo eller lagde, 1–2 setninger
- **Hva jeg gjorde:** brukte / endret / forkastet, og hvorfor
- **Commit:** hash fra `git log --oneline -1`
```

## Logg

### 2026-10-06 – Tolke tilbakemeldingen på product brief
- **Verktøy:** Claude (chat)
- **Type:** planlegging
- **Story:** -
- **Prompt:** Limte inn faglærerens tilbakemelding (`docs/tilbakemelding-product-brief.md`) og ba om en enklere forklaring av hva som mangler.
- **Svar (kort):** Briefen beskriver både fritekst og maler og må bestemme seg for malbasert v1. I tillegg trengs en fast regel for «for tynt datagrunnlag», et testsett med 10 spørsmål med fasit, én hovedbruker, sletting av duplikatbriefen, og oppsett av BMAD med PRD.
- **Hva jeg gjorde:** _noterte forandringene jeg må gjøre og begynte å endre product brief_
- **Commit:** – (ingen endring ennå)

### 2026-10-14 – Sjekkliste fra sensorveiledningen
- **Verktøy:** Claude (chat)
- **Prompt:** Lastet opp sensorveiledningen for del 1 og ba om en sjekkliste jeg kan legge i repoet og krysse av underveis.
- **Svar (kort):** Lagde `docs/sjekkliste.md` med punkter fra både tilbakemeldingen og sensorveiledningen, sortert i den rekkefølgen jeg bør jobbe.
- **Hva jeg gjorde:** La sjekklisten inn i repoet. 
- **Commit:** `1bd7ecc`
