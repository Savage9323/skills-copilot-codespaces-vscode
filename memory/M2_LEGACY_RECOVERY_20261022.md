# M2 — Legacy journal recovery v1 (October 22, 2026)

## Authority and provenance

The original unmodified journals remain at:

- ~/.local/share/savage-agent-memory/recent/student-benefits-intelligence/
- ~/.local/share/savage-agent-memory/recent/bountyhunter/

All 34 SBI and six BountyHunter legacy records matched read-only OpenCode
session_v2 session IDs. Session.directory and linked project.worktree both
resolved to each currently owner-registered project root. This independent
evidence was the basis for the strictly scoped migration; basename and
untrusted journal labels alone are insufficient for authorization.

The versioned, private migrated copies are stored under:

~/.local/share/savage-agent-memory/recent-v2/<registered-project-id>/

Their matching restricted checksum manifests are under:

~/.local/share/savage-agent-memory/migration-manifests/

Each migrated record is marked legacy-unverified-reference, contains original
source SHA-256 and independently verified session/project identity, and is
readable as *recollection*, never automatically treated as promoted durable
memory. Source files are not edited, renamed, deleted or overwritten.

To audit safely, without printing user content:

    python3 scripts/migrate-legacy-journals.py --project student-benefits-intelligence
    python3 scripts/migrate-legacy-journals.py --project bountyhunter

The already-applied migration refuses overwriting a migration manifest. Do
not re-run --apply against live data. If another version is needed, use a
newly reviewed schema/migration destination; do not delete existing evidence.

## Retrieval fixes

The plugin now evaluates both regular and migrated journal directories, checks
schema, safe session IDs, workspace provenance, timestamps and
legacy source hashes, then removes unknown-role transport snippets, and *then*
takes the newest four valid journals.
Expired, malformed and wrong-project entries cannot occupy those four slots.

The daily candidate scanner also reads the migrated store. It creates private
PENDING candidates only, with no automatic verification or promotion.

Unregistered workspaces receive a restricted onboarding context with no
global, project or historical memory. The human owner must map a resolved
workspace root in the private project-identity registry before authorization.

## Redaction

Contextual secret-value redaction preserves nonsensitive surrounding prose;
structured credential assignments and known credential patterns are masked.
Long opaque values are evaluated by character diversity and source context,
so ordinary commit/build/checksum IDs are less likely to be falsely removed.
Likely prompt-injection instructions are quarantined before model context.
No classifier guarantees detection of every credential or injection; secure
OS-level tool isolation remains a separate acceptance requirement.

## Limitations

Even verified session provenance does not prove the historical claims true.
A live fresh-session SBI test successfully recalled a synthetic historical
marker from the migrated store. The synthetic record and its prompt journal were
archived out of active retrieval afterwards. A parallel BountyHunter model test
timed out after 115 seconds without usable evidence, so cross-project model-level
acceptance remains INCOMPLETE. Source/session and allowed-role isolation checks
passed independently using deterministic native selection tests. M2 lifecycle final acceptance additionally
requires independently authenticated promotion, supersession and archival,
with a human-reviewed evidence process. M3 live machine-account authorization
and credential injection are separate blockers.

The prechange full configuration and private-memory snapshot is saved under
~/.savagedev/backups/20261022T075016Z/ and passed isolated restore checks.

## Project onboarding and resource isolation

New projects must be manually approved by the owner and added to mode-0600
~/.savagedev/project-identities.json with an exact, already-resolved repository
root (which must exist and have a .git marker). Registry backups and code review
must precede editing. Do not auto-register from a chat prompt, folder basename,
imported journal or unauthenticated shell command. Unknown workspaces receive
restricted onboarding guidance, not global/project memory or historical journals.

This mapping enforces model-context scoping, NOT Unix file protection between
agents sharing an OS account. A stronger production design uses separate Unix
identities or containers with restricted mounts, per-project read-only data
binds, no inherited BWS credentials, and real denied-shell/denied-read tests.
Do not create Unix accounts, alter mounts or rotate production credentials
without a separate owner-reviewed OS integration plan and rollback.
