# Status mot sensorveiledningen (del 1)

Skrevet 26.11.2026 som utkast. Irene går gjennom rapporten og krysser av i [sjekklisten](sjekkliste.md) selv.

**Kilder.** Selve sensorveiledningen ligger ikke i repoet. Rapporten følger de sju kriteriene og vektene slik de står i [tilbakemeldingen på product brief](tilbakemelding-product-brief.md) (§2), og punktene i [sjekklisten](sjekkliste.md), som bygger på sensorveiledningen. Sjekk kriteriene mot den fullstendige sensorveiledningen før innlevering.

**Tilstand 26.11.2026.** 345 commits på main. 33 PR-er er merget (#41–#75). Epic 1, 2, 3, 4 og 6 er ferdige. Epic 5 (brukertesting) og 7 (testsett og endelig README) er ikke startet. Epic 8 (mal 2 og Vercel) er strekkmål og valgfritt. Disse PR-ene er åpne og venter på gjennomgang:

| PR | Hva |
|---|---|
| [#76](https://github.com/IBE160-2026/G63-zumbo/pull/76) | Utkast til manus for brukertestingen (story 5.1) |
| [#77](https://github.com/IBE160-2026/G63-zumbo/pull/77) | README testet fra en ny klone (story 7.6) |
| [#78](https://github.com/IBE160-2026/G63-zumbo/pull/78) | Meldingen for ukjent mal viser spørsmålet |
| [#79](https://github.com/IBE160-2026/G63-zumbo/pull/79) | Færre kall til FHI når ingenting er lagret |

## Oversikt

| Kriterium | Vekt | Status | Det viktigste som mangler |
|---|---|---|---|
| 1. Prosess og KI-styring | 30 % | Godt i gang | KI-loggen har bare to oppføringer |
| 2. Funksjonalitet og omfang | 20 % | Kjerneflyten er ferdig | Én mal, ikke 3–5. Brukertesten er ikke gjort |
| 3. Kvalitetssikring og testing | 15 % | Godt i gang | Testsettet med 10 spørsmål og SM-4-gjennomgangen |
| 4. Design og brukeropplevelse | 10 % | Ferdig, ikke brukertestet | Brukertesten (SM-5, SM-6) |
| 5. Kodekvalitet og arkitektur | 10 % | Godt | Mappestrukturen i arkitekturen er utdatert |
| 6. README og kjørbarhet | 10 % | Nesten ferdig | PR #77, skjermbilde, testen for README-kommandoene |
| 7. Ryddighet i repoet | 5 % | Godt | Gå gjennom rotmappen før innlevering |

## 1. Prosess og KI-styring (30 %)

**Gjort**
- BMAD er satt opp i [`_bmad/`](../_bmad/), og planen ligger i [`_bmad-output/`](../_bmad-output/): [PRD](../_bmad-output/planning-artifacts/prds/prd-fhi-helsedata-2026-11-06/prd.md), [arkitektur](../_bmad-output/planning-artifacts/architecture/architecture.md), [epics og stories](../_bmad-output/planning-artifacts/epics.md) og [sprint-status](../_bmad-output/implementation-artifacts/sprint-status.yaml).
- Hver story har et issue (#1–#40), egen branch og en PR. Én spec per story ligger i [`_bmad-output/implementation-artifacts/`](../_bmad-output/implementation-artifacts/), og ting som er utsatt fra kodegjennomgangene, står i [`deferred-work.md`](../_bmad-output/implementation-artifacts/deferred-work.md).
- Beslutninger er skrevet ned med begrunnelse: i PRD-en (§11 «Avvik fra planen», for eksempel forsiden i FR-27 etter tilbakemelding fra en testperson) og i arkitekturen (AD-1 til AD-11, §1 om hvorfor `technology.md` ikke brukes).
- Planen er oppdatert når den endret seg, for eksempel PRD-en i [#59](https://github.com/IBE160-2026/G63-zumbo/pull/59) og sprint-status i hver story.
- Sesjonslogger for hver arbeidsøkt med KI ligger i [`.logs/irene-zumbo/`](../.logs/irene-zumbo/) (38 filer), med åpne punkter i [`issues.md`](../.logs/irene-zumbo/issues.md).
- Prompten til KI-forklaringen er skrevet av KI og rettet og godkjent av Irene ([#64](https://github.com/IBE160-2026/G63-zumbo/pull/64), [#65](https://github.com/IBE160-2026/G63-zumbo/pull/65)).

**Mangler**
- [`docs/ki-logg.md`](ki-logg.md) har bare to oppføringer, fra 6. og 14. oktober. Sjekklisten ber om prompt, kort svar, hva jeg gjorde og commit for hele veien. Det meste av KI-arbeidet står bare i `.logs/`.
- Sjekklistepunktet «Noter når KI-en tar feil, og hvordan jeg rettet det» er ikke samlet noe sted. Eksemplene ligger spredt i `.logs/` og i triagen i specene.

**Irene må selv**
- Bestemme om KI-loggen skal fylles ut med de viktigste øktene, eller om den skal lenke til `.logs/` og forklare hvordan den brukes. Det teller mest av alle kriteriene.
- Skrive noen eksempler på når KI-en tok feil og hvordan du rettet det. Kandidater fra denne uka: `setup-uv@v10`, som ikke fantes ([#75](https://github.com/IBE160-2026/G63-zumbo/pull/75)), og et utkast til manus som du retter selv ([#76](https://github.com/IBE160-2026/G63-zumbo/pull/76)).

## 2. Funksjonalitet og omfang (20 %)

**Gjort**
- Kjerneflyten virker for alle tre virus: velg virus på forsiden, så hent, graf, tabell, begrepsforklaringer, varsel og KI-forklaring (epic 2, 3, 4 og 6, PR [#47](https://github.com/IBE160-2026/G63-zumbo/pull/47)–[#73](https://github.com/IBE160-2026/G63-zumbo/pull/73)).
- Varselet om tynt datagrunnlag følger faste regler R1–R5 i [`kontrollregler.py`](../backend/src/backend/kontrollregler.py) ([#53](https://github.com/IBE160-2026/G63-zumbo/pull/53), [#58](https://github.com/IBE160-2026/G63-zumbo/pull/58)).
- Graf, tabell og varsel virker uten KI-nøkkel. Det er sjekket fra en ny klone i [#77](https://github.com/IBE160-2026/G63-zumbo/pull/77).
- Feil input gir norske meldinger (FR-5, [#48](https://github.com/IBE160-2026/G63-zumbo/pull/48), [#78](https://github.com/IBE160-2026/G63-zumbo/pull/78)). Når FHI er nede, vises de sist lagrede tallene med dato ([#52](https://github.com/IBE160-2026/G63-zumbo/pull/52), [#54](https://github.com/IBE160-2026/G63-zumbo/pull/54), [#56](https://github.com/IBE160-2026/G63-zumbo/pull/56)).
- Ekstra: «Hent nyeste tall nå» ([#69](https://github.com/IBE160-2026/G63-zumbo/pull/69)) og forsiden med viruskort ([#73](https://github.com/IBE160-2026/G63-zumbo/pull/73)).

**Mangler**
- Sjekklisten sier «3–5 maler». Appen har én mal (andel positive uke for uke) for tre virus. Mal 2 (to sesonger) er et strekkmål (#38, #39), og mal 3 og 4 er tatt ut i PRD §9.
- Fritekst er ikke bygget. Det er et strekkmål og står under Vision i briefen, så det er i tråd med planen.

**Irene må selv**
- Bestemme om mal 2 skal bygges, eller om valget av én mal for tre virus skal begrunnes i PRD §11 og i README-en. Sensor sammenligner med «3–5 maler».

## 3. Kvalitetssikring og testing (15 %)

**Gjort**
- 905 tester på main (915 med PR #78 og #79) som kjører uten nett og uten nøkkel (`pytest-socket`, [#43](https://github.com/IBE160-2026/G63-zumbo/pull/43)).
- Lagrede svar fra FHI og KI ligger i [`backend/tests/fixtures/`](../backend/tests/fixtures/): ekte svar for tabell 724, 729 og 731 i `fhi/`, en KI-forklaring i `ki/`, og grensetilfeller for R1–R5 i `konstruert/`.
- Tester for henting og tolking mot kjente tall (`test_fhi_*.py`), for reglene (`test_kontrollregler.py`) og for sidene (`test_web_*.py`).
- GitHub Actions kjører pytest og ruff på hver PR ([#75](https://github.com/IBE160-2026/G63-zumbo/pull/75), issue #74).
- Sjekklisten for KI-forklaringene står i PRD-en (FR-21, SM-4).
- Kodegjennomgang med `bmad-code-review` for hver story, med triage i specen.

**Mangler**
- Testsettet med 10 spørsmål og fasit (SM-1, SM-2, SM-3) er ikke laget (story 7.1–7.3, #32–#34). `tests/fixtures/testsett/` fra arkitekturen finnes ikke ennå.
- KI-forklaringene for testsettet er verken lagret eller gått gjennom mot FR-21 (story 7.4 og 7.5, #35, #36).
- Brukertesten (SM-5, SM-6) er ikke gjort (story 5.1, #28). Manuset er et utkast i [#76](https://github.com/IBE160-2026/G63-zumbo/pull/76).

**Irene må selv**
- Velge de 10 testspørsmålene og hente fasit manuelt fra FHI (story 7.1, #32).
- Gå gjennom KI-forklaringene mot FR-21 (story 7.5, #36).
- Rette manuset, skrive fasit og kjøre brukertesten med fem personer (story 5.1, #28).

## 4. Design og brukeropplevelse (10 %)

**Gjort**
- Skisse av hovedskjermen i PRD §6.0.
- Faste farger, skrift og avstander i [`style.css`](../backend/src/backend/static/style.css), med egne tester i `test_stil.py`. Designjusteringer i [#62](https://github.com/IBE160-2026/G63-zumbo/pull/62) og [#63](https://github.com/IBE160-2026/G63-zumbo/pull/63).
- Tilgjengelighet og mobil i story 3.7 ([#61](https://github.com/IBE160-2026/G63-zumbo/pull/61)): kontrast, tastaturnavigasjon, alternativtekst på grafen (NFR-6) og usikre uker merket med tekst, ikke bare farge.
- Forståelige feilmeldinger og tomtilstander, for eksempel «Tallene kan ikke vises akkurat nå» og «FHI har ikke publisert tall for sesongen … ennå».
- Forsiden ble laget etter tilbakemelding fra en testperson ([#73](https://github.com/IBE160-2026/G63-zumbo/pull/73)), og Irene sjekket den med Tab og i et smalt vindu.

**Mangler**
- Brukertesten med fem personer (SM-5, SM-6), og story 5.2 om å skrive om ord testpersonene ikke forsto.

**Irene må selv**
- Kjøre brukertesten og skrive resultatet inn i #28.
- Sjekke appen på en ekte mobil, ikke bare i et smalt vindu.

## 5. Kodekvalitet og arkitektur (10 %)

**Gjort**
- Arkitekturdokumentet begrunner mellomlagring i JSON-filer i stedet for database (AD-4), og SQLAlchemy er fjernet ([#41](https://github.com/IBE160-2026/G63-zumbo/pull/41)).
- Rene funksjoner skilt fra nett og filer (AD-1). Bare `fhi.py` kaller FHI, og det er testet.
- ruff for lint og formatering, også i CI.
- Død kode er ryddet underveis i triagen, for eksempel veien for virus som ikke var klare (story 6.2).

**Mangler**
- Mappestrukturen i arkitektur §6 er utdatert. Den nevner `index.html` og `_forklaring.html`, som nå er `forside.html`, `resultat.html` og `_ki_tekster.html`. `formatering.py` og `backend/scripts/` mangler, og `[tool.vercel]` står ikke i `pyproject.toml`.
- AD-3 sier at siste publiserte uke kommer fra dimensjonslisten for tabellen. Hvis #79 merges, må AD-3 oppdateres (forslaget står i PR-en).
- `Mal.tittel` brukes ikke lenger i koden hvis [#78](https://github.com/IBE160-2026/G63-zumbo/pull/78) merges.

**Irene må selv**
- Oppdatere arkitektur §6 og eventuelt AD-3 (for eksempel med `bmad-architecture`), eller be om det.

## 6. README og kjørbarhet (10 %)

**Gjort**
- [README](../README.md) med installering med uv, testkommandoer, oppstart, `.env.example` og hva som virker uten nøkkel ([#46](https://github.com/IBE160-2026/G63-zumbo/pull/46) og senere stories).
- Fulgt fra en ny klone 25.11.2026: alt virket. Rettelsene ligger i [#77](https://github.com/IBE160-2026/G63-zumbo/pull/77): hva appen gjør, data og kilde, begrensninger, installering av uv, mappeoversikt og lenker til BMAD-dokumentene og KI-loggen.
- Appen krever ingen betalt konto. KI-nøkkelen er valgfri.

**Mangler**
- [#77](https://github.com/IBE160-2026/G63-zumbo/pull/77) er ikke merget.
- Ingen skjermbilde i README-en (sjekklisten sier «gjerne»).
- Den automatiske testen som sjekker at kommandoene i README-en finnes (siste kriterium i #37).
- Windows-kommandoene i README-en er ikke prøvd.

**Irene må selv**
- Gå gjennom og merge [#77](https://github.com/IBE160-2026/G63-zumbo/pull/77), og notere testen fra en ny klone i #37 med dato.
- Ta et skjermbilde av forsiden og resultatsiden hvis du vil ha det med.

## 7. Ryddighet i repoet (5 %)

**Gjort**
- `.gitignore` holder ute `.venv`, `.env`, `.cache/` og andre cache-filer, og det er testet i `test_gitignore.py`.
- Ingen `.env` er noen gang lagt til i git-historikken, og ingen tekst som ligner en Anthropic-nøkkel (`sk-ant-…`) finnes i historikken (sjekket 26.11.2026).
- Duplikatbriefen i rotmappen er fjernet. Testdata ligger i `backend/tests/fixtures/`.
- Rotmappen har bare `README.md`, `CLAUDE.md`, `.env.example`, `.gitignore` og mappene `backend/`, `docs/`, `_bmad/`, `_bmad-output/`, `.github/`, `.claude/` og `.logs/`.

**Mangler**
- Ingenting kjent.

**Irene må selv**
- Bestemme om `.claude/` og `.logs/` skal ligge i repoet ved innlevering, og i så fall nevne dem i README-en (det gjør #77).
- Sjekke på nytt rett før fristen at alt er committet og pushet.

## Det Irene må gjøre, samlet

1. Fylle ut eller lenke opp KI-loggen, med eksempler på når KI-en tok feil (kriterium 1, 30 %).
2. Gå gjennom og merge #76, #77, #78 og #79.
3. Velge de 10 testspørsmålene med fasit (#32), og gå gjennom KI-forklaringene (#36).
4. Kjøre brukertesten (#28) og skrive om ord etterpå (#29).
5. Bestemme om mal 2 skal bygges, eller begrunne én mal i PRD §11.
6. Oppdatere arkitektur §6 (og AD-3 hvis #79 merges).
7. Krysse av i sjekklisten.
