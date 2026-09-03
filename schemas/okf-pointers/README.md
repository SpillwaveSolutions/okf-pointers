# Schemas — shipped

`Link` is a **sibling** of `TypedEdge`, not a subtype. Pointers does not modify [second-brain-core](https://github.com/SpillwaveSolutions/second-brain-core).

| File | What it is |
| --- | --- |
| `Link.schema.json` | Frontmatter for `type: pointer.link`. Field name is `link_type`, not `rel`. |
| `taxonomy.json` | Semantically versioned closed vocabulary (`okf.pointers.taxonomy/v1`). Additive = minor; rename/remove = major. Links do not record the version. |
| `registry.json` | Owned types for this plugin. |

Rules enforced by `scripts/ptr_common.py`:

- Never invent `link_type` values. Unknown = validation failure.
- Every `link_type` declares an inverse. A type with no inverse = validation failure. Reverse traversal returns the inverse name.
- One Link per file, exactly two ends. A `destinations` list fails.
- Creating a Link never mutates either endpoint. Destination may be unresolved at write time.

See [okf-plugin#73](https://github.com/SpillwaveSolutions/okf-plugin/issues/73).
