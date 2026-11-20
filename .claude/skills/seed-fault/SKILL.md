---
name: seed-fault
description: Seed and verify controlled faults, run repository checks including the raw data hash check, record real outputs in docs/SEEDED_FAULTS.md, and restore clean state.
---

# Seed Fault Workflow

1. Confirm a clean working tree and verify `python3 -m pytest tests/test_raw_hash.py -q`.
2. Apply one controlled fault at a time (`casual` in `feature_columns`, removing `.shift(1)` on `cnt_roll_7`, removing `raise` in `encode_weather`, or testing a `cp` into `data/raw` guard).
3. Run `python3 -m pytest tests/ -q` and record real output and fix details in `docs/SEEDED_FAULTS.md`.
4. Restore all tracked files and remove any stray files in `data/raw/`, then re-run `python3 -m pytest tests/ -q`.
