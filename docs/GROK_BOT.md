# Grok Bot binding — okf-pointers

Identity: `grok-bot/okf-pointers`

Owned types: pointer.link (BLOCKED on §2.3 — do not write)

Write path: pack scripts + `--author`. The model proposes prose; scripts commit frontmatter.

Isolation: second-brain-core worktree + PR. Point `SECOND_BRAIN_ROOT` at the session bundle.

Never hard-code a private remote. Never invent `rel` values. Never write types owned by another plugin.
