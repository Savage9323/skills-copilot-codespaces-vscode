# Chat 04 — independent Hermes acceptance handoff (2026-10-22)

**Status:** isolated H0-H4 pilot with reproducible evidence; H5 production adoption is not authorized.

**Source:** pinned official Nous Research Hermes git SHA
`944c3a434071f43e64b443d033f3eba30c64434c`.
**Chat 01 worktree:** `~/src/savage-agent-skills-hermes/` on branch
`feat/hermes-isolated-pilot-20261022`.
**Test root:** `~/.savagedev/evaluations/hermes-h0/`.
**Final restricted snapshot:**
`~/.savagedev/evaluations/hermes-h0/backups/hermes-pilot-20261022T110253Z/`.

## Reproduce without credentials, model calls or remote access

    cd ~/src/savage-agent-skills-hermes
    python3 scripts/hermes-eval/verify_pilot.py
    python3 -m unittest discover -s tests -p test_hermes_evaluation.py -v
    python3 scripts/hermes-eval/snapshot_restore.py --verify ~/.savagedev/evaluations/hermes-h0/backups/hermes-pilot-20261022T110253Z

Expected evidence: 32/32 verifier checks PASS; 8/8 unit checks PASS;
70 files copied/hash-verified into an isolated temporary restore; SQLite
integrity PASS; distinct restored synthetic profiles PASS. These are
**pilot assertions** requiring independent source and tool-event inspection.

## Native Hermes events to examine in read-only SQLite

- `profile/state.db`: real `terminal` and `skill_view` call/result rows.
- `profiles/mcp-fixture/state.db`: real synthetic MCP discovery and call/result.
- `profiles/sbi-fixture/state.db` and `profiles/bounty-fixture/state.db`: separate memories and sessions.
- `profiles/coding-worker/state.db`: terminal calls and disposable code edit.
- `profiles/coding-reviewer-v2/state.db`: read-only independent tests and denied host memory access.
- `profiles/resume-fixture/state.db`: two turns and four messages under same session after test gateway stop/unpark.

Review first failed reviewer result as INCOMPLETE, not PASS. Confirm tests
were independently rerun, the original test fixture was unchanged and the
worker only edited calculator.py. Separate real tools from generated text.

## Remaining acceptance gates

1. Production OS separation for agents with host shell authority, not merely Hermes profiles.
2. Native execution for all 19 shared skills (19 discoverable, 1 proven loaded).
3. Signed human M2 memory approval and independent project-scoped retrieval.
4. M3 project-scoped Bitwarden machine accounts and real deny/injection tests.
5. Production GitHub and SBI Supabase read-only MCP authentication and unrelated-project denials; Caido BountyHunter-only.
6. Full task-crash recovery, unattended scheduling controls, idle-GPU/latency/load tests and complete offline host restore.
7. Independent Chat 04 decision with PASS / PASS WITH WARNINGS / INCOMPLETE / FAIL classifications.

Do not approve production deployment, merging, secret migration or broad tool
access from this evidence alone. Chat 01 alone owns shared integration.
