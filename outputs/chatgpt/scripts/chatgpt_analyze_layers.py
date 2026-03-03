#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
MASTER = ROOT / "final_tables" / "claims_master.csv"
THEME_MEMBERS = ROOT / "third_pass_theme_members.csv"
C2 = ROOT / "second_pass_clustered_claims.csv"

OUT_META = ROOT / "META_NARRATIVE.md"
OUT_META_CSV = ROOT / "meta_narrative_table.csv"
OUT_DRIFT = ROOT / "CLAIM_DRIFT_LEDGER.csv"
OUT_DRIFT_NOTES = ROOT / "DRIFT_NOTES.md"

HEDGE_RE = re.compile(r"\b(may|might|could|possibly|perhaps|guess|not sure|i don't know|i do not know|suspect)\b", re.I)
STRONG_RE = re.compile(r"\b(will|won't|cannot|can't|never|must|always)\b", re.I)
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP = {
    "the","a","an","and","or","of","to","in","on","for","with","as","by","at","from","that","this","it",
    "is","are","was","were","be","been","being","i","we","you","they","he","she","them","our","my","your",
    "will","would","could","should","can","cannot","cant","wont","not","very","more","most","much","many",
    "about","into","over","under","than","then","there","their","its","if","but","so","do","does","did",
    "have","has","had","also","just","really","still","now","yet","one","two","three","new","old","current"
}

PILLAR_MAP = {
    "hallucination_misinformation": "capability_limits",
    "reasoning_common_sense": "capability_limits",
    "scaling_limits": "capability_limits",
    "agents_reliability": "capability_limits",
    "agi_timeline": "agi_trajectory",
    "safety_alignment": "safety_governance",
    "regulation_policy": "safety_governance",
    "openai_governance": "safety_governance",
    "copyright_ip": "safety_governance",
    "market_hype_bubble": "market_cycle",
    "self_driving_robotics": "deployment_case_studies",
}


def tokens(s: str) -> set[str]:
    t = [x for x in TOKEN_RE.findall(s.lower()) if len(x) >= 3 and x not in STOP]
    return set(t)


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def certainty_level(txt: str) -> str:
    h = len(HEDGE_RE.findall(txt))
    s = len(STRONG_RE.findall(txt))
    if s - h >= 2:
        return "high_assertion"
    if h - s >= 2:
        return "hedged"
    return "balanced"


def horizon_rank(h: str) -> tuple[int, int]:
    vals = [x for x in h.split(';') if x]
    if not vals:
        return (0, 0)
    years = []
    rank = 1
    for v in vals:
        if v.startswith("within_lifetime"):
            rank = max(rank, 2)
        elif v.startswith("within_10_years") or v.startswith("this_decade") or v.startswith("near_term"):
            rank = max(rank, 3)
        m = re.search(r"(20\d{2})", v)
        if m:
            years.append(int(m.group(1)))
            rank = max(rank, 4)
    year = max(years) if years else 0
    return (rank, year)


def load_master():
    return list(csv.DictReader(open(MASTER, encoding="utf-8")))


def load_members():
    return list(csv.DictReader(open(THEME_MEMBERS, encoding="utf-8")))


def load_c2_map():
    return {r["cluster2_id"]: r for r in csv.DictReader(open(C2, encoding="utf-8"))}


def build_meta(master_rows: list[dict]):
    by_year_pillar = defaultdict(lambda: Counter())
    by_pillar_status = defaultdict(lambda: Counter())
    by_pillar_occ = Counter()

    for r in master_rows:
        year = int(r["first_date"][:4])
        pillar = PILLAR_MAP.get(r["theme_label"], "other")
        occ = int(r["claim_occurrences"])
        by_year_pillar[year][pillar] += occ
        by_pillar_status[pillar][r["status_at_eval"]] += 1
        by_pillar_occ[pillar] += occ

    years = sorted(by_year_pillar)
    pillars = sorted({p for y in years for p in by_year_pillar[y]})

    with open(OUT_META_CSV, "w", newline="", encoding="utf-8") as f:
        cols = ["year"] + pillars
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for y in years:
            row = {"year": y}
            for p in pillars:
                row[p] = by_year_pillar[y].get(p, 0)
            w.writerow(row)

    top_pillars = [p for p, _ in by_pillar_occ.most_common()]

    with open(OUT_META, "w", encoding="utf-8") as f:
        f.write("# Meta Narrative\n\n")
        f.write("## Logic\n")
        f.write("- Unit analyzed: Theme3 rows from `final_tables/claims_master.csv`.\n")
        f.write("- Weighting: `claim_occurrences` per theme.\n")
        f.write("- Year assignment: theme `first_date` year.\n")
        f.write("- Abstraction: theme labels mapped to meta pillars (capability limits, AGI trajectory, safety/governance, market cycle, deployment case studies).\n")
        f.write("- Status view: counts of theme-level `status_at_eval` by pillar.\n\n")

        f.write("## Narrative Arc\n")
        if years:
            for y in years:
                c = by_year_pillar[y]
                top = ", ".join(f"{k}:{v}" for k, v in c.most_common(3))
                f.write(f"- {y}: dominant pillars -> {top}\n")
        f.write("\n")

        f.write("## Pillar Summary\n")
        for p in top_pillars:
            st = by_pillar_status[p]
            f.write(f"- {p}: occurrences={by_pillar_occ[p]}, themes={sum(st.values())}, supported={st.get('supported',0)}, contradicted={st.get('contradicted',0)}, mixed={st.get('mixed',0)}, unresolved={st.get('unresolved',0)}, untestable={st.get('untestable',0)}\n")

        f.write("\n## Interpretation\n")
        f.write("- The dominant macro story is persistent capability skepticism (reasoning/hallucination/scaling limits) plus sustained governance/safety focus.\n")
        f.write("- AGI timeline discussion remains high-volume but mostly unresolved at current evaluation date.\n")
        f.write("- Market-cycle claims exist but are secondary relative to technical/safety narratives.\n")


def build_drift(master_rows: list[dict], member_rows: list[dict], c2_map: dict[str, dict]):
    theme_meta = {r["theme3_id"]: r for r in master_rows}
    by_theme = defaultdict(list)
    for m in member_rows:
        tid = m["theme3_id"]
        if tid in theme_meta:
            by_theme[tid].append(m)

    ledger = []
    theme_drift_scores = []

    for tid, members in by_theme.items():
        members = sorted(members, key=lambda x: (x["first_date"], x["cluster2_id"]))
        if len(members) < 2:
            continue
        tmeta = theme_meta[tid]
        local_scores = []

        for i in range(1, len(members)):
            a = members[i - 1]
            b = members[i]
            ca = c2_map.get(a["cluster2_id"], {})
            cb = c2_map.get(b["cluster2_id"], {})

            ah = ca.get("horizon_values", "")
            bh = cb.get("horizon_values", "")
            ar, ay = horizon_rank(ah)
            br, by = horizon_rank(bh)

            if br > ar:
                hshift = "more_specific"
            elif br < ar:
                hshift = "less_specific"
            elif ay and by and by > ay:
                hshift = "deadline_pushed_out"
            elif ay and by and by < ay:
                hshift = "deadline_pulled_in"
            elif ah != bh:
                hshift = "changed"
            else:
                hshift = "stable"

            ac = certainty_level(a["representative_quote"])
            bc = certainty_level(b["representative_quote"])
            if ac == bc:
                cshift = "stable"
            elif ac == "hedged" and bc != "hedged":
                cshift = "hardened"
            elif ac != "hedged" and bc == "hedged":
                cshift = "softened"
            else:
                cshift = "changed"

            lex = 1.0 - jaccard(tokens(a["representative_quote"]), tokens(b["representative_quote"]))
            score = 0
            if hshift in {"less_specific", "deadline_pushed_out", "changed"}:
                score += 1
            if cshift == "softened":
                score += 1
            if lex > 0.65:
                score += 1
            local_scores.append(score)

            ledger.append(
                {
                    "theme3_id": tid,
                    "theme_label": tmeta["theme_label"],
                    "step_index": i,
                    "from_cluster2_id": a["cluster2_id"],
                    "to_cluster2_id": b["cluster2_id"],
                    "from_date": a["first_date"],
                    "to_date": b["first_date"],
                    "from_horizon_values": ah,
                    "to_horizon_values": bh,
                    "horizon_drift": hshift,
                    "from_certainty": ac,
                    "to_certainty": bc,
                    "certainty_drift": cshift,
                    "lexical_drift": f"{lex:.3f}",
                    "drift_score": score,
                    "from_quote": a["representative_quote"],
                    "to_quote": b["representative_quote"],
                }
            )

        if local_scores:
            theme_drift_scores.append((tid, tmeta["theme_label"], len(members), sum(local_scores) / len(local_scores)))

    ledger.sort(key=lambda r: (r["theme3_id"], int(r["step_index"])))
    with open(OUT_DRIFT, "w", newline="", encoding="utf-8") as f:
        cols = list(ledger[0].keys()) if ledger else [
            "theme3_id","theme_label","step_index","from_cluster2_id","to_cluster2_id","from_date","to_date",
            "from_horizon_values","to_horizon_values","horizon_drift","from_certainty","to_certainty",
            "certainty_drift","lexical_drift","drift_score","from_quote","to_quote"
        ]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        if ledger:
            w.writerows(ledger)

    top = sorted(theme_drift_scores, key=lambda x: x[3], reverse=True)[:25]
    ctr_h = Counter(r["horizon_drift"] for r in ledger)
    ctr_c = Counter(r["certainty_drift"] for r in ledger)

    with open(OUT_DRIFT_NOTES, "w", encoding="utf-8") as f:
        f.write("# Drift Notes\n\n")
        f.write("## Logic\n")
        f.write("- Unit analyzed: sequential cluster2 members within each Theme3.\n")
        f.write("- Horizon drift compares `horizon_values` specificity and timeline direction.\n")
        f.write("- Certainty drift compares hedge vs strong-assertion wording in representative quotes.\n")
        f.write("- Lexical drift = 1 - Jaccard(token overlap) between consecutive quotes.\n")
        f.write("- Drift score per step: +1 horizon loosen/push/change, +1 softened certainty, +1 high lexical drift (>0.65).\n\n")

        f.write("## Aggregate Drift Signals\n")
        f.write(f"- total transitions: {len(ledger)}\n")
        f.write("- horizon drift counts: " + ", ".join(f"{k}:{v}" for k, v in ctr_h.most_common()) + "\n")
        f.write("- certainty drift counts: " + ", ".join(f"{k}:{v}" for k, v in ctr_c.most_common()) + "\n\n")

        f.write("## Highest-Drift Themes\n")
        for tid, lbl, n, s in top:
            f.write(f"- {tid} | {lbl} | clusters={n} | avg_step_drift={s:.2f}\n")

        f.write("\n## How To Use\n")
        f.write("- Start with rows where `drift_score >= 2` in `CLAIM_DRIFT_LEDGER.csv`.\n")
        f.write("- Manually inspect the `from_quote` -> `to_quote` transitions for genuine goalpost movement vs topic branching.\n")


def main():
    master = load_master()
    members = load_members()
    c2_map = load_c2_map()
    build_meta(master)
    build_drift(master, members, c2_map)
    print("wrote", OUT_META)
    print("wrote", OUT_META_CSV)
    print("wrote", OUT_DRIFT)
    print("wrote", OUT_DRIFT_NOTES)


if __name__ == "__main__":
    main()
