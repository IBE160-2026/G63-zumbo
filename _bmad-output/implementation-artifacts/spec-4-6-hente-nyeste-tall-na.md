---
title: 'Story 4.6: Hente nyeste tall nå'
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

**Problem:** Tallene fornyes først når de er 24 timer gamle (FR-7), så brukeren kan ikke se nye tall fra FHI med en gang de publiseres på torsdag. `tjeneste` mangler en henting som hopper over mellomlageret, og siden sier ikke at FHI publiserer nye tall hver torsdag (FR-25, #27).

**Approach:** `Tjeneste.svar` får en tvungen henting som hopper over ferske lagrede tall og dimensjonslisten, og lagrer med nytt hentetidspunkt. Siden får teksten «FHI publiserer nye tall hver torsdag.» og knappen «Hent nyeste tall nå», som sender `POST /hent-nyeste` og får `303` til `GET /` for samme utvalg. `app.js` deaktiverer knappen når skjemaet sendes. Når FHI ikke svarer, vises sist lagrede tall med dato (FR-8). Uendrede tall gir samme nøkkel, så den lagrede KI-forklaringen gjenbrukes (AD-7). Testene kaller aldri FHI eller Claude på ekte.

</frozen-after-approval>

## Implementation Notes

- **`Tjeneste.svar(utvalg, nå, tving=False)`:** med `tving` hentes både tallene og dimensjonslisten fra FHI selv om de lagrede er ferske. En ny uke kommer da med selv om listen ble lagret før FHI publiserte. Pausen etter en feil (`PAUSE_ETTER_FEIL`) gjelder ikke, fordi brukeren ber om et nytt forsøk. Tvungne hentinger har egne nøkler i `_én_gang` (`…-tving`). Da deler samtidige trykk ett kall, og et tvunget kall blir aldri med på et vanlig kall som bare leser cachen.
- **`POST /hent-nyeste`** (skjemafelt `mal`, `virus`, `sesong` og `alder`, lest med `Form` fra python-multipart, som allerede er en avhengighet):
  - Et gyldig utvalg hentes med `tving=True`, og svaret er `303` til `/?…` for samme utvalg.
  - Når FHI ikke svarte og de lagrede tallene vises, får adressen `nyeste_feilet=<tidspunktet for forsøket i Unix-sekunder>`. `GET /` viser FR-8-meldingen og «Sist lagrede tall, hentet …» bare når forsøket er under fem minutter gammelt (`NYESTE_GJELDER`), og tallene er eldre enn forsøket. Dermed gir en adresse som lastes inn på nytt senere, ingen falsk melding om at FHI er nede.
  - Et ugyldig utvalg hentes ikke. Det får `303` til `/?…` med de samme verdiene, og siden viser feilmeldingen.
- **Siden:** under kilden og «Tallene for den siste uka …» står «FHI publiserer nye tall hver torsdag.» og knappen, i et skjema med skjulte felt (makroen `hent_nyeste` i `index.html`). Hentetidspunktet står allerede i kildehenvisningen. Mangler et gyldig utvalg tall (FHI nede uten lagrede tall, eller sesongen er ikke publisert), står teksten og knappen i meldingsboksen, så brukeren kan prøve igjen. For virus som ikke er klare, vises ikke knappen.
- **Pausen etter en feil** gjelder nå også datakallet. Svarte ikke FHI på tallene for under 60 sekunder siden, prøver et vanlig kall ikke igjen. Et tvunget kall prøver alltid.
- **`app.js`:** knappen deaktiveres når skjemaet sendes, og viser `data-ventetekst` («Henter nyeste tall …»). En deaktivert knapp kan ikke sende skjemaet på nytt. `pageshow` gjør knappen brukbar igjen når siden kommer tilbake fra nettleserens hurtigbuffer.
- **CSS:** en deaktivert knapp i skjemaet beholder fargene, så kontrasten holder. Den får ventepeker.
- **`test_stil.py`:** testen for labeler hopper over skjulte felt.
- **`web.utvalgsparametre`:** gir parametrene for et utvalg og brukes både av `forklaringsadresse` og av omdirigeringen.
- **Tester:**
  - `test_tjeneste_tving.py` (10) og `test_web_hent_nyeste.py` (27) dekker 303, ny lagring, FHI nede med og uten lagrede tall, ugyldig utvalg, at uendrede tall ikke gir nytt kall til Claude, og at endrede tall gir det.
  - De kaller aldri FHI eller Claude på ekte. pytest: 827 passed etter rettelsene fra kodegjennomgangen. ruff: OK.
- **Prøvd for hånd:** mot ekte FHI med demoskriptet. `POST /hent-nyeste` ga 303, og hentetidspunktet ble nytt.
- **Ikke testet automatisk:** at `app.js` faktisk deaktiverer knappen i en nettleser. Testene leser kildeteksten, som for 4.5.

## Review Triage Log

bmad-code-review med fire lag (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Acceptance Auditor fant ingen brudd på akseptansekriteriene. 7 rettet, 2 utsatt, 11 avvist.

- **medium, rettet:** `nyeste=feilet` ble stående i adressen. En ny innlasting, et bokmerke eller en delt lenke viste da at FHI var nede, også når FHI svarte og tallene var nye. Nå har merket tidspunktet for forsøket. Det gjelder i fem minutter, og bare for tall som er eldre enn forsøket. En verdi som ikke er et tall, ignoreres. Fire nye tester.
- **medium, rettet:** svarte dimensjonslisten, men ikke tallene, og var de lagrede tallene utdaterte, prøvde siden etter omdirigeringen FHI en gang til, med opptil 10 sekunder ekstra venting. Nå setter en feil på datakallet også pausen. Et vanlig kall prøver ikke igjen innen 60 sekunder. Testet både i `tjeneste` og på siden.
- **low, rettet:** ingen test viste at et tvunget kall ikke blir med på et vanlig kall, eller at samtidige tvungne kall deler ett kall. Det er nå to trådtester.
- **low, rettet:** et gyldig utvalg uten tall hadde verken teksten om torsdag eller knappen. Da kunne ikke brukeren hente en ny sesong som FHI publiserte på torsdag, før listen ble utdatert. Teksten og knappen står nå i meldingsboksen, med en test. Det dekker også at merket ikke endrer en side uten tall.
- **low, rettet:** sperren `if (knapp.disabled)` i `app.js` kunne aldri slå inn, så den er fjernet.
- **low, rettet:** `button:disabled` gjaldt alle knapper. Nå gjelder regelen bare `.hent-nyeste`.
- **low, rettet:** `test_stil.py` fjernet bare skjulte felt der `type` var første attributt. Nå finnes `type="hidden"` hvor som helst i taggen.
- **defer:** `POST /hent-nyeste` har ingen begrensning på hvor ofte FHI kan kalles, og ingen sjekk av opprinnelse. Det gjelder først når appen publiseres (story 8.3).
- **defer:** på Vercel er `/tmp`-cachen lokal for hver instans, så `GET /` etter `303` kan treffe en instans uten de nye tallene (story 8.3).
- **false:** README og spec-en er uenige om hvor knappen står. Kilden står under tabellen, så «under tabellen» stemmer.
- **false:** spec og sprint-status står som `in-progress`. De settes til `done` i dette steget.
- **avvist (low):** et vanlig og et tvunget kall for samme utvalg kan gå til FHI samtidig. Det er valgt med vilje, så et tvunget kall aldri får de gamle tallene fra et vanlig kall. AD-9 handler om dobbelttrykk, og to tvungne kall deler fortsatt ett kall. Skrivingen til cachen er atomisk.
- **avvist (low):** et tomt skjema gir en tom startside uten feilmelding. Skjemaet sender alltid de skjulte feltene, så det skjer bare med en forespørsel laget for hånd.
- **avvist (low):** et tomt skjema og `mal=9` er ikke sjekket mot siden. Feilmeldingen for et ugyldig utvalg er testet med sesongen 1999/2000, og `GET /` er testet for ugyldige verdier i story 3.1.
- **avvist (low):** knappen forblir deaktivert hvis brukeren stopper innlastingen med Esc. Det ville kreve en tidsbryter. En ny innlasting eller Tilbake (`pageshow`) gjør knappen brukbar igjen.
- **avvist (low):** skjermlesere får ikke vite at hentingen pågår. Knappen får ventetekst, og siden lastes på nytt innen sekunder med ny kildehenvisning.
- **avvist (low):** `app.js` er bare testet ved å lese kildeteksten. Prosjektet har ingen nettlesertest, og hullet står alt i deferred-work.md og issues.md fra 4.5.
- **avvist (low):** hvem som helst kan lage `nyeste_feilet` for hånd. Det gir bare en melding om at FHI ikke svarte i fem minutter, ingen andre tall.
- **avvist (low):** kontrasten på den deaktiverte knappen er ikke testet. Regelen endrer ikke farger, og fargene på `button` er alt testet i `test_stil.py`.
- **avvist (low):** `POST` kaster `Resultat` og stoler på cachen. Lokalt er det samme prosess og samme cache. På Vercel gjelder det utsatte punktet over.
