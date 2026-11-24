---
title: 'Story 2.6: Mellomlagre FHI-svar'
type: 'feature'
created: '2026-11-24'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen kan ikke lagre et FHI-svar og vise det igjen uten nytt kall (issue #11). Uten mellomlagring blir siden treg, og den virker ikke når FHI er nede (FR-7, FR-8, NFR-2).

**Approach:** Lag `backend/src/backend/config.py` med `les_innstillinger()` og dataklassen `Innstillinger`. Cachemappen er `CACHE_DIR`, ellers `/tmp/fhi-helsedata-cache` når `VERCEL` finnes, ellers `.cache/` i reporoten (AD-4, AD-6). `.env` lastes bare når funksjonen kalles, aldri ved import. Lag `backend/src/backend/mellomlager.py`, som er den eneste koden som leser og skriver cachen. Den lagrer `fhi/<Utvalg.nøkkel>.json` og `fhi/<tabell>-dimensjoner.json` som `{"hentet": ..., "svar": ...}` via en midlertidig fil og `os.replace`, og leser dem tilbake med hentetidspunktet. En fil som ikke kan leses, regnes som at den ikke finnes. Tester med `tmp_path` i `backend/tests/test_config.py` og `backend/tests/test_mellomlager.py` dekker lagring, lesing, ødelagt fil og valg av cachemappe.

</frozen-after-approval>

## Implementation Notes

- Nye filer: `backend/src/backend/config.py`, `backend/src/backend/mellomlager.py`, `backend/tests/test_config.py` og `backend/tests/test_mellomlager.py`. Endret: README (ny miljøvariabel `CACHE_DIR`), `.env.example`, `deferred-work.md` (punktene fra story 1.1 og 1.5 er lukket) og `sprint-status.yaml`.
- `les_innstillinger(miljø=None, env_fil=<reporot>/.env)`: uten `miljø` lastes `env_fil` med `load_dotenv(override=True)` (AD-6), og så leses `os.environ`. Testene sender alltid inn `miljø` som en `dict`. Da lastes `.env` aldri, og `os.environ` brukes ikke (AD-10).
- `Innstillinger` har `anthropic_api_key: str | None`, `anthropic_model: str` (standard `claude-haiku-5-5`) og `cache_dir: Path`. En tom verdi (`ANTHROPIC_API_KEY=`, `ANTHROPIC_MODEL=`, `CACHE_DIR=`) regnes som ikke satt. En relativ `CACHE_DIR` regnes fra reporoten. Med `override=True` overskriver en tom verdi i `.env` en verdi fra skallet. Det er AD-6 («`.env` vinner over skallet»). Det løser punktet fra story 1.1 i deferred-work.md. `VERCEL` teller når variabelen finnes, også med tom verdi, slik AD-4 sier («miljøvariabelen `VERCEL` finnes»).
- `mellomlager` tar cachemappen (`Path`) som argument, ikke `Innstillinger`, slik at den er lett å teste med `tmp_path`. Funksjonene er `lagre_svar(mappe, utvalg, svar, hentet)`, `les_svar(mappe, utvalg)`, `lagre_dimensjoner(mappe, tabell, svar, hentet)` og `les_dimensjoner(mappe, tabell)`. `les_*` gir `Lagret(hentet, svar)` eller `None`.
- `hentet` må ha tidssone. Den lagres i UTC som `2026-11-23T21:20:15Z` (hele sekunder, samme format som fixturene) og leses tilbake med tidssone UTC.
- En fil regnes som ikke-eksisterende (`None`) hvis den mangler eller ikke kan leses (`OSError`), ikke er gyldig UTF-8 eller JSON, ikke har nøyaktig `hentet` og `svar`, har en `hentet` uten tidssone eller som ikke kan tolkes, eller har et `svar` som ikke er et JSON-objekt.
- Skriving: mappen lages ved behov. Innholdet skrives til en midlertidig fil i samme mappe (`.<navn>.<tilfeldig>.tmp`), og så kalles `os.replace`. Feiler skrivingen, slettes den midlertidige fila og `OSError` sendes videre. `tjeneste` (2.9) bestemmer hva som skjer da.

## Review Triage Log

Gjennomgang med `bmad-code-review` (Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor). Ingen alvorlige funn og ingenting som krever endring i PRD eller arkitektur.

- **medium, rettet (Verification Gap):** `test_import_av_config_laster_ikke_env` kunne ikke feile. Den la en falsk `.env` i `tmp_path`, men `config` leser `REPOROT/.env`, og `find_dotenv()` leter fra filens mappe, ikke fra arbeidsmappen. AST-testen så bare etter `ast.Expr`. Nå importeres `config` i en egen prosess med en falsk `dotenv` som registrerer kall, og AST-testen stopper `dotenv`-kall overalt utenfor funksjoner.
- **medium, rettet:** README-en sa at tall vises når FHI er nede og hentes på nytt etter 24 timer. Det bygges først i story 2.9, og README-en sier nå at det er planlagt. README-en og `.env.example` nevner nå Vercel og relative stier.
- **low, rettet:** en relativ `CACHE_DIR` var avhengig av mappen appen ble startet fra (`backend/` eller reporoten). Den regnes nå fra reporoten.
- **low, rettet:** `deferred-work.md` var ikke oppdatert, slik specen sa. Punktene fra story 1.1 og 1.5 er lukket.
- **low, rettet:** en `hentet` som `0001-01-01T00:30:00+01:00` ga `OverflowError` i stedet for `None`. Bekreftet.
- **low, rettet:** vakt-testene for miljøvariabler og filskriving lette etter få tekster. Nå sjekkes miljøvariablene med AST, og listen for filskriving er bredere. En test uten `.env`, `geteuid` på Windows og docstringer om `ValueError` er lagt til.
- **avvist:** `override=True` gjør at en tom `ANTHROPIC_API_KEY=` i `.env` overskriver en nøkkel i skallet. Det er AD-6 («`.env` vinner over skallet», for å hindre at appen plukker opp en nøkkel fra skallet). Det står nå i docstringen.
- **false:** en `hentet` frem i tid ville gjort tallene ferske for alltid. `sesong.er_utdatert` (story 2.3) regner alt mer enn fem minutter frem i tid som utdatert.
- **avvist (low):** `.tmp`-filer kan bli liggende hvis prosessen drepes mellom `mkstemp` og `os.replace`. De leses aldri, og cachen kan slettes. Det står i docstringen.
- **avvist (low):** ingen `fsync` av mappen etter `os.replace`, og filene får 0600. Det er en cache som kan hentes på nytt, og den brukes av én prosess. Det står i docstringen.
- **avvist (low):** fildeskriptoren lekker hvis `os.fdopen` feiler, og en feil i oppryddingen kan skjule den første feilen. Det skjer bare ved svært sjeldne feil.
- **avvist (low):** `REPOROT` forutsetter en klone (redigerbar installasjon). Det er slik appen kjøres (`uv sync`), og på Vercel vinner `VERCEL`. Det står i docstringen.
- **false:** specen mangler akseptkriterier. Det er en oneshot-spec, og akseptkriteriene står i issue #11.
