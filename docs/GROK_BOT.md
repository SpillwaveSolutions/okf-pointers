# Grok Bot binding — okf-pointers

Identity: `grok-bot/okf-pointers`

Owned types: `pointer.link` (§2.3 resolved — sibling of `TypedEdge`; `link_type` stays `link_type`. Schema not yet landed.)

Write path: pack scripts + `--author`. The model proposes prose; scripts commit frontmatter. Do not modify `second-brain-core`.

Isolation: second-brain-core worktree + PR. Point `SECOND_BRAIN_ROOT` at the session bundle.

Never hard-code a private remote. Never invent `link_type` values. Never write types owned by another plugin.
