---
title: 'Story 4.4: Mellomlagre KI-forklaringen'
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

**Problem:** `ki.forklar` (story 4.3) kaller Claude hver gang, så samme tall kan gi ny tekst ved hver sidevisning. Story 4.4 (#25) krever at forklaringen lagres og gjenbrukes når tallene er de samme (FR-25, AD-7).

**Approach:** Nøkkelen er SHA-256 av kanonisk JSON (`sort_keys=True`) med utvalget, de tolkede ukene, regelutslagene, innholdet i promptfila og modellnavnet, men ikke hentetidspunktet. `ki.nøkkel(...)` regner den ut, `mellomlager` leser og skriver `ki/<nøkkel>.json` med `laget`, `modell` og `tekst`, og `Tjeneste.forklaring(...)` bruker den lagrede teksten når den finnes. Ellers kalles `ki.forklar`, og bare `Forklaring` lagres, ikke `ManglerNøkkel` eller `KiFeil`. Testene bruker en falsk klient og kaller aldri Claude.

</frozen-after-approval>

## Implementation Notes

- **`ki.nøkkel(serie, regelutslag, modell)`:** SHA-256 av kanonisk JSON (`sort_keys=True`, kompakt, `ensure_ascii=False`) med `utvalg` (mal, virus, sesong, aldersgruppe), `uker` (`[år, uke, tester, positive]`; andelen regnes ut fra disse), `regelutslag` (`[regel, tekst]`), `prompt` (innholdet i `forklaring.md`) og `modell`. Hentetidspunktet er ikke med.
- **`mellomlager`:** `forklaringsfil`, `lagre_forklaring` og `les_forklaring` for `ki/<nøkkel>.json` med `{"laget", "modell", "tekst"}`. Nøkkelen må være 64 små heksadesimale tegn. Skrivingen går via den samme atomiske skrivingen som for FHI-svar. En fil med feil form, ekstra felt, tom tekst eller tom modell regnes som ikke funnet.
- **`Tjeneste.forklaring(resultat, nå)`:**
  - Uten nøkkel gir den `ManglerNøkkel` uten å se i cachen. FR-22 sier at det skal stå at forklaringen krever en KI-nøkkel.
  - Uten tall gir den `KiFeil` uten å kalle Claude.
  - Ellers brukes en lagret forklaring, eller så kalles `ki.forklar`. Bare `Forklaring` lagres, med `nå` som `laget`.
  - Samtidige kall for samme nøkkel deler ett kall til Claude (`_én_gang`).
  - Feil ved lagring eller ved lesing av prompten logges, og metoden kaster aldri.
  - `Tjeneste` har fått `ny_ki_klient` for testene.
- **`ki.forklar`:** `ny_klient` er nå `None` som standard, og det betyr `anthropic.Anthropic`.
- **README:** forklaringer lagres i `ki/` i mellomlageret.
- **Tester:** `test_tjeneste_forklaring.py` (gjenbruk, endrede tall, regelutslag, prompt og modell, feil lagres ikke, uten nøkkel, uten tall, samtidige kall), `test_mellomlager.py` og `test_ki.py`. De kaller aldri Claude.
- pytest: 751 passed. ruff check og ruff format: OK.

## Review Triage Log

bmad-code-review med fire lag. Acceptance Auditor fant ingen brudd på akseptansekriteriene.

- medium, rettet: `Tjeneste.forklaring` kunne kaste `ValueError`. Det gjaldt en prompt som ikke er UTF-8, og `nå` uten tidssone ved lagring. Nå fanges `(OSError, ValueError)` begge steder, og forklaringen vises selv om den ikke kan lagres. Begge tilfellene har tester.
- low, rettet: `_én_gang`-docstringen nevnte bare FHI og 10 s.
- low, rettet: bruk av lagret forklaring ble ikke logget.
- low, rettet: tom `modell` ble lagret og lest som gyldig. Det manglet også tester for å lagre med en ugyldig nøkkel eller modell, og for ekstra felt med gyldig tekst.
- low, rettet: `ekstra`-trikset for `ny_klient` i `tjeneste`. `ki.forklar` tar nå `None`, og standardveien (`anthropic.Anthropic`) er testet med monkeypatch.
- false: prompten leses to ganger, så teksten kan havne under feil nøkkel. `_mal` er `@cache`, så begge leser den samme teksten i samme prosess.
- false: `laget` og `modell` brukes aldri. AD-7 krever feltene, og de er til feilsøking og SM-4.
- false: spec-en er uferdig, og sesjonslogg mangler. Begge fullføres i dette steget.
- avvist (low): ingen opprydding i `ki/`. Det er utsatt i arkitekturen §8 («Opprydding i gamle cachefiler»).
- avvist (low): ingen test for at en ventende forespørsel får samme `KiFeil`. `_én_gang` deler både resultat og feil og er testet for FHI i `test_tjeneste.py`. `KiFeil` er et vanlig returverdi-utfall.
- avvist (low): en endret prompt teller først etter omstart. `_mal` leses én gang per prosess, slik `forklar` også gjør.
- defer: nøkkelen tar ikke med `effort`, `max_tokens` eller formateringen av ukene, bare promptfila og modellen. Det følger AD-7, men en endring i `ki.py` (som «skjult antall tester» i 4.3) gir ikke ny forklaring før `.cache/ki/` slettes.
- defer (beslutning for Irene): prompten har «Hentet <tidspunkt>», men nøkkelen har det ikke. Siterer KI-en tidspunktet, kan en gjenbrukt forklaring vise et eldre tidspunkt enn kilden ved siden av. Valgene er å ta tidspunktet ut av prompten, eller å be KI-en ikke nevne det.

