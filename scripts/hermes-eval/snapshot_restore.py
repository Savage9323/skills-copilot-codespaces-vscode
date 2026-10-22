#!/usr/bin/env python3
"""Snapshot isolated Hermes pilot and verify an isolated restore, without live mutation.

Excludes runtime keys, .env, host Ollama weights, OpenCode config, model caches
and gateway/system services. SQLite is backed up transactionally.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile

ALLOWED_EXT = {".yaml", ".md", ".py", ".json", ".stdout", ".stderr", ".log"}
REJECT_NAMES = {".env", "credentials", "credentials.json", "tokens.json", "secrets.json"}
REJECT_PARTS = {"cache", "logs", "__pycache__", "tools", ".git", "tmp", "gateway", "keys", "auth"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_secure(source: Path, destination: Path):
    if source.is_symlink() or not source.is_file():
        raise ValueError("Unsafe source file")
    if source.stat().st_size > 12 * 1024 * 1024:
        raise ValueError("Oversized pilot file")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    destination.write_bytes(source.read_bytes())
    destination.chmod(0o600)


def sqlite_snapshot(source: Path, destination: Path):
    if source.is_symlink() or not source.is_file():
        raise ValueError("Missing SQLite state")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    original = sqlite3.connect("file:" + str(source) + "?mode=ro",
                               uri=True, timeout=5)
    copy = sqlite3.connect(destination)
    try:
        original.backup(copy, pages=100)
        result = copy.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise ValueError("SQLite integrity check failed")
    finally:
        original.close()
        copy.close()
    destination.chmod(0o600)


def files_to_capture(root: Path):
    for profile in [root / "profile", *sorted((root / "profiles").glob("*"))]:
        if not profile.is_dir() or profile.is_symlink():
            continue
        for pattern in ["config.yaml", "state.db", "SOUL.md",
                        "skills/*/SKILL.md", "memories/*.md"]:
            for path in profile.glob(pattern):
                if path.is_file() and not path.is_symlink():
                    yield path
    for folder, patterns in [
        (root / "fixtures/tiny-python-repo", ["*.py"]),
        (root / "fixtures", ["synthetic_mcp.py"]),
        (root / "evidence", ["*.stdout", "review-baseline.json",
                             "h0-h4-independent-verification-v*.json"])]:
        if not folder.is_dir() or folder.is_symlink():
            continue
        for pattern in patterns:
            yield from (p for p in folder.glob(pattern) if p.is_file()
                        and not p.is_symlink())


def snapshot(root: Path, target: Path) -> dict:
    if target.exists() or target.is_symlink():
        raise ValueError("Refusing to overwrite existing snapshot")
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Invalid isolated Hermes pilot root")
    target.mkdir(parents=True, mode=0o700)
    captured = set()
    entries = []
    try:
        for src in files_to_capture(root):
            rel = src.relative_to(root)
            if src.name.lower() in REJECT_NAMES or (
                any(p in REJECT_PARTS for p in rel.parts)):
                continue
            if src.suffix not in ALLOWED_EXT and src.name != "state.db":
                continue
            if str(rel) in captured:
                continue
            captured.add(str(rel))
            output = target / "files" / rel
            if src.name == "state.db":
                sqlite_snapshot(src, output)
            else:
                copy_secure(src, output)
            entries.append({"relative":str(rel),
                            "sha256":sha256(output),
                            "bytes":output.stat().st_size})
        if not any(e["relative"] == "profile/config.yaml" for e in entries):
            raise ValueError("Main profile config missing")
        if not any(e["relative"] == "profile/state.db" for e in entries):
            raise ValueError("Main SQLite session DB missing")
        manifest = {
            "schema": 1,
            "kind": "SAVAGEDEV_SYNTHETIC_HERMES_SNAPSHOT",
            "included": sorted(entries, key=lambda x:x["relative"]),
            "credentials": "EXCLUDED",
            "ollama_weights": "EXCLUDED",
            "host_runtime": "EXCLUDED",
            "production_open_code": "UNCHANGED",
        }
        manifest_file = target / "manifest.json"
        manifest_file.write_text(json.dumps(manifest,indent=2)+"\n")
        manifest_file.chmod(0o600)
        (target / "manifest.sha256").write_text(sha256(manifest_file)+"\n")
        (target / "manifest.sha256").chmod(0o600)
        return manifest
    except BaseException:
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        raise


def test_restore(snapshot_path: Path):
    manifest_path = snapshot_path / "manifest.json"
    if sha256(manifest_path) != (snapshot_path / "manifest.sha256").read_text().strip():
        raise ValueError("Manifest integrity mismatch")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("kind") != "SAVAGEDEV_SYNTHETIC_HERMES_SNAPSHOT":
        raise ValueError("Wrong snapshot type")
    with tempfile.TemporaryDirectory(prefix="hermes-isolated-restore-") as tmp:
        dest = Path(tmp) / "restored"
        dest.mkdir(mode=0o700)
        checked=0
        for item in manifest["included"]:
            relative = Path(item["relative"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unsafe manifest relative path")
            src = snapshot_path / "files" / relative
            if src.is_symlink() or not src.is_file():
                raise ValueError("Missing or replaced snapshot entry")
            if sha256(src) != item["sha256"]:
                raise ValueError("Snapshot entry hash mismatch")
            restored = dest / relative
            copy_secure(src,restored)
            if sha256(restored) != item["sha256"]:
                raise ValueError("Isolated restored file checksum mismatch")
            if restored.name == "state.db":
                con = sqlite3.connect("file:" + str(restored) + "?mode=ro",
                                      uri=True,timeout=3)
                try:
                    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("Restored SQLite invalid")
                finally:
                    con.close()
            checked += 1
        # Confirm restored memory from each synthetic fixture remains distinct.
        sbi=(dest/"profiles/sbi-fixture/memories/MEMORY.md").read_text()
        bounty=(dest/"profiles/bounty-fixture/memories/MEMORY.md").read_text()
        if ("QUARTZ-LANDFALL-1947" not in sbi or
            "MAPLE-ESTUARY-8265" not in bounty or
            "MAPLE-ESTUARY-8265" in sbi or
            "QUARTZ-LANDFALL-1947" in bounty):
            raise ValueError("Memory isolation not preserved in restored snapshot")
    return {"status":"PASS_WITH_LIMITATIONS",
            "isolation":"temp directory only; no active config replaced",
            "files_restored_and_hashed":checked,
            "separate_memory_profiles":"PASS",
            "sqlite_integrity":"PASS",
            "secrets_and_model_weights":"EXCLUDED",
            "full_host_recovery":"NOT_TESTED"}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,
                    default=Path.home()/".savagedev/evaluations/hermes-h0")
    ap.add_argument("--target",type=Path)
    ap.add_argument("--verify",type=Path)
    args=ap.parse_args()
    if args.verify:
        result=test_restore(args.verify)
    else:
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target=args.target or args.root/"backups"/("hermes-pilot-"+stamp)
        manifest=snapshot(args.root,target)
        result=test_restore(target)
        result["snapshot_path"]=str(target)
        result["captured_entries"]=len(manifest["included"])
        output=target/"restore-report.json"
        output.write_text(json.dumps(result,indent=2)+"\n")
        output.chmod(0o600)
    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
