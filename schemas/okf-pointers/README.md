# Schemas — unblocked

`Link.schema.json` is **not yet** in this tree. §2.3 is resolved: write it as a sibling of `TypedEdge`, not a subtype.

- Field name is `link_type`, not `rel`.
- Do not modify `second-brain-core` or contribute values to its `rel` vocabulary.
- `okf-plugin`'s graph engine must traverse both `type: pointer.link` and `TypedEdge`.

See [okf-plugin#73](https://github.com/SpillwaveSolutions/okf-plugin/issues/73). `scripts/ptr_common.py write` still refuses until the schema lands.
