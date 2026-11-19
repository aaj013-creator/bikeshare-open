# Seeded faults and failing runs

## Feature test written first: cnt_roll_3 (before the feature existed)

Command: python -m pytest tests/test_leakage.py -q

```
.venv/lib/python3.15/site-packages/pandas/core/indexes/base.py:3648: KeyError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_cnt_roll_3_on_named_date - KeyError: 'cnt_...
1 failed, 7 passed in 0.79s
```

## Unclassified-column test: new column appended to the raw CSV

Appended a numeric column new_col to data/raw/bike_daily.csv, ran python -m pytest tests/test_contract.py -q, then restored the file with git checkout. First version of the test passed (it counted feature_columns() as classified, so the new numeric column classified itself); fixed by listing DIRECT_COLS by hand. Output after the fix:

```
tests/test_contract.py:69: AssertionError
=========================== short test summary info ============================
FAILED tests/test_contract.py::test_every_raw_column_is_classified - Assertio...
1 failed, 4 passed in 1.14s
```

## Seeded faults (Exercise 2)

### Fault 1: Target leakage / unshifted lag violation
- **Fault seeded:** Exposing target components (`casual`, `registered`) or a feature that lacks `.shift(1)` / uses future rows.
- **Observed behavior / check:** Caught by leakage checks and `python3 -m pytest tests/test_leakage.py -q`.
- **Cleanup / restoration:** Revert temporary edits (`git checkout -- src/ tests/`) and re-run `python3 -m pytest tests/ -q`.

### Fault 2: Temporal / split boundary violation
- **Fault seeded:** Altering chronological ordering or train/validation/test split boundaries (`2011`, `H1 2012`, `H2 2012`).
- **Observed behavior / check:** Fails temporal split tests (`python3 -m pytest tests/test_split.py -q`).
- **Cleanup / restoration:** Restore modified files (`git checkout -- src/ tests/`) and re-run `python3 -m pytest tests/ -q`.

### Fault 3: Ingest / schema contract violation
- **Fault seeded:** Breaking required raw columns or minimum row count checks in `src/ingest.py`.
- **Observed behavior / check:** `python3 -m src.ingest` raises `ValueError` for missing required columns or row count below `EXPECTED_MIN_ROWS`.
- **Cleanup / restoration:** Restore `src/ingest.py` and `data/raw/bike_daily.csv` (`git checkout -- src/ingest.py data/raw/`).

### Fault 4: `cp` into `data/raw` and SHA-256 hash check
- **Fault seeded:** Copying a file into `data/raw/` (e.g., `cp data/raw/bike_daily.csv data/raw/bike_daily_copy.csv`) or modifying `data/raw/bike_daily.csv`.
- **Hash check verification:**
  - Baseline recorded via `shasum -a 256 data/raw/* > /tmp/bikeshare_raw_hashes.sha256` (`a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc  data/raw/bike_daily.csv`).
  - Running `shasum -a 256 -c /tmp/bikeshare_raw_hashes.sha256` detects content changes in `bike_daily.csv`, and checking `data/raw/` directory contents (`ls -la data/raw` or Python `Path("data/raw")` check) detects extra files copied into `data/raw/`.
- **Cleanup / restoration:** Remove extra files in `data/raw/`, run `git checkout -- data/raw/`, and re-verify `shasum -a 256 -c /tmp/bikeshare_raw_hashes.sha256`.
