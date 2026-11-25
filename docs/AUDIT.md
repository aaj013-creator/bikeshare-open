# Exercise 3: audits

Each member audits another member's branch in a fresh Claude Code session that did not produce it. One section per audit.

## Audit 1: Person A audits branch `ex2-faults` (Person B, Exercise 2)

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

### Verdict (Person A)

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

## Person C branch: `person-c-analysis` — independent review

Range reviewed: `adf1f92..a11b0c7` (Person C's target-transform experiment, report, result files, and audit/decision updates). A fresh `leakage-auditor` session was started against this branch, but the local Ollama request hit its five-minute timeout twice before returning a review. The findings below are a separate manual review; they are not represented as generated auditor output.

- **Target leakage:** `src/target_experiment.py` trains the delta model on `train[TARGET] - train['cnt_lag_1']`, then adds the validation/test row's prior-day lag back. The lag feature is shifted on the calendar-aligned feature frame, so the forecast does not use the target day's count.
- **Temporal ordering:** all models are cloned and fitted on the 2011 training partition; validation and test remain date-based partitions. The test option only changes which held-out partition is scored.
- **Calendar gaps / row loss:** the branch does not change feature generation or row filtering. Those behaviors remain covered by the inherited calendar and row-count contract.
- **Baselines:** each output includes the mean and persistence baselines alongside ridge, raw HGB, and delta HGB.
- **Conclusion:** no leakage issue found that invalidates the experiment's conclusion. The report correctly says same-day measured weather is inherited and limits the recommendation to a daily-updating setup.

Validation: `python -m pytest tests/ -q` in the review environment passed 18 tests. That environment had scikit-learn 1.2.2 and pandas 2.1.4, while `requirements.txt` pins scikit-learn 1.9.1 and pandas 3.0.5. Re-running the experiment here therefore produced different HGB scores; this is version drift, not evidence that the committed JSON files are reproducible in this environment. Re-run under the pinned requirements before relying on an exact reproduction. No `reports/audit.jsonl` is claimed.
