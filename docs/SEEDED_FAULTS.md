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

# Exercise 2: seeded faults

How these runs were done. Each fault was applied with a one-line `sed` edit to `src/features.py` in the project venv (pinned `requirements.txt`; `python -m pytest`), shown as a `git diff`. The fault and its fix are separate commits; the fix restores the file with `git checkout HEAD~1 -- src/features.py`, and the full suite is green again afterwards (18 passed).

The edits were made in a terminal, not through the agent, so the `PostToolUse` hook did not fire by itself and no agent turns were spent. The hook output below comes from running `.claude/hooks/check_leakage.sh` by hand with the payload the hook would receive:

```
printf '{"tool_input":{"file_path":"%s/src/features.py"}}' "$PWD" | CLAUDE_PROJECT_DIR="$PWD" bash .claude/hooks/check_leakage.sh; echo "exit=$?"
```

The script prints the last 20 lines of the pytest output to stderr, which is why the hook output starts part-way through the traceback. `exit=2` is the code that tells the agent to treat the failure as a system message.

**Agent turns to fix: not measured for any of the three faults** (manual edits, no agent run).

## Fault 1: forbidden column (`casual`) let through `feature_columns`

**Change** (commit `2a5c5fc`):

```diff
diff --git a/src/features.py b/src/features.py
index 3cf658b..2fe8b9d 100644
--- a/src/features.py
+++ b/src/features.py
@@ -81,7 +81,7 @@ def build_features(df: pd.DataFrame) -> pd.DataFrame:
 def feature_columns(df: pd.DataFrame) -> list[str]:
     """Numeric columns that are safe to feed the model."""
     numeric = df.select_dtypes(include="number").columns
-    return [c for c in numeric if c not in FORBIDDEN]
+    return [c for c in numeric if c not in FORBIDDEN or c == "casual"]


 if __name__ == "__main__":
```

**Red test:** `python -m pytest tests/test_leakage.py -q`

```text
.F.......                                                                                                                                      [100%]
====================================================================== FAILURES ======================================================================
_____________________________________________________________ test_no_forbidden_features _____________________________________________________________

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
============================================================== short test summary info ===============================================================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: forbidden columns in feature set: {'casual'}
1 failed, 8 passed in 0.75s
```

**Hook stderr** (manual run):

```text
Leakage tests failed after editing /Users/sana/bikeshare-open/src/features.py:
feats =         dteday  instant  season  ...  cnt_lag_7   cnt_roll_7   cnt_roll_3
0   2011-01-10     10.0  WINTER  ...     134....142857  2183.333333
713 2012-12-31    731.0  WINTER  ...      920.0  1531.428571  2077.333333

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
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed, 8 passed in 0.45s
exit=2
```

**Turns to fix:** not measured (manual).

**Fix** (commit `cec4b52`): restored the filter; `python -m pytest tests/ -q` gives `18 passed`.

## Fault 2: removed `.shift(1)` from `cnt_roll_7`

**Change** (commit `6cfe5ea`):

```diff
diff --git a/src/features.py b/src/features.py
index 3cf658b..dc27443 100644
--- a/src/features.py
+++ b/src/features.py
@@ -72,7 +72,7 @@ def build_features(df: pd.DataFrame) -> pd.DataFrame:
     # If you add a longer lag, raise LAG_WARMUP in src/config.py.
     out["cnt_lag_1"] = out[TARGET].shift(1)
     out["cnt_lag_7"] = out[TARGET].shift(LAG_WARMUP)
-    out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()
+    out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()
     out["cnt_roll_3"] = out[TARGET].shift(1).rolling(3).mean()

     return out.dropna().reset_index(drop=True)
```

**Red test:** `python -m pytest tests/test_leakage.py -q`

```text
....F....                                                                                                                                      [100%]
====================================================================== FAILURES ======================================================================
__________________________________________________________ test_rolling_mean_excludes_today __________________________________________________________

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
============================================================== short test summary info ===============================================================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
1 failed, 8 passed in 0.71s
```

**Hook stderr** (manual run):

```text
Leakage tests failed after editing /Users/sana/bikeshare-open/src/features.py:
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
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 8 passed in 0.44s
exit=2
```

**Turns to fix:** not measured (manual).

**Fix** (commit `58a066e`): restored `.shift(1)`; `python -m pytest tests/ -q` gives `18 passed`.

## Fault 3: removed the `raise` from `encode_weather`

Before this exercise nothing in the suite fed `encode_weather` an unseen label, so this fault would have gone unnoticed. The only evidence of the silent failure was running the function directly (this run was made earlier, with the system Python rather than the venv):

```
$ python3 -c 'import pandas as pd; from src.features import encode_weather; s = pd.Series(["GOOD", "SNOW"]); print(encode_weather(s).tolist())'
[0.0, nan]
```

So `test_encode_weather_rejects_unknown_label` was added to `tests/test_leakage.py` (commit `c84c0bf`). It lives in that file because the hook only runs `tests/test_leakage.py`. Deleting only the `raise` line would leave `if unknown:` with an empty body (a syntax error, not the intended fault), so the fault replaces the `raise` with `pass`.

**Change** (commit `c841e72`):

```diff
diff --git a/src/features.py b/src/features.py
index 3cf658b..a9ceae3 100644
--- a/src/features.py
+++ b/src/features.py
@@ -26,7 +26,7 @@ def encode_weather(series: pd.Series) -> pd.Series:
     known = series.dropna()
     unknown = set(known.unique()) - set(WEATHER_ORDER)
     if unknown:
-        raise ValueError(f"unmapped weather labels: {sorted(unknown)}")
+        pass
     return series.map(WEATHER_ORDER).astype(float)


```

**Red test:** `python -m pytest tests/test_leakage.py -q`

```text
........F                                                                                                                                      [100%]
====================================================================== FAILURES ======================================================================
_____________________________________________________ test_encode_weather_rejects_unknown_label ______________________________________________________

    def test_encode_weather_rejects_unknown_label():
        """Removing the raise in encode_weather must fail tests on unseen labels."""
        from src.features import encode_weather

        s = pd.Series(["GOOD", "SNOW"])
>       with pytest.raises(ValueError, match="unmapped weather labels"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_leakage.py:86: Failed
============================================================== short test summary info ===============================================================
FAILED tests/test_leakage.py::test_encode_weather_rejects_unknown_label - Failed: DID NOT RAISE ValueError
1 failed, 8 passed in 0.46s
```

**Hook stderr** (manual run):

```text
Leakage tests failed after editing /Users/sana/bikeshare-open/src/features.py:
........F                                                                [100%]
=================================== FAILURES ===================================
__________________ test_encode_weather_rejects_unknown_label ___________________

    def test_encode_weather_rejects_unknown_label():
        """Removing the raise in encode_weather must fail tests on unseen labels."""
        from src.features import encode_weather

        s = pd.Series(["GOOD", "SNOW"])
>       with pytest.raises(ValueError, match="unmapped weather labels"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_leakage.py:86: Failed
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_encode_weather_rejects_unknown_label - Fai...
1 failed, 8 passed in 0.43s
exit=2
```

**Turns to fix:** not measured (manual).

**Fix** (commit `fef9461`): restored the `raise`; `python -m pytest tests/ -q` gives `18 passed`.

## Fault 4: `cp` into `data/raw/`

**What happened.** The `Edit(./data/raw/**)` and `Write(./data/raw/**)` deny rules in `.claude/settings.json` only cover the agent's Edit and Write tools. A `cp` in Bash is a different tool, and `cp` is neither allowed nor denied by the settings. This run was typed in a terminal, not through the agent's Bash tool, so I have not tested whether the agent would be prompted. The copy went through silently:

```text
$ cp data/raw/bike_daily.csv data/raw/stray.csv
$ ls -la data/raw
total 352
drwxr-xr-x  4 sana  staff    128 Nov 19 17:58 .
drwxr-xr-x  3 sana  staff     96 Nov 19 14:18 ..
-rw-r--r--  1 sana  staff  86325 Nov 19 14:18 bike_daily.csv
-rw-r--r--  1 sana  staff  86325 Nov 19 17:58 stray.csv
```

The original integrity check, a SHA-256 of the one named file, still passes with the stray file sitting next to it:

```text
$ echo "a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc  data/raw/bike_daily.csv" | shasum -a 256 -c -
data/raw/bike_daily.csv: OK
```

**What catches it.** `tests/test_raw_hash.py` checks both the hash of `bike_daily.csv` and the full list of entries in `data/raw/`. First version of the test against the stray file (it only looked at regular files and used a relative path):

```text
$ python -m pytest tests/test_raw_hash.py -q
F                                                                                                                                              [100%]
====================================================================== FAILURES ======================================================================
________________________________________________________ test_raw_directory_hashes_and_files _________________________________________________________

    def test_raw_directory_hashes_and_files():
        raw_dir = Path("data/raw")
        files = sorted(p.name for p in raw_dir.iterdir() if p.is_file())
>       assert files == sorted(EXPECTED_RAW_HASHES), f"unexpected files in data/raw: {files}"
E       AssertionError: unexpected files in data/raw: ['bike_daily.csv', 'stray.csv']
E       assert ['bike_daily...., 'stray.csv'] == ['bike_daily.csv']
E
E         Left contains one more item: 'stray.csv'
E         Use -v to get more diff

tests/test_raw_hash.py:12: AssertionError
============================================================== short test summary info ===============================================================
FAILED tests/test_raw_hash.py::test_raw_directory_hashes_and_files - AssertionError: unexpected files in data/raw: ['bike_daily.csv', 'stray.csv']
1 failed in 0.04s
```

After `rm data/raw/stray.csv`:

```text
$ python -m pytest tests/test_raw_hash.py -q
.                                                                                                                                              [100%]
1 passed in 0.01s
```

**Guard implemented** (extra points). The test was then hardened (compares every entry in `data/raw/` except `.DS_Store`, not just regular files; uses `RAW` from `src/config.py` instead of a relative path) and is now run by `make data`, so the check runs at the start of `make all` as well as in `make test`:

```diff
diff --git a/Makefile b/Makefile
index 2b7a6ab..d3d937f 100644
--- a/Makefile
+++ b/Makefile
@@ -5,6 +5,7 @@ all: data features train

 data:
        python -m src.ingest
+       python -m pytest tests/test_raw_hash.py -q

 features:
        python -m src.features
```

```text
$ make data
python -m src.ingest
OK ingest: 728 rows, 2011-01-03 -> 2012-12-31
python -m pytest tests/test_raw_hash.py -q
.                                                                                                                                              [100%]
1 passed in 0.01s
```

**What else would have caught it.**
- A `PreToolUse` hook on `Bash` that blocks commands writing into `data/raw/` (`cp`, `mv`, `>`, `tee`). It would stop the write instead of detecting it afterwards. Not implemented here.
- `chmod -w data/raw` makes the copy fail for the normal user. Not tested here.

**Limits of what was built.** It detects after the fact and only when `make data` or `make test` runs; it does not prevent the write; and it only watches `data/raw/`.

## Commits

| Step | Commit |
|---|---|
| Add `test_encode_weather_rejects_unknown_label`, ignore notebook checkpoints | `c84c0bf` |
| Fault 1 / fix | `2a5c5fc` / `cec4b52` |
| Fault 2 / fix | `6cfe5ea` / `58a066e` |
| Fault 3 / fix | `c841e72` / `fef9461` |
| Harden raw hash test, run it from `make data` | "Harden raw hash test (all entries, RAW path); run it from make data" |
