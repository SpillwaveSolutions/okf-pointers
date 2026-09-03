# OKF Pointers

Git-native join table. One noun: the Link. Creating a link never mutates either of the files it links. Not a search index.

**Spec of record:** [okf-plugin#73](https://github.com/SpillwaveSolutions/okf-plugin/issues/73)

`Link` is a **sibling** of `TypedEdge`, not a subtype. The name `Link` stands, and `link_type` stays `link_type` — it is not a `rel`. Pointers does not modify [second-brain-core](https://github.com/SpillwaveSolutions/second-brain-core).

Companion: [okf-time-series](https://github.com/SpillwaveSolutions/okf-time-series) (#72) · [okf-remote](https://github.com/SpillwaveSolutions/okf-remote) (#74)

## Write a Link

The model proposes the body. The helper commits frontmatter.

```bash
python3 scripts/ptr_common.py write \
  --source epic_alpha_01 --source-type epic \
  --destination 2026-W34 --destination-type temporal.week \
  --link-type started_in \
  --author "$SECOND_BRAIN_IDENTITY" \
  --bundle "$SECOND_BRAIN_ROOT"
```

Reverse traversal returns the inverse name:

```bash
python3 scripts/ptr_common.py reverse --query 2026-W34 --bundle "$SECOND_BRAIN_ROOT"
# inbound hit: link_type=start_of (written as started_in)
```

## Taxonomy v1.0.0

Closed, semantically versioned in `schemas/okf-pointers/taxonomy.json`. Additive = minor; rename/remove = major. Links do not record the version.

| link_type | inverse |
| --- | --- |
| `contains` | `contained_by` |
| `started_in` | `start_of` |
| `ended_in` | `end_of` |
| `precedes` | `follows` |
| `scheduled_for` | `scheduled` |
| `references` | `referenced_by` |

A type with no inverse is a validation failure. Unknown values fail closed.

## Standing constraints

- Never invent `link_type` values.
- One Link per file, exactly two ends.
- Never write types owned by another plugin. Ticket IDs are wiki_ticket_sdd ULIDs.
- Linking never mutates endpoints. Destination may be unresolved at write time.
- Index-free correctness: a directory scan is a correct answer.
- Never hard-code a private remote. Use `SECOND_BRAIN_ROOT`.
- Do not modify `second-brain-core` or its `rel` vocabulary.

## Multi-host

Same table as second-brain-core. See docs/GROK_BOT.md, docs/LANG_CHAIN_DEEP_AGENTS.md, docs/ISOLATION.md.

## License

MIT. Copyright 2026 Rick Hightower / contributors.
