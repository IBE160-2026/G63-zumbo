# Utsatt arbeid

## Deferred from: code review of spec-1-1-rydde-uv-prosjektet-og-holde-nokler-og-cache-utenfor-git.md (2026-11-22)

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-rydde-uv-prosjektet-og-holde-nokler-og-cache-utenfor-git.md`
  summary: `config.les_innstillinger()` må behandle tom `ANTHROPIC_MODEL` og tom `ANTHROPIC_API_KEY` som ikke satt (bruk `os.getenv(...) or standard`).
  evidence: `.env.example` har `ANTHROPIC_MODEL=` og `ANTHROPIC_API_KEY=` med tomme verdier (AC i story 1.1). Kopieres fila uendret til `.env`, setter python-dotenv (`override=True`, AD-6) begge til `""`. Da gir `os.environ.get(navn, standard)` `""`, og en tom nøkkel kan bli tolket som at nøkkelen finnes. README og `.env.example` lover nå at tom modell gir standardmodellen.
