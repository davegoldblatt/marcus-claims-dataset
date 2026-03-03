#!/usr/bin/env python3
"""Build final output files: claims_final.jsonl, claims_canonical.csv, second_pass_audit.csv"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).parent

# Load all data
with open(BASE / "claims_scored.jsonl") as f:
    scored = {json.loads(line)["id"]: json.loads(line) for line in f}

# Re-read to preserve order
with open(BASE / "claims_scored.jsonl") as f:
    scored_list = [json.loads(line) for line in f]

with open(BASE / "claim_clusters.jsonl") as f:
    cluster_map = {json.loads(line)["id"]: json.loads(line)["cluster_id"] for line in f}

with open(BASE / "clusters.json") as f:
    clusters = json.load(f)

cluster_lookup = {c["cluster_id"]: c for c in clusters}

# 1. Build claims_final.jsonl — scored claims + cluster_id
print("Building claims_final.jsonl...")
with open(BASE / "claims_final.jsonl", "w") as f:
    for claim in scored_list:
        claim["cluster_id"] = cluster_map.get(claim["id"], "miscellaneous")
        f.write(json.dumps(claim, ensure_ascii=False) + "\n")

# 2. Build claims_canonical.csv — one row per cluster
print("Building claims_canonical.csv...")
cluster_claims = defaultdict(list)
for claim in scored_list:
    cid = cluster_map.get(claim["id"], "miscellaneous")
    cluster_claims[cid].append(claim)

with open(BASE / "claims_canonical.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "cluster_id", "canonical_statement", "claim_count",
        "date_first", "date_last", "span_days",
        "pct_supported", "pct_mixed", "pct_contradicted", "pct_untestable", "pct_pending",
        "specificity_high_pct", "falsifiability_yes_pct",
        "revision_notes"
    ])
    for cluster in sorted(clusters, key=lambda c: -c["claim_count"]):
        cid = cluster["cluster_id"]
        claims = cluster_claims[cid]
        n = len(claims)
        dates = sorted(c["claim_date"] for c in claims)

        from datetime import datetime
        try:
            d0 = datetime.strptime(dates[0], "%Y-%m-%d")
            d1 = datetime.strptime(dates[-1], "%Y-%m-%d")
            span = (d1 - d0).days
        except:
            span = 0

        status_counts = Counter(c.get("status_at_eval", "") for c in claims)
        spec_counts = Counter(c.get("specificity", "") for c in claims)
        fals_counts = Counter(c.get("falsifiability", "") for c in claims)

        writer.writerow([
            cid,
            cluster["canonical_statement"],
            n,
            dates[0], dates[-1], span,
            f"{status_counts.get('supported',0)/n*100:.1f}",
            f"{status_counts.get('mixed',0)/n*100:.1f}",
            f"{status_counts.get('contradicted',0)/n*100:.1f}",
            f"{status_counts.get('untestable',0)/n*100:.1f}",
            f"{status_counts.get('pending',0)/n*100:.1f}",
            f"{spec_counts.get('high',0)/n*100:.1f}",
            f"{fals_counts.get('yes',0)/n*100:.1f}",
            cluster.get("revision_notes", "")
        ])

# 3. Build second_pass_audit.csv — per-claim with cluster context
print("Building second_pass_audit.csv...")
with open(BASE / "second_pass_audit.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "id", "claim_date", "slug", "claim", "type", "target",
        "cluster_id", "canonical_statement",
        "specificity", "falsifiability", "status_at_eval",
        "horizon_type", "horizon_value"
    ])
    for claim in scored_list:
        cid = cluster_map.get(claim["id"], "miscellaneous")
        canonical = cluster_lookup.get(cid, {}).get("canonical_statement", "")
        writer.writerow([
            claim["id"], claim["claim_date"], claim["slug"],
            claim["claim"], claim["type"], claim.get("target", ""),
            cid, canonical,
            claim.get("specificity", ""), claim.get("falsifiability", ""),
            claim.get("status_at_eval", ""),
            claim.get("horizon_type", ""), claim.get("horizon_value", "")
        ])

# 4. Print summary stats
print("\n=== FINAL SUMMARY ===\n")

# Scorecard per cluster (top 15)
print("Top 15 clusters — scorecard:")
print(f"{'Cluster':<35} {'n':>4} {'Supp%':>6} {'Mix%':>6} {'Contr%':>6} {'Untest%':>7} {'Pend%':>6}")
for cluster in sorted(clusters, key=lambda c: -c["claim_count"])[:15]:
    cid = cluster["cluster_id"]
    claims = cluster_claims[cid]
    n = len(claims)
    sc = Counter(c.get("status_at_eval", "") for c in claims)
    print(f"{cid:<35} {n:>4} {sc.get('supported',0)/n*100:>5.1f}% {sc.get('mixed',0)/n*100:>5.1f}% {sc.get('contradicted',0)/n*100:>5.1f}% {sc.get('untestable',0)/n*100:>6.1f}% {sc.get('pending',0)/n*100:>5.1f}%")

# Repetition cadence: claims per quarter per cluster
print("\n\nRepetition cadence (claims per quarter) for top 10 clusters:")
for cluster in sorted(clusters, key=lambda c: -c["claim_count"])[:10]:
    cid = cluster["cluster_id"]
    claims = cluster_claims[cid]
    quarters = Counter()
    for c in claims:
        y = c["claim_date"][:4]
        m = int(c["claim_date"][5:7])
        q = f"{y}-Q{(m-1)//3+1}"
        quarters[q] += 1
    qs = sorted(quarters.items())
    print(f"\n  {cid} ({len(claims)} total):")
    for q, n in qs:
        bar = "█" * n
        print(f"    {q}: {bar} {n}")

print("\nDone.")
