# Epic 3 Context: Influensa på skjermen

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Brukeren (Sara, student uten medisinsk bakgrunn) kan velge utvalg i et enkelt skjema og se varsel, graf, tabell, kildehenvisning og begrepsforklaringer for influensa, også på mobil og med tastatur. Epicen bygger `web` (FastAPI og Jinja2), `templates/`, `static/app.js`, `static/style.css` og `begreper.py` oppå det ferdige svaret fra `tjeneste.svar` i epic 2. Den rører ikke regler eller tall. KI-forklaringen og «Hent nyeste tall nå» kommer i epic 4. Veiledende: 26.–28. november 2026. Mal 1 for influensa må virke senest 2. desember.

## Stories

- Story 3.1: Velge mal og utvalg på siden
- Story 3.2: Tabell, kildehenvisning og feilmelding
- Story 3.3: Graf uke for uke
- Story 3.4: Varsel om tynt datagrunnlag
- Story 3.5: Skrive tekstene til de sju begrepsforklaringene (Irene)
- Story 3.6: Begrepsforklaringer i appen
- Story 3.7: Tilgjengelighet og mobil

## Requirements & Constraints

- **Skjema:** malene vises som spørsmål på vanlig norsk. Mal 1 er «Vis andel positive tester for [virus] i sesongen [sesong]». Mal 2 vises ikke før epic 8. Bare influensa kan velges i epic 3. Sesonglisten har bare sesonger med minst én publisert uke, og siste sesong er standard. Aldersgruppe er valgfri med «Alle aldersgrupper» som standard pluss seks grupper, uten «Ukjent alder». Knappen heter «Vis tallene».
- **Ugyldig utvalg** (manglende felt, ukjent verdi, manipulert URL) gir den norske meldingen fra `Utvalg.fra_parametre` og ingen henting. Uten parametre vises bare skjemaet.
- **Rekkefølge på siden** (også på mobil, under hverandre): skjema, varsel, graf og tabell, kildehenvisning med hentetidspunkt og «FHI publiserer nye tall hver torsdag», begrepsforklaringer. Plassen til KI-forklaringen og knappen «Hent nyeste tall nå» kommer i epic 4.
- **Tabell:** kolonnene uke, tester, positive prøver og andel positive, med de samme tallene som grafen. Skjulte verdier vises som «skjult» eller «mangler», aldri som 0. Usikre uker (færre enn 30 tester, skjult antall tester, eller flere positive enn tester) får tegn og fotnote. Uker med flere positive enn tester viser andelen som den er (over 100 %) og får ordrett fotnoten «Flere positive prøver enn tester denne uka. Det kan skyldes hvordan prøvene er registrert. Tolk tallet med forsiktighet.» En uke med 0 tester og flere enn 0 positive får fotnoten, men ingen andel. Teksten finnes ikke i koden ennå.
- **Graf:** linjegraf med uker langs x-aksen og andel positive (%) langs y-aksen. Manglende uker gir brudd i linjen, ikke 0. Tittelen gjentar utvalget, for eksempel «Influensa, sesongen 2025/2026, alle aldersgrupper». Usikre uker har en annen punktform (for eksempel åpen sirkel), og forklaringen i grafen sier hva markeringen betyr. Alternativteksten har utvalg og hovedtrekk.
- **Varsel:** står over grafen bare når minst én regel slår inn. Det har ikon og overskrift (ikke bare farge), lister hver regel med den ferdige setningen fra `Regelutslag` og lenker til forklaringen av «for tynt datagrunnlag». Uten utslag vises det ikke.
- **Kildehenvisning:** under graf og tabell, med FHIs kildetekst ordrett, tabellnummer, tabellnavn og hentetidspunkt i norsk tid. Den vises også når KI-forklaringen mangler.
- **FHI nede:** FR-8-meldingen på norsk uten tekniske koder. Med lagrede tall vises de med «Sist lagrede tall, hentet [dato og klokkeslett]». Uten lagrede tall vises ingen graf eller tabell, og brukeren får forslag om å prøve igjen senere. Varsel og begrepsforklaringer gjelder også for lagrede tall.
- **Begrepsforklaringer:** sju faste tekster (andel positive, test og positiv prøve, sesong, aldersgruppe, overvåkingstype, MSIS, «for tynt datagrunnlag»), høyst tre setninger hver, skrevet av Irene og ikke av KI. Overvåkingstype sier at appen bruker vanlig klinisk praksis og nevner kort fyrtårnsystemet. De åpnes med mus, Enter og mellomrom.
- **Språk:** enkel norsk bokmål, `lang="nb"`. Ingen FHI-koder (`NONSTL`, `A+B`, `pos_rate`, «Non-Sentinel», «RS-virus (A+B)») vises. Feilmeldinger og tomme tilstander sier hva som skjedde og hva brukeren kan gjøre.
- **Tilgjengelighet:** kontrast minst 4,5:1 for tekst og 3:1 for linjer og symboler i grafen. Alt virker med tastatur alene og har synlig fokusmarkering. Ingen informasjon formidles bare med farge (sjekkes i gråtoner). Alle skjemafelt har `<label>`. Siden virker fra 360 piksler bredde uten vannrett rulling, og tabellen ruller inni sin egen boks.
- **Svartid og nøkkel:** med lagrede tall vises graf, tabell og varsel på under 5 sekunder. Alt i epic 3 virker uten `.env` og uten KI-nøkkel.
- **Ferdigkriterier for hver utviklerstory:** egne tester for akseptansekriteriene (app-tester med FastAPIs `TestClient`), `uv run pytest` består uten nett og uten nøkkel, `ruff check` og `ruff format --check` består, ingen import bryter avhengighetsretningen, og README oppdateres ved endret installering, oppstart, konfigurasjon eller tester.

## Technical Decisions

- **Server-HTML:** Jinja2-maler i `templates/` (`base.html`, `index.html`). Tabell, varsel, kildehenvisning og begrepsforklaringer (`<details>`/`<summary>`) står i HTML og virker uten JavaScript. All egen JavaScript ligger i `static/app.js`, og all stil i `static/style.css`. Ingen Node og ingen byggesteg.
- **Chart.js 4.6.1** fra `cdn.jsdelivr.net` med fast versjon og `integrity`-attributt. Grafen leser tallene fra en `<script type="application/json">`-blokk laget fra samme `Dataserie` som tabellen, med `null` for manglende uker.
- **Ruter:** `GET /` med query-parametrene `mal`, `virus`, `sesong` og `alder` viser skjema og resultat. Validering skjer bare i `domene.Utvalg.fra_parametre`. `web` kaller `tjeneste.svar(utvalg, nå)` og `tjeneste.sesonger(nå)`, og viser bare faste norske tekster. `tjeneste` fanger allerede `FhiUtilgjengelig`, markerer «sist lagrede» tall og gir en norsk melding for virus som ikke er klare (RSV, SARS-CoV-2) og for sesonger uten publiserte uker.
- **Avhengigheter:** `web` kan importere `tjeneste`, `domene` og `begreper`. `begreper.py` er en del av den rene kjernen og importerer aldri `httpx`, `anthropic`, `mellomlager`, `config` eller `web`.
- **Konfigurasjon:** `config.les_innstillinger()` kalles bare én gang, ved oppstart i `web`. Ingen modul laster `.env` ved import. App-testene overstyrer `les_innstillinger` og lager `Innstillinger` direkte, uten nøkkel og med `CACHE_DIR` lik `tmp_path`. FHI mockes med `respx`.
- **Formatering bare i Jinja2-filtre i `web`:** andel med én desimal og komma («20,8 %»), mellomrom som tusenskille, uker som «uke 50», hentetidspunkt i norsk tid (`Europe/Oslo`) som «20.11.2026 kl. 14:05». Tid lagres i UTC.
- **Kildehenvisning** lages bare av `domene.kildehenvisning(tabell, hentet)`. For 724: «Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, Folkehelseinstituttet (FHI).» og tabellnavnet «RESPIaggr Influensa antall og andel».
- **Faste tekster:** begrepsforklaringene i `begreper.py`. Feil-, varsel- og fotnotetekster i malene. Ingen tekst lages av KI i epic 3.
- **Farger:** tekst- og graffarger er CSS-variabler i `style.css`, som `app.js` leser. En automatisk test regner ut kontrasten.
- **Oppstart:** `cd backend && uv run uvicorn backend.web:app --reload`. Appen starter uten `.env`.
- **Navn:** moduler, funksjoner og dataklasser på norsk. Ord fra rammeverk og biblioteker beholdes på engelsk.

## Cross-Story Dependencies

- Alle stories bygger på `tjeneste.svar` og `tjeneste.sesonger` fra story 2.9 og på `Uke`, `Dataserie`, `Regelutslag` og `Kildehenvisning` fra epic 2.
- 3.1 lager `web`, `base.html` og skjemaet. 3.2–3.4 og 3.6 legger til deler av samme side.
- 3.3 bruker samme `Dataserie` som tabellen i 3.2, og testene sjekker at JSON-blokken har de samme tallene.
- 3.6 krever tekstene fra 3.5 (Irene) og legger lenken fra varselet i 3.4 til forklaringen av «for tynt datagrunnlag».
- 3.7 kommer sist og gjelder hele hovedskjermen (skjema, varsel, graf, tabell og begrepsforklaringer). En manuell sjekk i gråtoner, med tastatur og ved 360 piksler noteres i issuet.
- Epic 4 legger til `GET /forklaring`, KI-området med `aria-live="polite"` og `POST /hent-nyeste` på samme side. Epic 5 kan skrive om ord på siden etter brukertestingen. Epic 6 åpner RSV og SARS-CoV-2 i skjemaet. Mal 2 (epic 8) bruker hel og stiplet linje i samme graf.
