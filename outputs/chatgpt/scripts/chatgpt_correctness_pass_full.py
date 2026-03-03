#!/usr/bin/env python3
"""Full correctness adjudication pass for signal themes.

Conservative rules: unresolved/untestable by default unless strong evidence pattern.
Outputs:
- correctness_full_scorecard.csv
- correctness_full_claim_level.csv
- correctness_full_summary.md
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
IN_THEMES = ROOT / "third_pass_themes_signal.csv"
IN_MEMBERS = ROOT / "third_pass_theme_members.csv"
OUT_SCORECARD = ROOT / "correctness_full_scorecard.csv"
OUT_CLAIMS = ROOT / "correctness_full_claim_level.csv"
OUT_SUMMARY = ROOT / "correctness_full_summary.md"

AS_OF_DATE = "2026-03-02"

SRC_GPT5 = "https://openai.com/index/introducing-gpt-5/"
SRC_GPT5_CARD = "https://openai.com/blog/gpt-5-system-card/"
SRC_O1_CARD = "https://openai.com/index/openai-o1-system-card/"
SRC_OPENAI_STRUCTURE = "https://openai.com/our-structure/"
SRC_OPENAI_FOUNDATION = "https://openai.com/foundation/"
SRC_EU_AI_ACT = "https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-113"
SRC_ANTHROPIC_HELP = "https://support.claude.com/en/articles/8525154-claude-is-providing-incorrect-or-misleading-responses-what-s-going-on"

YEAR_RE = re.compile(r"\b(20\d{2})\b")


def adjudicate(row: dict) -> tuple[str, str, str, list[str]]:
    label = row["theme_label"]
    ctype = row["claim_type_mode"]
    quote = row["representative_quote"].lower()
    horizons = [h for h in row["horizon_values"].split(";") if h]

    # Normative claims are primarily value/prescription statements.
    if ctype == "normative":
        return (
            "untestable",
            "high",
            "Normative/prescriptive theme without a clear falsification condition.",
            [SRC_GPT5],
        )

    # Strongly supportable: hallucinations remain a live limitation.
    if label == "hallucination_misinformation":
        return (
            "supported",
            "high",
            "Primary model docs and provider guidance continue to report hallucination risk and non-zero factual errors.",
            [SRC_GPT5, SRC_GPT5_CARD, SRC_O1_CARD, SRC_ANTHROPIC_HELP],
        )

    # OpenAI governance/structure claims: partially testable, usually mixed.
    if label == "openai_governance":
        if "deferred indefinitely" in quote or "gpt-5 did fail" in quote:
            return (
                "contradicted",
                "medium",
                "GPT-5 launched publicly; specific deferment/failure framing is contradicted by release evidence.",
                [SRC_GPT5, SRC_OPENAI_STRUCTURE],
            )
        return (
            "mixed",
            "medium",
            "Governance concerns are partly supported by ongoing structure changes; broader strategic claims remain partly interpretive.",
            [SRC_OPENAI_STRUCTURE, SRC_OPENAI_FOUNDATION],
        )

    # Regulation timeline claims often partially checkable.
    if label == "regulation_policy":
        return (
            "mixed",
            "medium",
            "Regulatory implementation has advanced (EU AI Act staged application), but broader policy adequacy claims remain open.",
            [SRC_EU_AI_ACT],
        )

    # Safety/alignment typically shows both progress and unresolved issues.
    if label == "safety_alignment":
        return (
            "mixed",
            "medium",
            "Safety docs show mitigation progress while also acknowledging continuing limitations and ongoing work.",
            [SRC_GPT5_CARD, SRC_O1_CARD],
        )

    # Timeline-sensitive claims: if deadline not reached -> unresolved.
    explicit_years = []
    for h in horizons:
        m = YEAR_RE.search(h)
        if m:
            explicit_years.append(int(m.group(1)))

    if label == "agi_timeline":
        if any(y > 2026 for y in explicit_years):
            return (
                "unresolved",
                "high",
                "Timeline horizon extends beyond evaluation date.",
                [SRC_GPT5],
            )
        if "deferred indefinitely" in quote or "gpt-5 did fail" in quote:
            return (
                "contradicted",
                "medium",
                "Specific GPT-5 deferment/failure expectation conflicts with observed public release.",
                [SRC_GPT5],
            )
        return (
            "mixed",
            "low",
            "No consensus AGI endpoint reached by as-of date, but broad timeline claims are heterogeneous and hard to falsify at theme level.",
            [SRC_GPT5],
        )

    if label in {"market_hype_bubble", "copyright_ip", "self_driving_robotics", "agents_reliability", "scaling_limits", "reasoning_common_sense"}:
        return (
            "unresolved",
            "medium",
            "Theme remains open-ended or lacks a closed measurement endpoint by the as-of date.",
            [SRC_GPT5],
        )

    # Conservative fallback.
    return (
        "unresolved",
        "low",
        "Insufficient specificity for high-confidence adjudication at theme level.",
        [SRC_GPT5],
    )


def main():
    themes = list(csv.DictReader(open(IN_THEMES, encoding="utf-8")))

    score_rows = []
    for t in themes:
        status, conf, reason, sources = adjudicate(t)
        score_rows.append(
            {
                "theme3_id": t["theme3_id"],
                "theme_label": t["theme_label"],
                "target_mode": t["target_mode"],
                "claim_type_mode": t["claim_type_mode"],
                "first_date": t["first_date"],
                "last_date": t["last_date"],
                "claim_occurrences": t["claim_occurrences"],
                "goalpost_shift_candidate": t["goalpost_shift_candidate"],
                "status_at_eval": status,
                "confidence": conf,
                "as_of_date": AS_OF_DATE,
                "reason": reason,
                "sources": ";".join(sources),
            }
        )

    # Prioritize rows by adjudicability then magnitude.
    status_rank = {"contradicted": 0, "supported": 1, "mixed": 2, "unresolved": 3, "untestable": 4}
    score_rows.sort(key=lambda r: (status_rank.get(r["status_at_eval"], 9), -int(r["claim_occurrences"]), r["theme3_id"]))

    with open(OUT_SCORECARD, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "theme3_id", "theme_label", "target_mode", "claim_type_mode", "first_date", "last_date",
                "claim_occurrences", "goalpost_shift_candidate", "status_at_eval", "confidence", "as_of_date", "reason", "sources",
            ],
        )
        w.writeheader()
        w.writerows(score_rows)

    # Claim-level inheritance from theme-level judgments (cluster2 rows).
    members = list(csv.DictReader(open(IN_MEMBERS, encoding="utf-8")))
    tmap = {r["theme3_id"]: r for r in score_rows}
    claim_rows = []
    for m in members:
        tid = m["theme3_id"]
        if tid not in tmap:
            continue
        t = tmap[tid]
        claim_rows.append(
            {
                "theme3_id": tid,
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

    cnt = Counter(r["status_at_eval"] for r in score_rows)
    adjudicable = cnt["supported"] + cnt["contradicted"] + cnt["mixed"]

    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write("# Correctness Summary (Full Signal Themes)\n\n")
        f.write(f"As-of date: {AS_OF_DATE}\n")
        f.write(f"Themes scored: {len(score_rows)}\n")
        f.write("\nStatus counts:\n")
        for k in ["supported", "contradicted", "mixed", "unresolved", "untestable"]:
            f.write(f"- {k}: {cnt.get(k, 0)}\n")

        f.write("\nPercent of all themes:\n")
        total = len(score_rows) if score_rows else 1
        for k in ["supported", "contradicted", "mixed", "unresolved", "untestable"]:
            f.write(f"- {k}: {cnt.get(k, 0)/total:.1%}\n")

        f.write("\nAdjudicable subset (supported/contradicted/mixed):\n")
        f.write(f"- count: {adjudicable}\n")
        if adjudicable:
            f.write(f"- supported share: {cnt['supported']/adjudicable:.1%}\n")
            f.write(f"- contradicted share: {cnt['contradicted']/adjudicable:.1%}\n")
            f.write(f"- mixed share: {cnt['mixed']/adjudicable:.1%}\n")

        f.write("\nPrimary evidence sources used:\n")
        for s in [
            SRC_GPT5,
            SRC_GPT5_CARD,
            SRC_O1_CARD,
            SRC_OPENAI_STRUCTURE,
            SRC_OPENAI_FOUNDATION,
            SRC_EU_AI_ACT,
            SRC_ANTHROPIC_HELP,
        ]:
            f.write(f"- {s}\n")

        f.write("\nCaveat: this is a conservative, theme-level adjudication. Claim-level manual review is still needed for high-stakes conclusions.\n")

    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_CLAIMS}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
