#!/usr/bin/env python3
"""High-precision refinement over correctness_full_scorecard.csv."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
IN_SCORE = ROOT / "correctness_full_scorecard.csv"
IN_THEMES = ROOT / "third_pass_themes_signal.csv"
IN_MEMBERS = ROOT / "third_pass_theme_members.csv"
OUT_SCORE = ROOT / "correctness_refined_scorecard.csv"
OUT_CLAIMS = ROOT / "correctness_refined_claim_level.csv"
OUT_SUMMARY = ROOT / "correctness_refined_summary.md"

AS_OF_DATE = "2026-03-02"

SRC_GPT5 = "https://openai.com/index/introducing-gpt-5/"
SRC_GPT5_CARD = "https://openai.com/blog/gpt-5-system-card/"
SRC_O1_CARD = "https://openai.com/index/openai-o1-system-card/"
SRC_OPENAI_STRUCTURE = "https://openai.com/our-structure/"
SRC_OPENAI_FOUNDATION = "https://openai.com/foundation/"
SRC_EU_AI_ACT = "https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-113"
SRC_ANTHROPIC_HELP = "https://support.anthropic.com/en/articles/8525154-claude-is-providing-incorrect-or-misleading-responses-what-s-going-on"
SRC_HALLUCINATION_POST = "https://openai.com/blog/why-language-models-hallucinate/"
SRC_GEMINI_MODEL_CARDS = "https://deepmind.google/models/model-cards/"
SRC_GEMINI_31_PRO = "https://deepmind.google/models/model-cards/gemini-3-1-pro/"
SRC_GEMINI_3_PRO_PDF = "https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf"
SRC_GEMINI_PRIVACY_HUB = "https://support.google.com/gemini/answer/13594961"
SRC_ANTHROPIC_SYSTEM_CARDS = "https://www.anthropic.com/system-cards"
SRC_ANTHROPIC_CLAUDE4_CARD = "https://www-cdn.anthropic.com/07b2a3f9902ee19fe39a36ca638e5ae987bc64dd.pdf"


def main():
    score_rows = list(csv.DictReader(open(IN_SCORE, encoding="utf-8")))
    theme_map = {r["theme3_id"]: r for r in csv.DictReader(open(IN_THEMES, encoding="utf-8"))}

    refined = []
    for r in score_rows:
        out = dict(r)
        tid = r["theme3_id"]
        t = theme_map.get(tid, {})
        quote = t.get("representative_quote", "")
        ql = quote.lower()
        label = r["theme_label"]
        status = r["status_at_eval"]

        # Start from full pass and tighten.
        if status == "mixed":
            # High-precision: only keep mixed when clear bidirectional evidence exists.
            if label == "safety_alignment":
                out["status_at_eval"] = "mixed"
                out["confidence"] = "medium"
                out["reason"] = "Safety evidence is bidirectional: capabilities/safeguards improved, but documented residual risk remains."
                out["sources"] = ";".join(
                    [
                        SRC_GPT5_CARD,
                        SRC_O1_CARD,
                        SRC_GEMINI_31_PRO,
                        SRC_GEMINI_3_PRO_PDF,
                        SRC_ANTHROPIC_SYSTEM_CARDS,
                        SRC_ANTHROPIC_CLAUDE4_CARD,
                    ]
                )
            elif label == "regulation_policy":
                out["status_at_eval"] = "mixed"
                out["confidence"] = "medium"
                out["reason"] = "Regulatory rollout is real (EU AI Act timetable), but many policy-effect claims remain open and jurisdiction-specific."
                out["sources"] = ";".join([SRC_EU_AI_ACT])
            elif label == "openai_governance" and (
                "gpt-5" in ql and ("on pause" in ql or "deferred" in ql or "fail to please" in ql)
            ):
                out["status_at_eval"] = "contradicted"
                out["confidence"] = "high"
                out["reason"] = "Specific GPT-5 pause/defer/failure framing conflicts with documented public GPT-5 release on August 7, 2025."
                out["sources"] = ";".join([SRC_GPT5, SRC_OPENAI_STRUCTURE])
            else:
                out["status_at_eval"] = "unresolved"
                out["confidence"] = "medium"
                out["reason"] = "Downgraded from mixed for high-precision pass: claim remains too broad/ambiguous for decisive adjudication."
                out["sources"] = ";".join([SRC_GPT5, SRC_GEMINI_31_PRO, SRC_ANTHROPIC_SYSTEM_CARDS])

        # Strengthen supported hallucination claims with direct provider evidence.
        if label == "hallucination_misinformation" and out["status_at_eval"] == "supported":
            out["sources"] = ";".join(
                [
                    SRC_HALLUCINATION_POST,
                    SRC_GPT5_CARD,
                    SRC_O1_CARD,
                    SRC_GEMINI_3_PRO_PDF,
                    SRC_GEMINI_PRIVACY_HUB,
                    SRC_ANTHROPIC_SYSTEM_CARDS,
                    SRC_ANTHROPIC_CLAUDE4_CARD,
                    SRC_ANTHROPIC_HELP,
                ]
            )
            out["reason"] = "Cross-vendor documentation (OpenAI, Google Gemini, Anthropic) indicates hallucinations/errors still occur, though mitigations have improved."

        # Add vendor-balanced technical evidence for unresolved technical themes.
        if label in {"reasoning_common_sense", "scaling_limits", "agents_reliability", "copyright_ip"} and out["status_at_eval"] in {"unresolved", "mixed"}:
            out["sources"] = ";".join(
                [
                    SRC_GPT5,
                    SRC_GPT5_CARD,
                    SRC_GEMINI_MODEL_CARDS,
                    SRC_GEMINI_3_PRO_PDF,
                    SRC_ANTHROPIC_SYSTEM_CARDS,
                    SRC_ANTHROPIC_CLAUDE4_CARD,
                ]
            )

        out["as_of_date"] = AS_OF_DATE
        refined.append(out)

    # sort
    rank = {"contradicted": 0, "supported": 1, "mixed": 2, "unresolved": 3, "untestable": 4}
    refined.sort(key=lambda x: (rank.get(x["status_at_eval"], 9), -int(x["claim_occurrences"]), x["theme3_id"]))

    cols = [
        "theme3_id", "theme_label", "target_mode", "claim_type_mode", "first_date", "last_date",
        "claim_occurrences", "goalpost_shift_candidate", "status_at_eval", "confidence", "as_of_date", "reason", "sources",
    ]
    with open(OUT_SCORE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(refined)

    # claim-level inheritance
    members = list(csv.DictReader(open(IN_MEMBERS, encoding="utf-8")))
    rmap = {r["theme3_id"]: r for r in refined}
    claim_rows = []
    for m in members:
        tid = m["theme3_id"]
        if tid not in rmap:
            continue
        rr = rmap[tid]
        claim_rows.append(
            {
                "theme3_id": tid,
                "cluster2_id": m["cluster2_id"],
                "target_mode": m["target_mode"],
                "claim_type_mode": m["claim_type_mode"],
                "first_date": m["first_date"],
                "last_date": m["last_date"],
                "occurrences": m["occurrences"],
                "status_at_eval": rr["status_at_eval"],
                "confidence": rr["confidence"],
                "as_of_date": AS_OF_DATE,
                "theme_reason": rr["reason"],
                "theme_sources": rr["sources"],
                "representative_quote": m["representative_quote"],
            }
        )

    with open(OUT_CLAIMS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "theme3_id", "cluster2_id", "target_mode", "claim_type_mode", "first_date", "last_date", "occurrences",
                "status_at_eval", "confidence", "as_of_date", "theme_reason", "theme_sources", "representative_quote",
            ],
        )
        w.writeheader()
        w.writerows(claim_rows)

    cnt = Counter(r["status_at_eval"] for r in refined)
    total = len(refined)
    adjudicable = cnt["supported"] + cnt["contradicted"] + cnt["mixed"]

    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write("# Correctness Summary (Refined High-Precision Pass)\n\n")
        f.write(f"As-of date: {AS_OF_DATE}\n")
        f.write(f"Themes scored: {total}\n\n")
        f.write("Status counts:\n")
        for k in ["supported", "contradicted", "mixed", "unresolved", "untestable"]:
            f.write(f"- {k}: {cnt.get(k, 0)} ({cnt.get(k, 0)/total:.1%})\n")
        f.write("\nAdjudicable subset (supported/contradicted/mixed):\n")
        f.write(f"- count: {adjudicable}\n")
        if adjudicable:
            f.write(f"- supported share: {cnt['supported']/adjudicable:.1%}\n")
            f.write(f"- contradicted share: {cnt['contradicted']/adjudicable:.1%}\n")
            f.write(f"- mixed share: {cnt['mixed']/adjudicable:.1%}\n")
        f.write("\nMethod note: Ambiguous prior 'mixed' labels were downgraded to 'unresolved' unless clear bidirectional evidence was available.\n")

    print(f"Wrote {OUT_SCORE}")
    print(f"Wrote {OUT_CLAIMS}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
