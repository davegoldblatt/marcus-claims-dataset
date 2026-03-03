#!/usr/bin/env python3
"""Third-pass merge: cluster2 -> higher-level themes via topic buckets."""

from __future__ import annotations

import csv
import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
IN_C2 = ROOT / "second_pass_clustered_claims.csv"
OUT_THEMES = ROOT / "third_pass_themes.csv"
OUT_THEME_MEMBERS = ROOT / "third_pass_theme_members.csv"
OUT_REPORT = ROOT / "third_pass_report.txt"
OUT_MEMO = ROOT / "ANALYSIS_MEMO.md"
OUT_LOGIC = ROOT / "THIRD_PASS_LOGIC.md"


TOPIC_RULES = [
    ("hallucination_misinformation", re.compile(r"hallucinat|misinformation|false|bullshit|pastiche", re.I)),
    ("scaling_limits", re.compile(r"scal|bigger models|not enough|alone was never", re.I)),
    ("reasoning_common_sense", re.compile(r"reason|common sense|planning|semantics|symbolic|neurosymbolic", re.I)),
    ("agi_timeline", re.compile(r"\bagi\b|artificial general intelligence|lifetime|decade|by\s+20\d{2}", re.I)),
    ("safety_alignment", re.compile(r"alignment|safety|control|risk|danger|harm", re.I)),
    ("regulation_policy", re.compile(r"regulat|law|policy|oversight|government|ban", re.I)),
    ("openai_governance", re.compile(r"openai|sam altman|nonprofit|board|mission", re.I)),
    ("agents_reliability", re.compile(r"agent|agents|tool use|workflow|automation", re.I)),
    ("market_hype_bubble", re.compile(r"bubble|hype|winter|scam|valuation|revenue|profit|business model", re.I)),
    ("self_driving_robotics", re.compile(r"tesla|fsd|autopilot|self-driving|robot", re.I)),
    ("copyright_ip", re.compile(r"copyright|ip|licens|lawsuit|fair use", re.I)),
]

NOISE_RE = re.compile(
    r"(@[a-z0-9_]+|forbes.?s 7 must read|bestselling author|subscribe|restack|reposts|likes|this substack is reader-supported)",
    re.I,
)


@dataclass
class C2:
    cluster2_id: str
    target_mode: str
    claim_type_mode: str
    category_mode: str
    falsifiability_tier_mode: str
    first_date: str
    last_date: str
    occurrences: int
    distinct_posts: int
    horizon_values: str
    representative_quote: str
    source_urls: list[str]


def mode(vals: list[str]) -> str:
    c = Counter(vals)
    return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def topic_of(text: str) -> str:
    for label, rx in TOPIC_RULES:
        if rx.search(text):
            return label
    return "general_misc"


def parse_c2() -> list[C2]:
    out = []
    with IN_C2.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for x in r:
            rep = x["representative_quote"]
            if NOISE_RE.search(rep):
                continue
            out.append(
                C2(
                    cluster2_id=x["cluster2_id"],
                    target_mode=x["target_mode"],
                    claim_type_mode=x["claim_type_mode"],
                    category_mode=x["category_mode"],
                    falsifiability_tier_mode=x["falsifiability_tier_mode"],
                    first_date=x["first_date"],
                    last_date=x["last_date"],
                    occurrences=int(x["occurrences"]),
                    distinct_posts=int(x["distinct_posts"]),
                    horizon_values=x["horizon_values"],
                    representative_quote=rep,
                    source_urls=[u for u in x["source_urls"].split(";") if u],
                )
            )
    return out


def merge(c2s: list[C2]):
    buckets: dict[str, list[C2]] = defaultdict(list)
    for c in c2s:
        txt = f"{c.representative_quote}"
        topic = topic_of(txt)
        key = f"{c.target_mode}|{c.claim_type_mode}|{topic}"
        buckets[key].append(c)

    themes = []
    members = []

    for key, rows in buckets.items():
        target, ctype, topic = key.split("|", 2)
        theme_id = "theme3_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
        first_date = min(r.first_date for r in rows)
        last_date = max(r.last_date for r in rows)
        occ = sum(r.occurrences for r in rows)
        post_sum = sum(r.distinct_posts for r in rows)
        horizons = sorted({h for r in rows for h in r.horizon_values.split(";") if h})
        rep = sorted(rows, key=lambda r: (r.first_date, -r.occurrences, len(r.representative_quote)))[0].representative_quote

        themes.append(
            {
                "theme3_id": theme_id,
                "theme_label": topic,
                "target_mode": target,
                "claim_type_mode": ctype,
                "category_mode": mode([r.category_mode for r in rows]),
                "falsifiability_tier_mode": mode([r.falsifiability_tier_mode for r in rows]),
                "first_date": first_date,
                "last_date": last_date,
                "c2_clusters_merged": len(rows),
                "claim_occurrences": occ,
                "distinct_posts_sum": post_sum,
                "horizon_values": ";".join(horizons),
                "goalpost_shift_candidate": "yes" if len(horizons) >= 2 and occ >= 4 else "no",
                "representative_quote": rep,
                "cluster2_ids": ";".join(sorted(r.cluster2_id for r in rows)),
                "source_urls": ";".join(sorted({u for r in rows for u in r.source_urls})),
            }
        )

        for r in rows:
            members.append(
                {
                    "theme3_id": theme_id,
                    "cluster2_id": r.cluster2_id,
                    "target_mode": r.target_mode,
                    "claim_type_mode": r.claim_type_mode,
                    "category_mode": r.category_mode,
                    "occurrences": r.occurrences,
                    "first_date": r.first_date,
                    "last_date": r.last_date,
                    "representative_quote": r.representative_quote,
                }
            )

    return themes, members


def write_csv(path: Path, rows: list[dict], cols: list[str]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def write_report(themes: list[dict], c2_count: int):
    merged = sum(1 for t in themes if int(t["c2_clusters_merged"]) > 1)
    largest = max((int(t["claim_occurrences"]) for t in themes), default=0)
    goal = sum(1 for t in themes if t["goalpost_shift_candidate"] == "yes")
    with OUT_REPORT.open("w", encoding="utf-8") as f:
        f.write("Third-pass merge report\n")
        f.write(f"Run timestamp: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Input cluster2 rows: {c2_count}\n")
        f.write(f"Theme3 rows: {len(themes)}\n")
        f.write(f"Themes merging >1 cluster2: {merged}\n")
        f.write(f"Largest theme claim_occurrences: {largest}\n")
        f.write(f"Goalpost candidates: {goal}\n")


def write_memo(themes: list[dict]):
    top = sorted(themes, key=lambda x: int(x["claim_occurrences"]), reverse=True)[:15]
    with OUT_MEMO.open("w", encoding="utf-8") as f:
        f.write("# Analysis Memo: One-Level-Up Theme Merge\n\n")
        f.write("## Outcome\n")
        f.write("Third pass groups second-pass clusters into broader themes by target + claim type + topic bucket.\n")
        f.write("This is the synthesis layer to review before final scorecard work.\n\n")
        f.write("## Top Themes\n")
        for i, t in enumerate(top, 1):
            f.write(f"{i}. `{t['theme3_id']}` | `{t['theme_label']}` | occurrences={t['claim_occurrences']} | merged_c2={t['c2_clusters_merged']} | span={t['first_date']}..{t['last_date']}\n")
            f.write(f"   - target={t['target_mode']}, type={t['claim_type_mode']}\n")
            f.write(f"   - rep: {t['representative_quote']}\n")
        f.write("\n## Caveat\n")
        f.write("Topic-bucket merge improves consolidation but can over-merge nearby propositions; use `third_pass_theme_members.csv` for audit.\n")


def write_logic_doc():
    with OUT_LOGIC.open("w", encoding="utf-8") as f:
        f.write("# Third-Pass Logic\n\n")
        f.write("Theme key = `target_mode | claim_type_mode | topic_bucket`.\n")
        f.write("Topic buckets are assigned by regex rules over representative quotes.\n")
        f.write("This pass is intentionally broader than pass 2 to create narrative-level synthesis themes.\n")


def main():
    if not IN_C2.exists():
        raise SystemExit("Missing second pass clustered input")

    c2s = parse_c2()
    themes, members = merge(c2s)

    themes_sorted = sorted(themes, key=lambda x: int(x["claim_occurrences"]), reverse=True)
    members_sorted = sorted(members, key=lambda x: (x["theme3_id"], x["first_date"], x["cluster2_id"]))

    write_csv(
        OUT_THEMES,
        themes_sorted,
        [
            "theme3_id", "theme_label", "target_mode", "claim_type_mode", "category_mode", "falsifiability_tier_mode",
            "first_date", "last_date", "c2_clusters_merged", "claim_occurrences", "distinct_posts_sum", "horizon_values",
            "goalpost_shift_candidate", "representative_quote", "cluster2_ids", "source_urls",
        ],
    )
    write_csv(
        OUT_THEME_MEMBERS,
        members_sorted,
        [
            "theme3_id", "cluster2_id", "target_mode", "claim_type_mode", "category_mode", "occurrences", "first_date", "last_date", "representative_quote",
        ],
    )
    write_report(themes_sorted, len(c2s))
    write_memo(themes_sorted)
    write_logic_doc()

    print(f"Input cluster2: {len(c2s)}")
    print(f"Output themes: {len(themes_sorted)}")
    print(f"Wrote {OUT_THEMES}")
    print(f"Wrote {OUT_THEME_MEMBERS}")
    print(f"Wrote {OUT_REPORT}")
    print(f"Wrote {OUT_MEMO}")
    print(f"Wrote {OUT_LOGIC}")


if __name__ == "__main__":
    main()
