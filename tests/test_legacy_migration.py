import importlib.util
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/migrate-legacy-journals.py"
spec = importlib.util.spec_from_file_location("legacy_migration", SOURCE)
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.repo = self.base / "repos/sbi"
        (self.repo / ".git").mkdir(parents=True)
        self.other = self.base / "repos/unrelated"
        (self.other / ".git").mkdir(parents=True)
        self.registry = self.base / "approved-projects.json"
        self.registry.write_text(json.dumps({"projects": [{"id": "sbi", "root": str(self.repo)}]}))
        os.chmod(self.registry, 0o600)
        self.db = self.base / "sessions.sqlite"
        conn = sqlite3.connect(self.db)
        conn.executescript(
            "create table project(id text primary key, worktree text);"
            "create table session_v2(id text primary key, project_id text, directory text);"
        )
        conn.execute("insert into project values(?,?)", ("p1", str(self.repo)))
        conn.execute("insert into project values(?,?)", ("p2", str(self.other)))
        conn.commit()
        conn.close()
        self.recent = self.base / "recent"
        (self.recent / "sbi").mkdir(parents=True)
        self.new = self.base / "migrated"
        self.manifests = self.base / "manifests"

    def journal(self, sid, project="sbi", root=None, valid=True, directory=None, filename=None):
        path = self.recent / project / (filename or sid + ".json")
        data = {"project": project, "session_id": sid, "source": "legacy-hook",
                "captured_at": "2026-10-21T01:00:00Z",
                "snippets": [{"role": "user", "text": "We decided to keep human review."}]}
        if root:
            data["workspace_root"] = str(root)
        path.write_text(json.dumps(data))
        if valid:
            conn = sqlite3.connect(self.db)
            conn.execute("insert or replace into session_v2 values(?,?,?)",
                         (sid, "p1" if directory is None else "p2",
                          str(directory or self.repo)))
            conn.commit()
            conn.close()
        return path

    def run_migration(self, apply=False):
        return migration.migrate("sbi", registry=self.registry, db=self.db,
                                 recent_root=self.recent, migrated_root=self.new,
                                 manifest_root=self.manifests, apply=apply)

    def test_dry_run_never_writes(self):
        original = self.journal("ses_one")
        before = hashlib.sha256(original.read_bytes()).hexdigest()
        result = self.run_migration()
        self.assertEqual(result["summary"]["eligible"], 1)
        self.assertFalse(self.new.exists())
        self.assertFalse(self.manifests.exists())
        self.assertEqual(before, hashlib.sha256(original.read_bytes()).hexdigest())

    def test_migrate_preserves_original_and_provenance(self):
        original = self.journal("ses_one")
        before = original.read_bytes()
        result = self.run_migration(apply=True)
        target = self.new / "sbi/ses_one.json"
        content = json.loads(target.read_text())
        self.assertEqual(content["status"], "legacy-unverified-reference")
        self.assertEqual(content["workspace_root"], str(self.repo))
        self.assertEqual(content["legacy_migration"]["original_sha256"], migration.sha(before))
        self.assertEqual(original.read_bytes(), before)
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.manifests / "sbi-migration-v1.json").stat().st_mode & 0o777, 0o600)

    def test_unknown_session_quarantined(self):
        self.journal("no_db", valid=False)
        result = self.run_migration(apply=True)
        self.assertEqual(result["summary"]["quarantined"], 1)
        self.assertFalse((self.new / "sbi/no_db.json").exists())

    def test_other_project_worktree_quarantined(self):
        self.journal("other_ses", directory=self.other)
        result = self.run_migration(apply=True)
        self.assertEqual(result["summary"]["quarantined"], 1)
        self.assertFalse((self.new / "sbi/other_ses.json").exists())

    def test_unsafe_session_id_quarantined(self):
        self.journal("ses_one", filename="odd.json")
        result = self.run_migration(apply=True)
        self.assertEqual(result["summary"]["quarantined"], 1)

    def test_unapproved_project_denied(self):
        with self.assertRaisesRegex(ValueError, "authorized"):
            migration.migrate("other", registry=self.registry, db=self.db,
                              recent_root=self.recent, migrated_root=self.new,
                              manifest_root=self.manifests)

    def test_manifest_not_overwritten(self):
        self.journal("ses_one")
        self.run_migration(apply=True)
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.run_migration(apply=True)


if __name__ == "__main__":
    unittest.main()
