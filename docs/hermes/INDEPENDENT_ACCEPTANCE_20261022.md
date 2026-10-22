# SavageDev Hermes pilot — independent verification

Date: 2026-10-22. Decision: **isolated H0-H4 pilot passed with restrictions; H5 is not accepted or deployed**.

## Verified environment

- Official Nous Research Hermes checkout: commit `944c3a434071f43e64b443d033f3eba30c64434c` (MIT).
- Isolated state: `~/.savagedev/evaluations/hermes-h0/`; no global Hermes installation or paid provider.
- Existing OpenCode v2.0.26, Ollama v0.40.3 and canonical memory retained.
- Test model: `savagedev-hermes-qwen9b-64k`, 65,536-token context; original OpenCode model unchanged.
- Python 3.14 Docker sandbox; network disabled and synthetic project mounts only.

## Acceptance evidence

- Automated verifier: **32/32 PASS**, including real SQLite tool events, config restrictions and session continuity.
- Offline regression tests: **8/8 PASS**, including tampering, cross-memory restore and falsified event gates.
- Native Hermes tool execution: terminal, `skill_view`, synthetic read-only MCP discovery/call/result.
- Separate synthetic profile memory: SBI and BountyHunter fixture markers correct and not cross-disclosed.
- All 19 reviewed OpenCode SKILL.md manifests staged as SHA-matched copies in a separate Hermes profile and discovered as local skills. **Only capability-router had a proven native load event.**
- Disposable coding fixture: Hermes changed only calculator.py; host independently passed all 3 unit tests.
- Independent reviewer: first review **INCOMPLETE** because container lacked Git; second reviewer **PASS** using a read-only Git-derived checksum baseline and native test results.
- Host canonical memory not exposed inside the tested container. This does **not** prove isolation for unsandboxed host shell tools.
- Clean session resume: first attempt failed because the evaluation profile was parked; unparked using the supported gateway start command, then recovered a saved synthetic ticket. SQLite confirms same session, two turns, four messages, no tools.
- Selected configuration/session/memory snapshot restored privately with hash and SQLite integrity checks. It excludes real credentials, model weights and production host services.

## Repeatable checks

Run from the feature worktree:

    python3 scripts/hermes-eval/verify_pilot.py
    python3 -m unittest discover -s tests -p test_hermes_evaluation.py -v
    python3 scripts/hermes-eval/snapshot_restore.py --verify SNAPSHOT_DIRECTORY

The verifier directly queries saved Hermes SQLite tool records and independent fixture hashes. Model-generated assertions alone do not count as execution proof.

## Remaining restrictions

Hermes must remain a **pilot**, with OpenCode the primary production coding/review engine. No production GitHub, SBI Supabase, Caido or Bitwarden access was delegated to Hermes. Profile separation alone is not an OS security boundary. M2 signed human memory approval and M3 Bitwarden live authentication remain incomplete. Full long-running-task interruption recovery, all 19 skills' tool execution, multi-agent production permission policies, complete offline host recovery and independent Chat 04 acceptance remain open.

No push, merge, deployment, payment integration, global model change or credential migration is approved by this checkpoint.
