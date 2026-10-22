#!/usr/bin/env python3
"""Read-only check of effective ordered OpenCode V2 permission rules."""
import fnmatch
import json
import pathlib
import subprocess
import sys

HOME=pathlib.Path.home()
AGENTS=("Build","review","security","watchdog","cleanup-planner","lifecycle-auditor")
SECRET_TARGETS=(
    ".env",".env.example",".env.test","/tmp/private.env",
    "/tmp/id_rsa.key","/tmp/credentials.json",str(HOME/".ssh/id_ed25519"),
)
def effect(rules,action,target):
    decision=None
    for r in rules:
        if (fnmatch.fnmatchcase(action,r.get("action","")) and
                fnmatch.fnmatchcase(target,r.get("resource",""))):
            decision=r.get("effect")
    return decision

def main():
    try:
        output=subprocess.run(["opencode","debug","agents"],cwd=HOME,check=True,
                              capture_output=True,text=True,timeout=25)
        registry={a["name"]:a for a in json.loads(output.stdout)
                  if isinstance(a,dict) and a.get("name")}
        if not all(a in registry for a in AGENTS):
            raise ValueError("effective agent registry incomplete")
        count=0
        for name in AGENTS:
            rules=registry[name].get("permissions",[])
            for target in SECRET_TARGETS:
                if effect(rules,"read",target)!="deny":
                    raise ValueError("secret-file read policy violation for "+name)
                count+=1
            if name != "Build":
                if effect(rules,"external_directory","*")!="deny":
                    raise ValueError("external-directory restriction missing for "+name)
                count+=1
        for name,artifact,expected in [
            ("review",".ai-memory/REVIEW.md","allow"),
            ("security",".ai-memory/REVIEW.md","deny"),
            ("watchdog",".ai-memory/REVIEW.md","deny")]:
            if effect(registry[name]["permissions"],"edit",artifact)!=expected:
                raise ValueError("review authority incorrectly shared")
            count+=1
        print(json.dumps({"status":"PASS","effective_ordered_rule_checks":count,
            "checked_agents":list(AGENTS),
            "limitations":"Model-facing permissions only, not OS sandbox or complete runtime proof."},indent=2))
        return 0
    except (ValueError,OSError,KeyError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
        print("EFFECTIVE_PERMISSION_INCOMPLETE_OR_FAIL",file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
