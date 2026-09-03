---
name: ptr-validate
description: Validate the pointers catalog. Fails if any pointer.link file exists before §2.3 is decided.
---

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ptr_common.py" validate --bundle "$SECOND_BRAIN_ROOT"
```
