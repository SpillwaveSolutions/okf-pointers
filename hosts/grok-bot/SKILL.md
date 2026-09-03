---
name: grok-bot-okf-pointers
description: Bind a Grok Bot agent to okf-pointers. Isolation, identity, deterministic writes.
---

# Grok Bot / okf-pointers

Read docs/ONBOARDING.md first, then follow docs/GROK_BOT.md.

1. Identity: `grok-bot/okf-pointers`
2. Open an isolation session before writes (second-brain-core `scripts/brain_session.py open`) unless the human already pointed `SECOND_BRAIN_ROOT` at a session worktree.
3. Write owned types only (none until §2.3) via this pack's scripts + `--author`.
4. Close the session to PR. Report path + SHA.
5. Never document a private remote. Never write raw Markdown into the tree.
