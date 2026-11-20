---
name: seed-fault
description: Break, record, restore. Seed the one fault named in the argument into src/, show the tests catch it, append the real output to docs/SEEDED_FAULTS.md, then restore the file.
argument-hint: <fault, e.g. "remove .shift(1) from cnt_roll_7">
allowed-tools: Bash(python -m pytest:*), Bash(git diff:*), Bash(git status), Bash(git checkout:*)
---
Seed this fault: $ARGUMENTS

1. Run `git status`. Stop if src/ or tests/ has uncommitted changes.
2. Break: make the smallest edit in src/ that introduces the fault. Never touch tests/ or data/raw/bike_daily.csv.
3. Record: run `git diff` and `python -m pytest tests/test_leakage.py -q`. Append a section to docs/SEEDED_FAULTS.md with the fault description, the diff, the pytest output pasted verbatim, and any hook stderr. Paste real output, not a description of it.
4. Restore: undo only the edit from step 2 with `git checkout -- <the file you edited>`, then confirm `python -m pytest tests/ -q` passes. Never restore docs/.
