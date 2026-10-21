#!/usr/bin/env python3
"""Non-secret diagnostic: OpenCode V2 scope and permission policy."""
import fnmatch,json,pathlib,subprocess,sys
HOME=pathlib.Path.home()
def decide(agent,action,resource):
    effect=None
    for r in agent.get("permissions",[]):
        if fnmatch.fnmatchcase(action,r.get("action","")) and fnmatch.fnmatchcase(resource,r.get("resource","")):
            effect=r.get("effect")
    return effect
def main():
    failures=[]
    try:
        r=subprocess.run(["opencode","debug","agents"],capture_output=True,text=True,check=True,timeout=20)
        agents={a["name"]:a for a in json.loads(r.stdout) if isinstance(a,dict) and a.get("name")}
        checks=[
            ("review","edit",".ai-memory/REVIEW.md","allow"),
            ("security","edit",".ai-memory/REVIEW.md","deny"),
            ("watchdog","edit",".ai-memory/REVIEW.md","deny"),
            ("watchdog","edit",".ai-memory/ALERTS.md","allow"),
            ("security","shell","git push origin HEAD","deny"),
            ("security","shell","rm -rf /tmp/fixture","deny"),
            ("review","shell","git status --short","allow"),
            ("review","shell","git push origin HEAD","deny"),
            ("review","read",".env","deny"),
            ("security","read",".env","deny"),
            ("watchdog","read",".env","deny"),
        ]
        for name,action,resource,want in checks:
            got=decide(agents[name],action,resource)
            if got!=want: failures.append(f"{name}:{action}:{resource}:expected-{want}:got-{got}")
        global_cfg=json.loads((HOME/".config/opencode/opencode.json").read_text())
        bounty_cfg=json.loads((HOME/"BountyHunter/opencode.json").read_text())
        sbi_cfg=json.loads((HOME/"src/student-benefits-intelligence/opencode.json").read_text())
        g=set(global_cfg.get("mcp",{}).get("servers",{}))
        b=set(bounty_cfg.get("mcp",{}).get("servers",{}))
        s=set(sbi_cfg.get("mcp",{}).get("servers",{}))
        if "caido" in g or "caido" not in b or "caido" in s:failures.append("CAIDO_MCP_WRONG_SCOPE")
        if "supabase-sbi-readonly" in b or "supabase-sbi-readonly" not in s or "supabase-sbi-readonly" in g:
            failures.append("SUPABASE_MCP_WRONG_SCOPE")
        skills=list((HOME/".config/opencode/skills").glob("*/SKILL.md"))
        backups=list((HOME/".config/opencode/skills").glob("*.backup-*"))
        if len(skills)!=19 or backups:failures.append("SKILL_DISCOVERY_COUNT_OR_BACKUP_DUPLICATES")
        for label in ("memory-import.sh","vault-run.sh"):
            if not (HOME/"src/savage-agent-skills/scripts"/label).is_file():failures.append("MISSING_CENTRAL_SCRIPT_"+label)
        result={"status":"PASS" if not failures else "FAIL",
                "permission_checks":len(checks),
                "mcp_scopes":{"global":sorted(g),"bountyhunter":sorted(b),"sbi":sorted(s)},
                "active_skill_count":len(skills),"discovery_backup_count":len(backups),
                "failures":failures,
                "limitations":"Configuration only; native runtime events and OS isolation are distinct acceptance requirements."}
        print(json.dumps(result,indent=2))
        return 0 if not failures else 1
    except (OSError,ValueError,KeyError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
        print("CAPABILITY_POLICY_INCOMPLETE:"+type(e).__name__,file=sys.stderr)
        return 1
if __name__=="__main__":raise SystemExit(main())
