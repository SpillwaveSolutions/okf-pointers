---
name: ptr-reverse
description: Reverse-lookup Links by noun id. Returns the inverse name on inbound edges. Directory scan, no index.
---

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ptr_common.py" reverse \
  --query 2026-W34 --bundle "$SECOND_BRAIN_ROOT"
```

Outbound hits keep the written `link_type`. Inbound hits return the inverse (`started_in` → `start_of`). Engine is a filesystem scan.
