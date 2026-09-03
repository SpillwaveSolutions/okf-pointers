# AGENTS.md — okf-pointers

Dual-host agent plugin (Claude Code + Grok Build + Codex).

## Rules

- Read `docs/ONBOARDING.md` before writing.
- Write only the noun types listed in README.md.
- Deterministic writes go through `scripts/`.
- Do not invent relationship names.
- Do not hard-code real client or company names in samples. Northstar / Lumenfield only.
- Identity of the writer belongs in `author` frontmatter.
- Never hard-code a private remote. Use `SECOND_BRAIN_ROOT`.

## Layout

- `skills/` — progressive-disclosure skills
- `commands/` — slash-command shims
- `schemas/` — JSON Schema for owned nouns
- `sample-knowledge/` — fictional demo bundle
- `scripts/` — init / write / validate
