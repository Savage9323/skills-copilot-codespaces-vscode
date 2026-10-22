# SavageDev Hermes Agent — Isolated H0–H4 compatibility assessment
**Date:** 2026-10-22 | **Owner:** Chat 01 | **Disposition:** PILOT PASSED WITH RESTRICTIONS; H5 NOT AUTHORIZED FOR PRODUCTION

## Source and environment
Official source: https://github.com/NousResearch/hermes-agent, pinned SHA `944c3a434071f43e64b443d033f3eba30c64434c`, MIT license. Hermes CLI reports `vgit.944c3a4 (2026.9.24)`; source requires Python >=3.11,<3.15, isolated pinned Python 3.14.7. Host: WSL2, NVIDIA RTX 3060 12 GB, 32 GB Windows RAM, OpenCode 2.0.26, Ollama 0.40.3.

Source checkout: `~/src/hermes-agent-evaluation/`.
Isolated runtime: `~/.savagedev/evaluations/hermes-h0/`, containing `profile/`, `profiles/`, `tools/`, `fixtures/`, `evidence/`. Installed with `setup-hermes.sh --runtime-only` and a private `HERMES_HOME`/ `HERMES_RUNTIME_DIR`. The regular `~/.hermes` installation, OpenCode service, its global configs, and canonical memory were not modified. No paid API providers were configured or used.

Model alias `savagedev-hermes-qwen9b-64k`: copied Ollama Qwen3.5 9B OpenCode-fast model with `num_ctx=65536`, `num_predict=512`; the working original remains `num_ctx=32768`. Ollama OpenAI-compatible API is `http://127.0.0.1:11434/v1`. Hermes requires at least 64,000 context tokens for tool-capable sessions; an Ollama model with a suitable real context setting is mandatory.

The evaluation uses `python:3.14-slim` Docker with `docker_network: false`, `container_persistent: false`, dropped capabilities and no-new-privileges. `redis:7-alpine` was rejected for lack of Bash. Python image digest observed: `sha256:0514bc76712d64f8bb48adcb95b1ab0d88c69fee95d62fe4c18ee948bee9b1e1`.

## Evidence matrix
| Phase | Test | Verdict | Verifiable evidence and limits |
|---|---|---|---|
| H0 | Official source, license, Python, local-model, skills, MCP and security review | PASS for research | Source SHA pinned; inspect code/docs before future upgrades |
| H1 | Isolated pinned runtime setup and CLI import/version | PASS | Separate `HERMES_HOME`; no default user launcher or `~/.hermes` |
| H1 | Real local Qwen inference | PASS | `evidence/local-chat-smoke.stdout` exact `SAVAGEDEV_HERMES_LOCAL_OK`; cold end-to-end 106 seconds |
| H1 | Genuine terminal tool | PASS | `profile/state.db` assistant `terminal` call and separate native tool result `SAVAGEDEV_HERMES_DOCKER_TOOL_OK`; ~19 seconds |
| H1 | Performance & GPU fit | PASS WITH WARNINGS | 65536 context model loaded fully on RTX 3060, Ollama reported 7.6 GB model, GPU use peaked approximately 11.5 GB total during tests; concurrency/throughput/timeout/load benchmarks pending |
| H2 | Shared skill discovery | PASS for two copied skills | SHA-identical `capability-router`, `software-architect`; Hermes listed 53 builtin and 2 local enabled |
| H2 | Real skill loading | PASS | Native `skill_view` tool call/result in `profile/state.db`; `evidence/skill-load.stdout`; remaining 17 shared skills untested |
| H2 | Separate profile memory on fresh sessions | PASS for synthetic fixtures | SBI responded `QUARTZ-LANDFALL-1947`, BountyHunter `MAPLE-ESTUARY-8265`, own profile SQLite records only, no foreign marker |
| H2 | Existing M2 journal migration, promotion, sanitizer, Bitwarden | NOT TESTED with Hermes | Existing OpenCode memory remains authoritative; no historical user memory was imported into Hermes |
| H3 | Scoped MCP discovery and real invocation | PASS for synthetic MCP only | `mcp-fixture/state.db` native `tool_search`, `tool_describe`, `tool_call`, `mcp__savagedev_synthetic_readonly__fixture_checksum`; exact SHA prefix output; other profiles did not register server |
| H3 | Real GitHub, SBI Supabase, Caido MCP | NOT TESTED | No credentials inherited or production integrations copied |
| H4 | Disposable coding worker bug fix | PASS | Docker-only `calculator.py` correction, native terminal records, 3/3 host-independent unit tests, only implementation file changed (~45 seconds) |
| H4 | First independent reviewer | INCOMPLETE | The minimal container did not have Git; reviewer correctly declined to attest unmodified tests; preserved `evidence/h4-reviewer.stdout` |
| H4 | Second read-only reviewer | PASS for fixture | Different profile, read-only fixture and Git-derived baseline manifest, native terminal results, matching original test SHA and 3/3 tests (~51 seconds); independent host repeat passed |
| H4 | Unrelated host canonical-memory access | PASS for fixture denial | Native tool in air-gapped reviewer sandbox confirmed host memory file unavailable; `evidence/h4-negative-access.stdout`; no real secrets read |
| H4 | Interrupted-task resumability, long-running automation and crash restore | INCOMPLETE | Requires separate recovery test; do not claim production autonomous reliability |
| H5 | Shared platform adoption, production workflows | BLOCKED ON OWNER / INDEPENDENT ACCEPTANCE | No migration, merge, deployment, credential change or production reroute authorized |

## Security observations
- Hermes profiles are process-level configuration/memory separation, **not** OS identity isolation. Real agents sharing one Unix user or host shell can violate boundaries if unconstrained.
- The Docker code agent was air-gapped. The worker mounted **only a disposable Git fixture**; reviewer read-only mounts included only that fixture and independently generated checksum baseline. No real project directories, canonical memory, Bitwarden, or GitHub/Supabase credentials were passed.
- Gemini/OpenAI/OpenRouter and paid inference connections remained unconfigured. Local Ollama was the only tested inference provider. The test gateway was local/manual, not installed as a system service.
- The Docker host does not support the per-container disk-quota feature; `container_memory`/CPU limits do not replace durable disk quotas.
- Qwen3.5 9B successfully used tools, but some outputs and independent review depend on available sandbox binaries (Git absent in slim image). Hermes native session SQLite proves actual tool events, not text-only assertions.
- Existing M2 requires independently authenticated promotion; M3 Bitwarden machine-account access remains unauthenticated, and real MCP credentials must not be copied to Hermes without owner-approved OS isolation.

## Recovery and rollback
All Hermes pilot state is under the private evaluation root and official clean checkout. The custom 64K alias is separate from existing models. Stop only evaluation gateways and containers and unload only the pilot Ollama alias; do not stop the shared Ollama server or OpenCode. Private evidence remains under the eval root. Revert by disabling Hermes pilot profiles and removing only explicitly approved eval files; do not delete before reviewing the recovery manifest.

**Recommendation:** Continue Hermes as an **optional, isolated local orchestration pilot** while OpenCode retains ownership of live coding, review, memory, and project credentials. Move to H5 only after independent Chat 04 acceptance and specific owner approvals.
