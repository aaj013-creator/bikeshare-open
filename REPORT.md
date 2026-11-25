# Bikeshare demand report

Group: Aarushi Jain (A), Sana Gupta (B), Akshitaa Balasai (C).

## Results

All rows come from `make all`. "Final" is the committed pipeline (`reports/metrics.json`, with `cnt_roll_3` excluded). "With cnt_roll_3" is the same pipeline with the feature included (`reports/metrics.json` at commit `b965f53`). R² is unitless; MAE is rides/day. The decision to reject `cnt_roll_3` used validation only; its test rows are reported for completeness and were not used to decide.

| Model | Feature set | Validation R² | Validation MAE | Test R² | Test MAE |
|---|---|---:|---:|---:|---:|
| Mean | Final | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Persistence | Final | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Ridge | Final | 0.6475 | 832.9 | 0.5833 | 947.1 |
| HGB | Final | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| Mean | With cnt_roll_3 (rejected) | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Persistence | With cnt_roll_3 (rejected) | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Ridge | With cnt_roll_3 (rejected) | 0.6439 | 836.5 | 0.5800 | 946.2 |
| HGB | With cnt_roll_3 (rejected) | 0.1983 | 1311.6 | -0.5338 | 1998.7 |

## Headline finding

A naive model that uses every column scores R² 1.000, and that score is invalid: `casual + registered == cnt` on every row, so the model learns addition rather than demand (`python -m src.leakage_demo`). With those columns excluded and a chronological split (train 2011, validate H1 2012, test H2 2012), the mean baseline scores test R² -2.1441, because ridership grew about 65% and the 2011 average no longer describes late 2012. Ridge reaches test R² 0.5833 against a persistence baseline of 0.5099, a margin of only 0.0734, and loses to persistence on MAE (947.1 versus 840.1 rides). Gradient boosting scores -0.4975: far better than the mean baseline, but negative because a tree cannot predict above the largest count it saw in training, and most test days lie above the 2011 maximum. Our added feature, `cnt_roll_3`, lowered validation R² for both ridge (0.6475 to 0.6439) and HGB (0.2185 to 0.1983), so we rejected it and kept the original feature set.

## Exercise 4: target transformation

We modeled daily change rather than the absolute demand level: `z[t] = cnt[t] - cnt[t-1]`. HGB predicts `z[t]`; adding the observed previous day's demand yields the forecast in rides. The previous-day value is the existing calendar-aligned `cnt_lag_1`. We kept all 14 retained features, the 2011 training / H1 2012 validation / H2 2012 test split, and HGB's existing seed and parameters. All models were fitted on 2011 only. No target-dependent transformation was fitted on validation or test.

One candidate was evaluated on validation. The validation results and decision were committed before evaluating its test predictions. We then evaluated the frozen candidate on test once; we did not tune after that evaluation. Baseline test scores were already present in the inherited repository, so we do not claim they had never been viewed by the group.

| Model | Validation R² | Validation MAE | Test R² | Test MAE |
|---|---:|---:|---:|---:|
| Mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Ridge | 0.6475 | 832.9 | 0.5833 | 947.1 |
| Untransformed HGB | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| Daily-change HGB | 0.6079 | 834.3 | 0.5440 | 921.7 |

The transformation increases validation HGB R² by 0.3894 and reduces MAE by 462.3 rides. It makes the tree competitive with ridge, although ridge remains ahead by 0.0396 R² and 1.4 rides MAE. On the final test, transformed HGB improves substantially over raw HGB and beats ridge on MAE by 25.4 rides, but trails ridge by 0.0393 R² and still loses to persistence on MAE by 81.6 rides. These are holdout observations, not a new selection round.

This is defensible for daily updating: yesterday's observed total supplies the changing demand level, while the tree learns deviations from it. The reconstructed forecast can exceed historical training demand levels even though a tree partitions its feature space. It is not defensible as an unchanged multi-day forecast made before yesterday's demand is known. All comparisons also inherit the starter's use of same-day weather measurements; a real advance forecast would require available weather forecasts and a fresh evaluation. The transformation is a useful demonstration, not evidence that the tree universally wins. We retain the untransformed main pipeline as required.

Reproduce validation with `python -m src.target_experiment --out reports/target_validation.json`. Reproduce the frozen final comparison with `python -m src.target_experiment --test --out reports/target_experiment.json`. The experiment is on branch `person-c-analysis` and leaves `reports/metrics.json` untouched.

## Exercise 5: ridge vs persistence

For a deployment whose cost is proportional to absolute daily count error, we recommend persistence over ridge. Ridge's test R² is higher by 0.0734 (0.5833 versus 0.5099), indicating lower squared error, but its MAE is 107.0 rides higher (947.1 versus 840.1), about 12.7% worse. Ridge did win both validation metrics (R² 0.6475 versus 0.4507; MAE 832.9 versus 900.6), so that advantage did not persist for absolute error in H2 2012. Persistence also needs only yesterday's count, without a fitted scaler, model, or weather inputs. If unusually large errors carry disproportionate operational costs, ridge's squared-error advantage could justify it, but that requires an explicit cost function and further chronological evaluation. This is a retrospective interpretation of the assigned holdout comparison, not permission to retune on test or a claim of statistical significance.

## Attribution

Models: Aarushi Jain used qwen3.5:9b via local Ollama (`bikeshare-coder`, 64k context) throughout; a hosted model (glm-5.3-flash:cloud) was tried and returned 402, so it was not used. Sana Gupta seeded the Exercise 2 faults by hand in a terminal, so no agent turns were recorded. Akshitaa Balasai switched to OpenAI Codex (GPT-6, size undisclosed) for Exercises 4 and 5; Akshitaa Balasai's audit of `a-feature` used qwen3.5:9b. Aarushi Jain also used Claude (Anthropic) as a chat assistant outside the repo, to plan steps and draft commands, tests and text that A then ran, checked and edited.

Agent-generated (files or functions):
- qwen3.5:9b: the `cnt_roll_3` line in `src/features.py`; a first draft of the `cnt_roll_3` test (rejected and rewritten, DECISIONS 2026-11-16); both `leakage-auditor` outputs in `docs/AUDIT.md`; `reports/audit.jsonl`.
- Claude chat assistant: first drafts of `test_cnt_roll_3_on_named_date`, `test_every_raw_column_is_classified`, the `REJECTED_COLS`, `SOURCE_COLS`, `UNUSED_COLS` and `DIRECT_COLS` sets in `src/config.py`, Aarushi Jain's DECISIONS.md lines, the Audit 1 verdict, and the Results and Headline text.
- Codex: `src/target_experiment.py`, `reports/target_validation.json`, `reports/target_experiment.json`, first drafts of the Exercise 4 and 5 sections, and the review of `person-c-analysis` in `docs/AUDIT.md`.

Decisions that were ours (each has a line in docs/DECISIONS.md):
- Predict `cnt`; exclude `casual` and `registered` as leakage; split 2011 / H1 2012 / H2 2012 by date; report the mean and persistence baselines with every score (starter lines, kept).
- Treat R² 1.000 as invalid, and the ridge margin over persistence (0.0734 R², worse MAE) as small (starter lines; Headline finding).
- Reject `cnt_roll_3` because validation R² fell for ridge and HGB; test set not used (2026-11-16).
- Require the feature test to assert unconditionally on a named date (2026-11-16).
- Every raw column must be classified, with `DIRECT_COLS` written by hand (2026-11-17).
- Add the unknown-weather-label test, and check every file in `data/raw/` from `make data` (2026-11-19).
- Exercise 4: daily-change target, frozen after one validation candidate, defensible only when yesterday's count is known (2026-11-19). Proposed with Codex; reviewed and agreed by Akshitaa Balasai.
- Exercise 5: prefer persistence over ridge when cost is absolute error (2026-11-19). Proposed with Codex; reviewed and agreed by Akshitaa Balasai.
