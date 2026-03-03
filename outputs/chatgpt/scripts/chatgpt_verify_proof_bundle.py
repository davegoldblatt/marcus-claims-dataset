#!/usr/bin/env python3
"""Verify chatgpt proof bundle integrity."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    proof = root / "outputs" / "chatgpt" / "proof"

    manifest_path = proof / "chatgpt_posts_manifest.csv"
    ledger_path = proof / "chatgpt_processing_ledger.csv"
    coverage_path = proof / "chatgpt_coverage_report.json"

    missing = [p for p in [manifest_path, ledger_path, coverage_path] if not p.exists()]
    if missing:
        raise SystemExit(f"Missing proof files: {missing}")

    manifest = load_csv(manifest_path)
    ledger = load_csv(ledger_path)
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))

    if len(manifest) != len(ledger):
        raise SystemExit(f"Row mismatch: manifest={len(manifest)}, ledger={len(ledger)}")

    if coverage.get("total_posts_in_manifest") != len(manifest):
        raise SystemExit("Coverage total_posts_in_manifest mismatch")

    if coverage.get("reviewed_posts") != len(ledger):
        raise SystemExit("Coverage reviewed_posts mismatch")

    for row in ledger:
        if row.get("review_status") != "scanned_full_text":
            raise SystemExit(f"Unexpected review_status for {row.get('post_id')}: {row.get('review_status')}")

    for row in manifest:
        local = root / row["local_path"]
        if not local.exists():
            raise SystemExit(f"Missing file: {local}")
        if str(local.stat().st_size) != str(row["bytes"]):
            raise SystemExit(f"Byte mismatch for {local}")
        digest = sha256_file(local)
        if digest != row["sha256"]:
            raise SystemExit(f"Hash mismatch for {local}")

    print("PASS: proof bundle verified")
    print(f"Posts verified: {len(manifest)}")


if __name__ == "__main__":
    main()
