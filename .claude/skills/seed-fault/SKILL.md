---
name: seed-fault
description: Seed and verify controlled faults (including copying into data/raw and running a SHA-256 hash check), document results in docs/SEEDED_FAULTS.md, and restore clean repository state.
---

# Seed Fault Workflow

Use this skill when seeding a fault to test detection/guardrails in `bikeshare-open`.

## Steps
1. **Verify clean baseline & record raw hashes:**
   - Ensure `git status` is clean before introducing a fault.
   - Compute or verify SHA-256 hashes for `data/raw/*` using `shasum -a 256`.
2. **Seed the target fault:**
   - Apply one controlled fault at a time (leakage/lag fault, split fault, ingest/schema fault, or `cp` into `data/raw`).
3. **Run checks & hash verification:**
   - Run `python3 -m pytest tests/ -q`, `python3 -m src.ingest`, and the `data/raw` hash/file check.
   - Record commands, detection/failure behavior, and cleanup steps in `docs/SEEDED_FAULTS.md`.
4. **Restore clean state:**
   - Remove any extra files in `data/raw/` and restore modified tracked files with `git checkout -- .` (only on intended test edits).
   - Re-verify `shasum -a 256 -c` passes and `python3 -m pytest tests/ -q` passes.
