#!/usr/bin/env python3
"""Offline, redacted verification of the isolated Hermes Agent H0-H4 pilot.

Checks native SQLite events and immutable fixture provenance instead of
accepting model-generated text alone. No model runs, network, or secrets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

SOURCE_REVISION = "944c3a434071f43e64b443d033f3eba30c64434c"
EXPECT = {
    "local-chat-smoke.stdout": "SAVAGEDEV_HERMES_LOCAL_OK",
    "docker-tool-smoke.stdout": "SAVAGEDEV_HERMES_DOCKER_TOOL_OK",
    "memory-sbi-a.stdout": "QUARTZ-LANDFALL-1947",
    "memory-bounty-a.stdout": "MAPLE-ESTUARY-8265",
    "mcp-native.stdout": "FIXTURE_SHA256_PREFIX:" + hashlib.sha256(
        b"SAVAGEDEV_HERMES_MCP_TEST_727").hexdigest()[:16],
}


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for data in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def safe_private(path: Path) -> bool:
    return (path.is_file() and not path.is_symlink() and
            path.stat().st_mode & 0o077 == 0)


def messages(db: Path):
    if not safe_private(db):
        raise ValueError("missing or insecure profile SQLite database")
    con = sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True, timeout=4)
    try:
        return con.execute(
            "SELECT role, tool_name, tool_call_id, tool_calls, content "
            "FROM messages ORDER BY id").fetchall()
    finally:
        con.close()


def sqlite_sessions(db: Path):
    con = sqlite3.connect("file:" + str(db) + "?mode=ro",uri=True,timeout=4)
    try:
        return con.execute("SELECT DISTINCT session_id FROM messages").fetchall()
    finally:
        con.close()


def native_result(rows, tool: str, required: str | None = None) -> bool:
    return any(role == "tool" and name == tool and call_id and
               (required is None or required in (content or ""))
               for role, name, call_id, _calls, content in rows)


def audit(root: Path, source: Path) -> dict:
    result = {"status": "PASS", "checks": {}, "limits": []}
    checks = result["checks"]

    def check(name, passed):
        checks[name] = "PASS" if passed else "FAIL"
        if not passed:
            result["status"] = "FAIL"

    check("source_sha_pinned", source.is_dir() and not source.is_symlink()
          and subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip() == SOURCE_REVISION)
    check("isolated_profile", safe_private(root / "profile/config.yaml"))
    check("no_global_hermes_home", not (Path.home() / ".hermes").exists())

    for filename, expected in EXPECT.items():
        observed = root / "evidence" / filename
        check("output_" + filename.removesuffix(".stdout"),
              safe_private(observed) and observed.read_text().strip() == expected)

    config_paths = [root / "profile/config.yaml",
                    *(root / "profiles").glob("*/config.yaml")]
    for conf in config_paths:
        raw = conf.read_text()
        key = conf.parent.name + "_airgap"
        check(key, "docker_network: false" in raw and
              "container_persistent: false" in raw and
              "provider: custom" in raw and "127.0.0.1:11434/v1" in raw)
    check("no_real_credentials_in_fixture_mcp",
          "bws" not in (root / "profiles/mcp-fixture/config.yaml").read_text().lower()
          and "supabase" not in (root / "profiles/mcp-fixture/config.yaml").read_text().lower())

    primary = messages(root / "profile/state.db")
    check("native_terminal",
          native_result(primary, "terminal", "SAVAGEDEV_HERMES_DOCKER_TOOL_OK"))
    check("native_skill_view", native_result(primary, "skill_view", "capability-router"))
    mcprows = messages(root / "profiles/mcp-fixture/state.db")
    check("native_mcp",
          native_result(mcprows, "mcp__savagedev_synthetic_readonly__fixture_checksum",
                        EXPECT["mcp-native.stdout"]))
    check("mcp_only_in_fixture_profile",
          all("savagedev_synthetic_readonly" not in
              (root / "profiles" / slug / "config.yaml").read_text()
              for slug in ("sbi-fixture", "bounty-fixture")))

    sbi = messages(root / "profiles/sbi-fixture/state.db")
    bounty = messages(root / "profiles/bounty-fixture/state.db")
    def scoped(rows, present, absent):
        assistant = "\n".join((text or "") for role, _name, _cid, _calls, text in rows
                              if role == "assistant")
        return present in assistant and absent not in assistant
    check("native_sbi_fresh_recall",
          scoped(sbi, "QUARTZ-LANDFALL-1947", "MAPLE-ESTUARY-8265"))
    check("native_bounty_fresh_recall",
          scoped(bounty, "MAPLE-ESTUARY-8265", "QUARTZ-LANDFALL-1947"))

    fixture = root / "fixtures/tiny-python-repo"
    baseline = json.loads((root / "evidence/review-baseline.json").read_text())
    check("test_file_unchanged",
          hash_file(fixture / "test_calculator.py") == baseline["original_test_sha256"])
    check("implementation_changed",
          hash_file(fixture / "calculator.py") != baseline["original_calculator_sha256"])
    files = subprocess.run(["git", "-C", str(fixture), "diff", "--name-only"],
                           capture_output=True, text=True, timeout=10)
    check("worker_only_changed_implementation", files.returncode == 0 and
          files.stdout.strip() == "calculator.py")
    tests = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q"],
                           cwd=fixture, capture_output=True, text=True, timeout=20)
    check("independent_host_three_tests",
          tests.returncode == 0 and "Ran 3 tests" in tests.stderr
          and "\nOK" in tests.stderr)
    worker = messages(root / "profiles/coding-worker/state.db")
    reviewer = messages(root / "profiles/coding-reviewer-v2/state.db")
    check("worker_native_terminal", native_result(worker, "terminal"))
    check("reviewer_native_tests",
          native_result(reviewer, "terminal", "Ran 3 tests"))
    check("negative_memory_access",
          any(role == "tool" and name == "terminal" and call_id and
              "AGENT_RULES.md" in (content or "") and
              "No such file or directory" in (content or "") and
              "/workspace/calculator.py" in (content or "")
              for role, name, call_id, _calls, content in reviewer)
          and (root / "evidence/h4-negative-access.stdout").read_text().strip()
          == "GLOBAL_MEMORY_DENIED")

    resume = messages(root / "profiles/resume-fixture/state.db")
    sessions = {row_session[0] for row_session in
                sqlite_sessions(root / "profiles/resume-fixture/state.db")}
    check("native_clean_session_continuity",
          len(sessions) == 1 and len(resume) == 4 and
          [row[0] for row in resume] == ["user", "assistant", "user", "assistant"] and
          "ACK_TICKET_RECEIVED" in (resume[1][-1] or "") and
          "CITRINE-VAULT-4816" in (resume[-1][-1] or ""))

    result["summary"] = {"total": len(checks),
                         "passed": sum(v == "PASS" for v in checks.values()),
                         "failed": sum(v == "FAIL" for v in checks.values())}
    result["limits"] = [
        "Synthetic fixtures only; no production MCP credentials or migrations.",
        "No proof of real-agent Bitwarden authorization or host-user OS isolation.",
        "No full 19-skill validation, long-running automation or model benchmark.",
    ]
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path,
                    default=Path.home() / ".savagedev/evaluations/hermes-h0")
    ap.add_argument("--source", type=Path,
                    default=Path.home() / "src/hermes-agent-evaluation")
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    try:
        outcome = audit(ns.root, ns.source)
    except (OSError, ValueError, subprocess.SubprocessError, sqlite3.DatabaseError,
            json.JSONDecodeError) as err:
        outcome = {"status": "INCOMPLETE", "reason": type(err).__name__,
                   "checks": {}, "limits": ["Unable to verify all evidence."]}
    payload = json.dumps(outcome, indent=2) + "\n"
    if ns.output:
        if ns.output.exists() or ns.output.is_symlink():
            raise SystemExit("Refusing to overwrite existing acceptance evidence")
        fd = os.open(ns.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(payload)
    print(payload)
    return 0 if outcome["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
