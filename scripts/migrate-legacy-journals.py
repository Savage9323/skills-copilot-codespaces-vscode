#!/usr/bin/env python3
"""Versioned, evidence-backed legacy journal migration; originals are immutable."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from datetime import datetime, timezone

SID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
PROJECT = re.compile(r"^[a-z][a-z0-9._-]{0,62}$")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def private_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise ValueError("registry must be private and not symlinked")
    data = json.loads(path.read_text())
    if not isinstance(data.get("projects"), list):
        raise ValueError("registry missing projects")
    return data


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    if path.is_symlink():
        raise ValueError("refusing symlink destination")
    fd, name = tempfile.mkstemp(prefix=".journal-v2-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def migrate(project: str, *, registry: Path, db: Path, recent_root: Path,
            migrated_root: Path, manifest_root: Path, apply: bool = False) -> dict:
    if not PROJECT.fullmatch(project) or ".." in project:
        raise ValueError("invalid project slug")
    registered = private_json(registry)
    matches = [p for p in registered["projects"] if p.get("id") == project]
    if len(matches) != 1:
        raise ValueError("project must have unique authorized registry mapping")
    root = Path(matches[0]["root"]).resolve(strict=True)
    if not root.is_dir() or not (root / ".git").exists():
        raise ValueError("project root not present/verified")
    source = recent_root / project
    if not source.is_dir() or source.is_symlink():
        raise ValueError("missing or symlinked legacy journal root")
    if db.is_symlink():
        raise ValueError("symlink OpenCode database not accepted")
    connection = sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True, timeout=5)
    items = []
    summary = {"eligible": 0, "quarantined": 0, "already_current": 0}
    try:
        for journal in sorted(source.glob("*.json")):
            record = {"file": journal.name, "source_sha256": "", "classification": "quarantined", "reason": ""}
            try:
                if journal.is_symlink() or not journal.is_file() or journal.stat().st_size > 1_000_000:
                    raise ValueError("unsafe source file")
                original = journal.read_bytes()
                record["source_sha256"] = sha(original)
                data = json.loads(original)
                sid = data.get("session_id")
                if not isinstance(sid, str) or not SID.fullmatch(sid) or journal.name != sid + ".json":
                    raise ValueError("session ID/filename mismatch")
                if data.get("project") != project or not isinstance(data.get("snippets"), list):
                    raise ValueError("source project/snippet schema mismatch")
                if data.get("workspace_root"):
                    record["classification"] = "already_current"
                    summary["already_current"] += 1
                    items.append(record)
                    continue
                db_row = connection.execute(
                    "select s.directory, s.project_id, p.worktree "
                    "from session_v2 s join project p on p.id=s.project_id "
                    "where s.id=?", (sid,),
                ).fetchone()
                if not db_row or not db_row[2]:
                    raise ValueError("no independent matching OpenCode session/project")
                session_root = Path(db_row[0]).resolve(strict=True)
                verified_worktree = Path(db_row[2]).resolve(strict=True)
                if session_root != root or verified_worktree != root:
                    raise ValueError("session and project worktree mismatch")
                # Capture provenance without trusting legacy text as authority.
                migrated = dict(data)
                migrated["schema_version"] = 2
                migrated["workspace_root"] = str(root)
                migrated["status"] = "legacy-unverified-reference"
                migrated["warning"] = "Migrated historical conversation only. Not verified durable memory. Verify facts live."
                migrated["legacy_migration"] = {
                    "version": 1,
                    "original_sha256": record["source_sha256"],
                    "origin_session_id": sid,
                    "opencode_project_id": db_row[1],
                    "verification": "OpenCode read-only session_v2 and project.worktree",
                    "migrated_at": datetime.now(timezone.utc).isoformat(),
                }
                record["classification"] = "eligible"
                record["reason"] = "independent session+project root identity verified"
                if apply:
                    target = migrated_root / project / journal.name
                    if target.exists() or target.is_symlink():
                        raise ValueError("migrated destination exists; never overwrite")
                    atomic_json(target, migrated)
                    record["target_sha256"] = sha(target.read_bytes())
                summary["eligible"] += 1
            except (OSError, ValueError, KeyError, TypeError, sqlite3.DatabaseError) as error:
                record["classification"] = "quarantined"
                record["reason"] = str(error)[:160]
                summary["quarantined"] += 1
            items.append(record)
    finally:
        connection.close()
    result = {
        "migration_schema": 1,
        "project": project,
        "workspace_root": str(root),
        "source_count": len(items),
        "summary": summary,
        "dry_run": not apply,
        "originals_modified": False,
        "entries": items,
    }
    if apply:
        manifest = manifest_root / (project + "-migration-v1.json")
        if manifest.exists() or manifest.is_symlink():
            raise ValueError("migration manifest already exists; not overwriting")
        atomic_json(manifest, result)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--registry", default="~/.savagedev/project-identities.json")
    p.add_argument("--db", default="~/.local/share/opencode/opencode.db")
    p.add_argument("--recent-root", default="~/.local/share/savage-agent-memory/recent")
    p.add_argument("--migrated-root", default="~/.local/share/savage-agent-memory/recent-v2")
    p.add_argument("--manifest-root", default="~/.local/share/savage-agent-memory/migration-manifests")
    a = p.parse_args()
    try:
        result = migrate(a.project, registry=Path(a.registry).expanduser(),
                         db=Path(a.db).expanduser(), recent_root=Path(a.recent_root).expanduser(),
                         migrated_root=Path(a.migrated_root).expanduser(),
                         manifest_root=Path(a.manifest_root).expanduser(), apply=a.apply)
        # Never print snippets, filesystem paths, or session identifiers.
        print(json.dumps({"project": a.project, "summary": result["summary"],
                          "dry_run": result["dry_run"],
                          "originals_modified": result["originals_modified"]}))
        return 0 if not result["summary"]["quarantined"] else 2
    except (OSError, ValueError, sqlite3.DatabaseError) as e:
        print("LEGACY_MIGRATION_DENIED:" + type(e).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
