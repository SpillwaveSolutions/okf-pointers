#!/usr/bin/env python3
"""okf-pointers write/validate/reverse helper.

Link is a sibling of TypedEdge, not a subtype. Field name is link_type, not rel.
The model proposes the body. This script commits frontmatter.

Standing rules:
  - Never invent link_type values. Unknown = validation failure.
  - Every link_type declares an inverse. Reverse traversal returns the inverse.
  - One Link per file, exactly two ends.
  - Never mutate either endpoint. Destination may be unresolved at write time.
  - Never hard-code a private remote. Use SECOND_BRAIN_ROOT.
  - Do not modify second-brain-core or its rel vocabulary.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TAXONOMY = PLUGIN_ROOT / "schemas" / "okf-pointers" / "taxonomy.json"
OWNED_TYPE = "pointer.link"
SAFE_TOKEN = re.compile(r"[^A-Za-z0-9._-]+")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bundle_of(raw: str | None) -> Path:
    p = Path((raw or os.environ.get("SECOND_BRAIN_ROOT") or "knowledge").strip())
    p.mkdir(parents=True, exist_ok=True)
    return p


def resolve_author(explicit: str | None) -> str:
    author = (explicit or os.environ.get("SECOND_BRAIN_IDENTITY") or "").strip()
    if not author:
        print(json.dumps({"error": "claim an identity first", "hint": "pass --author or set SECOND_BRAIN_IDENTITY"}))
        raise SystemExit(1)
    return author


def taxonomy_path() -> Path:
    override = (os.environ.get("OKF_POINTERS_TAXONOMY") or "").strip()
    return Path(override) if override else DEFAULT_TAXONOMY


def load_taxonomy(path: Path | None = None) -> dict:
    p = path or taxonomy_path()
    if not p.exists():
        print(json.dumps({"error": "taxonomy missing", "path": str(p)}))
        raise SystemExit(1)
    data = json.loads(p.read_text(encoding="utf-8"))
    inverses = data.get("inverses") or {}
    if not isinstance(inverses, dict) or not inverses:
        print(json.dumps({"error": "taxonomy has no inverses", "path": str(p)}))
        raise SystemExit(1)
    errors = taxonomy_errors(inverses)
    if errors:
        print(json.dumps({"error": "taxonomy invalid", "errors": errors, "path": str(p)}))
        raise SystemExit(1)
    return data


def taxonomy_errors(inverses: dict) -> list[str]:
    errors: list[str] = []
    for name, inv in inverses.items():
        if not name or not isinstance(name, str):
            errors.append("empty link_type in taxonomy")
            continue
        if not inv or not isinstance(inv, str):
            errors.append(f"{name}: no inverse declared")
            continue
        if inv not in inverses:
            errors.append(f"{name}: inverse {inv} is not in the taxonomy")
            continue
        if inverses.get(inv) != name:
            errors.append(f"{name} ⇄ {inv} is not symmetric")
    return errors


def inverse_of(link_type: str, inverses: dict) -> str:
    inv = inverses.get(link_type)
    if not inv:
        raise KeyError(link_type)
    return inv


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    return _parse_yaml_lite(parts[1]), parts[2].lstrip("\n")


def _parse_yaml_lite(block: str) -> dict:
    meta: dict = {}
    key: str | None = None
    acc: list | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z0-9_]+:\s*$", raw):
            key = raw.split(":", 1)[0].strip()
            acc = []
            meta[key] = acc
            continue
        if key is not None and acc is not None and raw.strip().startswith("- "):
            acc.append(raw.strip()[2:].strip().strip("'\""))
            continue
        if ":" in raw and not raw.startswith(" "):
            key = None
            acc = None
            k, v = raw.split(":", 1)
            meta[k.strip()] = v.strip().strip("'\"")
    return meta


def dump_frontmatter(meta: dict) -> str:
    lines = ["---"]
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def write_md(path: Path, meta: dict, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_frontmatter(meta) + "\n" + body.rstrip() + "\n", encoding="utf-8")
    return path


def file_token(value: str) -> str:
    return SAFE_TOKEN.sub("_", value.strip())


def link_filename(source: str, link_type: str, destination: str) -> str:
    return f"{file_token(source)}__{file_token(link_type)}__{file_token(destination)}.md"


def raw_yaml_block(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""


def link_shape_errors(path: Path, meta: dict, raw_yaml: str) -> list[str]:
    errors: list[str] = []
    rel = str(path)
    if "rel" in meta:
        errors.append(f"{rel}: field is link_type, not rel")
    if "destinations" in meta:
        errors.append(f"{rel}: destinations list is several Links; one file per Link")
    if "links" in meta:
        errors.append(f"{rel}: links[] is TypedEdge shape; pointer.link is one edge per file")
    dest = meta.get("destination")
    if isinstance(dest, list):
        errors.append(f"{rel}: destination is a list; one file per Link")
    dest_keys = 0
    for line in raw_yaml.splitlines():
        if re.match(r"^destination:", line) or re.match(r"^destinations:", line):
            dest_keys += 1
    if dest_keys > 1:
        errors.append(f"{rel}: multiple destination keys; one file per Link")
    return errors


def required_field_errors(path: Path, meta: dict) -> list[str]:
    errors: list[str] = []
    rel = str(path)
    for field in ("title", "source", "source_type", "destination", "destination_type", "link_type"):
        val = meta.get(field)
        if not val or not isinstance(val, str):
            errors.append(f"{rel}: missing {field}")
    return errors


def cmd_init(args) -> int:
    bundle = bundle_of(args.bundle)
    d = bundle / "okf" / "pointers"
    d.mkdir(parents=True, exist_ok=True)
    idx = d / "index.md"
    if not idx.exists():
        write_md(
            idx,
            {"type": "Index", "title": "Pointers", "timestamp": now_iso()},
            "# Pointers\n\nGit-native join table. One noun: the Link. Sibling of TypedEdge.\n",
        )
    tax = load_taxonomy()
    print(json.dumps({"ok": True, "bundle": str(bundle), "taxonomy": tax.get("version")}))
    return 0


def cmd_write(args) -> int:
    author = resolve_author(args.author)
    tax = load_taxonomy()
    inverses = tax["inverses"]
    source = (args.source or "").strip()
    dest = (args.destination or "").strip()
    link_type = (args.link_type or "").strip()
    source_type = (args.source_type or "").strip()
    dest_type = (args.destination_type or "").strip()
    if getattr(args, "destinations", None):
        print(json.dumps({"error": "destinations list is several Links; one file per Link"}))
        return 1
    if not source or not dest or not link_type or not source_type or not dest_type:
        print(
            json.dumps(
                {
                    "error": "source, source_type, destination, destination_type, link_type required",
                }
            )
        )
        return 1
    if link_type not in inverses:
        print(json.dumps({"error": f"unknown link_type: {link_type}", "allowed": sorted(inverses)}))
        return 1
    if not inverses.get(link_type):
        print(json.dumps({"error": f"link_type has no inverse: {link_type}"}))
        return 1
    bundle = bundle_of(args.bundle)
    name = link_filename(source, link_type, dest)
    dest_path = bundle / "okf" / "pointers" / name
    title = args.title or f"{source} {link_type} {dest}"
    meta = {
        "type": OWNED_TYPE,
        "title": title,
        "source": source,
        "source_type": source_type,
        "destination": dest,
        "destination_type": dest_type,
        "link_type": link_type,
        "timestamp": now_iso(),
        "author": author,
    }
    body = args.body or f"# {title}\n"
    write_md(dest_path, meta, body)
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(dest_path),
                "link_type": link_type,
                "inverse": inverses[link_type],
                "endpoints_mutated": False,
                "destination_resolved": False,
            }
        )
    )
    return 0


def iter_pointer_files(bundle: Path):
    root = bundle / "okf" / "pointers"
    if not root.exists():
        return
    for p in sorted(root.rglob("*.md")):
        yield p


def cmd_validate(args) -> int:
    bundle = Path(args.bundle or os.environ.get("SECOND_BRAIN_ROOT") or "knowledge")
    tax = load_taxonomy()
    inverses = tax["inverses"]
    errors: list[str] = []
    n = 0
    root = bundle / "okf" / "pointers"
    if not root.exists():
        print(json.dumps({"ok": True, "nodes": 0, "errors": [], "taxonomy": tax.get("version")}))
        return 0
    for p in iter_pointer_files(bundle) or []:
        n += 1
        text = p.read_text(encoding="utf-8")
        meta, _body = parse_frontmatter(text)
        raw = raw_yaml_block(text)
        typ = meta.get("type", "")
        if p.name == "index.md":
            if typ not in {"Index", "index"}:
                errors.append(f"{p}: index must have type Index")
            continue
        if typ != OWNED_TYPE:
            errors.append(f"{p}: unowned type {typ}")
            continue
        errors.extend(link_shape_errors(p, meta, raw))
        errors.extend(required_field_errors(p, meta))
        lt = meta.get("link_type")
        if isinstance(lt, str) and lt:
            if lt not in inverses:
                errors.append(f"{p}: unknown link_type {lt}")
            elif not inverses.get(lt):
                errors.append(f"{p}: link_type {lt} has no inverse")
    result = {
        "ok": len(errors) == 0,
        "nodes": n,
        "errors": errors,
        "taxonomy": tax.get("version"),
        "engine": "filesystem",
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def cmd_reverse(args) -> int:
    bundle = Path(args.bundle or os.environ.get("SECOND_BRAIN_ROOT") or "knowledge")
    tax = load_taxonomy()
    inverses = tax["inverses"]
    q = (args.query or "").strip()
    if not q:
        print(json.dumps({"error": "query required"}))
        return 1
    hits = []
    root = bundle / "okf" / "pointers"
    if root.exists():
        for p in iter_pointer_files(bundle) or []:
            if p.name == "index.md":
                continue
            text = p.read_text(encoding="utf-8")
            meta, _body = parse_frontmatter(text)
            if meta.get("type") != OWNED_TYPE:
                continue
            src = str(meta.get("source") or "")
            dest = str(meta.get("destination") or "")
            lt = str(meta.get("link_type") or "")
            rel = "/" + str(p.relative_to(bundle)).replace("\\", "/")
            if src == q:
                hits.append(
                    {
                        "file": rel,
                        "direction": "out",
                        "link_type": lt,
                        "other": dest,
                        "other_type": meta.get("destination_type"),
                    }
                )
            if dest == q:
                inv = inverses.get(lt)
                hits.append(
                    {
                        "file": rel,
                        "direction": "in",
                        "link_type": inv,
                        "written_as": lt,
                        "other": src,
                        "other_type": meta.get("source_type"),
                    }
                )
    print(json.dumps({"ok": True, "query": q, "hits": hits, "engine": "scan", "taxonomy": tax.get("version")}))
    return 0


def cmd_taxonomy(args) -> int:
    tax = load_taxonomy()
    print(json.dumps(tax, indent=2))
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init")
    i.add_argument("--bundle", default="")

    w = sub.add_parser("write")
    w.add_argument("--bundle", default="")
    w.add_argument("--source", required=True)
    w.add_argument("--source-type", dest="source_type", required=True)
    w.add_argument("--destination", required=True)
    w.add_argument("--destination-type", dest="destination_type", required=True)
    w.add_argument("--link-type", dest="link_type", required=True)
    w.add_argument("--title", default="")
    w.add_argument("--body", default="")
    w.add_argument("--author", default="")
    w.add_argument("--destinations", default="", help=argparse.SUPPRESS)

    v = sub.add_parser("validate")
    v.add_argument("--bundle", default="")

    r = sub.add_parser("reverse")
    r.add_argument("--bundle", default="")
    r.add_argument("--query", required=True)

    t = sub.add_parser("taxonomy")
    t.add_argument("--bundle", default="")

    args = p.parse_args()
    return {
        "init": cmd_init,
        "write": cmd_write,
        "validate": cmd_validate,
        "reverse": cmd_reverse,
        "taxonomy": cmd_taxonomy,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
