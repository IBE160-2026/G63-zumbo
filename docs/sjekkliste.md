# Sjekkliste – IBE160 mappe, del 1

Basert på tilbakemeldingen på product brief (2026-10-06) og sensorveiledningen for del 1.
Kryss av ved å endre `[ ]` til `[x]`. Tallene i parentes viser hvilket kriterium i sensorveiledningen punktet hører til.

## Hele veien

- [ ] Commit ofte: små endringer med beskrivende meldinger (krit. 1)
- [ ] Før KI-loggen (`docs/ki-logg.md`): prompt, kort svar, hva jeg gjorde og commit (krit. 1)
- [ ] Noter når KI-en tar feil, og hvordan jeg rettet det (krit. 1 og 3)
- [ ] Ett issue per story, egen branch, og merge med pull request (krit. 1)
- [ ] Skriv ned viktige beslutninger med begrunnelse (krit. 1)
- [ ] Aldri legg API-nøkler eller `.env` i repoet (krit. 7)

## 1. Rette product brief

- [ ] Executive Summary og Solution beskriver malbasert v1
- [ ] Fritekst er flyttet til Vision
- [ ] Én hovedbruker er valgt
- [ ] Det står hva KI-en gjør i v1 (skriver forklaringen til tallene)
- [ ] Fast regel for «for tynt datagrunnlag» er bestemt
- [ ] Suksesskriterier med testsett: 10 malspørsmål med fasit hentet manuelt
- [ ] Kriteriet om bestått eksamen er byttet ut med et produktkriterium
- [ ] Duplikatbriefen i rotmappen er slettet
- [ ] Endringene er committet

## 2. Planlegging med BMAD

- [ ] BMAD er satt opp i repoet
- [ ] PRD med alle maler og datasett i v1
- [ ] Skisse av hovedskjermen: valg av mal, graf, forklaring og varsel (krit. 4)
- [ ] Arkitekturdokument som begrunner database eller mellomlagring (krit. 5)
- [ ] Epics og stories
- [ ] Dokumentene oppdateres når planen endrer seg (krit. 1)

## 3. Bygge appen

- [ ] 3–5 maler som henter, viser og forklarer riktige tall
- [ ] Varsel når det er for lite data
- [ ] Graf og tall virker uten KI-nøkkel
- [ ] Feilhåndtering ved feil input og når FHI-API-et ikke svarer
- [ ] Fritekst først når kjerneflyten er ferdig og testet (strekkmål)

## 4. Testing (krit. 3)

- [ ] Lagrede svar fra FHI og KI ligger i en egen testmappe, f.eks. `tests/fixtures/`
- [ ] Tester for henting og graf mot kjente tall
- [ ] Tester for regelen om for lite data
- [ ] Sjekkliste for å vurdere KI-forklaringene
- [ ] Testsettet med 10 spørsmål er kjørt, og resultatet er dokumentert
- [ ] Alle tester kjører uten nett og uten nøkkel

## 5. Design (krit. 4)

- [ ] Konsistente farger, skrift og avstander
- [ ] Grafer som kan leses uten å skille farger
- [ ] God kontrast, tastaturnavigasjon og alternativtekst på grafer
- [ ] Forståelige feilmeldinger og tomtilstander
- [ ] Fungerer på både mobil og PC

## 6. Kode (krit. 5)

- [ ] Mappestrukturen stemmer med arkitekturdokumentet
- [ ] Ingen død kode eller rester fra forkastede KI-forsøk
- [ ] Linter eller formatter i bruk, f.eks. ruff

## 7. README (krit. 6)

- [ ] Hva appen gjør og hvem den er for, gjerne med skjermbilde
- [ ] Forutsetninger med versjoner (Python, uv)
- [ ] Steg-for-steg oppstart med kommandoer som kan kopieres
- [ ] `.env.example` og forklaring av hva som virker uten nøkkel
- [ ] Hvordan testene kjøres
- [ ] Oversikt over mappene og lenker til BMAD-dokumentene og KI-loggen
- [ ] Testet: fulgt README fra en ny klone av repoet

## 8. Før innlevering

- [ ] `.gitignore` holder ute `.venv`, `.env` og cache-filer (krit. 7)
- [ ] Ingen nøkler i commit-historikken (krit. 7)
- [ ] Ingen løse eller gamle filer i rotmappen (krit. 7)
- [ ] Planleggingsdokumentene stemmer med appen, og avvik er forklart (krit. 1 og 2)
- [ ] Alle tester består (krit. 3)
- [ ] Alt er committet og pushet før fristen
