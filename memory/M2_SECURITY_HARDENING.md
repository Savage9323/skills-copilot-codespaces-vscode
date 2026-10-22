# SavageDev M2 — Scoped memory hardening

The working OpenCode V2 savage-auto-memory hooks for prompt capture, context,
compaction, and private journal persistence are preserved.

Project identity now uses resolved repository/workspace root and owner-only
~/.savagedev/project-identities.json. Owner-registered roots use their assigned
canonical project identifier; unregistered roots use basename + path hash.
Same-basename repositories cannot share project memory by name alone.

Canonical directories use 0700, Markdown files use 0600. The plugin reads only
the mapped project's canonical files and the allowlisted global AGENT_RULES.md.
All text is passed as quoted reference data, not trusted instructions.

Private journals require a safe session ID, exact matching project identifier
and resolved workspace_root. Legacy basename-only journals are preserved but
excluded from automatic retrieval and candidate promotion. Nonadjacent duplicate
snippets are collapsed. Sensitive material and likely prompt-injection strings
are quarantined/redacted, with metadata-only quarantine logs.

The candidate scanner checks the same journal identity and provenance. Stale
facts require rechecking; conflicts and supersessions preserve rejected history.

Evidence: private SavageDev evidence/chat01-20261021/m2-collision-a.jsonl and
m2-collision-b.jsonl; two same-named fixture repositories used distinct hashed
IDs. The synthetic canonical fact was deleted after tests; the current service
requires the empty fixture workspace directories until its old session references
are released. The prechange M6 snapshot was verified in isolation.

Security limits: pattern/entropy classification is not perfect. Filesystem read
hooks and model permissions are not an OS sandbox; shell, custom tools, and
different Unix identities need separate resource isolation. Reviewer and
approver labels are not authenticated humans, so unattended promotion is not
approved. Do not mark full M2 acceptance yet.
