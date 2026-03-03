#!/usr/bin/env python3
"""Second-pass clustering for extracted claims.

Inputs:
- first_pass_claims.csv

Outputs:
- second_pass_clustered_claims.csv: cluster-level rollups
- second_pass_cluster_members.csv: claim-to-cluster assignments
- second_pass_cluster_report.txt: diagnostics
"""

from __future__ import annotations

import csv
import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
IN_CLAIMS = ROOT / "first_pass_claims.csv"
OUT_CLUSTERS = ROOT / "second_pass_clustered_claims.csv"
OUT_MEMBERS = ROOT / "second_pass_cluster_members.csv"
OUT_REPORT = ROOT / "second_pass_cluster_report.txt"

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "as", "by", "at", "from", "that", "this", "it",
    "is", "are", "was", "were", "be", "been", "being", "i", "we", "you", "they", "he", "she", "them", "our", "my", "your",
    "will", "would", "could", "should", "can", "cannot", "cant", "wont", "not", "very", "more", "most", "much", "many",
    "about", "into", "over", "under", "than", "then", "there", "their", "its", "if", "but", "so", "do", "does", "did",
    "have", "has", "had", "also", "just", "really", "still", "now", "yet", "likely", "unlikely", "need", "must", "should",
    "one", "two", "three", "first", "second", "new", "old", "current",
}

GENERIC_AI_WORDS = {
    "ai", "agi", "llm", "llms", "gpt", "chatgpt", "model", "models", "language", "large", "machine", "learning", "transformer",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass
class ClaimRow:
    claim_id: str
    claim_date: str
    slug: str
    url: str
    quote: str
    canonical_norm: str
    category: str
    claim_type: str
    falsifiability_tier: str
    target: str
    horizon_type: str
    horizon_value: str
    token_set: set[str] = field(default_factory=set)
    trigram_set: set[str] = field(default_factory=set)


@dataclass
class Cluster:
    cluster_id: str
    block_key: str
    member_ids: list[str] = field(default_factory=list)
    member_rows: list[ClaimRow] = field(default_factory=list)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def content_tokens(text: str) -> set[str]:
    toks = []
    for t in tokenize(text):
        if len(t) < 3:
            continue
        if t in STOPWORDS:
            continue
        toks.append(t)
    return set(toks)


def char_trigrams(s: str) -> set[str]:
    s = re.sub(r"\s+", " ", s.strip().lower())
    if not s:
        return set()
    if len(s) < 3:
        return {s}
    return {s[i : i + 3] for i in range(len(s) - 2)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def dice(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return (2.0 * inter) / (len(a) + len(b))


def pair_similarity(a: ClaimRow, b: ClaimRow) -> tuple[float, int]:
    tok = jaccard(a.token_set, b.token_set)
    tri = dice(a.trigram_set, b.trigram_set)
    overlap = len((a.token_set - GENERIC_AI_WORDS) & (b.token_set - GENERIC_AI_WORDS))
    return 0.65 * tok + 0.35 * tri, overlap


def theme_label(rows: list[ClaimRow]) -> str:
    counts = Counter()
    for r in rows:
        for tok in r.token_set:
            if tok in GENERIC_AI_WORDS:
                continue
            counts[tok] += 1
    top = [t for t, _ in counts.most_common(4)]
    return "_".join(top) if top else "misc_claims"


def parse_rows() -> list[ClaimRow]:
    rows: list[ClaimRow] = []
    with IN_CLAIMS.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for x in r:
            cr = ClaimRow(
                claim_id=x["claim_id"],
                claim_date=x["claim_date"],
                slug=x["slug"],
                url=x["url"],
                quote=x["quote"],
                canonical_norm=x["canonical_norm"],
                category=x["category"],
                claim_type=x["claim_type"],
                falsifiability_tier=x["falsifiability_tier"],
                target=x["target"],
                horizon_type=x["horizon_type"],
                horizon_value=x["horizon_value"],
            )
            cr.token_set = content_tokens(cr.canonical_norm)
            cr.trigram_set = char_trigrams(cr.canonical_norm)
            rows.append(cr)
    rows.sort(key=lambda z: (z.claim_date, z.claim_id))
    return rows


def threshold_for_type(claim_type: str) -> float:
    if claim_type == "causal":
        return 0.32
    if claim_type == "predictive":
        return 0.34
    if claim_type == "descriptive":
        return 0.38
    return 0.40


def cluster_rows(rows: list[ClaimRow]) -> list[Cluster]:
    by_block: dict[str, list[ClaimRow]] = defaultdict(list)
    for r in rows:
        by_block[r.target].append(r)

    all_clusters: list[Cluster] = []

    for block_key, block_rows in by_block.items():
        clusters: list[Cluster] = []

        for row in block_rows:
            best_idx = -1
            best_sim = 0.0
            best_overlap = 0

            for idx, c in enumerate(clusters):
                members = c.member_rows
                if len(members) > 30:
                    step = max(1, len(members) // 25)
                    members = members[::step]

                local_best = 0.0
                local_overlap = 0
                for m in members:
                    sim, overlap = pair_similarity(row, m)
                    if sim > local_best:
                        local_best = sim
                        local_overlap = overlap

                if local_best > best_sim:
                    best_sim = local_best
                    best_overlap = local_overlap
                    best_idx = idx

            threshold = threshold_for_type(row.claim_type)
            if best_idx >= 0 and best_sim >= threshold and (best_overlap >= 1 or row.horizon_value):
                c = clusters[best_idx]
                c.member_ids.append(row.claim_id)
                c.member_rows.append(row)
            else:
                cid = "cluster2_" + hashlib.sha1(f"{block_key}|{row.claim_id}".encode("utf-8")).hexdigest()[:12]
                clusters.append(
                    Cluster(
                        cluster_id=cid,
                        block_key=block_key,
                        member_ids=[row.claim_id],
                        member_rows=[row],
                    )
                )

        all_clusters.extend(clusters)

    return all_clusters


def mode(vals: list[str]) -> str:
    c = Counter(vals)
    return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def write_outputs(clusters: list[Cluster]) -> None:
    with OUT_CLUSTERS.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "cluster2_id",
            "theme_label",
            "target_mode",
            "claim_type_mode",
            "category_mode",
            "falsifiability_tier_mode",
            "first_date",
            "last_date",
            "occurrences",
            "distinct_posts",
            "horizon_values",
            "goalpost_shift_candidate",
            "representative_quote",
            "supporting_claim_ids",
            "source_urls",
        ])

        for c in sorted(clusters, key=lambda cl: len(cl.member_rows), reverse=True):
            rows = c.member_rows
            dates = sorted([r.claim_date for r in rows if r.claim_date != "unknown"])
            first_date = dates[0] if dates else "unknown"
            last_date = dates[-1] if dates else "unknown"
            horizons = sorted({r.horizon_value for r in rows if r.horizon_value})
            posts = sorted({r.slug for r in rows})
            urls = sorted({r.url for r in rows})

            goalpost = "yes" if len(horizons) >= 2 and len(rows) >= 3 else "no"
            rep = sorted(rows, key=lambda r: (r.claim_date, len(r.quote)))[0].quote

            w.writerow([
                c.cluster_id,
                theme_label(rows),
                mode([r.target for r in rows]),
                mode([r.claim_type for r in rows]),
                mode([r.category for r in rows]),
                mode([r.falsifiability_tier for r in rows]),
                first_date,
                last_date,
                len(rows),
                len(posts),
                ";".join(horizons),
                goalpost,
                rep,
                ";".join(sorted(c.member_ids)),
                ";".join(urls),
            ])

    with OUT_MEMBERS.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "cluster2_id",
            "claim_id",
            "claim_date",
            "target",
            "claim_type",
            "category",
            "falsifiability_tier",
            "horizon_type",
            "horizon_value",
            "quote",
            "url",
        ])
        for c in clusters:
            for r in sorted(c.member_rows, key=lambda z: (z.claim_date, z.claim_id)):
                w.writerow([
                    c.cluster_id,
                    r.claim_id,
                    r.claim_date,
                    r.target,
                    r.claim_type,
                    r.category,
                    r.falsifiability_tier,
                    r.horizon_type,
                    r.horizon_value,
                    r.quote,
                    r.url,
                ])

    sizes = [len(c.member_rows) for c in clusters]
    gt1 = sum(1 for s in sizes if s > 1)
    with OUT_REPORT.open("w", encoding="utf-8") as f:
        f.write("Second-pass clustering report\n")
        f.write(f"Run timestamp: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Input claims: {sum(sizes)}\n")
        f.write(f"Clusters: {len(clusters)}\n")
        f.write(f"Clusters with >1 claim: {gt1}\n")
        f.write(f"Largest cluster size: {max(sizes) if sizes else 0}\n")
        f.write(f"Output: {OUT_CLUSTERS}\n")
        f.write(f"Members: {OUT_MEMBERS}\n")


def main() -> None:
    if not IN_CLAIMS.exists():
        raise SystemExit(f"Missing input: {IN_CLAIMS}")

    rows = parse_rows()
    clusters = cluster_rows(rows)
    write_outputs(clusters)

    print(f"Input claims: {len(rows)}")
    print(f"Clusters: {len(clusters)}")
    print(f"Wrote {OUT_CLUSTERS}")
    print(f"Wrote {OUT_MEMBERS}")
    print(f"Wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
