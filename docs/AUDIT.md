# Exercise 3 audit

## Person C branch: `person-c-analysis`

Branch reviewed against `origin/main` (`b8eebc5`); branch commit reviewed: `a6026ab` (2026-11-22). This is a preliminary Codex self-review of the branch diff, not the required review by a different team member and not output from `/leakage-auditor`.

> No finding from the five required checks changes a number or invalidates a conclusion in the inspected diff. `src/target_experiment.py` forms the training target as `cnt - cnt_lag_1`, where the lag is built from the prior calendar day; it fits on the 2011 training partition and evaluates later date partitions. Calendar reindexing and lag warmup/drop behavior are inherited from `src/features.py`, which explicitly inserts missing dates before shifting and is covered by the existing row-count contract. The experiment reports both mean and persistence baselines beside each model. The main limitation is stated in `REPORT.md`: same-day measured weather is inherited from the starter features, so these scores describe a daily-updating setup with weather available, not a forecast made before that day's weather is known.

This does **not** fulfill the assignment's requirement that another team member run `/leakage-auditor` on this branch before merge. A teammate must run the configured auditor against `person-c-analysis`, inspect its output, and append their own section and verdict here. Keep this preliminary review labeled separately; do not represent it as the teammate audit or synthesize `reports/audit.jsonl`.

## Previous SDK attempt

On 2026-11-19, from the local checkout, Codex attempted:

```sh
.venv/bin/python agent/audit.py . --out reports/audit.jsonl
```

The SDK attempt did not complete. Its diagnostic output was:

```text
Ignoring 5 permissions.allow entries from .claude/settings.json: this workspace has not been trusted. Run Claude Code interactively here once and accept the trust dialog, or set projects["/Users/bala/bikeshare-open"].hasTrustDialogAccepted: true in /Users/bala/.claude.json.
[claude-code:unrecognized_model] {"model":"bikeshare-coder","query_source":"sdk"}
```

No Ollama executable was found on PATH and `http://localhost:11434/api/tags` refused the connection. No `reports/audit.jsonl` was fabricated. The successful configured-model run and teammate review remain outstanding.
