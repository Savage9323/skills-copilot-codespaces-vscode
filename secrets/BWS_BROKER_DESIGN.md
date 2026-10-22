# M3 — Restricted Bitwarden broker

scripts/vault-run.sh accepts only an approved project slug and named action.
scripts/vault-broker.py checks owner-private project mapping and approved
executable allowlist, fixed arguments, and executable SHA-256, then calls
Bitwarden Secrets Manager without using a shell. It blocks invalid project
IDs, unknown actions, modified executables, symlinks, and group/world-writeable
executable files. It does not print secrets.

The 0600 policy ~/.config/savage-agent/vault-consumers.json is empty by
default: no runtime action is currently authorized. No token is stored or
created. Machine-account read permissions, runtime injection, revocation,
OS-level containment, and credential recovery require separate live testing.
A model with unrestricted host shell access could bypass a broker, so this
is a fail-closed execution interface, NOT a complete secrets sandbox.

Only a trusted OS credential broker or user-approved secure setup may supply
BWS_ACCESS_TOKEN. Do not paste the token into ChatGPT, files or logs.
No credential migration, rotation, or project mapping mutation was performed.

Synthetic tests: python3 -m unittest discover -s tests -p test_vault_broker.py -v
