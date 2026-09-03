---
name: ptr-write
description: Write a pointer.link. Sibling of TypedEdge. Field is link_type, not rel. One file, two ends.
---

The model proposes the body. `scripts/ptr_common.py` commits frontmatter.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ptr_common.py" write \
  --source epic_alpha_01 --source-type epic \
  --destination 2026-W34 --destination-type temporal.week \
  --link-type started_in \
  --author "$SECOND_BRAIN_IDENTITY" \
  --bundle "$SECOND_BRAIN_ROOT"
```

Rules:

- `link_type` must be in `schemas/okf-pointers/taxonomy.json`. Unknown values fail. Every type declares an inverse.
- One Link per file. Do not pass a destinations list.
- Creating a Link never mutates either endpoint. Destination may be unresolved.
- Do not modify `second-brain-core`. Do not write `rel`.
