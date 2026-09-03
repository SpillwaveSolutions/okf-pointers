# AGENTS.md — okf-pointers

Dual-host agent plugin (Claude Code + Grok Build + Codex).

## Rules

- Read `docs/ONBOARDING.md` before writing.
- Write only `pointer.link`. Field is `link_type`, not `rel`.
- Deterministic writes go through `scripts/ptr_common.py`.
- Do not invent `link_type` values. Every type declares an inverse.
- One Link per file. Never mutate endpoints.
- Do not hard-code real client or company names in samples. Northstar / Lumenfield only.
- Identity of the writer belongs in `author` frontmatter.
- Never hard-code a private remote. Use `SECOND_BRAIN_ROOT`.
- Do not modify `second-brain-core`.

## Layout

- `skills/` — progressive-disclosure skills
- `commands/` — slash-command shims
- `schemas/` — JSON Schema for owned nouns plus the versioned taxonomy
- `sample-knowledge/` — fictional demo bundle
- `scripts/` — init / write / validate / reverse
