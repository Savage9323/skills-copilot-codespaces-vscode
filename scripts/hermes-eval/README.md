# Hermes pilot verification and recovery

This directory is a **pilot-only** toolchain. Run from the isolated integration
worktree `~/src/savage-agent-skills-hermes` on SavageDev WSL2.

Official Hermes source is pinned at `944c3a434071f43e64b443d033f3eba30c64434c`
under `~/src/hermes-agent-evaluation`.

Runtime state is privately scoped at `~/.savagedev/evaluations/hermes-h0`.
The original install used `HERMES_HOME=.../profile`,
`HERMES_RUNTIME_DIR=.../tools` and `bash setup-hermes.sh --runtime-only`.
The normal installer and global profile were intentionally not used.

## Recheck accepted evidence

    python3 scripts/hermes-eval/verify_pilot.py
    python3 -m unittest discover -s tests -p test_hermes_evaluation.py -v

The verifier requires native tool records in Hermes SQLite, not generated
text. It also checks private file permissions and independent Git/fixture
hashes. It never runs inference or accesses external services.

## Selected isolated backup and restore

    python3 scripts/hermes-eval/snapshot_restore.py
    python3 scripts/hermes-eval/snapshot_restore.py --verify /path/to/pilot/snapshot

The verifier restores to a disposable temporary directory, checks all hashes
and SQLite DB integrity, and proves two synthetic memories stay separate.
No active profile is overwritten. Existing snapshots cannot be overwritten.
Model weights and production OpenCode configuration are not backed up here.

## Copied skill manifests

    python3 scripts/hermes-eval/stage_skills.py --source SOURCE --dest NEW_EMPTY_PROFILE_SKILLS

Only individual reviewed SKILL.md files are copied; scripts and credentials
are never copied or executed by this command. Destination must not exist.
The 19-skill manifest is recorded in the isolated skills-batch profile.
Discovery does not establish actual tool execution for all skills.

## Safe stopping and rollback

Stop only the identified Hermes **evaluation** profile gateway using the
Hermes CLI, after verifying its profile and active work. A stopped named
profile may be *parked* by the Hermes multiplexer and must be explicitly
unparked with `hermes gateway start` before resuming sessions. Do not kill
shared Ollama or OpenCode processes; do not remove the custom model alias
without confirming no pilot is using it. Preserve the snapshot and manifest.
Never perform blanket process termination or recursively delete user data.

This evaluation does not approve production deployment, secret access,
provider payments, automatic agent scheduling or a merge to main.
