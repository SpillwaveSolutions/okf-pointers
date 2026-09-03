---
name: ptr-write
description: Write a pointer.link. §2.3 is resolved; helper refuses until Link.schema.json lands.
---

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ptr_common.py" write
```

§2.3 decision: `Link` is a sibling of `TypedEdge`. Field name is `link_type`, not `rel`. Do not modify second-brain-core.
