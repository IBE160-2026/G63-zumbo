# Lagrede svar fra FHI

Ekte svar fra FHIs åpne API, hentet én gang manuelt. Testene leser bare disse
filene og kaller aldri FHI.

Hver fil har samme format som cachen (AD-4):

```json
{"hentet": "<ISO 8601 i UTC>", "svar": <rått svar fra FHI>}
```

| Fil | Forespørsel | Hentet |
| --- | --- | --- |
| `724-dimensjoner.json` | `GET https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension` | 23.11.2026 |
| `724-influensa-2025-2026-alle-nonstl.json` | `POST https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data`, se kroppen under | 23.11.2026 |

Kroppen i `POST`-forespørselen. Alle dimensjoner må være med. Ukene er de 33
ukene fra `2025-w40` til `2026-w20` i dimensjonslisten:

```json
{
  "dimensions": [
    {"code": "dateusedforstatistics", "filter": "item", "values": ["2025-w40", "…", "2026-w20"]},
    {"code": "aldersgruppe", "filter": "item", "values": ["Alle"]},
    {"code": "influenzatypeandsubtype", "filter": "item", "values": ["A+B"]},
    {"code": "surveillancetype", "filter": "item", "values": ["NONSTL"]},
    {"code": "MEASURE_TYPE", "filter": "item", "values": ["Detections", "Tests", "pos_rate"]}
  ],
  "response": {"format": "json-stat2"}
}
```

## Valg: JSON (`json-stat2`), ikke CSV

FHI kan svare med `json-stat2`, `csv2` (norske etiketter), `csv3` (koder) eller
`parquet`. Vi bruker `json-stat2`:

- Svaret lagres som et vanlig JSON-objekt i `svar`, ikke som en CSV-tekst inne i
  JSON.
- Tallene har riktig type (`64`, `0.9112915`), så vi slipper å tolke semikolon,
  anførselstegn og desimaltegn.
- Både kodene (`NONSTL`, `pos_rate`) og etikettene («Non-Sentinel»,
  «Andel (%)») står i `dimension`.
- `updated` sier når FHI sist endret tabellen.

Verdiene ligger i én flat liste, `value`. Rekkefølgen følger `id` og `size`:
uke først, måltall sist. Uke `2025-w40` er altså de tre første tallene:
påvisninger, testede og andel.

## FLAGG

FLAGG forteller hvorfor en verdi mangler. Sjekket 23.11.2026:

- `GET …/Table/724/flag` gir bare ett flagg: `0`, «Verdi finnes i tabellen».
- I `csv3` er FLAGG-kolonnen `"0"` på hver rad. I `csv2` er den tom (`""`).
- I `json-stat2` ligger flaggene i `status` og `extension.flags`. I dette svaret
  er `status` en tom streng og `extension.flags` er tom.
- En bredere spørring (alle aldersgrupper, `NONSTL` og `STL`, `A+B`, `A` og
  `B`, hele sesongen) ga 4 752 verdier uten `null` og uten andre flagg.

Ekte data for tabell 724 har altså ingen skjulte verdier nå. Skjulte og
manglende verdier må derfor testes med konstruerte data i
`tests/fixtures/konstruert/`.
