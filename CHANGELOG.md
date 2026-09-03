# Changelog

## 0.2.0 — 2026-09-03

- `Link.schema.json` shipped. Sibling of TypedEdge; field is `link_type`, not `rel`.
- Semantically versioned taxonomy `okf.pointers.taxonomy/v1` at 1.0.0. Every type declares an inverse.
- `ptr_common.py write` commits one file per Link. Unknown `link_type` fails. Endpoints are never mutated. Destination may be unresolved.
- `reverse` returns the inverse name on inbound edges. Engine is a filesystem scan.
- `validate` fails closed on unknown types, missing inverses, `destinations` lists, and a `rel` field.
- Northstar / Lumenfield sample Links.

## 0.1.1 — 2026-09-03

- Command shim for `ptr-validate` filled. `pointer.link` write remains refused until okf-plugin#73 §2.3.

## 0.1.0 — 2026-09-03

- Initial scaffold. Spec: okf-plugin#73.
