# Tillegg til PRD: tekniske detaljer om FHI-API-et

Hentet fra FHIs åpne API 20. november 2026. Dette er grunnlag for arkitektur og stories, ikke krav i seg selv.

## Endepunkter

- Metadata: `GET https://statistikk-data.fhi.no/api/open/v1/msis/Table/{tabell}/metadata`
- Dimensjoner: `GET https://statistikk-data.fhi.no/api/open/v1/msis/Table/{tabell}/dimension`
- Data: `POST https://statistikk-data.fhi.no/api/open/v1/msis/Table/{tabell}/data`

## Dimensjoner

| Dimensjonskode | 724 Influensa | 729 RSV | 731 SARS-CoV-2 | Verdi i v1 |
| --- | --- | --- | --- | --- |
| `dateusedforstatistics` | `2024-w40` … `2026-w46` | samme | samme | ukene i valgt sesong |
| `aldersgruppe` | `Alle`, `0-4 år`, `5-14 år`, `15-29 år`, `30-64 år`, `65-79 år`, `80+ år`, `Ukjent` | samme | samme | valgt aldersgruppe (`Alle` som standard) |
| `surveillancetype` | `NONSTL`, `STL` | samme | samme | `NONSTL` |
| `influenzatypeandsubtype` | `A+B`, `A`, `B` | – | – | `A+B` |
| `rsvtype` | – | `A`, `B`, `UNK`, `A+B` | – | `A+B` |
| `MEASURE_TYPE` | `Detections`, `Tests`, `pos_rate` | samme | samme | alle tre |

Svar i CSV-format har kolonnene «Påvisninger», «Testede», «Andel (%)» og «FLAGG». FLAGG-kolonnen er aktuell for å finne skjulte verdier (R3).

## Sjekk av RSV-totalen

Spørring mot tabell 729, alle aldersgrupper, Non-Sentinel:

| Uke | A | B | Ukjent | «RS-virus (A+B)» | Testede |
| --- | --- | --- | --- | --- | --- |
| 2025-w50 | 29 | 37 | 123 | 189 | 9 808 |
| 2025-w51 | 37 | 35 | 159 | 231 | 10 001 |

`A+B` er altså totalen, inkludert prøver med ukjent type. Etiketten «RS-virus (A+B)» er misvisende og bør ikke vises for brukeren.

## Sesong i metadataene for tabell 724

Metadataene har ingen sesongdimensjon. De sier at influensaepidemiene kommer fra desember til april, at sesongen navngis «2024/2025», og at tidsperioden er «Uke 40-2024-d.d.». Uke 20 som sluttuke står ikke der.

## Kildehenvisning foreslått av FHI

- 729: «Kilde: MSIS-labdatabase og Referanselaboratoriet for RS-virus, Folkehelseinstituttet (FHI).»
- 731: «Kilde: MSIS-labdatabase og Referanselaboratoriet for koronavirus med utbruddspotensiale, Folkehelseinstituttet (FHI).»
- 724: tilsvarende, med referanselaboratoriet for influensa. Ordlyden må sjekkes i metadataene.

FHI skal oppgis som kilde ved all presentasjon av tallene.
