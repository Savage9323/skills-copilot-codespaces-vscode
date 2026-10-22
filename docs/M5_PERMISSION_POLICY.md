# M5 — SavageDev shared capabilities (2026-10-21)

Live OpenCode v2.0.26 uses ordered V2 permissions with action, resource,
effect, not V1 permission/bash. Chat 01 owns global integration.

## Scoped MCP registrations

- Global: github-readonly and disabled ddgs.
- SBI: supabase-sbi-readonly as a repository-local server.
- BountyHunter: Caido only, plus inherited global servers.
- Caido's local service remains offline; failure is BountyHunter-scoped.

## Model-facing permission safeguards

- Global ordered rules ask for external directories and global configuration
  edits, deny reads of credential files, deny destructive shell operations
  and request approval before pushing.
- Reviewer is restricted to read-only investigation shell commands and may
  write the independent REVIEW.md approval artifact.
- Security is deny-by-default with permitted read/search, narrow audits,
  and writes limited to evidence/alert artifacts.
- Watchdog is deny-by-default and can write its ALERTS.md.
- BountyHunter denies SBI Supabase tool names and asks before Caido tools.

Limit: model-level OpenCode permission checking is not an OS sandbox.
Host shell authority remains broad outside the agent harness. Cross-project
isolation cannot be considered complete without further native and OS-level
testing. Missing or fabricated tool events do not count as proof.

## Evidence and tests

Run: python3 scripts/check-capability-policy.py
Native successful read and shell events:
~/.savagedev/evidence/chat01-20261021/m7-review-realtool.jsonl
Native rejected synthetic .env read event:
~/.savagedev/evidence/chat01-20261021/m7-secret-read-denial.jsonl

12 duplicate backup SKILL.md directories were checksum-verified and moved
out of OpenCode discovery into
~/.savagedev/archives/opencode-skill-backups-20261021/.
19 intended skill directories remain discoverable.

Skill docs now point to the two validated scripts in
~/src/savage-agent-skills/scripts/ (the central repository root),
rather than nonexistent skill-local scripts.

Pending: all-agent negative tests, OS-level isolation, live BWS injection,
full independent platform acceptance.

## 2026-10-21 follow-up hardening

Updated effective Review, Security, Watchdog, Cleanup Planner and Lifecycle
Auditor rules with final explicit read, glob/grep secret-path denials and
external-directory denial. Global Build policy also places secret-file
denials after its general allow rules. No agent or model was restarted; config
reload succeeded after restoring empty synthetic workspace paths referenced
by the existing OpenCode service.

Verify:
python3 scripts/verify-agent-denials.py

This proves ordered configuration decisions, not arbitrary system-call denial.
A model-driven native skill-load attempt timed out after 125 seconds without
tool events and must be classified INCOMPLETE. Do not assert a skill-load pass
or treat nonzero/fake events as successful tool execution.
