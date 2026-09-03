#!/usr/bin/env python3
"""okf-pointers write/validate helper.

Schema for pointer.link is BLOCKED on okf-plugin#73 §2.3.
This helper:
  - inits the pointers catalog
  - validates plugin layout and any markdown under okf/pointers
  - REFUSES to write type: pointer.link until OKF_POINTERS_SCHEMA=unlocked

It does not invent rel values. It does not mutate linked files.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

BLOCKED_TYPE = "pointer.link"


def bundle_of(raw: str | None) -> Path:
    p = Path((raw or os.environ.get("SECOND_BRAIN_ROOT") or "knowledge").strip())
    p.mkdir(parents=True, exist_ok=True)
    return p


def cmd_init(args) -> int:
    bundle = bundle_of(args.bundle)
    d = bundle / "okf" / "pointers"
    d.mkdir(parents=True, exist_ok=True)
    idx = d / "index.md"
    if not idx.exists():
        idx.write_text(
            "---\ntype: Index\ntitle: Pointers\n---\n\n"
            "# Pointers\n\nGit-native join table. Schema blocked on okf-plugin#73 §2.3.\n"
            "This catalog is empty on purpose.\n",
            encoding="utf-8",
        )
    print(json.dumps({"ok": True, "bundle": str(bundle), "schema": "blocked"}))
    return 0


def cmd_write(args) -> int:
    if os.environ.get("OKF_POINTERS_SCHEMA") != "unlocked":
        print(
            json.dumps(
                {
                    "error": "pointer.link schema is blocked on okf-plugin#73 §2.3",
                    "hint": "Do not write Link files until TypedEdge vs Link is decided. See the analysis comment on #73.",
                    "type_refused": BLOCKED_TYPE,
                }
            )
        )
        return 1
    print(json.dumps({"error": "unlocked flag set but schema still not implemented"}))
    return 1


def cmd_validate(args) -> int:
    bundle = Path(args.bundle or os.environ.get("SECOND_BRAIN_ROOT") or "knowledge")
    errors = []
    n = 0
    root = bundle / "okf" / "pointers"
    if not root.exists():
        print(json.dumps({"ok": True, "nodes": 0, "errors": [], "note": "empty catalog (schema blocked)"}))
        return 0
    for p in root.rglob("*.md"):
        n += 1
        text = p.read_text(encoding="utf-8")
        if f"type: {BLOCKED_TYPE}" in text or f"type: {BLOCKED_TYPE}" in text.replace('"', ""):
            errors.append(f"{p}: {BLOCKED_TYPE} files are forbidden until §2.3 is decided")
    result = {"ok": len(errors) == 0, "nodes": n, "errors": errors, "schema": "blocked"}
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--bundle", default="")
    w = sub.add_parser("write")
    w.add_argument("--bundle", default="")
    v = sub.add_parser("validate")
    v.add_argument("--bundle", default="")
    args = p.parse_args()
    return {"init": cmd_init, "write": cmd_write, "validate": cmd_validate}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
