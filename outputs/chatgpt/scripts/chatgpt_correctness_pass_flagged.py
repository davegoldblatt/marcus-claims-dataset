#!/usr/bin/env python3
"""Preliminary correctness adjudication for flagged goalpost themes.

Scope: 10 flagged themes only.
Outputs:
- correctness_scorecard.csv (theme-level)
- correctness_claim_level.csv (cluster2-level inherited from theme)
- correctness_summary.md
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
IN_AUDIT = ROOT / "goalpost_shift_audit.csv"
IN_MEMBERS = ROOT / "third_pass_theme_members.csv"
OUT_SCORECARD = ROOT / "correctness_scorecard.csv"
OUT_CLAIM_LEVEL = ROOT / "correctness_claim_level.csv"
OUT_SUMMARY = ROOT / "correctness_summary.md"

AS_OF_DATE = "2026-03-02"

# Status definitions used here:
# - supported: evidence aligns with claim
# - contradicted: evidence clearly conflicts
# - mixed: claim has partially supported and partially contradicted components
# - unresolved: insufficiently specific or deadline not reached
# - untestable: normative/value claim

ADJ = {
    "theme3_3c553598e33f": {
        "status": "mixed",
        "confidence": "medium",
        "reason": "AGI has not been declared achieved by frontier labs as of 2026-03-02 (supports skepticism), but capabilities advanced substantially with GPT-5, so broad anti-progress framing is not fully supported.",
        "sources": [
            "https://openai.com/index/introducing-gpt-5/",
            "https://openai.com/blog/gpt-5-system-card/",
        ],
    },
    "theme3_a708e869f9a5": {
        "status": "supported",
        "confidence": "high",
        "reason": "Frontier model documentation still reports non-zero hallucination/error rates and explicitly notes ongoing hallucination limitations.",
        "sources": [
            "https://openai.com/index/introducing-gpt-5/",
            "https://openai.com/index/openai-o1-system-card/",
            "https://support.anthropic.com/en/articles/8525154-claude-is-providing-incorrect-or-misleading-responses-what-s-going-on",
        ],
    },
    "theme3_03bbb277b41d": {
        "status": "unresolved",
        "confidence": "low",
        "reason": "Theme appears weakly aligned to copyright/IP and representative claims are broad methodological questions without clear measurable endpoints.",
        "sources": [
            "https://openai.com/index/introducing-gpt-5/",
        ],
    },
    "theme3_7d22014cb9c1": {
        "status": "mixed",
        "confidence": "medium",
        "reason": "GPT-5 was released (not deferred indefinitely) and OpenAI valuation remained high, which conflicts with strong near-term deflation scenarios; broader governance skepticism remains partly interpretive.",
        "sources": [
            "https://openai.com/index/introducing-gpt-5/",
            "https://openai.com/our-structure/",
            "https://openai.com/foundation/",
        ],
    },
    "theme3_4d4764672c3e": {
        "status": "untestable",
        "confidence": "high",
        "reason": "Normative claim about what is required for AGI (abstraction/compositionality) lacks agreed operational test and deadline.",
        "sources": [
            "https://openai.com/index/introducing-gpt-5/",
        ],
    },
    "theme3_0572199dc099": {
        "status": "untestable",
        "confidence": "high",
        "reason": "Normative/common-sense architecture prescription; valuable but not directly falsifiable as stated.",
        "sources": [
            "https://openai.com/index/introducing-gpt-5/",
        ],
    },
    "theme3_1229d1997f18": {
        "status": "unresolved",
        "confidence": "medium",
        "reason": "Claim concerns long-run valuation viability of pure LLM plays; as of 2026-03-02 evidence is inconclusive and horizon remains open.",
        "sources": [
            "https://openai.com/foundation/",
            "https://openai.com/our-structure/",
        ],
    },
    "theme3_c5056806d534": {
        "status": "unresolved",
        "confidence": "high",
        "reason": "Contains AGI-by-2029 style timeline references; deadline has not passed as of 2026-03-02.",
        "sources": [
            "https://openai.com/index/introducing-gpt-5/",
        ],
    },
    "theme3_e8ec12058b83": {
        "status": "unresolved",
        "confidence": "medium",
        "reason": "Broad skepticism about deep learning doing 'everything' remains open-ended without concrete endpoint/metric.",
        "sources": [
            "https://openai.com/index/introducing-gpt-5/",
            "https://openai.com/blog/gpt-5-system-card/",
        ],
    },
    "theme3_7e94375ad3bc": {
        "status": "mixed",
        "confidence": "low",
        "reason": "Guardrail/common-sense concerns persist, while formal regulation has advanced (e.g., EU AI Act timetable), yielding mixed directionality.",
        "sources": [
            "https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-113",
            "https://openai.com/index/introducing-gpt-5/",
        ],
    },
}


def main():
    flagged = [r for r in csv.DictReader(open(IN_AUDIT, encoding="utf-8")) if r["goalpost_shift_flag"] == "yes"]

    score_rows = []
    for r in flagged:
        tid = r["theme3_id"]
        a = ADJ.get(tid)
        if not a:
            continue
        score_rows.append(
            {
                "theme3_id": tid,
                "theme_label": r["theme_label"],
                "target_mode": r["target_mode"],
                "claim_type_mode": r["claim_type_mode"],
                "first_date": r["first_date"],
                "last_date": r["last_date"],
                "goalpost_shift_score": r["goalpost_shift_score"],
                "status_at_eval": a["status"],
                "confidence": a["confidence"],
                "as_of_date": AS_OF_DATE,
                "reason": a["reason"],
                "sources": ";".join(a["sources"]),
            }
        )

    score_rows.sort(key=lambda x: (x["status_at_eval"], x["theme3_id"]))

    with open(OUT_SCORECARD, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "theme3_id", "theme_label", "target_mode", "claim_type_mode", "first_date", "last_date",
                "goalpost_shift_score", "status_at_eval", "confidence", "as_of_date", "reason", "sources",
            ],
        )
        w.writeheader()
        w.writerows(score_rows)

    # claim-level inheritance from theme judgment (cluster2 level)
    member_rows = [r for r in csv.DictReader(open(IN_MEMBERS, encoding="utf-8")) if r["theme3_id"] in {x["theme3_id"] for x in score_rows}]
    theme_map = {r["theme3_id"]: r for r in score_rows}
    claim_out = []
    for m in member_rows:
        t = theme_map[m["theme3_id"]]
        claim_out.append(
            {
                "theme3_id": m["theme3_id"],
                "cluster2_id": m["cluster2_id"],
                "target_mode": m["target_mode"],
                "claim_type_mode": m["claim_type_mode"],
                "first_date": m["first_date"],
                "last_date": m["last_date"],
                "occurrences": m["occurrences"],
                "status_at_eval": t["status_at_eval"],
                "confidence": t["confidence"],
                "as_of_date": AS_OF_DATE,
                "theme_reason": t["reason"],
                "theme_sources": t["sources"],
                "representative_quote": m["representative_quote"],
            }
        )

    with open(OUT_CLAIM_LEVEL, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "theme3_id", "cluster2_id", "target_mode", "claim_type_mode", "first_date", "last_date", "occurrences",
                "status_at_eval", "confidence", "as_of_date", "theme_reason", "theme_sources", "representative_quote",
            ],
        )
        w.writeheader()
        w.writerows(claim_out)

    cnt = Counter(r["status_at_eval"] for r in score_rows)
    adjudicable = cnt["supported"] + cnt["contradicted"] + cnt["mixed"]
    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write("# Correctness Summary (Flagged Goalpost Themes)\n\n")
        f.write(f"As-of date: {AS_OF_DATE}\n")
        f.write(f"Themes scored: {len(score_rows)}\n")
        f.write("\nStatus counts:\n")
        for k in ["supported", "contradicted", "mixed", "unresolved", "untestable"]:
            f.write(f"- {k}: {cnt.get(k, 0)}\n")
        f.write("\nInterpretation:\n")
        if adjudicable:
            f.write(f"- Adjudicable subset (supported/contradicted/mixed): {adjudicable}\n")
            f.write(f"- Supported share in adjudicable subset: {cnt['supported'] / adjudicable:.1%}\n")
            f.write(f"- Contradicted share in adjudicable subset: {cnt['contradicted'] / adjudicable:.1%}\n")
            f.write(f"- Mixed share in adjudicable subset: {cnt['mixed'] / adjudicable:.1%}\n")
        else:
            f.write("- No claims met adjudicable threshold.\n")
        f.write("\nCaveat: this pass covers only the 10 goalpost-flagged themes, not the full corpus.\n")

    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_CLAIM_LEVEL}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
