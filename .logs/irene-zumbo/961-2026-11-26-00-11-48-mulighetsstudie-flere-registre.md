# Mulighetsstudie: flere registre

## 2026-11-26 kl. 00:11 — Irene Zumbo

### Oppgave
En mulighetsstudie for Vision, uten endringer i appen: finnes genomovervåkning (NGS, varianter av SARS-CoV-2 og influensa) og vaksinasjonsdekning (SYSVAK, influensa og covid-19) i FHIs åpne API, hvordan ser dataene ut, og hva ville det kreve å ta dem inn i appen? Resultatet skulle ligge i `docs/mulighetsstudie-flere-registre.md` på en egen branch, med en PR mot ibe som ikke merges.

### Plan
- Gjøre noen få kall mot `statistikk-data.fhi.no/api/open/v1/` (12 i alt): kildeliste, tabellister, dimensjoner, metadata og noen datautvalg.
- Sammenligne med hvordan appen henter og tolker MSIS (`fhi.py`, `domene.py`, `kontrollregler.py`) og med PRD-en og briefens Vision.
- Skrive studien med kilder, en vurdering av hvor stort arbeidet er, og en anbefaling.

### Resultat
- `docs/mulighetsstudie-flere-registre.md` på branchen `mulighetsstudie-flere-registre` (commit på branchen), PR #81 i IBE160-2026/G63-zumbo. PR-en er ikke merget.
- Funn: begge kildene finnes i det åpne API-et (`ngs`, `sysvak`). NGS har månedstall, ingen aldersgrupper og ny tabell for hver sesong, og november har bare 7 sekvenser. SYSVAKs ukestabeller (928, 955) viser antall vaksinasjoner, ikke dekning. Dekning i % finnes bare per sesong for 65+ og 75+ (753, 751, 750), med tall per fylke og kommune. SYSVAK bruker de samme skjulte verdiene som MSIS (`:`), men et annet ukeformat (`2026.36`).
- Anbefaling: begynne med vaksinasjonsdekning 65+ (5–7 stories) og vente med varianter (6–8 stories).
- Statistikkbanken (statistikk.fhi.no) ble ikke åpnet.

### Åpne punkter
- Irene: lese og vurdere mulighetsstudien i PR #81 (ikke merget).
- Spørre FHI om lav dekning i SYSVAK før ca. 2020 skyldes registreringen, og om det finnes en stabil måte å finne NGS-tabellene for hver sesong på.
