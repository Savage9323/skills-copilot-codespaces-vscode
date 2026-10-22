#!/usr/bin/env python3
"""Fail-closed Bitwarden Secrets Manager broker for pre-approved local actions."""
import argparse
import hashlib
import json
import os
import pathlib
import re
import sys

PROJECT_PATTERN=re.compile(r"^[a-z][a-z0-9._-]{1,62}$")
UUID=re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
ACTION_PATTERN=re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
def private_json(path):
    p=pathlib.Path(path).expanduser()
    if not p.is_file() or p.is_symlink() or p.stat().st_mode & 0o077:
        raise ValueError("missing or insecure private policy file")
    value=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(value,dict):raise ValueError("invalid policy shape")
    return value

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def build_command(project,action,mapping,policy,bws_binary):
    if not PROJECT_PATTERN.fullmatch(project) or not ACTION_PATTERN.fullmatch(action):
        raise ValueError("invalid project or action")
    if mapping.get("provider")!="bitwarden":raise ValueError("unexpected secrets provider")
    entry=mapping.get("projects",{}).get(project)
    project_id=entry.get("project_id","") if isinstance(entry,dict) else ""
    if not UUID.fullmatch(project_id):raise ValueError("project not enrolled with verified UUID")
    approved=policy.get("actions",{}).get(project,{}).get(action)
    if not isinstance(approved,dict):raise ValueError("action not on trusted executable allowlist")
    exe=approved.get("executable","")
    args=approved.get("args")
    expected=approved.get("sha256")
    if not isinstance(exe,str) or not pathlib.Path(exe).is_absolute() or not isinstance(args,list) or not isinstance(expected,str):
        raise ValueError("invalid allowlist entry")
    if not all(isinstance(x,str) and len(x)<=256 and "\x00" not in x for x in args):
        raise ValueError("invalid fixed command arguments")
    p=pathlib.Path(exe)
    if p.is_symlink() or not p.is_file() or p.stat().st_mode & 0o022:
        raise ValueError("approved executable missing, symlinked or group/world-writable")
    if sha256_file(p)!=expected:
        raise ValueError("trusted executable checksum changed")
    bws=pathlib.Path(bws_binary)
    if not bws.is_file():
        raise ValueError("Bitwarden CLI unavailable")
    return [str(bws),"run","--project-id",project_id,"--",str(p),*args]

def main():
    parser=argparse.ArgumentParser(description="SavageDev allowlisted runtime secret broker")
    parser.add_argument("project")
    parser.add_argument("action")
    parser.add_argument("--check",action="store_true",help="Validate approval and checksum without token/injection")
    x=parser.parse_args()
    try:
        # Paths are fixed: caller cannot substitute self-authored policy files.
        mapping=private_json("~/.config/savage-agent/vault-projects.json")
        policy=private_json("~/.config/savage-agent/vault-consumers.json")
        bws="/usr/local/bin/bws"
        bws_path=pathlib.Path(bws)
        if bws_path.is_symlink() or not bws_path.is_file() or bws_path.stat().st_uid!=0 or bws_path.stat().st_mode & 0o022:
            raise ValueError("Bitwarden CLI not trusted or unavailable")
        cmd=build_command(x.project,x.action,mapping,policy,bws)
        if x.check:
            print("ALLOWLIST_CHECK_PASS (no credential access attempted)")
            return 0
        if not os.environ.get("BWS_ACCESS_TOKEN"):
            raise ValueError("Bitwarden machine authentication not loaded in a trusted runtime")
        # Replace current process; never invoke shell or print injected credentials.
        os.execvpe(str(cmd[0]),cmd,os.environ.copy())
    except (OSError,ValueError,TypeError,KeyError) as e:
        print("BWS_BROKER_DENIED:"+str(e),file=sys.stderr)
        return 1
if __name__=="__main__":
    raise SystemExit(main())
