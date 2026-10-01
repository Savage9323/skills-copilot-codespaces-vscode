# AI Memory Sources

## OpenCode / Ollama

Preferred capture:
`opencode session export <session-id> --sanitize`

Local Ollama models share continuity through OpenCode's global skills, instructions, MCP configuration, and this memory store. Ollama itself does not maintain cross-model project memory.

## ChatGPT

ChatGPT account memory/conversation history is not assumed to be available to local OpenCode/Ollama models.

Use a structured handoff based on `HANDOFF_TEMPLATE.md`, then import it into the inbox and reconcile it.

## Other AI systems

Any other model/agent may contribute a handoff if it records:
- source
- project
- timestamp
- claims/decisions
- evidence
- uncertainty

No source is allowed to overwrite canonical memory without reconciliation.
