#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # .../marcus_scrape
CHATGPT_MASTER = ROOT / "outputs" / "chatgpt" / "tables" / "chatgpt_claims_master.csv"
CLAUDE_CROSSWALK = ROOT / "claude" / "claude_crosswalk_label_to_cluster.csv"
CLAUDE_CANON = ROOT / "claude" / "claude_claims_canonical.csv"
CLAUDE_FINAL = ROOT / "claude" / "claude_claims_final.jsonl"

OUT_BRIDGE = ROOT / "outputs" / "chatgpt" / "tables" / "chatgpt_hybrid_claim_bridge.csv"
OUT_RECON = ROOT / "outputs" / "chatgpt" / "tables" / "chatgpt_hybrid_reconciliation.csv"
OUT_DOC = ROOT / "outputs" / "chatgpt" / "docs" / "chatgpt_HYBRID_RECONCILIATION.md"

CONF_SCORE = {"high": 3, "medium": 2, "low": 1}


def parse_date(s: str) -> date | None:
    try:
        y, m, d = s.split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        return None


def overlap_days(a0: date | None, a1: date | None, b0: date | None, b1: date | None) -> int:
    if not all([a0, a1, b0, b1]):
        return 0
    lo = max(a0, b0)
    hi = min(a1, b1)
    return max(0, (hi - lo).days + 1)


@dataclass
class ClaudeCluster:
    cluster_id: str
    claim_count: int
    date_first: date | None
    date_last: date | None
    pct_supported: float
    pct_mixed: float
    pct_contradicted: float
    pct_untestable: float
    pct_pending: float


# heuristic target affinity for cluster IDs
CLUSTER_TARGET_HINTS = {
    "openai": {"openai"},
    "altman": {"openai"},
    "gpt": {"llms", "openai"},
    "llm": {"llms", "general_ai"},
    "agi": {"agi", "general_ai"},
    "scaling": {"llms", "agi", "general_ai"},
    "regulation": {"regulation", "general_ai"},
    "self_regulation": {"regulation", "general_ai"},
    "copyright": {"general_ai", "llms"},
    "deepfakes": {"ai_safety", "general_ai"},
    "musk": {"tesla", "general_ai"},
    "driverless": {"tesla"},
    "tesla": {"tesla"},
    "agents": {"llms", "general_ai"},
    "benchmark": {"llms", "general_ai"},
    "hallucination": {"llms", "ai_safety"},
}


def cluster_target_match(cluster_id: str, target_mode: str) -> int:
    low = cluster_id.lower()
    matches = set()
    for key, tgts in CLUSTER_TARGET_HINTS.items():
        if key in low:
            matches |= tgts
    return 1 if target_mode in matches else 0


def load_claude_clusters() -> dict[str, ClaudeCluster]:
    out = {}
    with CLAUDE_CANON.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for x in r:
            out[x["cluster_id"]] = ClaudeCluster(
                cluster_id=x["cluster_id"],
                claim_count=int(x["claim_count"]),
                date_first=parse_date(x["date_first"]),
                date_last=parse_date(x["date_last"]),
                pct_supported=float(x["pct_supported"]),
                pct_mixed=float(x["pct_mixed"]),
                pct_contradicted=float(x["pct_contradicted"]),
                pct_untestable=float(x["pct_untestable"]),
                pct_pending=float(x["pct_pending"]),
            )
    return out


def load_claude_claims_by_cluster() -> dict[str, list[dict]]:
    out = defaultdict(list)
    with CLAUDE_FINAL.open(encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            j = json.loads(ln)
            out[j.get("cluster_id", "")].append(j)
    return out


def choose_candidate(theme_row: dict, candidates: list[dict], cl_map: dict[str, ClaudeCluster], shared_clusters: set[str]):
    t0 = parse_date(theme_row["first_date"])
    t1 = parse_date(theme_row["last_date"])
    target = theme_row["target_mode"]

    scored = []
    for c in candidates:
        cid = c["claude_cluster_id"]
        conf = c["match_confidence"].lower()
        base = CONF_SCORE.get(conf, 0)
        cc = cl_map.get(cid)
        ov = overlap_days(t0, t1, cc.date_first if cc else None, cc.date_last if cc else None)
        ov_bonus = 1 if ov > 0 else 0
        t_bonus = cluster_target_match(cid, target)
        score = base * 10 + t_bonus * 3 + ov_bonus
        scored.append((score, base, t_bonus, ov_bonus, ov, cid, conf, c["match_rationale"]))

    scored.sort(reverse=True)
    best = scored[0] if scored else None

    bridge_conf = "none"
    map_status = "mapped"
    manual_review = "no"
    if not best:
        map_status = "unmapped_no_candidate"
        manual_review = "yes"
    else:
        _, base, t_bonus, _, _, cid, conf, _ = best
        if conf == "low":
            bridge_conf = "low"
            map_status = "mapped_low_conf"
            manual_review = "yes"
        elif conf == "medium":
            # precision-first requires target compatibility OR date overlap support
            if t_bonus == 0:
                bridge_conf = "low"
                map_status = "mapped_medium_weak_target"
                manual_review = "yes"
            else:
                bridge_conf = "medium"
        else:
            bridge_conf = "high"

        if cid in shared_clusters:
            manual_review = "yes"

    return scored, best, map_status, bridge_conf, manual_review


def aggregate_claude_for_theme(cluster_id: str | None, t0: date | None, t1: date | None, claims_by_cluster: dict[str, list[dict]]):
    if not cluster_id:
        return None
    rows = claims_by_cluster.get(cluster_id, [])
    if not rows:
        return None

    filt = []
    for r in rows:
        d = parse_date(r.get("claim_date", ""))
        if t0 and t1 and d and t0 <= d <= t1:
            filt.append(r)
    use = filt if filt else rows

    c = Counter(r.get("status_at_eval", "unknown") for r in use)
    n = len(use)
    if n == 0:
        return None

    pct = {k: (c.get(k, 0) * 100.0 / n) for k in ["supported", "contradicted", "mixed", "pending", "untestable"]}

    # claude primary directional status
    directional = {"supported": pct["supported"], "contradicted": pct["contradicted"], "mixed": pct["mixed"]}
    claude_primary = sorted(directional.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    return {
        "n": n,
        "pct": pct,
        "primary": claude_primary,
    }


def hybrid_status(chatgpt_status: str, p: dict[str, float] | None):
    if p is None:
        return "no_bridge"

    sup = p["supported"]
    con = p["contradicted"]

    if chatgpt_status == "contradicted" and con >= 10:
        return "contradicted"
    if chatgpt_status == "supported" and sup >= 40:
        return "supported"
    if chatgpt_status == "unresolved" and sup >= 50 and con < 10:
        return "lean_supported"
    if chatgpt_status == "unresolved" and con >= 15 and sup < 30:
        return "lean_contradicted"
    return "mixed_or_unresolved"


def agreement_band(chatgpt_status: str, claude_primary: str | None, hstatus: str):
    if claude_primary is None:
        return "low"
    if chatgpt_status in {"supported", "contradicted", "mixed"} and chatgpt_status == claude_primary:
        return "high"
    if (chatgpt_status == "supported" and claude_primary == "contradicted") or (
        chatgpt_status == "contradicted" and claude_primary == "supported"
    ):
        return "low"
    if chatgpt_status in {"unresolved", "untestable"} and hstatus in {
        "lean_supported",
        "lean_contradicted",
        "mixed_or_unresolved",
    }:
        return "medium"
    return "medium"


def main():
    master = list(csv.DictReader(CHATGPT_MASTER.open(encoding="utf-8")))
    cl_map = load_claude_clusters()
    claims_by_cluster = load_claude_claims_by_cluster()

    cross = list(csv.DictReader(CLAUDE_CROSSWALK.open(encoding="utf-8")))
    by_label = defaultdict(list)
    cluster_label_count = Counter()
    for r in cross:
        lbl = r["chatgpt_theme_label"]
        by_label[lbl].append(r)
        cluster_label_count[r["claude_cluster_id"]] += 1
    shared_clusters = {cid for cid, n in cluster_label_count.items() if n > 1}

    bridge_rows = []
    recon_rows = []

    for t in master:
        tid = t["theme3_id"]
        label = t["theme_label"]
        target = t["target_mode"]
        t0 = parse_date(t["first_date"])
        t1 = parse_date(t["last_date"])

        candidates = by_label.get(label, [])
        scored, best, map_status, bridge_conf, manual_review = choose_candidate(t, candidates, cl_map, shared_clusters)

        if best:
            _, _, _, _, ov_days, cid, conf, rationale = best
        else:
            cid, conf, rationale, ov_days = "", "", "", 0

        agg = aggregate_claude_for_theme(cid if cid else None, t0, t1, claims_by_cluster)

        claude_sup = agg["pct"]["supported"] if agg else 0.0
        claude_con = agg["pct"]["contradicted"] if agg else 0.0
        claude_mix = agg["pct"]["mixed"] if agg else 0.0
        claude_pen = agg["pct"]["pending"] if agg else 0.0
        claude_unt = agg["pct"]["untestable"] if agg else 0.0
        claude_n = agg["n"] if agg else 0
        claude_primary = agg["primary"] if agg else None

        hstat = hybrid_status(t["status_at_eval"], agg["pct"] if agg else None)
        band = agreement_band(t["status_at_eval"], claude_primary, hstat)

        bridge_rows.append(
            {
                "theme3_id": tid,
                "theme_label": label,
                "target_mode": target,
                "chatgpt_status_at_eval": t["status_at_eval"],
                "chatgpt_confidence": t["confidence"],
                "selected_claude_cluster_id": cid,
                "selected_match_confidence": conf,
                "bridge_confidence": bridge_conf,
                "mapping_status": map_status,
                "manual_review": manual_review,
                "date_overlap_days": ov_days,
                "selected_match_rationale": rationale,
                "candidate_count": len(candidates),
                "candidate_clusters": ";".join(sorted({c['claude_cluster_id'] for c in candidates})),
            }
        )

        recon_rows.append(
            {
                "theme3_id": tid,
                "theme_label": label,
                "target_mode": target,
                "claim_type_mode": t["claim_type_mode"],
                "chatgpt_status_at_eval": t["status_at_eval"],
                "chatgpt_confidence": t["confidence"],
                "selected_claude_cluster_id": cid,
                "bridge_confidence": bridge_conf,
                "mapping_status": map_status,
                "manual_review": manual_review,
                "claude_claims_in_window": claude_n,
                "claude_supported_pct": f"{claude_sup:.1f}",
                "claude_contradicted_pct": f"{claude_con:.1f}",
                "claude_mixed_pct": f"{claude_mix:.1f}",
                "claude_pending_pct": f"{claude_pen:.1f}",
                "claude_untestable_pct": f"{claude_unt:.1f}",
                "claude_primary_status": claude_primary or "none",
                "hybrid_status": hstat,
                "agreement_band": band,
                "goalpost_shift_flag": t["goalpost_shift_flag"],
                "goalpost_shift_score": t["goalpost_shift_score"],
                "first_date": t["first_date"],
                "last_date": t["last_date"],
                "claim_occurrences": t["claim_occurrences"],
            }
        )

    bridge_rows.sort(key=lambda r: (r["mapping_status"], r["theme_label"], r["theme3_id"]))
    recon_rows.sort(key=lambda r: (r["hybrid_status"], r["theme_label"], r["theme3_id"]))

    with OUT_BRIDGE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(bridge_rows[0].keys()))
        w.writeheader()
        w.writerows(bridge_rows)

    with OUT_RECON.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(recon_rows[0].keys()))
        w.writeheader()
        w.writerows(recon_rows)

    # summary doc
    c_map = Counter(r["mapping_status"] for r in bridge_rows)
    c_hyb = Counter(r["hybrid_status"] for r in recon_rows)
    c_band = Counter(r["agreement_band"] for r in recon_rows)
    c_conf = Counter(r["bridge_confidence"] for r in bridge_rows)
    manual = sum(1 for r in bridge_rows if r["manual_review"] == "yes")

    with OUT_DOC.open("w", encoding="utf-8") as f:
        f.write("# Hybrid Reconciliation\n\n")
        f.write("## Logic\n")
        f.write("- Direction: ChatGPT theme3 -> Claude cluster (many-to-one).\n")
        f.write("- Mapping priority: crosswalk confidence + target compatibility + date overlap (precision-first).\n")
        f.write("- Low-confidence mappings are retained but marked `manual_review=yes`.\n")
        f.write("- Orphan/unmapped themes are not force-fit.\n")
        f.write("- Claude verdict aggregation uses claim-level statuses from `claude_claims_final.jsonl` filtered to theme date window when possible.\n")
        f.write("- Hybrid status thresholds follow Claude-proposed rules.\n\n")

        f.write("## Mapping Summary\n")
        f.write(f"- themes processed: {len(bridge_rows)}\n")
        for k, v in c_map.items():
            f.write(f"- {k}: {v}\n")
        f.write("- bridge_confidence: " + ", ".join(f"{k}:{v}" for k, v in c_conf.items()) + "\n")
        f.write(f"- manual_review rows: {manual}\n\n")

        f.write("## Hybrid Status Summary\n")
        for k, v in c_hyb.items():
            f.write(f"- {k}: {v}\n")
        f.write("- agreement_band: " + ", ".join(f"{k}:{v}" for k, v in c_band.items()) + "\n\n")

        f.write("## Caveats\n")
        f.write("- Crosswalk granularity mismatch remains: 164 theme3 rows vs 54 Claude clusters.\n")
        f.write("- Shared Claude clusters across multiple labels require target-based disambiguation; marked for manual review.\n")
        f.write("- `copyright_ip` and `self_driving_robotics` mappings are weaker and should be audited first.\n")
        f.write("- Percent-based comparison is preferred over raw counts due to extraction density asymmetry.\n")

    print(f"wrote {OUT_BRIDGE}")
    print(f"wrote {OUT_RECON}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
