#!/usr/bin/env python3
"""Goalpost-shift pass over one-level-up themes.

Inputs:
- third_pass_themes_signal.csv
- third_pass_theme_members.csv
- second_pass_clustered_claims.csv

Outputs:
- goalpost_shift_audit.csv
- goalpost_shift_summary.md
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
IN_THEMES = ROOT / "third_pass_themes_signal.csv"
IN_MEMBERS = ROOT / "third_pass_theme_members.csv"
IN_C2 = ROOT / "second_pass_clustered_claims.csv"
OUT_AUDIT = ROOT / "goalpost_shift_audit.csv"
OUT_SUMMARY = ROOT / "goalpost_shift_summary.md"

YEAR_RE = re.compile(r"\b(20\d{2})\b")
HEDGE_RE = re.compile(r"\b(may|might|could|possibly|perhaps|i\s+don'?t\s+know|my\s+best\s+guess|not\s+sure)\b", re.I)
STRONG_RE = re.compile(r"\b(will|won'?t|never|cannot|can'?t|always|must)\b", re.I)


@dataclass
class C2Row:
    cluster2_id: str
    first_date: str
    last_date: str
    horizon_values: str
    representative_quote: str
    occurrences: int


def parse_c2_map() -> dict[str, C2Row]:
    out = {}
    with IN_C2.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for x in r:
            out[x["cluster2_id"]] = C2Row(
                cluster2_id=x["cluster2_id"],
                first_date=x["first_date"],
                last_date=x["last_date"],
                horizon_values=x["horizon_values"],
                representative_quote=x["representative_quote"],
                occurrences=int(x["occurrences"]),
            )
    return out


def parse_horizon(h: str):
    if not h:
        return ("none", None)
    h = h.strip()
    if re.match(r"^20\d{2}-12-31$", h):
        return ("explicit", int(h[:4]))
    if h == "near_term":
        return ("relative", 2)
    if h == "this_decade":
        return ("relative", 6)
    if h == "within_10_years":
        return ("relative", 10)
    if h == "within_lifetime":
        return ("relative", 30)
    return ("relative", None)


def specificity_rank(htype: str) -> int:
    # higher is more specific
    return {"explicit": 3, "relative": 2, "none": 1}.get(htype, 1)


def avg(vals):
    nums = [v for v in vals if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)


def main():
    c2_map = parse_c2_map()

    # theme -> cluster2 list
    members = defaultdict(list)
    with IN_MEMBERS.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for x in r:
            members[x["theme3_id"]].append(x["cluster2_id"])

    rows = []
    with IN_THEMES.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for t in r:
            theme_id = t["theme3_id"]
            cids = members.get(theme_id, [])
            crows = [c2_map[cid] for cid in cids if cid in c2_map]
            crows.sort(key=lambda z: (z.first_date, z.cluster2_id))
            if not crows:
                continue

            split = max(1, len(crows) // 2)
            early = crows[:split]
            late = crows[split:]
            if not late:
                late = crows[-1:]

            def collect_horizon(group):
                types, vals = [], []
                distinct = set()
                for c in group:
                    hs = [h for h in c.horizon_values.split(";") if h]
                    if not hs:
                        hs = [""]
                    for h in hs:
                        htype, hv = parse_horizon(h)
                        types.append(htype)
                        vals.append(hv)
                        if h:
                            distinct.add(h)
                return types, vals, distinct

            e_types, e_vals, e_dist = collect_horizon(early)
            l_types, l_vals, l_dist = collect_horizon(late)
            all_dist = sorted(e_dist | l_dist)

            e_spec = avg([specificity_rank(x) for x in e_types]) or 1
            l_spec = avg([specificity_rank(x) for x in l_types]) or 1
            e_h = avg(e_vals)
            l_h = avg(l_vals)

            horizon_shift = "yes" if len(all_dist) >= 2 else "no"
            shift_type = []
            pushed = 0
            if e_h is not None and l_h is not None and l_h > e_h + 1.0:
                shift_type.append("deadline_pushed_out")
                pushed = 1
            if l_spec + 0.4 < e_spec:
                shift_type.append("less_specific_over_time")
            if e_spec + 0.4 < l_spec:
                shift_type.append("more_specific_over_time")
            if not shift_type and horizon_shift == "yes":
                shift_type.append("horizon_changed")

            def certainty_scores(group):
                hedge = 0
                strong = 0
                total = 0
                for c in group:
                    txt = c.representative_quote
                    h = len(HEDGE_RE.findall(txt))
                    s = len(STRONG_RE.findall(txt))
                    hedge += h
                    strong += s
                    total += max(1, len(YEAR_RE.findall(txt)) + h + s)
                return hedge / total, strong / total

            e_hedge, e_strong = certainty_scores(early)
            l_hedge, l_strong = certainty_scores(late)

            certainty_shift = "stable"
            if l_hedge - e_hedge > 0.08:
                certainty_shift = "softened"
            elif l_strong - e_strong > 0.08:
                certainty_shift = "hardened"

            score = 0
            if horizon_shift == "yes":
                score += 1
            if "less_specific_over_time" in shift_type:
                score += 1
            if pushed:
                score += 2
            if certainty_shift == "softened":
                score += 1

            flag = "yes" if score >= 2 else "no"

            rows.append(
                {
                    "theme3_id": theme_id,
                    "theme_label": t["theme_label"],
                    "target_mode": t["target_mode"],
                    "claim_type_mode": t["claim_type_mode"],
                    "first_date": t["first_date"],
                    "last_date": t["last_date"],
                    "c2_clusters_merged": t["c2_clusters_merged"],
                    "claim_occurrences": t["claim_occurrences"],
                    "distinct_horizon_values": ";".join(all_dist),
                    "horizon_shift_detected": horizon_shift,
                    "horizon_shift_type": ";".join(shift_type) if shift_type else "none",
                    "certainty_shift": certainty_shift,
                    "goalpost_shift_score": str(score),
                    "goalpost_shift_flag": flag,
                    "cluster2_ids": t["cluster2_ids"],
                    "representative_quote": t["representative_quote"],
                }
            )

    rows.sort(key=lambda x: (int(x["goalpost_shift_score"]), int(x["claim_occurrences"])), reverse=True)

    with OUT_AUDIT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "theme3_id", "theme_label", "target_mode", "claim_type_mode", "first_date", "last_date",
                "c2_clusters_merged", "claim_occurrences", "distinct_horizon_values", "horizon_shift_detected",
                "horizon_shift_type", "certainty_shift", "goalpost_shift_score", "goalpost_shift_flag",
                "cluster2_ids", "representative_quote",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    flagged = [r for r in rows if r["goalpost_shift_flag"] == "yes"]
    with OUT_SUMMARY.open("w", encoding="utf-8") as f:
        f.write("# Goalpost Shift Summary\n\n")
        f.write(f"Themes audited: {len(rows)}\n")
        f.write(f"Flagged as potential goalpost shift: {len(flagged)}\n\n")
        f.write("Top flagged themes:\n")
        for r in flagged[:25]:
            f.write(
                f"- {r['theme3_id']} | {r['theme_label']} | score={r['goalpost_shift_score']} | "
                f"target={r['target_mode']} | type={r['claim_type_mode']} | span={r['first_date']}..{r['last_date']} | "
                f"shift={r['horizon_shift_type']} | certainty={r['certainty_shift']}\n"
            )

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Themes audited: {len(rows)}")
    print(f"Flagged: {len(flagged)}")


if __name__ == "__main__":
    main()
