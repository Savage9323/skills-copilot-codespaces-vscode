"""Regression tests of evaluation evidence gates and isolated snapshot restoration."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest


BASE=Path(__file__).resolve().parents[1]/"scripts/hermes-eval"
def load(name, file):
    spec=importlib.util.spec_from_file_location(name,BASE/file)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

ev=load("hermes_verifier","verify_pilot.py")
snap=load("hermes_snapshot","snapshot_restore.py")


class PilotEvidenceTests(unittest.TestCase):
    def test_native_result_requires_real_tool_role_and_call_id(self):
        tool="terminal"
        marker="FIXTURE"
        fake=[("assistant",None,None,None,"FIXTURE")]
        self.assertFalse(ev.native_result(fake,tool,marker))
        simulated=[("tool",tool,None,None,marker)]
        self.assertFalse(ev.native_result(simulated,tool,marker))
        genuine=[("tool",tool,"call_001",None,marker)]
        self.assertTrue(ev.native_result(genuine,tool,marker))

    def test_private_file_requirements(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"evidence.txt"
            p.write_text("test fixture")
            p.chmod(0o644)
            self.assertFalse(ev.safe_private(p))
            p.chmod(0o600)
            self.assertTrue(ev.safe_private(p))
            q=Path(t)/"link"
            q.symlink_to(p)
            self.assertFalse(ev.safe_private(q))


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)/"pilot"
        self.root.mkdir()
        (self.root/"profile").mkdir()
        (self.root/"profile/config.yaml").write_text("model: synthetic\n")
        c=sqlite3.connect(self.root/"profile/state.db")
        c.execute("create table messages (id integer primary key, content text)")
        c.execute("insert into messages(content) values('synthetic')")
        c.commit()
        c.close()
        for slug,value in [("sbi-fixture","QUARTZ-LANDFALL-1947"),
                           ("bounty-fixture","MAPLE-ESTUARY-8265")]:
            d=self.root/"profiles"/slug/"memories"
            d.mkdir(parents=True)
            (d/"MEMORY.md").write_text(value)
        (self.root/"profile/.env").write_text("DO_NOT_BACK_UP_SECRET")
        (self.root/"fixtures/tiny-python-repo").mkdir(parents=True)
        (self.root/"fixtures/tiny-python-repo/calculator.py").write_text("return 7\n")
        self.target=self.root/"backups/test-one"

    def test_snapshot_and_isolated_restore(self):
        entries=snap.snapshot(self.root,self.target)
        self.assertGreaterEqual(len(entries["included"]),4)
        restored=snap.test_restore(self.target)
        self.assertEqual(restored["files_restored_and_hashed"],len(entries["included"]))
        self.assertEqual(restored["separate_memory_profiles"],"PASS")
        self.assertFalse((self.target/"files/profile/.env").exists())
        self.assertNotIn("DO_NOT_BACK_UP_SECRET",(self.target/"manifest.json").read_text())

    def test_changed_snapshot_entry_fails_closed(self):
        snap.snapshot(self.root,self.target)
        entry=self.target/"files/profile/config.yaml"
        entry.write_text("tampered")
        with self.assertRaisesRegex(ValueError,"hash mismatch"):
            snap.test_restore(self.target)

    def test_modified_manifest_fails_closed(self):
        snap.snapshot(self.root,self.target)
        manifest=self.target/"manifest.json"
        manifest.write_text(manifest.read_text()+"\n")
        with self.assertRaisesRegex(ValueError,"Manifest integrity mismatch"):
            snap.test_restore(self.target)

    def test_existing_backup_never_overwritten(self):
        snap.snapshot(self.root,self.target)
        with self.assertRaisesRegex(ValueError,"Refusing to overwrite"):
            snap.snapshot(self.root,self.target)

    def test_symlink_file_not_copied(self):
        other=self.root/"profile/config.yaml"
        link=self.root/"profile/SOUL.md"
        link.symlink_to(other)
        snap.snapshot(self.root,self.target)
        self.assertFalse((self.target/"files/profile/SOUL.md").exists())

    def test_invalid_memory_scope_fails_restore(self):
        p=self.root/"profiles/bounty-fixture/memories/MEMORY.md"
        p.write_text("QUARTZ-LANDFALL-1947")
        snap.snapshot(self.root,self.target)
        with self.assertRaisesRegex(ValueError,"Memory isolation"):
            snap.test_restore(self.target)


if __name__=="__main__":
    unittest.main()
