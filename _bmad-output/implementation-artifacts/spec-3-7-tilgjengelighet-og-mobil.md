---
title: 'Story 3.7: Tilgjengelighet og mobil'
type: 'feature'
created: '2026-11-24'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sara skal kunne bruke siden på mobil og med tastatur (issue #21, NFR-4, NFR-5, NFR-7, NFR-11). Stilen er foreløpig, og siden mangler fokusmarkering, faste farger og skrift.

**Approach:** `static/style.css` gjøres ferdig med Irenes designvalg (24.11.2026):
- Farger fra FHIs palett som CSS-variabler: hovedfarge `#386E84`, varselfarge `#D14641`, bakgrunn `#FFFFFF`, tekst `#222222`. `app.js` leser graffargene herfra.
- Skrift: Fraunces med SOFT 100 og WONK 0 (fet) til overskrifter, Poppins til brødtekst og tabeller. Filene ligger som woff2 i `static/fonts/` med lisensfilene (OFL), og hentes ikke fra Google.
- Linjen «Laget av en student ved Høgskolen i Molde, med tall fra FHI. Dette er ikke en tjeneste fra FHI.» Ingen FHI-logo.
- Under hentetidspunktet: «Tallene for den siste uka kan bli justert når flere prøvesvar kommer inn.»
- Overskriften på varselet beholdes som «For tynt datagrunnlag».
- Nytt krav FR-26 i PRD-en, merket «Lagt til 24. november 2026: Irenes beslutning»: nederst på siden overskriften «Hvorfor ikke bare spørre en chatbot?» og teksten «En chatbot kan finne på tall eller bruke gamle tall, og den sier sjelden hvor tallene kommer fra. Denne appen henter tallene direkte fra Folkehelseinstituttet, viser når de ble hentet, og sier fra når det er for lite data til å konkludere. KI brukes bare til å forklare tallene med enkle ord, aldri til å lage dem.»

Akseptansekriteriene i #21: kontrast minst 4,5:1 for tekst og 3:1 for linjer og symboler i grafen, synlig fokusmarkering på alle valg, knapper og forklaringer, ingen vannrett rulling ved 360 piksler og tabellen ruller i egen boks, en automatisk test som regner ut kontrasten fra variablene i `style.css`, en test for at alle skjemafelt har `<label>`, og en manuell sjekk i gråtoner, med tastatur og ved 360 piksler notert i issuet.

</frozen-after-approval>

## Implementation Notes

- **Farger:** alle farger står som variabler i `:root` i `style.css` og ingen andre steder (testet). Graffargene peker på palettfargene med `var()`. Kontrast mot hvitt: tekst 15,9:1, hovedfarge 5,6:1, varselfarge 4,50:1. Varselfargen brukes bare til ramme og ikon. Overskriften i varselet har tekstfargen. `--skillelinje` (#D0D0D0) er bare pynt (rutenett og tynne linjer) og bærer ingen informasjon.
- **Skrift:** `static/fonts/` har Fraunces (variabel, aksene opsz, wght, SOFT og WONK) og Poppins 400 og 600, tegnsettet «latin» fra Google Fonts, lastet ned én gang. Lisensfilene er OFL 1.1 fra google/fonts. Grafen bruker Poppins, og `app.js` tegner den når skriften er lastet.
- **Tekster:** avsenderlinjen står i `<footer class="avsender">` i `base.html`. Justeringsteksten står rett under kilden og bare når det finnes en kilde. FR-26 står som siste del av innholdet, under begrepsforklaringene.
- **Planer:** FR-26 er lagt i PRD-en (ny §6.8, §9 og §11), i `epics.md` (kravliste, dekning og epic 3) og i `epic-3-context.md`. Arkitekturen er ikke endret: FR-26 er en fast tekst i malen, som arkitekturen allerede tillater.
- **Tester:** `tests/test_stil.py` (ny): kontrast regnet ut fra variablene, farger bare i `:root`, fokusmarkering, smal skjerm, skrift og lisens, `<label>` for alle skjemafelt, avsenderlinjen og ingen `<img>`, justeringsteksten, overskriften i varselet og FR-26. 631 tester består.
- **Manuell sjekk i Chrome uten vindu:** i en ramme på 360 piksler er `scrollWidth` lik `clientWidth` (360). Tabellboksen ruller selv (435 i 328 piksler). Skriftene lastes, og grafen tegnes. I gråtoner skilles varselet med ramme og ikon. Fokusmarkeringen på lenken i varselet er synlig. En ekte gjennomgang med Tab-tasten er ikke gjort og står som åpent punkt for Irene.

## Review Triage Log

Kortere gjennomgang etter Irenes valg: ingen subagenter (Blind Hunter er hoppet over). Jeg sjekket endringene selv mot akseptansekriteriene i #21 og designvalgene.

- AK 1, kontrast: oppfylt og testet.
- AK 2, synlig fokusmarkering: oppfylt for `a`, `button`, `select`, `summary` og tabellboksen (`[tabindex]`). Sett i skjermbilde.
- AK 3, 360 piksler og tabellen i egen boks: oppfylt, målt i Chrome.
- AK 4, CSS-variabler som `app.js` leser, kontrasttest og `<label>`-test: oppfylt.
- AK 5, manuell sjekk notert i issuet: notert som kommentar på #21. Tastatursjekken med ekte Tab gjenstår for Irene.
- **low, avvist:** på 360 piksler kuttes spørsmålet i mallisten («Vis andel positive tester for [virus] i s…»). Det er nettleserens egen nedtrekksliste. Hele teksten vises når listen åpnes, og siden ruller ikke vannrett.
- **low, avvist:** testene for fokus og smal skjerm leser CSS-teksten og kan ikke se den ferdige siden. Uten en nettlesertest er det det beste en automatisk test kan gjøre. Målingen i Chrome er gjort for hånd.
- **low, utsatt (fra før):** ingen automatisk nettlesertest av grafen. Datasettet i sjekken har ingen usikre uker, så åpne sirkler er ikke sett med øynene ennå.
