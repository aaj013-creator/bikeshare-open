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
