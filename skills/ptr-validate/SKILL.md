---
name: ptr-validate
description: Validate the pointers catalog. Fail-closed taxonomy. One file per Link. Inverse required.
---

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ptr_common.py" validate --bundle "$SECOND_BRAIN_ROOT"
```

Fails on unknown `link_type`, a type with no inverse, a `destinations` list, a `rel` field, or an unowned `type`. Index-free: a directory scan is a correct answer.
