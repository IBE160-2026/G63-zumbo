# Epic 2 Context: Riktige influensatall med kontrollregler

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Appen kan hente, mellomlagre og tolke influensatall (tabell 724) for et utvalg, og avgjør med kontrollreglene R1–R5 om datagrunnlaget er for tynt. Epicen bygger hele den rene kjernen (`domene`, `sesong`, tolking i `fhi`, `kontrollregler`) og skallet under nettsiden (`fhi.hent`, `config`, `mellomlager`, `tjeneste`), slik at epic 3 bare trenger å vise ett ferdig svar. Alt testes uten nett. Regler og tall er faste i koden og gir samme svar hver gang. Veiledende: 23.–25. november 2026. Mal 1 for influensa må virke senest 2. desember.

## Stories

- Story 2.1: Domenemodellen
- Story 2.2: Gyldige utvalg fra parametre
- Story 2.3: Sesonger, uker og utdaterte tall
- Story 2.4: Tolke FHI-svar til en komplett dataserie
- Story 2.5: Hente fra FHI med tidsgrense
- Story 2.6: Mellomlagre FHI-svar
- Story 2.7: Kontrollregler R1–R3
- Story 2.8: Kontrollregler R4–R5
- Story 2.9: Sette sammen svaret for et utvalg

## Requirements & Constraints

- **Begreper:** Et utvalg er mal + virus + sesong + aldersgruppe. Overvåkingstypen er alltid vanlig klinisk praksis (`NONSTL`), virustypen alltid totalen (`A+B` for influensa). Virus → tabell: influensa 724, RSV 729, SARS-CoV-2 731. Aldersgruppe er valgfri med standard «Alle aldersgrupper» pluss seks grupper (0–4, 5–14, 15–29, 30–64, 65–79, 80+). «Ukjent alder» godtas ikke.
- **Sesong:** uke 40 til og med uke 20 året etter, skrevet «2025/2026». Uke 53 er en vanlig uke. Sesongen som pågår slutter ved siste publiserte uke. Sesongene starter med 2024/2025.
- **Skjulte verdier** (`..`, `.`, `:`, tom) og uker FHI ikke sendte blir `None`, aldri `0`. Andel er `None` for manglende uker.
- **Manglende uke:** tester eller positive er `None`. **Usikker uke:** færre enn 30 tester, skjult antall tester, eller flere positive enn tester (andelen vises som den er, med fotnote; R2 teller fortsatt bare færre enn 30 tester). Endret 24. november 2026: Irenes beslutning i story 2.4.
- **Ugyldige utvalg** (manglende felt, ukjent verdi, manipulert URL som `../x`) gir en norsk melding om hva som må rettes, uten FHI-koder, og ingen henting.
- **Mellomlagring:** tall som er 24 timer eller eldre hentes på nytt (23 t 59 min er ferskt).
- **FHI nede:** tidsavbrudd etter 10 s, HTTP-feil eller ugyldig svar. Da brukes lagrede tall merket «sist lagrede», ellers sier svaret at det ikke finnes tall. Kontrollreglene gjelder også for lagrede tall.
- **Kontrollregler** beregnes over alle forventede uker i utvalget:
  - R1: summen av positive < 20 (19 → utslag, 20 → ikke). Skjulte verdier telles ikke.
  - R2: mer enn 20 % av ukene har et *kjent* antall tester < 30 (4/20 → ikke, 5/20 → utslag). 29 teller, 30 ikke. Skjult antall tester telles under R3, ikke R2.
  - R3: mer enn 20 % av ukene er manglende (2/10 → ikke, 3/10 → utslag). En uke med to skjulte verdier teller én gang.
  - R4: færre enn 3 uker med data (2 → utslag, 3 → ikke). Manglende uker er ikke uker med data.
  - R5: minst én uke starter før 1. mars 2025 og minst én slutter 1. mars 2025 eller senere. 2024/2025 gir alltid utslag, 2025/2026 og 2026/2027 aldri.
  - Reglene skal aldri svekkes for å gi færre varsler.
- **Kildehenvisning:** FHIs egen kildetekst (ordrett), tabellnummer, tabellnavn og hentedato. For 724: «Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, Folkehelseinstituttet (FHI).» og «RESPIaggr Influensa antall og andel».
- **Ferdigkriterier for hver story:** egne tester for akseptansekriteriene, `uv run pytest` består uten nett og uten nøkkel, `ruff check` og `ruff format --check` består, ingen import bryter avhengighetsretningen, og README oppdateres ved endret installering, oppstart, konfigurasjon eller tester.

## Technical Decisions

- **Ren kjerne:** `domene`, `sesong`, `kontrollregler` og tolkefunksjonene i `fhi` importerer aldri `httpx`, `anthropic`, `mellomlager`, `config` eller `web`, og får «nå» som argument (aldri `datetime.now()` inne i kjernen). Tillatte importer: `sesong`, `kontrollregler` og fhi-tolking → `domene`. Fhi-tolking → `sesong`. `fhi.hent` og `mellomlager` → `config`. `tjeneste` → alle disse.
- **`domene.py`** eier `Utvalg`, `Uke` (år, ukenummer, tester, positive, andel, avledede `usikker` og `manglende`), `Dataserie`, `Regelutslag`, `Kildehenvisning` og de faste listene (virus → tabell, aldersgrupper, maler). FHI-koder (`NONSTL`, `A+B`, `80+ år`, `pos_rate`) finnes bare i `domene.py` og `fhi.py`. Validering skjer bare i `Utvalg.fra_parametre(parametre, gyldige_sesonger)` (query-felt `mal`, `virus`, `sesong`, `alder`). `Utvalg.nøkkel` er den eneste koden som lager filnavn fra et utvalg, med bare trygge tegn og likt for like utvalg. Kildehenvisning lages bare av `domene.kildehenvisning(tabell, hentet)`.
- **`sesong.py`:** ISO-uker og sesonger, `sesonger_fra_dato(nå)` (reserve for sesonglisten) og `er_utdatert(hentet, nå)`. Begge tidspunktene må ha tidssone. Tid lagres i UTC.
- **`fhi.py`:** `fhi.hent(...)` er den eneste koden som kaller `statistikk-data.fhi.no`. Den bruker `httpx` med 10 s tidsgrense, og alle feil blir `FhiUtilgjengelig`. Dimensjonslisten hentes med en egen funksjon. `fhi.tolk(rått_svar, utvalg)` lager en `Dataserie` med én `Uke` per forventet uke i sesongen frem til siste publiserte uke. Siste publiserte uke og sesonglisten kommer fra den høyeste uken i dimensjonen `dateusedforstatistics`. Formatet er JSON (`json-stat2`). Forespørselen, FLAGG og særheter i formatet står i `backend/tests/fixtures/fhi/README.md`.
- **`config.py`:** `les_innstillinger()` gir en `Innstillinger`-dataklasse og er den eneste koden som leser miljøvariabler (`ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `CACHE_DIR`, `VERCEL`). Cachemappen er `CACHE_DIR`, ellers `/tmp/fhi-helsedata-cache` når `VERCEL` finnes, ellers `.cache/` i reporoten. Ingen modul laster `.env` ved import.
- **`mellomlager.py`:** den eneste koden som leser og skriver cachen. Filene heter `fhi/<Utvalg.nøkkel>.json` og `fhi/<tabell>-dimensjoner.json` og inneholder `{"hentet": <ISO 8601 UTC>, "svar": <rått FHI-svar>}`, samme format som fixturene. Skriving går via en midlertidig fil og `os.replace`. En fil som ikke kan leses, behandles som om den ikke finnes.
- **`kontrollregler.vurder(serie) -> list[Regelutslag]`:** `Regelutslag` har `regel` (`"R1"`–`"R5"`) og en ferdig setning på enkel norsk med de faktiske tallene, for eksempel «6 av 20 uker har færre enn 30 tester». Tom liste betyr ingen varsel.
- **`tjeneste.py`:** `svar(utvalg, nå)` gir `Dataserie`, `Regelutslag` og `Kildehenvisning` med hentetidspunkt, og en markering når tallene er «sist lagrede». `sesonger(nå)` gir sesonglisten. En lås per utvalg gjør at samtidige kall deler ett kall til FHI. `tjeneste` fanger `FhiUtilgjengelig` og logger tekniske detaljer med `logging` på nivå INFO.
- **Tester:** FHI mockes med `respx`, cachen bruker `tmp_path`, og testene lager `Innstillinger` direkte uten nøkkel. Grensetilfellene for R1–R5 ligger som konstruerte data i `tests/fixtures/konstruert/`. Fixturene `724-influensa-2025-2026-alle-nonstl.json` og `724-dimensjoner.json` i `tests/fixtures/fhi/` er grunnlaget for tolking og henting.
- **Navn:** moduler, funksjoner og dataklasser på norsk. Ord fra rammeverk og biblioteker beholdes på engelsk.

## Cross-Story Dependencies

- 2.1 er grunnlaget for alle andre stories.
- 2.2 tar listen over gyldige sesonger som argument. Listen lages i 2.3, 2.4 og 2.9.
- 2.4 bygger på 2.1, 2.3 og fixturene fra story 1.3. 2.5 bruker de samme fixturene med `respx`.
- 2.6 krever `Utvalg.nøkkel` (2.2) og `config`.
- 2.7 og 2.8 bygger på `Uke` og `Dataserie` (2.1) og skriver til samme `kontrollregler.vurder`.
- 2.9 setter sammen 2.3–2.8 og er det epic 3 (`GET /`) og epic 4 (`POST /hent-nyeste`, som tvinger ny henting) bygger på.
- RSV og SARS-CoV-2 kommer i epic 6. Listene i `domene` har dem fra start, men henting og kildetekst for 729 og 731 testes først der. Mal 2 (epic 8) kaller `vurder` én gang per sesong.
