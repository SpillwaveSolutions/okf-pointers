# Write isolation

This pack does not fork the protocol. Canonical helper:

[second-brain-core/docs/ISOLATION.md](https://github.com/SpillwaveSolutions/second-brain-core/blob/main/docs/ISOLATION.md)
and `scripts/brain_session.py` in that repository.

```
read  → origin/main (shared truth) + optional session overlay
write → brain/<actor>/<session-id> worktree only
close → commit, push to the checkout's existing remote, open PR
merge → human or green auto-merge on non-overlapping paths
```

Branch name: `brain/<sanitized-actor>/<session-id>`.

Public samples use **lumenfield-detector** and **northstar-console** only. This document never names a private remote. `SECOND_BRAIN_ROOT` is a local path the human already has.
