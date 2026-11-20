# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.
- 2026-11-16: Agent model is qwen3.5:9b via Ollama (`bikeshare-coder`, 64k context) on a 16 GB laptop. `make model` failed on Ollama 0.40.16 (`ollama create -f -` reads no stdin), so built from a temp Modelfile; set OLLAMA_FLASH_ATTENTION=1 and OLLAMA_KV_CACHE_TYPE=q8_0 so the 64k context fits in memory. A hosted model (glm-5.3-flash:cloud) returned 402 (no credits), so stayed local.
- 2026-11-16: Added `Bash(python -c*)` to the new-feature skill's allowed-tools. Its feature-list injection was blocked by permissions, so the skill could not load.
- 2026-11-16: Feature `cnt_roll_3` = mean of `cnt` on d-3, d-2, d-1 (`shift(1).rolling(3)`). Availability: uses only days strictly before d, so it is known at prediction time. Test written first and failed on KeyError; it checks 2011-06-15 against (4460 + 5020 + 4891) / 3 hand-computed from the raw CSV. Rejected the agent's first version of the test: its assert sat inside an `if`, so it could never fail.
- 2026-11-16: Rejected `cnt_roll_3` from the model. Validation R^2 ridge 0.6475 -> 0.6439, hgb 0.2185 -> 0.1983 (both worse; below the +0.01 bar). Added `REJECTED_COLS` to `FORBIDDEN` in src/config.py, so the feature is still built and tested but never reaches a model; metrics.json is back to the original numbers. Test set not consulted.
- 2026-11-16: Declined an agent edit that would have overwritten DECISIONS.md and deleted the starter lines.
- 2026-11-17: Every raw column must be in a named set in src/config.py (FORBIDDEN, SOURCE_COLS, UNUSED_COLS, DIRECT_COLS) or be dteday; tests/test_contract.py fails otherwise. DIRECT_COLS is written out by hand rather than taken from feature_columns(): with the denylist alone, a new numeric column in the raw CSV became a model feature automatically and the first version of this test passed. We would rather a new column fail loudly than enter the model silently.
- 2026-11-19: Split Exercise 2 fault runs and fixes into separate commits (`casual` in `feature_columns`, removing `.shift(1)` on `cnt_roll_7`, and removing `raise` in `encode_weather`) with real outputs recorded in `docs/SEEDED_FAULTS.md`.
- 2026-11-19: Added in-repo raw hash verification in `tests/test_raw_hash.py`, documented `PreToolUse` / `chmod -w` / hash-check defenses for `cp` into `data/raw`, and added `.claude/skills/seed-fault/SKILL.md` plus `CLAUDE.md` guidance.
