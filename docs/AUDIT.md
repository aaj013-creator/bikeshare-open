# Exercise 3 audit status

## Peer audit: awaiting repository

The assignment asks for `/leakage-auditor` against a teammate's repository, but does not name an assigned partner. Obtain another classmate/group's assignment repository URL. No peer repository was supplied, so no peer audit or verdict is claimed here. Replace this status with the URL, audited commit, verbatim auditor output and a one-paragraph human verdict identifying findings that change numbers.

## Own-repository SDK attempt

On 2026-11-19, from the local `person-c-analysis` checkout:

```sh
.venv/bin/python agent/audit.py . --out reports/audit.jsonl
```

The attempt did not return a completed result and was interrupted. Its diagnostic output was:

```text
Ignoring 5 permissions.allow entries from .claude/settings.json: this workspace has not been trusted. Run Claude Code interactively here once and accept the trust dialog, or set projects["/Users/bala/bikeshare-open"].hasTrustDialogAccepted: true in /Users/bala/.claude.json.
[claude-code:unrecognized_model] {"model":"bikeshare-coder","query_source":"sdk"}
```

No Ollama executable was found on PATH and `http://localhost:11434/api/tags` refused the connection. No `reports/audit.jsonl` was fabricated. Run the command on the group's configured Ollama machine after `make check-model` succeeds, inspect the real findings, then commit the output. This document is an incomplete-status record, not the required completed audit deliverable.
