# Local Toolchain Memory

Last verified broadly: 2026-09-28 to 2026-10-01

Verify versions live before version-sensitive work.

## Primary workstation

- Windows 11 host
- WSL2 Ubuntu primary development environment
- NVIDIA GeForce RTX 3060 12 GB
- Docker Desktop with WSL integration
- Git/GitHub CLI
- Node.js / npm / pnpm
- Python
- VS Code CLI
- Azure CLI
- Ollama
- OpenCode

## Local AI

Use OpenCode as the agent/orchestration layer and Ollama as the interchangeable local model runtime.

Stable starting coding model:
- qwen2.5-coder:14b

Other locally installed models may exist. Query `ollama list` and verify `ollama ps` / `nvidia-smi` before assuming availability or GPU placement.

## Shared-agent architecture

- Global instructions: ~/.config/opencode/AGENTS.md
- Global skills: ~/.config/opencode/skills/
- Shared memory: ~/.config/opencode/memory/
- Project-specific instructions: repository AGENTS.md
- Project/live state outranks memory
