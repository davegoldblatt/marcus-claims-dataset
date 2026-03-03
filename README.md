# Marcus AI Claims Dataset

Gary Marcus is the most prolific AI skeptic on the internet. Since May 2022, he's published 474 posts on Substack making claims about AI's limitations, the companies building it, and where the industry is headed.

We extracted every testable claim. 2,218 of them. Scored each one against the evidence as of March 2, 2026. Here's what the data shows.

## He's more right than wrong

Among claims where the evidence is checkable:

* **59.9% supported**
* **33.7% mixed**
* **6.4% contradicted**

That's not the number most people expect from either side.

## But the interesting part is where

His best work is specific and technical. When Marcus points at a broken thing and says "that's broken," the evidence backs him up almost perfectly. LLM security vulnerabilities: 100% supported, 0% contradicted. Sora video unreliable: 90% supported, 0% contradicted. Agents premature for production: 88% supported, 0% contradicted. Across those three clusters, not a single claim was contradicted by the evidence.

His worst work is market prediction. "GenAI bubble will burst": 27% contradicted, his single worst cluster out of 54. He went from "potential AI winter" (2023) to "greatest capital destruction in history" (2025) to "the whole thing was a scam" (Feb 2026). The crash hasn't come.

He writes more about the thing he's getting wrong. His hallucination cluster (most vindicated thesis) spiked when he established it in early 2023, then settled into a steady drumbeat. His bubble cluster (most contradicted) went from near-zero in 2023 to his highest quarterly output in Q4 2025.

## How it was built

Two LLM pipelines analyzed the same corpus, then a reconciliation layer compared their outputs:

* **Claude Code (Opus 4.6)**: 2,218 individual claims, 54 clusters. Claim-level granularity, willing to render verdicts.
* **Codex (ChatGPT)**: 164 themes, 11 categories. Theme-level, conservative — defaults to "unresolved" unless clear cross-vendor evidence exists.

A hybrid reconciliation layer maps both into a unified view. Full methodology in `DATASET_GUIDE.md`.

## Start here

| File | What it gives you |
|------|-------------------|
| `DATASET_GUIDE.md` | Full methodology, decision rules, file inventory |
| `outputs/chatgpt/tables/chatgpt_hybrid_reconciliation.csv` | Canonical reconciled view — both pipelines per theme |
| `claude/claude_analysis_memo.md` | Narrative findings with scorecard and goalpost analysis |
| `claude/claude_claims_final.jsonl` | Every claim with verbatim quotes, scores, and cluster assignment |
| `claude/claude_claims_canonical.csv` | One row per cluster with aggregate stats and revision notes |

## What's not here

The raw posts (`posts/*.txt`) are excluded — copyrighted Substack content. A **proof bundle** verifies all 474 posts were processed without publishing full text.

## Caveats

All verdicts are LLM-scored, not human-verified. "Supported" means "supported according to an LLM evaluating evidence available as of March 2026." Spot-check against source posts before citing specific claims. See **Known Limitations** for the full list.

## Built by

David Goldblatt, with Claude Code (Opus 4.6) and Codex (ChatGPT) running independent pipelines. Built 2026-03-02 in a single session. Provenance: `claude/claude_AUDIT_LOG.md`.
