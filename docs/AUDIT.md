# Exercise 3: audits

Each member audits another member's branch in a fresh Claude Code session that did not produce it. One section per audit.

## Audit 1: Aarushi Jain audits branch `ex2-faults` (Sana Gupta, Exercise 2)

Range audited: `git diff 1e38653..ex2-faults` (9 files: seed-fault skill, .gitignore, CLAUDE.md, Makefile, DECISIONS.md, SEEDED_FAULTS.md, src/features.py, tests/test_leakage.py, tests/test_raw_hash.py).

Model: qwen3.5:9b via local Ollama (`bikeshare-coder`, 64k context), fresh session, 2026-11-24.

How it ran. The first attempt (`@agent-leakage-auditor ...`) was answered by the main session itself: the export shows no subagent call, only one shell command. A second attempt asked for the Agent tool with `subagent_type "leakage-auditor"`. Its first call failed with "Invalid tool parameters", the retry launched the `leakage-auditor` subagent, but after about 20 minutes its token count stopped at 4.8k and `ollama ps` showed the model "Stopping...", so I stopped it. The output below is the first run, unedited.

### Auditor output (verbatim)

```text
❯ @agent-leakage-auditor audit branch ex2-faults. Its changes are in git diff
  1e38653..ex2-faults. Do not edit any files. Report your findings exactly as
  you would to a reviewer.

  Thought for 3m 53s, ran 1 shell command (ctrl+o to expand)

⏺ Audit of branch ex2-faults (1e38653 → HEAD)

  This branch implements Exercise 2: fault seeding — three seeded faults in
  src/, plus a fourth "anti-cheat" guard for data/raw/. Here is my verdict.

  ---

  ✅ Correctness & Compliance

  Rule: Never write to data/raw/
  Status: ✅ Compliant
  Evidence: The only edit to data/raw/ is a read-only test (test_raw_hash.py).
    No cp, mv, or > into the directory.
  ────────────────────────────────────────
  Rule: Temporal split only (no random)
  Status: ✅ Compliant
  Evidence: No changes in src/train.py; the branch doesn't touch feature
    engineering beyond what already exists. Existing code uses temporal_split
    per CLAUDE.md.
  ────────────────────────────────────────
  Rule: No forbidden columns in model
  Status: ✅ Demonstrated via tests
  Evidence: Tests added (test_no_forbidden_features) catch if a forbidden
    column slips through feature_columns().
  ────────────────────────────────────────
  Rule: Lag/rolling features built on gap-free calendar + shifted
  Status: ✅ Guarded by tests
  Evidence: test_rolling_mean_excludes_today ensures .shift(1) is present
    before rolling.
  ────────────────────────────────────────
  Rule: No new dependencies
  Status: ✅ Compliant
  Evidence: Only stdlib, pandas, scikit-learn, pytest.

  ---

  ✅ Leakage Guards (the core of Ex2)

  The branch adds three seeded faults, each with a dedicated test and a fix
  commit:

  Fault: 1. casual allowed through feature_columns()
  What was broken: Changed or c not in FORBIDDEN to or c not in FORBIDDEN or c
    == "casual"
  Test that catches it: test_no_forbidden_features asserts cols & FORBIDDEN ==
    ∅
  Fix commit: cec4b52 (restores original filter)
  ────────────────────────────────────────
  Fault: 2. .shift(1) removed from cnt_roll_7
  What was broken: Rolling mean included today → target leakage
  Test that catches it: test_rolling_mean_excludes_today computes expected
    value from prior 7 days and asserts equality
  Fix commit: 58a066e (restores .shift(1))
  ────────────────────────────────────────
  Fault: 3. raise removed from encode_weather()
  What was broken: Unknown weather labels (e.g., "SNOW") would silently become
    NaN
  Test that catches it: test_encode_weather_rejects_unknown_label asserts
    ValueError on ["GOOD", "SNOW"]
  Fix commit: fef9461 (restores raise ValueError)
  ────────────────────────────────────────
  Fault: 4. Unauthorized file in data/raw/
  What was broken: cp ... data/raw/stray.csv would slip past a name-only hash
    check
  Test that catches it: test_raw_hash.py checks both SHA-256 and that the
    directory contains exactly EXPECTED_RAW_HASHES.keys()
  Fix commit: N/A (new guard, no "fix" commit)

  ---

  ✅ Test Coverage & Hook Integration

  Aspect: Leakage test lives in tests/test_leakage.py
  Status: ✅ All four tests are there.
  ────────────────────────────────────────
  Aspect: Hook only runs test_leakage.py
  Status: ✅ .claude/hooks/check_leakage.sh runs pytest tests/test_leakage.py.
    This is why the new weather test had to live in that file, not a separate
    one.
  ────────────────────────────────────────
  Aspect: Full test suite passes after fixes
  Status: ✅ Commit log shows final hash fef9461 with message Fix fault 3:
    restore raise from encode_weather (test goes red), implying full suite
    green afterwards. The docs/SEEDED_FAULTS.md confirms "python -m pytest
    tests/ -q gives 18 passed".
  ────────────────────────────────────────
  Aspect: Raw hash test wired into pipeline
  Status: ✅ Makefile now runs python -m pytest tests/test_raw_hash.py -q as
    part of make data.

  ---

  ✅ Documentation & Decision History

  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │         Item          │                     Status                      │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Decisions recorded in │ ✅ Four new entries (2026-11-19) explain:       │
  │  docs/DECISIONS.md    │                                                 │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ — Test for unknown    │ Weather encoding guard added to leakage tests.  │
  │ weather label         │                                                 │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ — Three faults seeded │ Each fault/fix pair is a commit; no agent hook  │
  │  by hand              │ counted.                                        │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ — Fourth fault (cp    │ SHA-256 extended to check all entries in the    │
  │ into data/raw/)       │ directory.                                      │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ — Rationale for test  │ Hook only runs test_leakage.py, so new leakage  │
  │ location              │ tests live there.                               │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ .gitignore updated    │ ✅ Added .ipynb_checkpoints/ (from commit       │
  │                       │ c84c0bf).                                       │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │                       │ ✅ Two bullets under "Raw data and fault        │
  │ CLAUDE.md extended    │ seeding" explain the read-only rule and         │
  │                       │ /seed-fault <desc> workflow.                    │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Seed-fault skill      │ ✅ .claude/skills/seed-fault/SKILL.md exists    │
  │ added                 │ and matches the documented workflow.            │
  └───────────────────────┴─────────────────────────────────────────────────┘

  ---

  ⚠️ Minor Observations (not blocking)

  1. Empty line removal in src/features.py:
     One commit (d8cc103 → 3cf658b) removes a blank line before
     encode_weather(). This is stylistic, not functional, and doesn't affect
     leakage semantics.
  2. Agent vs. manual fault seeding:
     All three faults were seeded manually (via sed in a terminal), not through
     the agent's Bash tool. That's fine for Ex2, but it means no "agent turn"
     count is recorded — the decision is documented in docs/SEEDED_FAULTS.md.

  ---

  🔍 Summary

  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │       Criterion       │                     Verdict                     │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Leakage tests present │ ✅ Yes                                          │
  │  and correct?         │                                                 │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Temporal split        │ ✅ Yes (unchanged)                              │
  │ respected?            │                                                 │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Forbidden columns     │ ✅ Yes (test_no_forbidden_features)             │
  │ guarded?              │                                                 │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Lag/rolling features  │ ✅ Yes (test_rolling_mean_excludes_today)       │
  │ correctly shifted?    │                                                 │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Unknown weather       │ ✅ Yes                                          │
  │ labels rejected?      │ (test_encode_weather_rejects_unknown_label)     │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Raw data integrity    │ ✅ Yes (test_raw_hash.py run via make data)     │
  │ checked in pipeline?  │                                                 │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Documentation         │ ✅ Yes (DECISIONS.md, CLAUDE.md,                │
  │ complete?             │ SEEDED_FAULTS.md, skill)                        │
  └───────────────────────┴─────────────────────────────────────────────────┘

  No violations found. The branch cleanly implements the Exercise 2
  requirements: three seeded faults with tests and fixes, plus a fourth
  anti-cheat guard for raw data integrity. All changes are documented, all tests
  pass after fixes, and no forbidden columns or leakage patterns reach the
  model.

✻ Brewed for 8m 43s · done 8:01 PM```

### Verdict (Aarushi Jain)

No finding changes a number, and I agree with the overall verdict: the three faults are the required ones, each has a fault commit and a fix commit, and the branch leaves no functional change in `src/`. What I ran to check: `git diff 1e38653..ex2-faults -- src/features.py` shows one deleted blank line and nothing else; `git diff --stat 1e38653..ex2-faults` lists no file under `data/raw/`, and `shasum -a 256 data/raw/bike_daily.csv` still begins `a6bed1577f6e4de5`; `make test` on main after the merge gives 18 passed.

Where I disagree with the auditor:
- "One commit (d8cc103 -> 3cf658b)": these are blob ids from the diff's `index` line, not commits (`git cat-file -t` returns `blob`). The change itself (one blank line) is real and harmless.
- "Tests added (test_no_forbidden_features)": that test is from the starter. This branch added `test_encode_weather_rejects_unknown_label` and `tests/test_raw_hash.py`.
- "All four tests are there" (in test_leakage.py): the raw-data test is in `tests/test_raw_hash.py`, run by `make data` and `make test`, not by the PostToolUse hook.
- "Full test suite passes after fixes": the auditor inferred this from commit messages and SEEDED_FAULTS.md instead of running pytest, against its own instruction to verify by running. I ran it (18 passed).

Agreed, and worth keeping: faults were seeded by hand, so no agent turn counts exist (B records this in SEEDED_FAULTS.md and DECISIONS.md).

Missed by the auditor (no number changes): `test_rolling_mean_excludes_today` wraps its assert in `if all(...)`, so it would pass silently if a day in its window were missing. On this data the window for row 200 is complete, which is why Fault 2 went red. It is a starter test outside this branch.

## Audit 2: configured `leakage-auditor` on `a-feature`

Range audited: `c2ca066..1e38653` (`origin/a-feature`; the branch tip is already an ancestor of `main`, so `main..a-feature` is empty). Fresh Claude Code session using the repository's `leakage-auditor` agent and local Qwen3.5:9b via Ollama (`bikeshare-coder`, 65,536-token context), 2026-11-25.

### Auditor output (verbatim)

```text
All tests pass. Let me now verify each check against the diff and report findings:

## Audit Results

### Check 1: Target Leakage
**PASS.** The new feature `cnt_roll_3` (line 77 of features.py) is:
- `out["cnt_roll_3"] = out[TARGET].shift(1).rolling(3).mean()`
- Uses `.shift(1)` before rolling, excluding today's value
- Properly tested in `tests/test_leakage.py::test_cnt_roll_3_on_named_date` which verifies it equals `(4460 + 5020 + 4891) / 3 = 4790.33` for 2011-06-15
- Added to `REJECTED_COLS` in config.py because it "hurt validation" (not leakage)

### Check 2: Temporal Ordering
**PASS.** All lags use `.shift(1)` before aggregation, split uses date boundaries, and models fit only on train data.

### Check 3: Calendar Gaps
**PASS.** `reindex_to_calendar()` (lines 34-50) creates a gap-free calendar using `pd.date_range(..., freq="D")` before shifting, correctly handling the missing 2011-03-10 row.

### Check 4: Silent Row Loss
**PASS.** The `.dropna()` on line 79 is bounded by `test_only_expected_rows_are_dropped` which validates against `LAG_WARMUP = 7`.

### Check 5: Unreported Baseline
**PASS.** Both baselines are reported next to every model:
- `DummyRegressor(strategy="mean")` provides mean baseline (R² -0.9318, -2.1441)
- `PersistenceBaseline("cnt_lag_1")` provides persistence baseline (R² 0.4507, 0.5099)

All five checks pass.
```

### Verdict and verification

The agent's five checks pass. Independently ran `python -m pytest tests/ -q` in the `a-feature` worktree: 16 passed.

## Akshitaa Balasai branch: `person-c-analysis` — independent review

Range reviewed: `adf1f92..a11b0c7` (Akshitaa Balasai's target-transform experiment, report, result files, and audit/decision updates). A fresh `leakage-auditor` session was started against this branch, but the local Ollama request hit its five-minute timeout twice before returning a review. The findings below are a separate manual review; they are not represented as generated auditor output.

- **Target leakage:** `src/target_experiment.py` trains the delta model on `train[TARGET] - train['cnt_lag_1']`, then adds the validation/test row's prior-day lag back. The lag feature is shifted on the calendar-aligned feature frame, so the forecast does not use the target day's count.
- **Temporal ordering:** all models are cloned and fitted on the 2011 training partition; validation and test remain date-based partitions. The test option only changes which held-out partition is scored.
- **Calendar gaps / row loss:** the branch does not change feature generation or row filtering. Those behaviors remain covered by the inherited calendar and row-count contract.
- **Baselines:** each output includes the mean and persistence baselines alongside ridge, raw HGB, and delta HGB.
- **Conclusion:** no leakage issue found that invalidates the experiment's conclusion. The report correctly says same-day measured weather is inherited and limits the recommendation to a daily-updating setup.

Validation: `python -m pytest tests/ -q` in the review environment passed 18 tests. That environment had scikit-learn 1.2.2 and pandas 2.1.4, while `requirements.txt` pins scikit-learn 1.9.1 and pandas 3.0.5. Re-running the experiment here therefore produced different HGB scores; re-run under the pinned requirements before relying on exact reproduction.

The `a-feature` row in `reports/audit.jsonl` is a structured summary of the completed interactive auditor output and independent checks. It is not the `agent/audit.py` batch SDK's output: the batch run did not return a structured result before it was stopped.

## Audit 3: Sana Gupta audits `person-c-analysis`

This audit was done after the branch had already been merged (merge commit `8566185` on `main`). Range audited: `git diff 8566185^1 8566185`, which is what Person C's branch added to `main` (6 files: `REPORT.md`, `docs/AUDIT.md`, `docs/DECISIONS.md`, `reports/target_experiment.json`, `reports/target_validation.json`, `src/target_experiment.py`). The agent was pointed only at the one code file, `src/target_experiment.py`; it did not review the report, the JSON files or the docs.

Model: qwen3.5:9b via local Ollama (`bikeshare-coder`, 65,536-token context), fresh Claude Code session, 2026-11-25.

### How it ran

- First attempt: `@agent-leakage-auditor audit branch person-c-analysis ...` for the whole diff. The main session thought for 4m 10s and launched the subagent, then Claude Code stopped at a permission prompt (auto mode cannot run its safety check through `localhost:11434`). I denied one prompt by mistake and told the agent to retry. After 15m 8s the session showed 515 tokens and no review, so I interrupted it. No output from this run is used below.
- Second attempt: restarted with `API_TIMEOUT_MS=1800000` and a narrower prompt (only `src/target_experiment.py`, five checks, one short paragraph each). The main session wrote its own summary after about 10 minutes, and the background subagent finished after 23m 51s (32m 12s for the whole session). The output below is this second run, unedited (exported with `/export`).
- Both the main session's summary and the subagent's report are in the transcript. The subagent was reported as `general-purpose`, not as a separate `leakage-auditor` entry. The checks it ran are not the five used in Audit 2 (target leakage, temporal ordering, calendar gaps, silent row loss, unreported baseline), and the main session's "Check 5: Fault seeding awareness" is not a leakage check.

### Auditor output (verbatim)

```text
▗ ▗   ▖ ▖  Claude Code v2.1.332
           bikeshare-coder · API Usage Billing
 ▘▘   ▝▝   ~/bikeshare-open

▎ Using bikeshare-coder (from .claude/settings.json) · /model

❯ @agent-leakage-auditor audit src/target_experiment.py only, from branch
  person-c-analysis (git diff 8566185^1 8566185 -- src/target_experiment.py).
  Go through your five checks one at a time, one short paragraph each. Do not
  edit any files.

  Thought for 2m 33s (ctrl+o to expand)

⏺ Agent(Audit target_experiment.py diff)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Auto mode can't check actions in this session. Its safety check runs
  on the server, and your requests go through localhost:11434, which
  doesn't pass it through. Actions that need the check now ask for your
  approval. To work without these prompts, switch permission mode with
  Shift+Tab. To use auto mode, ask whoever runs localhost:11434 to pass
  Claude Code's server-side safety check through: https://code.claude.co
  m/docs/en/permission-modes#server-side-classifier-review

  Thought for 2m 37s (ctrl+o to expand)

⏺ I've launched the leakage auditor agent to review the diff. You'll be notified
  when it completes. In the meantime, let me read the file directly to give you
  immediate context:

  Thought for 4m 19s, ran 1 shell command (ctrl+o to expand)

⏺ Audit Summary: src/target_experiment.py

  Check 1: Temporal split compliance — Uses temporal_split(df) from src.train,
  which respects the train=2011, valid=H1 2012, test=H2 2012 rule. No random
  splitting detected.

  Check 2: Leakage via lag features — The code fits models on cnt_lag_1 in
  training only, then predicts residual demand (today minus yesterday). This is
  valid incremental prediction, not leakage. However, the test set includes
  cnt_lag_1, which requires proper computation there too (not leaking future
  values).

  Check 3: Baseline reporting — Reports R² and MAE for all models including
  "hgb_delta" (persistence baseline), but missing the mean baseline (long-term
  average) alongside the persistence baseline as required.

  Check 4: Forbidden columns — No explicit exclusion of casual or registered;
  relies on feature_columns(). If those columns slip into features, it's a
  problem in the feature engineering module, not here.

  Check 5: Fault seeding awareness — Does not hardcode dates except through
  load_raw()/temporal_split(). No Sandy (2012-10-29) special-casing or
  assumptions baked in directly.

  The agent will complete its detailed audit shortly.

✻ Brewed for 10m 12s · done 7:22 PM

› Message from general-purpose
  Note: bikeshare-coder (the safety classifier) was unavailable (timed out) when
  reviewing this subagent's work. Please carefully verify the subagent's
  actions and output before acting on them.

    Audit of src/target_experiment.py (git diff 8566185^1 8566185):

    Check 1: No forbidden columns leak into features — PASS. The script uses
  `feature_columns(df)` from `src/features.py`, which filters out all columns in
  `FORBIDDEN`. That set includes `LEAKAGE_COLS = {"casual", "registered",
  "cnt"}`, so the target itself and its components are excluded.

    Check 2: Temporal split is correct — PASS. The experiment calls
  `temporal_split(df)` from `src/train.py`, which implements the required split:
  train = 2011, valid = H1 2012, test = H2 2012 (using `TRAIN_END="2011-12-31"`
  and `VALID_END="2012-06-30"`). The `--test` flag correctly controls whether
  the test set is included in validation.

    Check 3: Lag features respect calendar indexing — PASS/Note. The residual
  model fits on `train[TARGET] - train['cnt_lag_1']`. The `cnt_lag_1` comes from
  `src/features.py`, which `.shift(1)` after `reindex_to_calendar()`,
  respecting the calendar index and shifting by days rather than rows. A
  dedicated leakage test exists in `tests/test_leakage.py` for this pattern, but
  I did not inspect it.

    Check 4: Baselines are reported alongside models — PASS. The experiment
  outputs both baselines: `baseline_mean` and `baseline_persistence`. The
  persistence baseline is correctly computed as yesterday's count via the
  `cnt_lag_1` feature. This matches the non-negotiable rule to report both
  baselines.

    Check 5: No new dependencies; runnable module with one-line summary — PASS.
  The file imports only standard library plus `pandas`, `sklearn` (already
  pinned in requirements), and local modules. Running `python -m
  src.target_experiment --out reports/experiment.json` prints a JSON-formatted
  result. This deviates from the project's `OK ...` pattern used by pipeline
  stages, but the script is an experiment/analysis tool rather than a stage that
  must conform.

    Summary: The file adheres to all five checks; no blocking issues found.

  Thought for 4m 19s (ctrl+o to expand)

⏺ The agent has completed its audit of src/target_experiment.py. Here are the
  findings:

  Audit Results: All Checks Pass ✓

  Check 1: No forbidden columns leak into features — The script uses
  feature_columns(df) from src/features.py, which filters out all FORBIDDEN
  columns including casual, registered, and cnt. PASS.

  Check 2: Temporal split is correct — Uses temporal_split(df) implementing the
  required train=2011, valid=H1 2012, test=H2 2012 split. The --test flag
  properly controls test set inclusion. PASS.

  Check 3: Lag features respect calendar indexing — The residual model fits on
  train[TARGET] - train['cnt_lag_1']. The cnt_lag_1 comes from src/features.py,
  which shifts after reindexing to calendar, respecting the index and shifting
  by days rather than rows. A leakage test exists in tests/test_leakage.py. PASS
  with note.

  Check 4: Baselines are reported alongside models — The experiment outputs both
  baselines: baseline_mean and baseline_persistence. The persistence baseline
  is computed via cnt_lag_1. MATCHES requirements. However, my initial read
  flagged this as missing the mean baseline — need to verify this is actually
  present in the output.

  Check 5: No new dependencies; runnable module — Only standard library + pandas
  + sklearn (already pinned) + local modules. Prints JSON-formatted results.
  Deviates from the project's OK ... pattern but acceptable for an experiment
  tool. PASS.

  ---

  One item to verify: Check 4 claimed both baselines are reported, but my
  initial read of the diff showed only R² and MAE metrics being computed. The
  subagent may have been reading a different version or there's a discrepancy.
  Would you like me to double-check the actual output format produced by this
  script?

✻ Baked for 32m 12s · done 7:43 PM

⏺ Agent "Audit target_experiment.py diff" finished · 23m 51s
```

### Which findings I agree with

I checked each claim against the code rather than the transcript.

- **Temporal split (agree).** `temporal_split` in `src/train.py` splits by date with `TRAIN_END = "2011-12-31"` and `VALID_END = "2012-06-30"` (`src/config.py` lines 54-55), so train is 2011, validation is H1 2012 and test is H2 2012. There is no random split. `src/target_experiment.py` calls `temporal_split` unchanged.
- **Lag leakage (agree).** `cnt_lag_1` is `out[TARGET].shift(1)` (`src/features.py` line 73). `reindex_to_calendar` is called at line 53, before any shift, so the lag is by calendar day and the missing 2011-03-10 row cannot misalign it. Validation and test rows get their lag from the same `build_features` frame. The residual model is fitted on `train[TARGET] - train['cnt_lag_1']` and `cnt_lag_1` is added back at prediction time, which uses only the previous day's observed count.
- **Forbidden columns (agree).** `FORBIDDEN` is the union of four sets (`src/config.py` line 51) and `LEAKAGE_COLS = {"casual", "registered", "cnt"}` (line 31), so the subagent's description is correct. `feature_columns` is the existing filter and the branch does not change it.
- **Baselines (agree with the subagent, disagree with the main session).** `MODELS` in `src/train.py` contains `baseline_mean` and `baseline_persistence`, and `experiment()` builds its results from `MODELS`. The committed validation JSON has both. The main session's Check 3 ("missing the mean baseline") is wrong, and it also labels `hgb_delta` as the persistence baseline, but `hgb_delta` is the residual HGB model. The main session's closing paragraph contradicts the subagent on this point and asks whether to re-check; my checks below settle it.
- **No new dependencies (agree).** The file imports only the standard library, scikit-learn and local modules.

### What I disagree with or could not confirm

- The subagent says that running `python -m src.target_experiment --out reports/experiment.json` prints JSON. The transcript shows only one shell command in the main session, so I do not treat this as a run the agent performed. I ran the module myself (below).
- The subagent's Check 3 says it did not inspect the leakage test in `tests/test_leakage.py`.
- Silent row loss and calendar gaps were not checked by the agent for this branch. By reading the code, `src/target_experiment.py` does not drop rows itself and does not change feature generation.
- The agent did not review `REPORT.md`, `reports/target_experiment.json` (the test numbers) or the docs.

### What I ran to check

All from a clean checkout of `main` in the pinned `.venv` (scikit-learn 1.9.1, pandas 3.0.5):

```text
grep -n "FORBIDDEN" src/config.py
grep -n "LEAKAGE_COLS\|TRAIN_END\|VALID_END\|REJECTED_COLS" src/config.py
grep -n "def temporal_split" -A 12 src/train.py
grep -n "MODELS\|baseline" src/train.py
grep -n "cnt_lag_1\|shift(1)" src/features.py
grep -n "reindex_to_calendar" src/features.py
python -m pytest tests/ -q                    # 18 passed
python -m src.target_experiment --out /tmp/valid_check.json
diff of /tmp/valid_check.json vs origin/person-c-analysis:reports/target_validation.json  # no differences
git status --short                            # clean (nothing written to the repo)
```

The validation output reproduced exactly: raw HGB R² 0.2185 / MAE 1296.6, residual HGB 0.6079 / 834.3, ridge 0.6475 / 832.9, persistence 0.4507 / 900.6, mean -0.9318 / 2002.2. I wrote the output to `/tmp` so no reports were overwritten, and I did not re-run `--test`.

### Verdict and comparison with Person C's manual review

I found no leakage in `src/target_experiment.py`. This agrees with the manual review Person C added under Audit 2. That review could not confirm the committed numbers because it ran on scikit-learn 1.2.2 and pandas 2.1.4; under the pinned requirements the validation JSON reproduces exactly. Limits of this audit: the auditor was a 9B local model whose summary contained one false finding (the missing mean baseline), only one file was in scope, and the test-split numbers in `reports/target_experiment.json` were not re-run.
