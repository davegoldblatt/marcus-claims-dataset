#!/usr/bin/env python3
"""Merge all batch JSONL files into claims_raw.jsonl with sequential IDs, sorted by date."""

import json
import glob
from pathlib import Path

BATCH_DIR = Path(__file__).parent / "batches"
OUTPUT = Path(__file__).parent / "claims_raw.jsonl"

# Read all claims from all batch files in order
all_claims = []
batch_files = sorted(BATCH_DIR.glob("batch_*.jsonl"))

for bf in batch_files:
    with open(bf) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                claim = json.loads(line)
                # Remove any id field that might have snuck in
                claim.pop("id", None)
                all_claims.append(claim)
            except json.JSONDecodeError as e:
                print(f"WARNING: Bad JSON in {bf.name}: {e}")

print(f"Total claims loaded: {len(all_claims)}")

# Sort by claim_date, then slug for stable ordering
all_claims.sort(key=lambda c: (c.get("claim_date", ""), c.get("slug", "")))

# Assign sequential IDs
for i, claim in enumerate(all_claims, 1):
    claim["id"] = f"claim_{i:04d}"

# Write output
with open(OUTPUT, "w") as f:
    for claim in all_claims:
        f.write(json.dumps(claim, ensure_ascii=False) + "\n")

print(f"Written {len(all_claims)} claims to {OUTPUT}")

# Quick stats
types = {}
targets = {}
dates = set()
for c in all_claims:
    t = c.get("type", "unknown")
    types[t] = types.get(t, 0) + 1
    dates.add(c.get("claim_date", "")[:7])  # year-month

print(f"\nBy type:")
for t, count in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {t}: {count}")

print(f"\nDate range: {min(dates)} to {max(dates)}")
print(f"Unique months: {len(dates)}")
