import hashlib
from pathlib import Path

EXPECTED_RAW_HASHES = {
    "bike_daily.csv": "a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc",
}


def test_raw_directory_hashes_and_files():
    raw_dir = Path("data/raw")
    files = sorted(p.name for p in raw_dir.iterdir() if p.is_file())
    assert files == sorted(EXPECTED_RAW_HASHES), f"unexpected files in data/raw: {files}"
    for name, expected_hash in EXPECTED_RAW_HASHES.items():
        actual_hash = hashlib.sha256((raw_dir / name).read_bytes()).hexdigest()
        assert actual_hash == expected_hash, f"hash mismatch for {name}: {actual_hash}"
