# OKF Pointers

Git-native join table. One noun: the Link. Creating a link never mutates either of the files it links. Not a search index.

**Spec of record:** [okf-plugin#73](https://github.com/SpillwaveSolutions/okf-plugin/issues/73)

**§2.3 resolved.** `Link` is a sibling noun to `TypedEdge`, not a subtype. The name `Link` stands, and `link_type` stays `link_type` — it is not a `rel`. Pointers does not modify [second-brain-core](https://github.com/SpillwaveSolutions/second-brain-core). Schema work is unblocked; `Link.schema.json` is the next write.

Companion: [okf-time-series](https://github.com/SpillwaveSolutions/okf-time-series) (#72) · [okf-remote](https://github.com/SpillwaveSolutions/okf-remote) (#74)

## Standing constraints

- Never invent `link_type` values.
- Never write types owned by another plugin. Ticket IDs are wiki_ticket_sdd ULIDs.
- Index-free correctness: a directory scan is a correct answer.
- Never hard-code a private remote. Use `SECOND_BRAIN_ROOT`.
- Do not modify `second-brain-core` or its `rel` vocabulary.

## Multi-host

Same table as second-brain-core. See docs/GROK_BOT.md, docs/LANG_CHAIN_DEEP_AGENTS.md, docs/ISOLATION.md.

## License

MIT. Copyright 2026 Rick Hightower / contributors.
