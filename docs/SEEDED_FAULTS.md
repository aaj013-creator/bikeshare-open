# Seeded faults and failing runs

## Feature test written first: cnt_roll_3 (before the feature existed)

Command: python -m pytest tests/test_leakage.py -q

```
.venv/lib/python3.15/site-packages/pandas/core/indexes/base.py:3648: KeyError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_cnt_roll_3_on_named_date - KeyError: 'cnt_...
1 failed, 7 passed in 0.79s
```
