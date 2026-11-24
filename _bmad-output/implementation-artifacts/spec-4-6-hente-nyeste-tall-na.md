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

- **`Tjeneste.svar(utvalg, nå, tving=False)`:** med `tving` hentes både tallene og dimensjonslisten fra FHI selv om de lagrede er ferske. En ny uke kommer da med selv om listen ble lagret før FHI publiserte. Pausen etter en feil (`PAUSE_ETTER_FEIL`) gjelder ikke, fordi brukeren ber om et nytt forsøk. Tvungne hentinger har egne nøkler i `_én_gang` (`…-tving`). Da deler samtidige trykk ett kall, og et tvunget kall blir aldri med på et vanlig kall som bare leser cachen.
- **`POST /hent-nyeste`** (skjemafelt `mal`, `virus`, `sesong` og `alder`, lest med `Form` fra python-multipart, som allerede er en avhengighet):
  - Et gyldig utvalg hentes med `tving=True`, og svaret er `303` til `/?…` for samme utvalg.
  - Når FHI ikke svarte og de lagrede tallene vises, får adressen `nyeste=feilet`. `GET /` viser da FR-8-meldingen og «Sist lagrede tall, hentet …», selv om de lagrede tallene er ferske.
  - Et ugyldig utvalg hentes ikke. Det får `303` til `/?…` med de samme verdiene, og siden viser feilmeldingen.
- **Siden:** under kilden og «Tallene for den siste uka …» står «FHI publiserer nye tall hver torsdag.» og knappen, i et skjema med skjulte felt. Hentetidspunktet står allerede i kildehenvisningen. Knappen vises bare når det finnes tall.
- **`app.js`:** knappen deaktiveres når skjemaet sendes, og viser `data-ventetekst` («Henter nyeste tall …»). Et nytt trykk mens den er deaktivert stoppes. `pageshow` gjør knappen brukbar igjen når siden kommer tilbake fra nettleserens hurtigbuffer.
- **CSS:** en deaktivert knapp beholder fargene, så kontrasten holder. Den får ventepeker.
- **`test_stil.py`:** testen for labeler hopper over skjulte felt.
- **`web.utvalgsparametre`:** gir parametrene for et utvalg og brukes både av `forklaringsadresse` og av omdirigeringen.
- **Tester:**
  - `test_tjeneste_tving.py` (7) og `test_web_hent_nyeste.py` (18) dekker 303, ny lagring, FHI nede med og uten lagrede tall, ugyldig utvalg, at uendrede tall ikke gir nytt kall til Claude, og at endrede tall gir det.
  - De kaller aldri FHI eller Claude på ekte. pytest: 815 passed. ruff: OK.
- **Prøvd for hånd:** mot ekte FHI med demoskriptet. `POST /hent-nyeste` ga 303, og hentetidspunktet ble nytt.
- **Ikke testet automatisk:** at `app.js` faktisk deaktiverer knappen i en nettleser. Testene leser kildeteksten, som for 4.5.
