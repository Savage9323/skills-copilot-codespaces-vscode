# Recent Conversation Memory

Automatic recent OpenCode conversation recollections are **not stored in this Git repository**.

They live in private local state:

```text
~/.local/share/savage-agent-memory/recent/<project-slug>/<session-id>.json
```

This repository keeps only documentation and durable canonical memory.

The local recent-session store provides short-term conversational continuity across new OpenCode sessions on the same machine. It is:

- redacted for high-signal credential patterns
- bounded in size when injected into model context
- marked as unverified recollection
- excluded from Git by design

Canonical memory remains in:

```text
memory/projects/<project>.md
```

Consequential facts still require repository/live verification.
