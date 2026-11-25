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
| `729-dimensjoner.json` | `GET https://statistikk-data.fhi.no/api/open/v1/msis/Table/729/dimension` | 25.11.2026 |
| `729-rsv-2025-2026-alle-nonstl.json` | `POST https://statistikk-data.fhi.no/api/open/v1/msis/Table/729/data`, se kroppen under | 25.11.2026 |
| `731-dimensjoner.json` | `GET https://statistikk-data.fhi.no/api/open/v1/msis/Table/731/dimension` | 25.11.2026 |
| `731-sars-cov-2-2025-2026-alle-nonstl.json` | `POST https://statistikk-data.fhi.no/api/open/v1/msis/Table/731/data`, se kroppen under | 25.11.2026 |

Kroppen i `POST`-forespørselen, sendt med `Content-Type: application/json`.
Alle dimensjoner må være med. `…` står for resten av ukene: i den ekte
forespørselen er `values` alle de 33 ukene fra `2025-w40` til `2026-w20`, i
samme rekkefølge som i dimensjonslisten (`2025-w40`, `2025-w41`, …,
`2025-w52`, `2026-w01`, …, `2026-w20`). ISO-året 2025 har ingen uke 53.

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

For tabell 729 (RSV) er kroppen den samme, bortsett fra at
`influenzatypeandsubtype` er byttet ut med `rsvtype`:

```json
{"code": "rsvtype", "filter": "item", "values": ["A+B"]}
```

`A+B` er totalen, også prøver med ukjent type (se PRD-ens addendum). FHI kaller
den «RS-virus (A+B)». Den etiketten vises ikke i appen. I svaret fra 729 kommer
`surveillancetype` før `rsvtype` i `id`. Tolkingen bruker `id` og `size`, så
rekkefølgen spiller ingen rolle. `GET …/Table/729/flag` gir også bare flagg `0`
(sjekket 25.11.2026).

For tabell 731 (SARS-CoV-2) er kroppen den samme, men uten typedimensjon:
`influenzatypeandsubtype` er tatt ut, og ingen annen dimensjon er lagt til.
Tabellen har ingen inndeling i virustyper. I svaret fra 731 står
`aldersgruppe` først i `id`, foran ukene. `GET …/Table/731/flag` gir også bare
flagg `0` (sjekket 25.11.2026).

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
påvisninger, testede og andel (`64`, `7023`, `0.9112915`).

Dette må tolkingen passe på:

- Ukedimensjonen må finnes med koden `dateusedforstatistics`. `role.time` er
  `null`, så den kan ikke finnes ut fra rollen.
- Ukekodene har formen `ÅÅÅÅ-wUU` med liten `w` (`2025-w40`).
- I dimensjonslisten ligger aldersgruppene som `children` under `Alle`, ikke
  ved siden av den.
- I dimensjonslisten har kategoriene for `MEASURE_TYPE` `"children": null`.
  De andre dimensjonene har `[]`.

## FLAGG

FLAGG forteller hvorfor en verdi mangler. Sjekket 23.11.2026:

- `GET …/Table/724/flag` gir bare ett flagg: `0`, «Verdi finnes i tabellen».
- I `csv3` er FLAGG-kolonnen `"0"` på hver rad. I `csv2` er den tom (`""`).
- I `json-stat2` ligger flaggene i `status` og `extension.flags`. I dette svaret
  er `status` en tom streng og `extension.flags` er tom.
- En bredere spørring (alle aldersgrupper, `NONSTL` og `STL`, `A+B`, `A` og
  `B`, hele sesongen) ga 4 752 verdier uten `null` og uten andre flagg.

Ekte data for tabell 724 har altså ingen skjulte verdier nå. Vi har derfor
ikke sett hvordan en skjult verdi ser ut i `json-stat2` fra FHI. Etter
JSON-stat-formatet blir den `null` i `value`, og da er `status` et objekt eller
en liste med et flaggsymbol for den plassen i stedet for en tom streng.
Flaggsymbolet forklares i `extension.flags`. Dette er en antakelse, ikke noe vi
har sett.

Skjulte og manglende verdier må derfor testes med konstruerte data i
`backend/tests/fixtures/konstruert/`, i samme `json-stat2`-form som her.
