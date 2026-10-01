# Recent Conversation Memory

This directory stores short-term, redacted recollections of recent OpenCode sessions.

Layout:

```text
recent/<project-slug>/<session-id>.json
```

This is different from canonical project memory:

- `memory/projects/<project>.md` = durable verified facts and decisions
- `memory/recent/<project>/...` = recent conversational continuity

Recent conversation memory is automatically captured on OpenCode `session.idle` by the V2 `savage-auto-memory` plugin.

Recent memory is injected into new model requests for the same project, but it is explicitly marked as unverified recollection. Consequential facts still need live/repository verification.

Secrets must not be stored here. The plugin redacts high-signal credential patterns and excludes tool/reasoning payloads, but users should still avoid pasting secrets into AI conversations.
