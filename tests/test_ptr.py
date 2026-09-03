#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ptr_common.py"


def run(args, env=None):
    e = os.environ.copy()
    e.pop("OKF_POINTERS_SCHEMA", None)
    if env:
        e.update(env)
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=e)


class TestPtr(unittest.TestCase):
    def test_write_refused_while_blocked(self):
        r = run(["write"])
        self.assertNotEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertIn("§2.3", data["error"] + data.get("hint", ""))

    def test_empty_catalog_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run(["init", "--bundle", tmp]).returncode, 0)
            r = run(["validate", "--bundle", tmp])
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_pointer_link_file_fails_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(["init", "--bundle", tmp])
            p = Path(tmp) / "okf" / "pointers" / "epic__started_in__2026-W34.md"
            p.write_text("---\ntype: pointer.link\ntitle: no\n---\n\n# no\n", encoding="utf-8")
            r = run(["validate", "--bundle", tmp])
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
