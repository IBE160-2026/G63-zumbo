---
title: 'Story 2.6: Mellomlagre FHI-svar'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
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

- Nye filer: `backend/src/backend/config.py`, `backend/src/backend/mellomlager.py`, `backend/tests/test_config.py` og `backend/tests/test_mellomlager.py`. Endret: README (ny miljøvariabel `CACHE_DIR`), `.env.example` og `deferred-work.md`.
- `les_innstillinger(miljø=None, env_fil=<reporot>/.env)`: uten `miljø` lastes `env_fil` med `load_dotenv(override=True)` (AD-6), og så leses `os.environ`. Testene sender alltid inn `miljø` som en `dict`. Da lastes `.env` aldri, og `os.environ` brukes ikke (AD-10).
- `Innstillinger` har `anthropic_api_key: str | None`, `anthropic_model: str` (standard `claude-haiku-5-5`) og `cache_dir: Path`. En tom verdi (`ANTHROPIC_API_KEY=`, `ANTHROPIC_MODEL=`, `CACHE_DIR=`) regnes som ikke satt. Det løser punktet fra story 1.1 i deferred-work.md. `VERCEL` teller når variabelen finnes, også med tom verdi, slik AD-4 sier («miljøvariabelen `VERCEL` finnes»).
- `mellomlager` tar cachemappen (`Path`) som argument, ikke `Innstillinger`, slik at den er lett å teste med `tmp_path`. Funksjonene er `lagre_svar(mappe, utvalg, svar, hentet)`, `les_svar(mappe, utvalg)`, `lagre_dimensjoner(mappe, tabell, svar, hentet)` og `les_dimensjoner(mappe, tabell)`. `les_*` gir `Lagret(hentet, svar)` eller `None`.
- `hentet` må ha tidssone. Den lagres i UTC som `2026-11-23T21:20:15Z` (hele sekunder, samme format som fixturene) og leses tilbake med tidssone UTC.
- En fil regnes som ikke-eksisterende (`None`) hvis den mangler eller ikke kan leses (`OSError`), ikke er gyldig UTF-8 eller JSON, ikke har nøyaktig `hentet` og `svar`, har en `hentet` uten tidssone eller som ikke kan tolkes, eller har et `svar` som ikke er et JSON-objekt.
- Skriving: mappen lages ved behov. Innholdet skrives til en midlertidig fil i samme mappe (`.<navn>.<tilfeldig>.tmp`), og så kalles `os.replace`. Feiler skrivingen, slettes den midlertidige fila og `OSError` sendes videre. `tjeneste` (2.9) bestemmer hva som skjer da.
