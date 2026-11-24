# Epic 4 Context: KI-forklaring og nyeste tall

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Brukeren får en kort KI-forklaring av tallene med kilde, og kan hente nyeste tall fra FHI med en gang. Appen virker fortsatt helt uten KI-nøkkel. Etter epicen er mal 1 for influensa ferdig. Fast frist: 2. desember 2026 (veiledende 29. november–2. desember).

## Stories

- Story 4.1: Utkast til prompt
- Story 4.2: Rette og godkjenne prompten (Irene)
- Story 4.3: KI-forklaring med tre utfall
- Story 4.4: Mellomlagre KI-forklaringen
- Story 4.5: Forklaringen på siden
- Story 4.6: Hente nyeste tall nå

## Requirements & Constraints

- **Forklaringen:** kort, på norsk, høyst 120 ord, med enkle ord. Merket «Skrevet av KI», med kildehenvisningen ved siden av. Den settes inn i et område med `aria-live="polite"` som viser «Forklaringen lages …» mens den hentes.
- **Hva modellen får:** bare de hentede tallene (tolkede uker), utvalget, resultatet av kontrollreglene og kildehenvisningen. Ingenting annet.
- **Innholdsregler (sjekkes manuelt mot lagrede forklaringer):** bare tall som finnes i dataene; ingen gjetting på årsaker (vær, vaksiner, tiltak); ingen faguttrykk uten forklaring; når varselet vises, sier forklaringen at tallene er usikre, og hvorfor.
- **Uten nøkkel eller ved feil:** uten nøkkel står det at forklaringen krever en KI-nøkkel, og at graf, tabell og varsel er komplette uten den. Ved feil fra modellen eller ved nettverksfeil står det at forklaringen ikke kunne lages akkurat nå. Resten av siden vises alltid.
- **Hente nyeste tall nå:** knappen «Hent nyeste tall nå» henter uten mellomlager og lagrer med nytt hentetidspunkt. Den er deaktivert mens hentingen pågår og kan brukes med tastatur. Hvis FHI er nede, vises sist lagrede tall med dato. Når tallene er uendret, gjenbrukes den lagrede forklaringen.
- **Svartid:** med lagrede tall vises graf, tabell og varsel på under 5 sekunder, uten å vente på KI-en.
- **Ferdigkriterier for hver utviklerstory:** egne tester for akseptansekriteriene, `uv run pytest` består uten nett og uten nøkkel, `ruff check` og `ruff format --check` består, ingen import bryter avhengighetsretningen, og README oppdateres ved endret installering, oppstart, konfigurasjon eller tester.

## Technical Decisions

- **Claude via Anthropics SDK:** bare `ki.py` importerer `anthropic`. Modellen er `claude-haiku-5-5` og kan overstyres med `ANTHROPIC_MODEL`. Klienten lages med eksplisitt `api_key=` og bare når nøkkelen finnes. `ki.forklar(...)` gir alltid `Forklaring(tekst)`, `ManglerNøkkel` eller `KiFeil` og kaster aldri videre.
- **Konfigurasjon:** `config.les_innstillinger()` laster `.env` fra reporoten med `override=True` og returnerer en `Innstillinger`-dataklasse. Bare `web` kaller den, én gang ved oppstart. Ingen modul laster `.env` ved import. `.env.example` viser `ANTHROPIC_API_KEY=` og `ANTHROPIC_MODEL=`.
- **Formatering:** ukene, utvalget og kilden skrives inn i prompten med de samme funksjonene som tabellen bruker, fra `formatering.py` (story 4.3, Irenes beslutning på #23).
- **Prompten** ligger i `backend/src/backend/prompts/forklaring.md` og er en fast tekst. Faste tekster for `ManglerNøkkel` og `KiFeil` står i malene, ikke i JavaScript.
- **Mellomlagring av forklaringen:** `ki/<nøkkel>.json` med `laget`, `modell` og `tekst`. Nøkkelen er SHA-256 av kanonisk JSON (`sort_keys=True`) med utvalg, tolkede uker, regelutslag, promptinnholdet og modellnavnet, men uten hentetidspunkt. Bare `Forklaring` lagres.
- **Ruter:** `GET /forklaring` med samme parametre som siden gir et HTML-fragment (`_forklaring.html`) som `app.js` setter inn. Feil eller annen status enn 200 gir teksten fra `data-feiltekst`. `POST /hent-nyeste` svarer `303` til `GET /` for samme utvalg.
- **Kildehenvisningen** lages bare med `domene.kildehenvisning(tabell, hentet)`, og den samme brukes under grafen og ved forklaringen.
- **Testdata:** lagrede KI-svar ligger i `tests/fixtures/ki/`. Testene bruker en falsk klient og trenger verken nett eller nøkkel.

## Cross-Story Dependencies

- 4.1 → 4.2: Irene retter og godkjenner prompten før 4.3 bygges.
- 4.3 bygger på den godkjente prompten. 4.4 bygger på 4.3, fordi promptinnholdet inngår i nøkkelen. 4.5 bruker 4.3 og 4.4.
- 4.6 trenger tvungen henting uten mellomlager i `tjeneste`, som mangler i dag, og gjenbruk av forklaringen fra 4.4.
- Bygger på epic 2 (`tjeneste.svar`, `Dataserie`, `Regelutslag`, kildehenvisning) og epic 3 (siden, malene, `app.js`).
