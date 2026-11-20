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


## Fault 1: Forbidden column (`casual`) included in `feature_columns`

Command: `python3 -m pytest tests/test_leakage.py -q`

```text
.F......                                                                                                                                [100%]
================================================================== FAILURES ===================================================================
_________________________________________________________ test_no_forbidden_features __________________________________________________________

feats =         dteday  instant  season      yr mnth holiday  ... month_cos  weather_severity  cnt_lag_1  cnt_lag_7   cnt_roll...  DEC       N  ...  1.000000               1.0     1796.0      920.0  1531.428571  2077.333333

[714 rows x 29 columns]

    def test_no_forbidden_features(feats):
        """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
        construction, so this cannot discover a *new* leaky column. What it
        catches is someone editing feature_columns() or FORBIDDEN -- which is
        exactly the fault the Step 7 hook demonstrates."""
        cols = set(feature_columns(feats))
>       assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E       AssertionError: forbidden columns in feature set: {'casual'}
E       assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_7', 'dayofweek', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'cnt_roll_3', 'days_since_2011', 'instant', ...})

tests/test_leakage.py:31: AssertionError
============================================================== warnings summary ===============================================================
../../../Library/Frameworks/Python.framework/Versions/3.14/lib/python3.14/site-packages/anyio/pytest_plugin.py:14
  /Library/Frameworks/Python.framework/Versions/3.14/lib/python3.14/site-packages/anyio/pytest_plugin.py:14: PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.
  The CallSpec2 alias will be removed in pytest 10.
  Update imports to use CallSpec instead.
  See [https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed](https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed)
    from _pytest.python import CallSpec2

-- Docs: [https://docs.pytest.org/en/stable/how-to/capture-warnings.html](https://docs.pytest.org/en/stable/how-to/capture-warnings.html)
=========================================================== short test summary info ===========================================================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: forbidden columns in feature set: {'casual'}
1 failed, 7 passed, 1 warning in 0.71s


## Fault 2: Removed `.shift(1)` from `cnt_roll_7`

Command: `python3 -m pytest tests/test_leakage.py -q`

```text
....F...                                                                                                                                [100%]
================================================================== FAILURES ===================================================================
______________________________________________________ test_rolling_mean_excludes_today _______________________________________________________

feats =         dteday  instant  season      yr mnth holiday  ... month_cos  weather_severity  cnt_lag_1  cnt_lag_7   cnt_roll...  DEC       N  ...  1.000000               1.0     1796.0      920.0  1789.857143  2077.333333

[714 rows x 29 columns]

    def test_rolling_mean_excludes_today(feats):
        """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
        by_date = feats.set_index("dteday")[TARGET]
        date = feats.dteday.iloc[200]
        window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
        if all(d in by_date.index for d in window):
            expected = sum(by_date[d] for d in window) / 7
>           assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E           assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
E             
E             comparison failed
E             Obtained: 4389.0
E             Expected: 4414.857142857143 ± 0.00441486

tests/test_leakage.py:57: AssertionError
============================================================== warnings summary ===============================================================
../../../Library/Frameworks/Python.framework/Versions/3.14/lib/python3.14/site-packages/anyio/pytest_plugin.py:14
  /Library/Frameworks/Python.framework/Versions/3.14/lib/python3.14/site-packages/anyio/pytest_plugin.py:14: PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.
  The CallSpec2 alias will be removed in pytest 10.
  Update imports to use CallSpec instead.
  See [https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed](https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed)
    from _pytest.python import CallSpec2

-- Docs: [https://docs.pytest.org/en/stable/how-to/capture-warnings.html](https://docs.pytest.org/en/stable/how-to/capture-warnings.html)
=========================================================== short test summary info ===========================================================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
1 failed, 7 passed, 1 warning in 0.71s

## Fault 3: Removed `raise` from `encode_weather`

Command: `python3 -c 'import pandas as pd; from src.features import encode_weather; s = pd.Series(["GOOD", "SNOW"]); print(encode_weather(s).tolist())'`

```text
[0.0, nan]