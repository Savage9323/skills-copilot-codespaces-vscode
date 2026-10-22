# SavageDev Hermes H5 — controlled integration plan (not deployed)

## Gate 1: Reproducibility and independent acceptance
- Retain pinned source SHA, exact model Modelfile, container image digest, isolated install command and versioned profile backups.
- Use read-only native Hermes `state.db` event records to confirm actual terminal/skill/MCP calls. Do not accept textual descriptions or unavailable-tool excuses as a PASS.
- Run independent full restore and interrupted-task resume tests in an isolated environment.
- Verify per-project approval boundaries and denied cross-project agent-tool calls at the OS layer.
- Chat 04 reviews all evidence and may classify PASS / PASS WITH WARNINGS / INCOMPLETE / FAIL.

## Gate 2: Capability parity without migrating canonical state
- Keep OpenCode primary developer, test runner and reviewer. Hermes may coordinate disposable tasks and call **approved** OpenCode runners as a *strictly scoped subprocess* only after permissions are proven.
- Import copies of up to the 19 reviewed OpenCode skills to distinct Hermes profiles, with hashes, dependencies and each skill's actual `skill_view` test. Never share the live writable skills tree or unknown scripts.
- Keep canonical SavageDev project memory owned by OpenCode. A future optional Hermes memory adapter must be read-only and provenance-aware, and honor M2 rejection, supersession, aging, restricted globals and human signed promotion. No automatic migration of historical journals.
- Gate production GitHub and Supabase MCP use behind independently read-only, project-only credentials with Docker/file-system isolation; Caido remains BountyHunter-only and can be offline without affecting website/SBI agents.
- Preserve Bitwarden vault boundaries. No BWS tokens or production values visible to a model, generic shell or unrelated project.

## Gate 3: Agent roles and isolation
1. Hermetic, network-disabled research/test worker using synthetic fixtures.
2. Separate reviewer profile and OS read-only mounts; independent evidence checker refuses missing tests and untrusted output.
3. Security and Watchdog workflows with explicit limited tools, memory and project roots.
4. Website/SEO/analytics assistants using dedicated project roots and read-only APIs by default.
5. Explicit human approvals before production writes, deployment, publishing, payment, secrets or configuration edits.

## Gate 4: Automation and recovery
- Test Hermes scheduling and job replay only with disposable tasks; no recurring production cron or messaging gateway installed.
- Test process interruption, checkpoint resumability, context/session continuity and failure isolation.
- Demonstrate hash-verified isolated profile/session/skills/config restore, then peer-review a rehearsed recovery SOP.
- Production rollback must leave original OpenCode/Ollama config and canonical memory unchanged.

## Performance/operations
- The tested 64K Qwen3.5 9B model loaded at ~7.6 GB and nearly exhausted the 12 GB RTX3060 in some sessions with competing GPU use; cap concurrency and obtain idle-GPU acceptance.
- Cold CLI local request ~106 sec, warm tool task ~19 sec, skill load ~20 sec, MCP ~24 sec, coding ~45 sec, reviewer ~51 sec. These are **single pilot observations**, not benchmarks or SLA.
- $0-first: Ollama and local Docker only. No paid APIs or automatic billing activation.
- Review source updates deliberately; no unattended changing the pinned Hermes checkout.

## Owner decisions still required
- Whether to approve a new GitHub review-only feature branch push, after final evidence is packaged.
- Whether to authorize H5 production integration at all (NOT authorized by this pilot).
- Secure scoped machine identities, Bitwarden bootstrap, public-key reviewer trust, and OS-specific mounts/permissions (requires explicit approval).
- Independent Chat 04 acceptance and a representative idle-GPU performance window.

Until all gates pass, disposition is **PILOT ONLY — DO NOT MERGE OR DEPLOY**.
