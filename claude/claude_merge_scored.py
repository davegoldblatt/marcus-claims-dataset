#!/usr/bin/env python3
"""Merge scored chunks into claims_scored.jsonl and print aggregate stats."""

import json
from collections import Counter
from pathlib import Path

CHUNK_DIR = Path(__file__).parent / "pass2_chunks"
OUTPUT = Path(__file__).parent / "claims_scored.jsonl"

all_claims = []
for i in range(12):
    path = CHUNK_DIR / f"chunk_{i:02d}_scored.jsonl"
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    all_claims.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"WARNING: Bad JSON in {path.name}: {e}")

# Sort by ID
all_claims.sort(key=lambda c: c.get("id", ""))

print(f"Total scored claims: {len(all_claims)}")

# Validate all have the new fields
missing = 0
for c in all_claims:
    for field in ["specificity", "falsifiability", "evaluation_date", "status_at_eval"]:
        if field not in c:
            missing += 1
            print(f"  MISSING {field} in {c.get('id', '?')}")
print(f"Missing fields: {missing}")

# Write
with open(OUTPUT, "w") as f:
    for c in all_claims:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print(f"\nWritten to {OUTPUT}")

# Stats
print("\n=== AGGREGATE STATS ===\n")

for field in ["specificity", "falsifiability", "status_at_eval"]:
    counts = Counter(c.get(field, "MISSING") for c in all_claims)
    total = sum(counts.values())
    print(f"{field}:")
    for val, n in counts.most_common():
        print(f"  {val}: {n} ({n/total*100:.1f}%)")
    print()

# Status by year
print("status_at_eval by year:")
years = sorted(set(c["claim_date"][:4] for c in all_claims))
for year in years:
    year_claims = [c for c in all_claims if c["claim_date"].startswith(year)]
    counts = Counter(c.get("status_at_eval", "?") for c in year_claims)
    total = len(year_claims)
    parts = []
    for status in ["supported", "mixed", "contradicted", "untestable", "pending"]:
        n = counts.get(status, 0)
        parts.append(f"{status}:{n}({n/total*100:.0f}%)")
    print(f"  {year} (n={total}): {', '.join(parts)}")

# Status by type
print("\nstatus_at_eval by claim type:")
for ctype in ["descriptive", "predictive", "causal", "normative"]:
    type_claims = [c for c in all_claims if c.get("type") == ctype]
    counts = Counter(c.get("status_at_eval", "?") for c in type_claims)
    total = len(type_claims)
    parts = []
    for status in ["supported", "mixed", "contradicted", "untestable", "pending"]:
        n = counts.get(status, 0)
        parts.append(f"{status}:{n}({n/total*100:.0f}%)")
    print(f"  {ctype} (n={total}): {', '.join(parts)}")

# Contradicted claims list
print("\n=== ALL CONTRADICTED CLAIMS ===\n")
contradicted = [c for c in all_claims if c.get("status_at_eval") == "contradicted"]
for c in contradicted:
    print(f"  {c['id']} ({c['claim_date']}): {c['claim'][:100]}")
