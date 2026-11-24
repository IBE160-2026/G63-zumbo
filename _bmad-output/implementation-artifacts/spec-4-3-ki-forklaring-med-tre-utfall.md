---
title: 'Story 4.3: KI-forklaring med tre utfall'
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

**Problem:** Det finnes en godkjent prompt (story 4.2, #23), men ingen kode som fyller den ut og kaller Claude. Story 4.3 (#24) krever at `ki.forklar(...)` alltid gir `Forklaring(tekst)`, `ManglerNøkkel` eller `KiFeil` og aldri kaster videre (FR-20, FR-22, NFR-1, AD-6).

**Approach:** Lag `backend/src/backend/ki.py`, den eneste modulen som importerer `anthropic`. `forklar` fyller ut `prompts/forklaring.md` med utvalget, ukene, regelutslagene og kildehenvisningen. Uten nøkkel kalles ikke Claude. Klienten lages med eksplisitt `api_key=` og modellen fra `Innstillinger` (`claude-haiku-5-5`, kan overstyres med `ANTHROPIC_MODEL`). Alle feil blir `KiFeil`. Testene bruker en falsk klient og tekst fra `tests/fixtures/ki/` og kaller aldri Claude.

Beslutninger fra brukeren (Irene):
- Ukene skrives inn i `{uker}` slik de står i tabellen på siden, for eksempel «uke 50: 1 210 tester, 252 positive, 20,8 %», med «skjult», «mangler» og «kan ikke regnes ut» der tabellen viser det.
- `config.les_innstillinger()` skal behandle tom `ANTHROPIC_MODEL` eller `ANTHROPIC_API_KEY` som ikke satt.

</frozen-after-approval>

## Implementation Notes

- **Formatering flyttet til `formatering.py`.** `ki` får ikke importere `web` (AD-1), men ukene skal stå slik de står i tabellen. Derfor er `tall`, `andel`, `andelstekst`, `uke`, `utvalgstekst` og `tidspunkt` flyttet fra `web.py` til den rene modulen `formatering.py`, som `web` registrerer som Jinja2-filtre og `ki` bruker i prompten. Nye: `ukelinje` («uke 50: 1 210 tester, 252 positive, 20,8 %») og `kildetekst` (samme tekst som under grafen; malen bruker den nå). Arkitekturen §2 og §4 og epic 4-konteksten er oppdatert.
- **Skjulte tall i en ukelinje:** «uke 3: skjult tester, 5 positive, mangler», altså samme ord i samme rekkefølge som cellene i tabellen.
- **Regelutslag** står som «- setning» på hver sin linje. Uten utslag er feltet tomt, slik den godkjente prompten sier.
- **`ki.forklar(serie, regelutslag, kilde, innstillinger, ny_klient=anthropic.Anthropic)`.** Uten nøkkel returnerer den `ManglerNøkkel` før klienten lages. Klienten lages med `api_key=`, `timeout=15` og `max_retries=1` i en `with`. Kallet bruker `max_tokens=4096` og `output_config={"effort": "low"}`, og tenkingen er på som standard i Haiku 5.5. Bare `stop_reason == "end_turn"` med ikke-tom tekst gir `Forklaring`; alt annet og alle unntak gir `KiFeil`. Bare feiltypen og statuskoden logges.
- **`config`:** tom eller blank `ANTHROPIC_API_KEY`/`ANTHROPIC_MODEL` var allerede «ikke satt» siden story 2.6. Nye tester dekker verdier med bare mellomrom og tomme verdier i `.env` som overstyrer skallet.
- **Fixture:** `tests/fixtures/ki/forklaring-influensa-2025-2026-alle.txt` er skrevet for hånd etter reglene i prompten. Ekte svar lagres i story 7.4 (#35).
- **README:** hvordan nøkkelen settes i `.env`, omstart, at `.env` vinner, og standardmodellen.
- `httpx2` er lagt til som dev-avhengighet fordi `test_ki.py` lager SDK-feil med den.
- pytest: 691 passed. ruff check og ruff format: OK.
- **Endringer før merge (Irenes beslutninger på PR #66):**
  - Overskriften «Kilde:» er strøket i prompten, fordi FHIs tekst starter med «Kilde:».
  - Skjulte tall skrives som «skjult antall tester», og andelen som «andel mangler» eller «andel kan ikke regnes ut». Tabellen er uendret.
  - `ukelinje` er flyttet fra `formatering` til `ki`, fordi den nå bare gjelder prompten.
  - En ny test i `test_web_tabell.py` sammenligner tallene i hver ukelinje med tabellen på siden. Den dekker tre fixturer, også skjulte tall og 0 tester. Det løser punktet som var utsatt fra gjennomgangen.
  - pytest: 698 passed.

## Review Triage Log

bmad-code-review med fire lag (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Acceptance Auditor fant ingen brudd på akseptansekriteriene.

- medium, rettet: klienten ble aldri lukket. Nå `with ny_klient(...) as klient`, og testen sjekker at den lukkes.
- medium, rettet: `timeout`, `max_retries`, `max_tokens` og `output_config` var ikke testet, og den falske klienten godtok alle argumenter. Nå sjekkes argumentene mot den ekte signaturen til `anthropic.Anthropic` og `Messages.create`, og verdiene testes.
- low, rettet: `TIDSGRENSE` gjelder per forsøk. Senket fra 20 til 15 s, og docstringen sier at hele kallet kan ta drøyt 30 s.
- low, rettet: `MAKS_TOKENS` 2048 kunne bli for lite med tenking. Økt til 4096, med docstring om at Haiku 5.5 tenker som standard. (Påstanden om at tenking ikke er på, er feil: den er på som standard i Haiku 5.5.)
- low, rettet: `HARDT_MELLOMROM` og `NBSP` i testene var skrevet som usynlige tegn. Nå `"\u00a0"`.
- low, rettet: testen for «samme tekst som tabellen» sammenlignet funksjonene med seg selv. Nå sjekker den at Jinja2-filtrene er nøyaktig de samme funksjonene som i `formatering`.
- low, rettet: logging var bare testet for 401. Nå også for uventet feil med nøkkelen i meldingen, og for et ubrukelig svar.
- low, rettet: README-testen sjekker nå de nye påstandene (omstart, `.env` vinner, tom verdi).
- low, rettet: `httpx2` var ikke en deklarert avhengighet.
- low, rettet: arkitekturen §2, epic 4-konteksten og docstringen til `Kildehenvisning` nevnte ikke `formatering`.
- low, rettet: testen for tomt regelutslag brukte `kontrollregler.vurder(SERIE)` i stedet for `()`.
- false: blank nøkkel rett i `Innstillinger` gir 401 i stedet for `ManglerNøkkel`. I appen lages `Innstillinger` bare av `les_innstillinger`, som gjør blanke verdier om til `None`.
- false: et regelutslag med linjeskift bryter formatet. Tekstene kommer fra faste setninger i `kontrollregler` og har ingen linjeskift.
- false: README beskriver noe som ikke finnes ennå. Den sier at forklaringen vises fra story 4.5, og at `ki.forklar` ikke kaster, og det stemmer.
- false: spec-en er uferdig. Den fullføres i dette steget.
- avvist (low): programmeringsfeil skjules som `KiFeil`. At `forklar` aldri kaster, er et krav (AD-6), og `test_prompt.py` sjekker allerede at prompten bare har de fire plassholderne.
- avvist (low): tom `serie.uker` sendes til Claude. `fhi.tolk` lager en uke for hver forventet uke, og siden viser ikke forklaringen uten tall (4.5).
- avvist (low): `UTSLAG` i testene passer ikke til serien. Testene sjekker bare formatet i prompten.
- avvist (low): Konfigurasjon- og Feil-radene i arkitekturen kunne sagt mer. README og `config.py` beskriver oppførselen allerede.
- defer (Verification Gap): ingen test sammenligner den ferdige HTML-tabellen med `ukelinje`. I dag sikrer filtertesten at tekstene er like.

