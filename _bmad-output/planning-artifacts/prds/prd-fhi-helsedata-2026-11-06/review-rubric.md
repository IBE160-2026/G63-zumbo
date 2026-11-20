# Gjennomgang av PRD mot sjekklisten — FHI Helsedata-utforsker

Gjennomgått 2026-11-20 mot `.claude/skills/bmad-prd/assets/prd-validation-checklist.md`. Eksemplene i PRD-en ble sjekket mot ekte tall fra FHIs API samme dag (tabell 729: RSV 0–4 og 80+ år; tabell 731: SARS-CoV-2, alle aldersgrupper; overvåkingstype vanlig klinisk praksis).

**Karakter:** Middels (Fair) — tre funn med høy alvorlighet, ingen kritiske.

## Samlet vurdering

Kravene er konkrete, har ID-er og grenseverdier, og regelen for tynt datagrunnlag kan testes. Det svake punktet er at flere eksempler ikke stemmer med de ekte tallene. Med vanlig klinisk praksis har alle utvalgene vi sjekket minst 129 tester per uke og ingen skjulte verdier, så R2 og R3 slår ikke inn. Eksemplet i UJ-2 og varselet i skissen er dermed feil, og mal 2-eksemplet i FR-24 kan ikke lenger velges. Uten rettelse vil stories og brukertester bygges på tilfeller som ikke finnes.

## Beslutningsklarhet — god (adequate)

Valgene står som beslutninger med begrunnelse: overvåkingstype (§4), sesong (§4), minst tre uker (FR-17) og grensene i R1–R5. Det PRD-en ikke sier, er hva valget av vanlig klinisk praksis koster for varselet. R2 og R3 blir i praksis regler som bare slår inn i konstruerte testdata.

### Funn
- **high** R2 og R3 slår ikke inn i ekte data (§6.5, FR-15, FR-16). Minste antall tester per uke er 129 (SARS-CoV-2, 5–14 år, 2025/2026), og ingen uker har skjulte verdier. Varsler i ekte data kommer fra R1 (smale aldersgrupper tidlig i sesongen som pågår, for eksempel RSV 80+ år 2026/2027 med 6 positive) og R5 (2024/2025). *Rett:* Skriv det i §6.5 og i SM-3, og si at R2 og R3 testes med konstruerte data.
- **low** R4 slår alltid inn i de to første ukene av en ny sesong (FR-17). Det er riktig oppførsel, men står ikke. *Rett:* Legg det til som konsekvens.

## Innhold fremfor pynt — sterk (strong)

Én persona, og den bærer reisene. NFR-ene har tall (5 s, 4,5:1, 3:1, 360 px). Visjonen er spesifikk for MSIS-data og beredskap.

### Funn
- **low** NFR-3 «enkle ord» er et adjektiv uten grense. *Rett:* Knytt kravet til brukertestingen (SM-5).

## Strategisk sammenheng — sterk (strong)

Tesen er tydelig: et raskt og ærlig situasjonsbilde, der varselet er like viktig som tallene. Rekkefølgen (influensa først, så RSV og SARS-CoV-2, deretter mal 2) følger av den. Suksesskriteriene måler korrekthet og forståelse, og motvektene SM-C1 og SM-C2 hindrer at varsler svekkes.

## Hva «ferdig» betyr — god (adequate)

De fleste FR-ene har testbare konsekvenser med grenseverdier.

### Funn
- **medium** FR-8 «bruker for lang tid» har ingen grense. *Rett:* Sett en tidsgrense, merket som antakelse.
- **medium** FR-7: «fornyes når de er eldre enn neste publisering» er ulogisk, fordi data ikke kan være eldre enn en publisering som ikke har skjedd. *Rett:* Data hentet før siste publisering (torsdag) regnes som utdaterte.
- **medium** SM-5: «svarer riktig» sier ikke hva som er riktig, eller hvem som vurderer. *Rett:* Fasit skrives før testen, og to i gruppen vurderer svarene.
- **medium** Kildehenvisningen er ulikt beskrevet: §3 sier tabellnummer og hentedato, FR-12 sier også tabellnavn, og skissen viser den bare under KI-forklaringen, mens FR-12 sier under graf og tabell. *Rett:* Samme innhold i §3 og FR-12, og kildelinje under graf og tabell i skissen.

## Ærlig omfang — sterk (strong)

Ikke-mål og «Ikke med nå» er konkrete. Tre antakelser og tre åpne spørsmål er rimelig for et studentprosjekt.

### Funn
- **high** UJ-2 og varselet i skissen bruker eksempler som ikke stemmer (§2.3, §6.0). RSV 80+ år i 2024/2025 har ingen uker med færre enn 30 tester, og «6 av 20 uker har færre enn 30 tester» forekommer ikke i ekte data. *Rett:* Bruk et utvalg der R1 slår inn (RSV 80+ år i sesongen som pågår), og merk tallene i skissen som illustrasjon.

## Bruk videre (arkitektur, stories) — god (adequate)

Begrepslisten finnes og brukes stort sett likt. ID-ene er sammenhengende.

### Funn
- **high** FR-24: «Sammenligning av 2025/2026 med 2024/2025 gir alltid varsel etter R5» kan ikke velges. Mal 2 har ikke valg av sesong, og «denne sesongen» er 2026/2027. *Rett:* Beskriv sammenligningen som faktisk gjøres (2026/2027 mot 2025/2026, ingen R5), og at R5 bare slår inn hvis forrige sesong er 2024/2025.

## Form — sterk (strong)

Fire brukerreiser er passe for en app med én brukertype og tydelige feiltilfeller.

## Mekaniske merknader

- ID-ene er sammenhengende og unike: FR-1–FR-24, NFR-1–NFR-11, SM-1–SM-6, SM-C1–SM-C2 og UJ-1–UJ-4.
- Alle `[ANTAKELSE]`-merker i teksten står i kapittel 13, og omvendt.
- UJ-4 har ingen navngitt person («en medstudent»). Det er greit, fordi reisen handler om oppsett og ikke om brukeren.
