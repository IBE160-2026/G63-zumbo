---
title: 'Story 2.1: Domenemodellen'
type: 'feature'
created: '2026-11-23'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det finnes ingen felles dataklasser eller faste lister ennå (issue #6). Uten `domene.py` vil fhi-tolking, kontrollregler, web og KI-prompt lage hver sin variant av «uke», «skjult verdi», «aldersgruppe» og kildehenvisning (AD-2).

**Approach:** Skriv `backend/src/backend/domene.py` med de frosne dataklassene `Utvalg`, `Uke`, `Dataserie`, `Regelutslag` og `Kildehenvisning`, faste lister for virus → tabell (724/729/731), de sju aldersgruppevalgene og mal 1, og funksjonen `kildehenvisning(tabell, hentet)` med FHIs kildetekster fra addendumet. `Uke.usikker` (færre enn 30 tester eller skjult antall tester) og `Uke.manglende` (tester eller positive er `None`) regnes ut i `Uke`, og `Uke.andel` er `None` for manglende uker, aldri 0. Modulen importerer bare standardbiblioteket (AD-1). Tester i `backend/tests/test_domene.py` dekker 29 og 30 tester, skjulte verdier, kildehenvisningen for 724 og at ingen skallmoduler importeres.

</frozen-after-approval>

## Implementation Notes

