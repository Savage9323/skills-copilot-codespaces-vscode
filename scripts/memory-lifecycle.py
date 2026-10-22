#!/usr/bin/env python3
"""Evidence-gated SavageDev memory candidates. No auto-promotion or network use."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = 1
SLUG = re.compile(r"^[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?$")
SENSITIVE = re.compile(
    r"(?:\b(?:password|passphrase|credential|secret|token|api[_ -]?key|"
    r"private[_ -]?key|access[_ -]?key|recovery[_ -]?code|session[_ -]?cookie|"
    r"authorization|bearer|social security|passport|bank account|credit card|"
    r"BWS_ACCESS_TOKEN|OPENAI_API_KEY)\b|"
    r"gh[pousr]_[A-Za-z0-9_]{12,}|sk-(?:proj-)?[A-Za-z0-9_-]{12,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"https?://[^\s]*[?&](?:key|token|sig|auth)=)",
    re.IGNORECASE,
)
PII = re.compile(
    r"(?:\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b|"
    r"\b(?:\+1[-. ]?)?\(?[2-9][0-9]{2}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b|"
    r"\b[0-9]{1,6}\s+[A-Za-z]{3,24}\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)\b)",
    re.IGNORECASE,
)
INJECTION = re.compile(
    r"\b(?:ignore (?:all |any |the )?(?:previous |prior |system )?(?:instructions|rules)|"
    r"disregard (?:all |previous |the )?(?:instructions|rules)|"
    r"you are now|system prompt|developer instructions)\b", re.I
)
KINDS = (
    ("decision", re.compile(r"^(?:i|we) (?:approved|decided|chose|selected|confirmed)\b", re.I)),
    ("next_action", re.compile(r"^(?:we should|next(?: step)?(?: is|:)|please (?:implement|build|fix|update|verify))\b", re.I)),
    ("completion", re.compile(r"^(?:completed|implemented|deployed|merged|fixed|verified|finished)\b", re.I)),
    ("blocker", re.compile(r"^(?:blocked(?: by)?|blocker:|error:|failure:|still failing)\b", re.I)),
    ("fact", re.compile(r"^(?:[a-z0-9][a-z0-9 /._-]{2,42})\s*:\s*\S", re.I)),
)
EXCLUDE_SUBJECTS = {"decision", "blocker", "next step", "next", "completed", "error", "failure", "status"}
ALLOWED_STATES = {"PENDING", "CONFLICT", "STALE_RECHECK", "VERIFIED_REPO", "VERIFIED_LIVE", "PROMOTED", "REJECTED", "SUPERSEDED", "ARCHIVED"}

SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
OPAQUE = re.compile(r"(?<![a-zA-Z0-9])([A-Za-z0-9+/_=-]{28,})(?![a-zA-Z0-9])")

def opaque_secret(text):
    for m in OPAQUE.finditer(text):
        token=m.group(1)
        classes=sum(bool(re.search(pattern,token)) for pattern in (r"[a-z]",r"[A-Z]",r"[0-9]",r"[-_+=/]"))
        if classes>=3 and len(set(token))>=12:
            return True
    return False

def authorized_identity(project, workspace_root, registry):
    """Recompute the same resolved repo-root identity as the V2 plugin."""
    if not isinstance(workspace_root,str):
        return False
    try:
        real=Path(workspace_root).resolve(strict=True)
        if not real.is_dir() or str(real)!=workspace_root:
            return False
        root=real
        while root.parent!=root and not (root/".git").exists():
            root=root.parent
        reg=Path(registry).expanduser()
        if reg.is_file():
            if reg.is_symlink() or (reg.stat().st_mode & 0o077):
                raise ValueError("unsafe project registry")
            data=json.loads(reg.read_text())
            for item in data.get("projects",[]):
                if not ensure_project(item["id"]):
                    return False
                if Path(item["root"]).resolve(strict=True)==root:
                    return item["id"]==project
        label=re.sub(r"[^a-z0-9._-]+","-",root.name.lower()).strip("-")[:40] or "workspace"
        return project==label+"-"+digest(str(root))[:16]
    except (OSError,ValueError,KeyError,TypeError):
        return False

def utcnow():
    return datetime.now(timezone.utc)

def iso(dt):
    return dt.isoformat().replace("+00:00", "Z")

def parse_time(text):
    try:
        return datetime.fromisoformat(str(text).replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return None

def ensure_project(project):
    if not SLUG.fullmatch(project) or project in {".", ".."} or ".." in project:
        raise ValueError("invalid project slug")
    return project

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def clean_claim(text):
    text = re.sub(r"\s+", " ", text).strip().strip("-*#> ")
    if not text or len(text) > 280 or len(text) < 11:
        return None
    if SENSITIVE.search(text) or PII.search(text) or INJECTION.search(text) or opaque_secret(text):
        return None
    if any(ord(c) < 32 for c in text):
        return None
    return text

def classify(text):
    for kind, pattern in KINDS:
        if pattern.match(text):
            return kind
    return None

def topic(text, kind):
    if kind != "fact":
        return None
    match = re.match(r"^([a-z0-9][a-z0-9 /._-]{2,42})\s*:\s*(.+)$", text, re.I)
    if not match:
        return None
    name = re.sub(r"\s+", " ", match.group(1).lower()).strip()
    return name if name not in EXCLUDE_SUBJECTS else None

def private_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    if path.is_symlink():
        raise ValueError("refusing symlink target")
    fd, temp_name = tempfile.mkstemp(prefix=".m2-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2, sort_keys=True)
            out.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)

def state_file(state_root, project):
    return Path(state_root).expanduser() / "candidates" / (ensure_project(project) + ".json")

def load_state(state_root, project):
    path = state_file(state_root, project)
    if not path.exists():
        return {"schema": SCHEMA, "project": project, "candidates": {}}
    if path.is_symlink():
        raise ValueError("refusing symlink state")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA or data.get("project") != project or not isinstance(data.get("candidates"), dict):
        raise ValueError("state schema/project mismatch")
    return data

def save_state(state_root, project, state):
    private_write(state_file(state_root, project), state)

def expire_and_conflicts(state, now=None, days=30):
    now = now or utcnow()
    items = state["candidates"]
    buckets = defaultdict(list)
    for c in items.values():
        if c.get("topic") and c["status"] not in {"REJECTED", "PROMOTED", "SUPERSEDED", "ARCHIVED"}:
            buckets[c["topic"]].append(c)
    conflicted = set()
    for group in buckets.values():
        if len({c["claim"].split(":", 1)[-1].strip().casefold() for c in group}) > 1:
            conflicted.update(c["id"] for c in group)
    for c in items.values():
        if c["status"] in {"PROMOTED", "REJECTED", "SUPERSEDED", "ARCHIVED"}:
            continue
        if c["id"] in conflicted:
            c["status"] = "CONFLICT"
        elif c["status"] == "CONFLICT":
            c["status"] = "PENDING"
        timestamp = parse_time(c.get("last_seen"))
        if c["status"] == "PENDING" and (timestamp is None or now - timestamp > timedelta(days=days)):
            c["status"] = "STALE_RECHECK"
        if c["status"] in {"VERIFIED_REPO", "VERIFIED_LIVE"}:
            reviewed = parse_time((c.get("verification") or {}).get("at"))
            max_age = 7 if c.get("topic") in {"production revision", "status", "deployment", "current branch"} else days
            if reviewed is None or now - reviewed > timedelta(days=max_age) or reviewed > now + timedelta(minutes=5):
                c["status"] = "STALE_RECHECK"
    return state

def scan(state, journal_root, project, days=30, now=None, registry=None):
    project = ensure_project(project)
    now = now or utcnow()
    registry = registry or Path.home()/".savagedev/project-identities.json"
    source_dir = Path(journal_root).expanduser() / project
    examined = 0
    new = 0
    if source_dir.is_symlink():
        raise ValueError("refusing symlink journal directory")
    for path in sorted(source_dir.glob("*.json")) if source_dir.is_dir() else []:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        session_id = data.get("session_id")
        if (data.get("project") != project
            or not isinstance(data.get("snippets"), list)
            or not isinstance(session_id,str) or not SESSION_ID.fullmatch(session_id)
            or path.name != session_id+".json"
            or not authorized_identity(project,data.get("workspace_root"),registry)):
            continue
        examined += 1
        seen_at = parse_time(data.get("captured_at")) or datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        for snip in data["snippets"][:60]:
            if not isinstance(snip, dict) or snip.get("role") != "user":
                continue  # Assistant summaries cannot establish evidence.
            for line in str(snip.get("text", "")).splitlines()[:30]:
                claim = clean_claim(line)
                if claim is None:
                    continue
                kind = classify(claim)
                if kind is None:
                    continue
                unique = digest(project + "\0" + re.sub(r"\s+", " ", claim).casefold())
                items = state["candidates"]
                if unique not in items:
                    items[unique] = {
                        "id": unique, "project": project, "kind": kind, "claim": claim,
                        "topic": topic(claim, kind), "first_seen": iso(seen_at),
                        "last_seen": iso(seen_at), "status": "PENDING",
                        "sources": [], "verification": None, "promotion": None,
                        "sensitivity": "PENDING_REVIEW", "freshness_window_days": days,
                        "superseded_by": None, "archived_at": None
                    }
                    new += 1
                item = items[unique]
                previous_time = parse_time(item.get("last_seen"))
                if previous_time is None or seen_at > previous_time:
                    item["last_seen"] = iso(seen_at)
                provenance = {"journal": path.name, "sha256": source_hash}
                if provenance not in item["sources"]:
                    item["sources"].append(provenance)
                    item["sources"] = item["sources"][-10:]
    expire_and_conflicts(state, now=now, days=days)
    return {"journals_examined": examined, "new_candidates": new, "total_candidates": len(state["candidates"]), "statuses": dict(Counter(c["status"] for c in state["candidates"].values()))}

def get_item(state, claim_id):
    if not re.fullmatch(r"[0-9a-f]{64}", claim_id) or claim_id not in state["candidates"]:
        raise ValueError("unknown candidate id")
    return state["candidates"][claim_id]

def review(state, claim_id, outcome, reviewer, evidence=None, reason=None):
    item = get_item(state, claim_id)
    if item["status"] == "PROMOTED":
        raise ValueError("cannot re-review promoted item")
    if outcome == "REJECTED":
        if not reason or len(reason.strip()) < 8:
            raise ValueError("rejection needs an explanatory reason")
        item["status"] = "REJECTED"
        item["verification"] = {"reviewer": reviewer, "at": iso(utcnow()), "reason": reason[:200]}
    elif outcome in {"VERIFIED_REPO", "VERIFIED_LIVE"}:
        if item["status"] == "CONFLICT":
            raise ValueError("resolve conflicting claims before verification")
        if not evidence:
            raise ValueError("independent evidence file required")
        f = Path(evidence).expanduser().resolve()
        if not f.is_file() or f.stat().st_size < 1 or f.stat().st_size > 2_000_000:
            raise ValueError("evidence must be a nonempty bounded file")
        # Evidence is a recorded human attestation, NOT semantic proof by itself.
        item["verification"] = {
            "reviewer": reviewer, "at": iso(utcnow()), "kind": outcome,
            "evidence_path": str(f), "evidence_sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
        }
        item["status"] = outcome
    else:
        raise ValueError("invalid review status")
    return item

def resolve_conflict(state, preferred_id, superseded_ids, reviewer, evidence, reason):
    """Explicit conflict adjudication; winner remains unverified."""
    winner = get_item(state, preferred_id)
    if winner["status"] != "CONFLICT" or not winner.get("topic"):
        raise ValueError("preferred candidate is not an unresolved factual conflict")
    if not reason or len(reason.strip()) < 8:
        raise ValueError("conflict resolution requires an explanatory rationale")
    if not evidence:
        raise ValueError("conflict resolution requires independent evidence")
    if not superseded_ids or len(set(superseded_ids)) != len(superseded_ids):
        raise ValueError("superseded candidate identifiers missing or duplicated")
    siblings = {
        c["id"] for c in state["candidates"].values()
        if c["id"] != preferred_id and c.get("topic") == winner["topic"]
        and c["status"] not in {"PROMOTED", "REJECTED"}
    }
    if set(superseded_ids) != siblings:
        raise ValueError("all conflicting siblings must be explicitly resolved")
    for claim_id in superseded_ids:
        candidate = get_item(state, claim_id)
        if candidate.get("topic") != winner["topic"] or candidate["status"] == "PROMOTED":
            raise ValueError("conflict candidates must share topic and not be promoted")
    f = Path(evidence).expanduser().resolve()
    if not f.is_file() or f.stat().st_size < 1 or f.stat().st_size > 2_000_000:
        raise ValueError("evidence must be a nonempty bounded file")
    check = {
        "at": iso(utcnow()), "reviewer": reviewer,
        "evidence_path": str(f), "evidence_sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
        "reason": reason[:200], "preferred": preferred_id, "superseded": list(superseded_ids)
    }
    for claim_id in superseded_ids:
        other = state["candidates"][claim_id]
        other["status"] = "SUPERSEDED"
        other["superseded_by"] = preferred_id
        other["conflict_resolution"] = check
    winner["status"] = "PENDING"
    winner["verification"] = None
    winner["conflict_resolution"] = check
    return winner


def archive_candidate(state, claim_id, reviewer, reason):
    item=get_item(state, claim_id)
    if item["status"] == "PROMOTED":
        raise ValueError("promoted claim needs explicit supersession, not archive")
    if not reviewer or not reason or len(reason.strip())<8:
        raise ValueError("archiving requires reviewer and explanatory reason")
    item["status"]="ARCHIVED"
    item["archived_at"]=iso(utcnow())
    item["archive_record"]={"reviewer":reviewer,"reason":reason[:200]}
    return item

def promote(state, claim_id, approver, canonical_root):
    item = get_item(state, claim_id)
    if item["status"] not in {"VERIFIED_REPO", "VERIFIED_LIVE"} or not item.get("verification"):
        raise ValueError("verified state and evidence required before promotion")
    reviewer = item["verification"]["reviewer"]
    if not approver or approver.casefold() == reviewer.casefold():
        raise ValueError("a distinct approver is required")
    f = Path(item["verification"]["evidence_path"])
    if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != item["verification"]["evidence_sha256"]:
        raise ValueError("evidence changed or missing")
    if SENSITIVE.search(item["claim"]) or PII.search(item["claim"]) or INJECTION.search(item["claim"]):
        raise ValueError("sensitive or untrusted content cannot be promoted")
    reviewed = parse_time(item["verification"].get("at"))
    max_age = 7 if item.get("topic") in {"production revision", "status", "deployment", "current branch"} else 30
    if reviewed is None or utcnow() - reviewed > timedelta(days=max_age) or reviewed > utcnow() + timedelta(minutes=5):
        raise ValueError("verification is stale; recheck evidence before promotion")
    target = Path(canonical_root).expanduser() / "projects" / item["project"] / "VERIFIED_FACTS.md"
    if target.exists() and target.is_symlink():
        raise ValueError("refusing symlink canonical file")
    existing = target.read_text(encoding="utf-8") if target.exists() else "# Verified facts — evidence gated\n\n"
    marker = "<!-- m2-id:" + item["id"] + " -->"
    if marker in existing:
        raise ValueError("duplicate promotion")
    item["promotion"] = {"approver": approver, "at": iso(utcnow())}
    rendered = (marker + "\n- " + item["claim"] + "  \n"
                "  *Source: " + item["verification"]["kind"] +
                "; reviewed " + item["verification"]["at"] +
                "; evidence SHA-256 " + item["verification"]["evidence_sha256"] + "*\n\n")
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".m2-facts-")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as w:
            w.write(existing + rendered)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    item["status"] = "PROMOTED"
    return str(target)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Private, evidence-gated SavageDev memory candidate workflow")
    parser.add_argument("action", choices=["scan", "status", "review", "resolve", "promote", "archive"])
    parser.add_argument("--project", required=True)
    parser.add_argument("--recent-root", default="~/.local/share/savage-agent-memory/recent")
    parser.add_argument("--state-root", default="~/.local/share/savage-agent-memory")
    parser.add_argument("--identity-map", default="~/.savagedev/project-identities.json")
    parser.add_argument("--canonical-root", default="~/.savagedev/memory")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--write", action="store_true", help="Required to persist newly scanned candidates")
    parser.add_argument("--id", help="SHA256 candidate identifier, for review/promote")
    parser.add_argument("--outcome", choices=["VERIFIED_REPO", "VERIFIED_LIVE", "REJECTED"])
    parser.add_argument("--reviewer", help="Person who checked claim against evidence")
    parser.add_argument("--evidence", help="Non-secret evidence artifact; existence/hash recorded, meaning manually checked")
    parser.add_argument("--reason", help="Rejection rationale")
    parser.add_argument("--supersede", help="Comma-separated conflicting candidate IDs")
    parser.add_argument("--approver", help="Distinct person authorizing promotion")
    args = parser.parse_args(argv)
    try:
        project = ensure_project(args.project)
        state = load_state(args.state_root, project)
        if args.days < 1 or args.days > 3650:
            raise ValueError("days must be 1..3650")
        if args.action == "scan":
            result = scan(state, args.recent_root, project, days=args.days, registry=args.identity_map)
            if args.write:
                save_state(args.state_root, project, state)
            result["written"] = args.write
        elif args.action == "status":
            result = {"project": project, "statuses": dict(Counter(c["status"] for c in state["candidates"].values())),
                      "total_candidates": len(state["candidates"])}
        elif args.action == "review":
            if not args.id or not args.reviewer or not args.outcome:
                raise ValueError("review requires --id, --reviewer and --outcome")
            item = review(state, args.id, args.outcome, args.reviewer, args.evidence, args.reason)
            save_state(args.state_root, project, state)
            result = {"id": item["id"], "status": item["status"]}
        elif args.action == "archive":
            if not args.id or not args.reviewer or not args.reason:
                raise ValueError("archiving requires --id, --reviewer and --reason")
            item=archive_candidate(state,args.id,args.reviewer,args.reason)
            save_state(args.state_root,project,state)
            result={"id":item["id"],"status":item["status"]}
        elif args.action == "resolve":
            if not args.id or not args.reviewer or not args.reason or not args.supersede:
                raise ValueError("resolution requires --id, --reviewer, --reason and --supersede")
            item = resolve_conflict(state, args.id, args.supersede.split(","), args.reviewer,
                                    args.evidence, args.reason)
            save_state(args.state_root, project, state)
            result = {"id": item["id"], "status": item["status"], "resolution": "evidence recorded; re-verification required"}
        else:
            if not args.id or not args.approver:
                raise ValueError("promotion requires --id and --approver")
            target = promote(state, args.id, args.approver, args.canonical_root)
            save_state(args.state_root, project, state)
            result = {"id": args.id, "status": "PROMOTED", "canonical_file": target}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("Memory lifecycle: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
