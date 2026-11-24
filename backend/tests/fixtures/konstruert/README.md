# Konstruerte data

Data vi har laget selv for å teste tilfeller som ikke finnes i de ekte svarene fra FHI. Formatet er det samme som cachen og `../fhi/` (AD-4).

| Fil | Hva den viser | Brukes i |
| --- | --- | --- |
| `724-skjulte-verdier.json` | Influensa, 80+ år, 2026/2027, uke 40–46. Uke 40 er vanlig. Uke 41 har `..` som tester, uke 42 har `.` som positive, uke 43 har `:` og tom verdi, uke 44 mangler i svaret, uke 45 har `null` som positive, og uke 46 har 0 positive av 29 tester. | `test_fhi_tolk.py` (story 2.4) |

Skjulte verdier i `json-stat2` er ikke sett i ekte data fra FHI (se `../fhi/README.md`). Svaret tar derfor med både `null` og tekstene `..`, `.`, `:` og tom verdi.
