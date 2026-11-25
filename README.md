# G63 — Biobytes

Prosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng). Gjennomføres solo etter godkjenning fra faglærer.

## Prosjekt: FHI Helsedata-utforsker

KI-assistert applikasjon for å utforske FHIs åpne statistikk om smittsomme sykdommer og laboratoriefunn.

### Hva appen gjør

Appen viser hvor stor andel av testene for influensa, RSV og koronavirus (SARS-CoV-2) som var positive, uke for uke, for hele Norge. Den er laget for folk uten medisinsk bakgrunn, for eksempel studenter som skriver om beredskap.

- Forsiden har ett kort per virus med andelen positive i den siste uka med tall.
- Et klikk på et kort åpner resultatsiden. Der kan du velge sesong og aldersgruppe og se en graf, en tabell, korte forklaringer av ordene og en kildehenvisning.
- Appen sier fra med et varsel når tallene er for usikre til å trekke konklusjoner, og forklarer hvorfor. Reglene for varselet står i koden (`kontrollregler.py`), ikke i KI-en.
- En kort forklaring med enkle ord skrives av KI (Claude) hvis du har en KI-nøkkel. Uten nøkkel virker alt annet.

### Data og kilde

Tallene hentes fra Folkehelseinstituttets (FHI) åpne statistikk-API, fra Meldingssystem for smittsomme sykdommer (MSIS):

| Tabell | Virus |
| --- | --- |
| 724 «RESPIaggr Influensa antall og andel» | Influensa |
| 729 «RESPIaggr RSV antall og andel» | RSV |
| 731 «RESPIaggr SARS-CoV-2 antall og andel» | SARS-CoV-2 |

Tallene er ukentlige for hele landet fra uke 40 i 2024, fra vanlig klinisk praksis. De er aggregerte og har ingen opplysninger om enkeltpersoner. FHI publiserer nye tall hver torsdag. Appen viser kilden og når tallene ble hentet under hver graf.

### Begrensninger

- Bare tre virus, og bare tall fra uke 40 i 2024 og senere. Eldre tall finnes bare på bestilling fra FHI.
- Bare hele landet, ingen fylker.
- Tallene teller tester, ikke personer.
- Appen er ikke en offisiell kilde, gir ingen råd om smittevern og spår ikke hvordan smitten vil utvikle seg.
- Appen kjøres lokalt. Publisering på Vercel er valgfritt (story 8.3) og ikke gjort.
- Sammenligning av to sesonger (mal 2) er et strekkmål og ikke bygget.
- KI-forklaringen krever en egen nøkkel fra Anthropic, som koster penger å bruke.

## Medlemmer

- Irene Zumbo

## Dokumentasjon

- [Product Brief (proposal)](docs/product-brief.md)
- [PRD (kravene)](_bmad-output/planning-artifacts/prds/prd-fhi-helsedata-2026-11-06/prd.md), med tekniske detaljer om FHI-API-et i [addendum.md](_bmad-output/planning-artifacts/prds/prd-fhi-helsedata-2026-11-06/addendum.md)
- [Arkitektur](_bmad-output/planning-artifacts/architecture/architecture.md)
- [Epics og stories](_bmad-output/planning-artifacts/epics.md). Story-numrene i denne README-en (for eksempel «story 4.3») viser hit.
- [Sjekkliste](docs/sjekkliste.md) og [KI-logg](docs/ki-logg.md)

## Kom i gang

Krever git og [uv](https://docs.astral.sh/uv/). Du trenger ikke installere Python selv: uv henter riktig versjon (3.13). Alle `uv`-kommandoene kjøres fra `backend/`.

Har du ikke uv, installerer du det slik og åpner en ny terminal etterpå:

    # macOS og Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Windows (PowerShell)
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

Sjekk at det virker med `uv --version`.

### Installere

    git clone https://github.com/IBE160-2026/G63-zumbo.git
    cd G63-zumbo/backend
    uv sync

`uv sync` installerer appen og utviklingsverktøyene (pytest, pytest-socket, respx og ruff) med versjonene som er låst i `uv.lock`. Første gang kan det ta et minutt, fordi uv også laster ned Python.

### Kjøre testene og ruff

Fra `backend/`:

    uv run pytest
    uv run ruff check
    uv run ruff format --check

Du skal se at pytest bare melder `passed` og ingen `failed`, at `ruff check` skriver `All checks passed!`, og at `ruff format --check` skriver `files already formatted`. Alle tre kommandoene skal bestå før hver commit. GitHub Actions kjører de samme tre på hver PR og hver push til main (`.github/workflows/tester.yml`), og PR-en får en grønn hake når alle består. Testene kjører uten nett: `pytest-socket` stopper alle nettverkskall, så ingen test kan kalle FHI eller Claude ved et uhell. Testene trenger heller ingen KI-nøkkel og leser aldri `.env`. De bruker lagrede svar i `backend/tests/fixtures/`. Ekte svar fra FHI for tabell 724 (influensa), 729 (RSV) og 731 (SARS-CoV-2) ligger i `backend/tests/fixtures/fhi/`, og README-en der forklarer formatet og hvordan de ble hentet.

### Starte appen

Fra `backend/`:

    uv run uvicorn backend.web:app --reload

Vent til terminalen skriver `Application startup complete`, og åpne så http://127.0.0.1:8000 i nettleseren. Er port 8000 i bruk, legger du til `--port 8002` og åpner http://127.0.0.1:8002. Forsiden på `/` viser ett kort per virus med andelen positive i siste uke med tall. Trykk på et kort for å åpne resultatsiden på `/resultat`, der du kan endre sesong og aldersgruppe. Gamle adresser med valg (`/?mal=…`) sendes videre til `/resultat`. Appen starter uten `.env`. `--reload` starter appen på nytt når koden endres. Stopp den med Ctrl+C. Første gang tar forsiden et sekund eller to, fordi tallene hentes fra FHI. Det krever nett.

### KI-nøkkel er valgfri

`.env` er valgfri. Appen virker uten KI-nøkkel: alt unntatt KI-forklaringen virker. Vil du ha KI-forklaringen, trenger du en nøkkel fra [Anthropic Console](https://console.anthropic.com/). Kopier `.env.example` til `.env` i reporoten (mappen over `backend/`) og fyll inn `ANTHROPIC_API_KEY`. Fra reporoten:

    cp .env.example .env

På Windows heter kommandoen `copy .env.example .env`.

Åpne `.env` i en teksteditor og lim inn nøkkelen etter likhetstegnet, uten mellomrom og uten anførselstegn:

    ANTHROPIC_API_KEY=din-nøkkel-her

Start appen på nytt etterpå, fordi `.env` bare leses når appen starter. Verdiene i `.env` vinner over miljøvariabler med samme navn i skallet. En tom verdi regnes som ikke satt, også når skallet har en verdi.

`ANTHROPIC_MODEL` kan stå tom; da brukes standardmodellen `claude-haiku-5-5`. `.env` og mellomlageret i `.cache/` holdes utenfor git.

Forklaringen lages i `backend/src/backend/ki.py` med prompten i `backend/src/backend/prompts/forklaring.md` (story 4.3). Uten nøkkel kalles ikke Claude. Feiler kallet, blir det ingen forklaring, men resten av siden virker som før.

Forklaringen står nederst på siden, under «Forklaring» (story 4.5). Siden viser graf, tabell og varsel med en gang, og `app.js` henter forklaringen fra `GET /forklaring` etterpå. Mens den lages, står det «Forklaringen lages …». Uten nøkkel står det at forklaringen krever en KI-nøkkel, og feiler noe, står det at forklaringen ikke kunne lages akkurat nå.

Vil du se de tre utfallene uten en ekte nøkkel, starter du appen med en falsk Claude. Fra `backend/`:

    uv run python scripts/vis_forklaring.py forklaring
    uv run python scripts/vis_forklaring.py uten-nokkel
    uv run python scripts/vis_forklaring.py feil

Åpne så http://127.0.0.1:8001 (port 8001, så den ikke kolliderer med den vanlige appen), og trykk på et viruskort. Tallene hentes fra FHI som vanlig, men Claude kalles aldri, og mellomlageret er en midlertidig mappe, så den falske forklaringen havner ikke i `.cache/ki/`. Stopp med Ctrl+C.

### Mellomlager

Svar fra FHI lagres i `.cache/` i reporoten. Tall du har sett før, brukes uten nytt kall, også når FHI er nede (da merket «sist lagrede»), og tall som er 24 timer eller eldre, hentes på nytt (`tjeneste.py`, story 2.9). Knappen «Hent nyeste tall nå» under tabellen henter tallene fra FHI med en gang, uten å bruke de lagrede, og lagrer dem med nytt hentetidspunkt (`POST /hent-nyeste`, story 4.6). FHI publiserer nye tall hver torsdag. Svarer ikke FHI, vises de sist lagrede tallene. Er tallene de samme som før, brukes den lagrede KI-forklaringen. Vil du ha mellomlageret et annet sted, setter du `CACHE_DIR` i `.env` eller i miljøet. En relativ sti regnes fra reporoten. På Vercel (miljøvariabelen `VERCEL` finnes) brukes `/tmp/fhi-helsedata-cache` når `CACHE_DIR` ikke er satt. KI-forklaringer lagres i `ki/` i den samme mappen, og de samme tallene gir den samme forklaringen uten nytt kall til Claude (story 4.4). En ny prompt, et nytt ukeformat (`UKEFORMAT` i `ki.py`) eller en annen modell gir en ny forklaring. Mappen kan slettes når som helst; alt hentes på nytt.

## Struktur

- `backend/`: Python-prosjektet (uv). Koden ligger i `backend/src/backend/`, testene i `backend/tests/`.
- `docs/`: prosjektdokumentasjon (product brief, sjekkliste, KI-logg)
- `_bmad-output/`: planleggingen (PRD, arkitektur, epics og stories) og specene for hver story
- `.github/workflows/`: den automatiske sjekken med pytest og ruff
- `.logs/`: logg over arbeidsøktene og åpne punkter
