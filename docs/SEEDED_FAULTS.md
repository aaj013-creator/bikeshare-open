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
