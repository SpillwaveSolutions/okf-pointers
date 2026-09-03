#!/usr/bin/env python3
"""Link write/validate/reverse. Fail-closed taxonomy. One file per Link. Never mutate endpoints."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ptr_common.py"
AUTHOR = ["--author", "grok-bot/northstar-console"]


def run(args, env=None):
    e = os.environ.copy()
    e.pop("OKF_POINTERS_TAXONOMY", None)
    if env:
        e.update(env)
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=e)


def write_link(bundle, extra=None):
    args = [
        "write",
        "--bundle",
        bundle,
        "--source",
        "epic_alpha_01",
        "--source-type",
        "epic",
        "--destination",
        "2026-W34",
        "--destination-type",
        "temporal.week",
        "--link-type",
        "started_in",
        "--title",
        "Epic Alpha started in W34",
        "--body",
        "Northstar kicked off Epic Alpha this week.",
        *AUTHOR,
    ]
    if extra:
        args.extend(extra)
    return run(args)


class TestPtr(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bundle = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_write_succeeds_and_does_not_mutate_endpoints(self):
        endpoint = Path(self.bundle) / "okf" / "temporal" / "2026" / "08" / "W34" / "2026-W34.md"
        endpoint.parent.mkdir(parents=True, exist_ok=True)
        original = "---\ntype: temporal.week\ntitle: 2026-W34\nperiod: 2026-W34\nstatus: finalized\n---\n\n# week\n"
        endpoint.write_text(original, encoding="utf-8")
        r = write_link(self.bundle)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data["ok"])
        self.assertFalse(data["endpoints_mutated"])
        self.assertEqual(data["inverse"], "start_of")
        self.assertTrue(Path(data["path"]).exists())
        self.assertIn("started_in", Path(data["path"]).name)
        self.assertEqual(endpoint.read_text(encoding="utf-8"), original)

    def test_unknown_link_type_fails(self):
        r = run(
            [
                "write",
                "--bundle",
                self.bundle,
                "--source",
                "a",
                "--source-type",
                "epic",
                "--destination",
                "b",
                "--destination-type",
                "ticket",
                "--link-type",
                "owns",
                *AUTHOR,
            ]
        )
        self.assertNotEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertIn("unknown link_type", data["error"])

    def test_type_without_inverse_fails_validate(self):
        broken = Path(self.tmp.name) / "broken-taxonomy.json"
        broken.write_text(
            json.dumps(
                {
                    "schema": "okf.pointers.taxonomy/v1",
                    "version": "0.0.0-broken",
                    "inverses": {"contains": "contained_by", "contained_by": "contains", "orphan": ""},
                }
            ),
            encoding="utf-8",
        )
        env = {"OKF_POINTERS_TAXONOMY": str(broken)}
        r = run(["validate", "--bundle", self.bundle], env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("taxonomy invalid", r.stdout)

    def test_multi_destination_file_fails_validate(self):
        run(["init", "--bundle", self.bundle])
        p = Path(self.bundle) / "okf" / "pointers" / "epic__contains__many.md"
        p.write_text(
            "---\n"
            "type: pointer.link\n"
            "title: many\n"
            "source: epic_alpha_01\n"
            "source_type: epic\n"
            "destination: software_engineer__atlas__001\n"
            "destination_type: temporal.session\n"
            "link_type: contains\n"
            "destinations:\n"
            "  - software_engineer__atlas__001\n"
            "  - software_engineer__atlas__002\n"
            "---\n\n# many\n",
            encoding="utf-8",
        )
        r = run(["validate", "--bundle", self.bundle])
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertIn("destinations", r.stdout)

    def test_rel_field_fails_validate(self):
        run(["init", "--bundle", self.bundle])
        p = Path(self.bundle) / "okf" / "pointers" / "a__started_in__b.md"
        p.write_text(
            "---\n"
            "type: pointer.link\n"
            "title: no\n"
            "source: a\n"
            "source_type: epic\n"
            "destination: b\n"
            "destination_type: temporal.week\n"
            "link_type: started_in\n"
            "rel: started_in\n"
            "---\n\n# no\n",
            encoding="utf-8",
        )
        r = run(["validate", "--bundle", self.bundle])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("link_type, not rel", r.stdout)

    def test_unresolved_destination_is_ok(self):
        r = run(
            [
                "write",
                "--bundle",
                self.bundle,
                "--source",
                "research__lumen__001",
                "--source-type",
                "temporal.session",
                "--destination",
                "epic_alpha_01",
                "--destination-type",
                "epic",
                "--link-type",
                "references",
                *AUTHOR,
            ]
        )
        self.assertEqual(r.returncode, 0, r.stdout)
        v = run(["validate", "--bundle", self.bundle])
        self.assertEqual(v.returncode, 0, v.stdout)

    def test_reverse_returns_inverse_name(self):
        self.assertEqual(write_link(self.bundle).returncode, 0)
        r = run(["reverse", "--bundle", self.bundle, "--query", "2026-W34"])
        self.assertEqual(r.returncode, 0, r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(data["engine"], "scan")
        self.assertEqual(len(data["hits"]), 1)
        hit = data["hits"][0]
        self.assertEqual(hit["direction"], "in")
        self.assertEqual(hit["link_type"], "start_of")
        self.assertEqual(hit["written_as"], "started_in")
        self.assertEqual(hit["other"], "epic_alpha_01")
        out = run(["reverse", "--bundle", self.bundle, "--query", "epic_alpha_01"])
        outbound = json.loads(out.stdout)["hits"][0]
        self.assertEqual(outbound["direction"], "out")
        self.assertEqual(outbound["link_type"], "started_in")

    def test_write_without_identity_fails(self):
        env = os.environ.copy()
        env.pop("SECOND_BRAIN_IDENTITY", None)
        r = run(
            [
                "write",
                "--bundle",
                self.bundle,
                "--source",
                "a",
                "--source-type",
                "epic",
                "--destination",
                "b",
                "--destination-type",
                "week",
                "--link-type",
                "started_in",
            ],
            env=env,
        )
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("identity", r.stdout.lower())

    def test_sample_validates(self):
        sample = ROOT / "sample-knowledge"
        r = run(["validate", "--bundle", str(sample)])
        self.assertEqual(r.returncode, 0, r.stdout)
        data = json.loads(r.stdout)
        self.assertGreaterEqual(data["nodes"], 3)

    def test_sample_reverse_epic(self):
        sample = ROOT / "sample-knowledge"
        r = run(["reverse", "--bundle", str(sample), "--query", "epic_alpha_01"])
        self.assertEqual(r.returncode, 0, r.stdout)
        data = json.loads(r.stdout)
        types = {h["link_type"] for h in data["hits"]}
        self.assertIn("started_in", types)

    def test_taxonomy_versioned(self):
        r = run(["taxonomy"])
        self.assertEqual(r.returncode, 0, r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(data["schema"], "okf.pointers.taxonomy/v1")
        self.assertEqual(data["version"], "1.0.0")
        self.assertFalse(data["policy"]["links_record_version"])
        self.assertEqual(data["inverses"]["contains"], "contained_by")
        self.assertEqual(data["inverses"]["contained_by"], "contains")


if __name__ == "__main__":
    unittest.main()
