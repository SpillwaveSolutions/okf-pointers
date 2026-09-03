---
name: ptr-write
description: Refuses to write pointer.link until §2.3 is decided.
---

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ptr_common.py" write
```

Expected: error, schema blocked on okf-plugin#73.
