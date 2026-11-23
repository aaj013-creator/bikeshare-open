# Bikeshare demand report

## Results

Final untransformed pipeline, with the rejected `cnt_roll_3` excluded. Values below match the existing `reports/metrics.json`; R² is unitless and MAE is rides/day.

| Model | Validation R² | Validation MAE | Test R² | Test MAE |
|---|---:|---:|---:|---:|
| Mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Ridge | 0.6475 | 832.9 | 0.5833 | 947.1 |
| HGB | 0.2185 | 1296.6 | -0.4975 | 1972.6 |

Person A's final integration remains: add the required before/after feature comparison and ensure its eight rows agree with the committed metrics evidence. This table describes the final retained pipeline only.

## Headline finding

Under the chronological split, ridge reaches test R² 0.5833 against persistence's 0.5099, but has worse MAE (947.1 versus 840.1). HGB has negative test R² (-0.4975), yet improves on the training-mean baseline (-2.1441). These comparisons support a growth/extrapolation limitation rather than the claim that any negative R² model loses to every baseline. Person A rejected the three-day rolling feature after validation R² declined for ridge (0.6475 to 0.6439) and HGB (0.2185 to 0.1983); the original feature set is retained.

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

Person C used OpenAI Codex (GPT-6; parameter count not disclosed), rather than the group's earlier `qwen3.5:9b` via Ollama (`bikeshare-coder`, 64k context). The prior model configuration and unsuccessful hosted-model attempt are recorded in `docs/DECISIONS.md`. Person C's work therefore represents a switch in assistant; it is not a local Qwen run.

Agent-generated work:

- Codex wrote `src/target_experiment.py`, ran the validation and frozen test comparison, and generated the two target-experiment JSON files.
- Codex drafted this report, including the deployment recommendation and methodological interpretation, and appended the corresponding decision records.
- Codex manually reviewed the `person-c-analysis` diff; no issue in the five required checks was found that changes a number or invalidates a conclusion. The configured audit model was unavailable, and a different team member still needs to run `/leakage-auditor` on this branch before merge. See `docs/AUDIT.md`.
- Existing features, tests, fault documentation and configuration came from A/B and the starter, as recorded in the earlier history.

Human-specified choices and inherited group decisions:

- The user assigned Person C Exercises 3–5 and attribution, supplied the group repository, and requested compliance with the assignment.
- The existing group record specifies the prediction target, exclusions, chronological split and both baselines (the five starter decision lines).
- Person A's recorded decision rejected `cnt_roll_3` using validation evidence (2026-11-16).

The target-transformation choice, defensibility argument and deployment recommendation above were proposed by Codex, not independently supplied by the user. The group must review these claims before submission. Person C's Exercise 3 remains incomplete until a different team member runs `/leakage-auditor` on the `person-c-analysis` branch before it is merged and records their review in `docs/AUDIT.md`.
