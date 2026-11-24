# Konstruerte data

Data vi har laget selv for å teste tilfeller som ikke finnes i de ekte svarene fra FHI. Formatet er det samme som cachen og `../fhi/` (AD-4).

| Fil | Hva den viser | Brukes i |
| --- | --- | --- |
| `724-skjulte-verdier.json` | Influensa, 80+ år, 2026/2027, uke 40–46. Uke 40 er vanlig. Uke 41 har `..` som tester, uke 42 har `.` som positive, uke 43 har `:` og tom verdi, uke 44 mangler i svaret, uke 45 har `null` som positive, og uke 46 har 0 positive av 29 tester. | `test_fhi_tolk.py` (story 2.4) |
| `724-r1-19-positive.json` | Influensa, alle aldre, 2025/2026, uke 40–49. 19 kjente positive. Uke 44 har `..` som positive. R1 slår inn. | `test_kontrollregler.py` (story 2.7) |
| `724-r1-20-positive.json` | Som over, men med 20 kjente positive. R1 slår ikke inn. | `test_kontrollregler.py` (story 2.7) |
| `724-r2-4-av-20-uker.json` | Influensa, alle aldre, 2025/2026, 20 uker (uke 40 i 2025 til uke 7 i 2026). 4 uker har færre enn 30 tester (29, 20, 10 og 0). I tillegg en uke med 30 tester, en med `..` som tester og en med 45 positive av 40 tester. Ingen av de tre teller i R2, så R2 slår ikke inn. | `test_kontrollregler.py` (story 2.7) |
| `724-r2-5-av-20-uker.json` | Som over, men uke 3 i 2026 har også 29 tester. 5 av 20 uker gir utslag i R2. | `test_kontrollregler.py` (story 2.7) |
| `724-r3-2-av-10-uker.json` | Influensa, alle aldre, 2025/2026, uke 40–49. Uke 42 har to skjulte verdier (`.` og `..`), og uke 45 har `:` som positive. 2 av 10 uker er manglende, så R3 slår ikke inn. | `test_kontrollregler.py` (story 2.7) |
| `724-r3-3-av-10-uker.json` | Som over, men uke 47 mangler i svaret. 3 av 10 uker gir utslag i R3. | `test_kontrollregler.py` (story 2.7) |

Skjulte verdier i `json-stat2` er ikke sett i ekte data fra FHI (se `../fhi/README.md`). Svaret tar derfor med både `null` og tekstene `..`, `.`, `:` og tom verdi.
