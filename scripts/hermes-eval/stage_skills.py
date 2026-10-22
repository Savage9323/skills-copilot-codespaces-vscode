#!/usr/bin/env python3
"""Stage only reviewed SKILL.md copies into an isolated Hermes pilot profile.

This does NOT install skills globally, copy scripts or enable their tools.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re

NAME = re.compile(r"^[a-z][a-z0-9-]{2,80}$")

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def stage(source: Path, destination: Path):
    if not source.is_dir() or source.is_symlink():
        raise ValueError("Source must be a real skills directory")
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination already exists; refusing overwrite")
    names = sorted(source.glob("*/SKILL.md"))
    records = []
    for item in names:
        if (item.is_symlink() or item.parent.is_symlink() or
            not NAME.fullmatch(item.parent.name) or item.stat().st_size>150_000):
            raise ValueError("Invalid skill source")
        raw=item.read_text(encoding="utf-8")
        if not raw.startswith("---\n") or not re.search(r"(?m)^name:\s*"+re.escape(item.parent.name)+r"\s*$",raw):
            raise ValueError("Invalid SKILL.md name/frontmatter")
        records.append({"name":item.parent.name,"sha256":digest(item),"bytes":len(item.read_bytes())})
    if len(records)<1 or len({x["name"] for x in records})!=len(records):
        raise ValueError("Incomplete or duplicate skill inventory")
    destination.mkdir(parents=True,mode=0o700)
    for r in records:
        p=destination/r["name"]
        p.mkdir(mode=0o700)
        t=p/"SKILL.md"
        source_file=source/r["name"]/"SKILL.md"
        t.write_bytes(source_file.read_bytes())
        t.chmod(0o600)
        if digest(t)!=r["sha256"]:
            raise ValueError("Copied skill hash mismatch")
    return {"stage":"COPIES_ONLY","skill_count":len(records),"entries":records,
            "scripts_copied":False,"secrets_copied":False,"tools_executed":False}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,
         default=Path.home()/".config/opencode/skills")
    parser.add_argument("--dest",type=Path,
         default=Path.home()/".savagedev/evaluations/hermes-h0/profiles/skills-batch/skills")
    args=parser.parse_args()
    manifest=stage(args.source,args.dest)
    report=args.dest.parent/"skill-import-manifest.json"
    with report.open("x") as f:json.dump(manifest,f,indent=2)
    report.chmod(0o600)
    print(json.dumps({"stage":manifest["stage"],"skill_count":manifest["skill_count"],
                      "scripts_copied":False,"tools_executed":False},indent=2))


if __name__=="__main__":
    main()
