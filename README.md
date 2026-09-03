# OKF Pointers

Git-native join table. One noun: the Link. Creating a link never mutates either of the files it links. Not a search index.

**Spec of record:** [okf-plugin#73](https://github.com/SpillwaveSolutions/okf-plugin/issues/73)

**Blocked on §2.3.** `TypedEdge` vs `Link` is unresolved. Analysis is on the issue. This repository is scaffolded; `scripts/ptr_common.py write` refuses `pointer.link` until a human decides.

Companion: [okf-time-series](https://github.com/SpillwaveSolutions/okf-time-series) (#72) · [okf-remote](https://github.com/SpillwaveSolutions/okf-remote) (#74)

## Standing constraints

- Never invent `rel` values.
- Never write types owned by another plugin. Ticket IDs are wiki_ticket_sdd ULIDs.
- Index-free correctness: a directory scan is a correct answer.
- Never hard-code a private remote. Use `SECOND_BRAIN_ROOT`.

## Multi-host

Same table as second-brain-core. See docs/GROK_BOT.md, docs/LANG_CHAIN_DEEP_AGENTS.md, docs/ISOLATION.md.

## License

MIT. Copyright 2026 Rick Hightower / contributors.
