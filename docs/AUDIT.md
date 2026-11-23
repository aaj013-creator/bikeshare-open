# Exercise 3 audit

## Peer repository

Repository: [K-Pat/Activation-Monitoring-D33](https://github.com/K-Pat/Activation-Monitoring-D33)

Commit reviewed: `main` at `248a303` (2026-11-22).

The assignment's `/leakage-auditor` could not be run here: its configured `bikeshare-coder` model requires a local Ollama service, which was unavailable. The following is Codex's manual code-review output, not output from that subagent:

> No inspected issue changes a reported result. `probe/common.py:29-40` holds out one complete task at a time and fits scaling inside each training fold, so the reported held-out-task scores do not share test-task rows with training. `probe/extract.py:124-129` selects row 0, the final prompt-token activation, before generation; therefore the 100% first-turn result demonstrates that the probe distinguishes the honest and attack prompt conditions before behavior occurs. The README already identifies this prompt confound and does not present the probe as a validated behavior detector. The repository is a different study from the bikeshare exercise, so chronological forecasting checks do not apply. A simple majority-class accuracy baseline is absent; this is an interpretation/comparison gap, not evidence that the reported held-out predictions or AUROC values are numerically wrong.

Human verdict: I agree that prompt differences undermine a behavioral-detection interpretation, but they do not invalidate the reported condition-classification scores. The repo discloses that limitation. Its data contain 684 honest and 547 attack turns, so a pooled majority-class baseline would be 684/1231 = 55.6% accuracy; adding this comparison would help contextualize 88% layer-47 pooled accuracy but would not change that measured accuracy or AUROC. I found no issue in the inspected code that warrants changing an existing reported number.

## Own-repository audit

On 2026-11-19, from the local `person-c-analysis` checkout:

```sh
.venv/bin/python agent/audit.py . --out reports/audit.jsonl
```

The SDK attempt did not complete. Its diagnostic output was:

```text
Ignoring 5 permissions.allow entries from .claude/settings.json: this workspace has not been trusted. Run Claude Code interactively here once and accept the trust dialog, or set projects["/Users/bala/bikeshare-open"].hasTrustDialogAccepted: true in /Users/bala/.claude.json.
[claude-code:unrecognized_model] {"model":"bikeshare-coder","query_source":"sdk"}
```

No Ollama executable was found on PATH and `http://localhost:11434/api/tags` refused the connection. No `reports/audit.jsonl` was fabricated. A successful own-repository SDK audit remains outstanding; run the command on the group's configured Ollama machine after `make check-model` succeeds, inspect the findings, and commit the real output.
