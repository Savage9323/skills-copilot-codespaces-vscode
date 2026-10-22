# M2 — Evidence-gated automatic memory candidates

Implementation branch: feat/m2-memory-lifecycle-20261021. This pipeline is
additive to the already working V2 savage-auto-memory plugin. Scans do not
replace context injection or write to canonical memory.

## Authority and paths

- Runtime canonical truth: ~/.savagedev/memory/global/ and
  ~/.savagedev/memory/projects/<project>/.
- Private recent context: ~/.local/share/savage-agent-memory/recent/<project>/*.json.
  Project IDs now derive from authorized repository roots; old basename-only
  journals are retained but cannot be injected without provenance.
- New untrusted candidates: ~/.local/share/savage-agent-memory/candidates/<project>.json.
- Legacy ~/.config/opencode/memory links to the central repo's historical
  memory/ tree. It is not a second writable runtime canonical store. Validate
  historical entries against live evidence before selectively migrating.
- Never write raw recent journals or pending candidates into canonical memory.

## Lifecycle

1. Plugin captures private OpenCode prompts and recent-session context.
2. Scheduled scanner reads only role=user snippets matching the project.
3. Conservative deterministic rules extract explicit decisions, blockers,
   completions, next actions, and structured facts.
4. Scanner rejects probable secrets, sensitive identifiers and obvious injected
   instructions. These are defense-in-depth filters, not absolute privacy protection.
5. Candidate records are deduplicated by claim hash and have bounded source
   provenance. They are PENDING, never automatically VERIFIED.
6. Same-topic incompatible factual values become CONFLICT. Old unverified
   candidates become STALE_RECHECK and remain unpromoted.
7. CONFLICT requires explicit resolution: select the supported claim, identify
   and reject all contradictory sibling IDs, record independent evidence and
   rationale. The preferred claim returns to PENDING and must be verified again.
8. A reviewer manually attests VERIFIED_REPO or VERIFIED_LIVE with a non-secret
   evidence file. A checksum is stored, but file existence/checksum does not
   prove its contents support the claim. Human semantic review is required.
9. A distinct approver explicitly promotes verified candidates. Only promoted
   facts are written to project canonical VERIFIED_FACTS.md, with provenance
   identifier, source type, verification date and evidence digest.
10. No journal or candidate is automatically deleted. Retention/destruction
   must be handled by a separately approved and tested policy.

## Safe commands

Dry-run one project without writing or printing private claims:

    python3 scripts/memory-lifecycle.py scan --project student-benefits-intelligence

Show candidate counts:

    python3 scripts/memory-lifecycle.py status --project student-benefits-intelligence

Write candidates for all projects, never promote:

    scripts/memory-lifecycle-scan-all.sh

To verify a claim, manually inspect it in the restricted candidate file and
independently check the current repository/provider/runtime. Example:

    python3 scripts/memory-lifecycle.py review --project <slug> --id <sha256> \
      --outcome VERIFIED_REPO --reviewer <reviewer> \
      --evidence <non-secret-evidence-file>

To resolve conflicts without prematurely promoting the winner:

    python3 scripts/memory-lifecycle.py resolve --project <slug> --id <preferred-sha256> \
      --supersede <loser-sha256>[,<other-loser-sha256>] \
      --reviewer <reviewer> --evidence <non-secret-evidence> \
      --reason "Evidence supports preferred current value"

Re-verify the preferred claim after conflict resolution. Conflicting records
remain in private candidate history marked REJECTED, not silently erased.

Only after a different, accountable person checks and explicitly approves:

    python3 scripts/memory-lifecycle.py promote --project <slug> --id <sha256> \
      --approver <distinct-approver>

The supplied reviewer and approver labels are not authenticated identities.
An AI agent must not self-certify a claim. Production-grade automated promotion
needs stronger authenticated authorization and semantic evidence validation.

## Scheduling and test

Optional systemd user service/timer files are in systemd/. The timer scans
daily, never reviews/promotes, and needs no tokens, secrets, or network.

    python3 -m unittest discover -s tests -p 'test_memory_lifecycle.py' -v
    bash doctor.sh

Conservative rules deliberately miss ambiguous claims. A journal captured_at
timestamp is not necessarily the original date of every statement and cannot
establish whether an old production status is currently true.
