# Marcus AI Claims Dataset — Guide

## What This Is

A structured, auditable dataset of every testable AI claim Gary Marcus made on his Substack (garymarcus.substack.com), from May 2022 through March 2026. The corpus is 474 posts.

Two independent LLM pipelines analyzed the same text:

- **Claude** (Opus 4.6) extracted and scored **2,218 individual claims** across 54 clusters. Designed for claim-level granularity — willing to render supported/contradicted/mixed verdicts on each claim.
- **ChatGPT** extracted and scored **164 themes** across 11 categories. Designed for theme-level conservatism — defaults to "unresolved" unless clear cross-vendor evidence exists.

A **hybrid reconciliation layer** maps Claude's claim-level verdicts into ChatGPT's theme structure, producing a unified view that preserves both perspectives.

The pipelines are complementary, not competing. Claude answers "was this specific sentence right?" ChatGPT answers "what are the macro patterns and how have they drifted?" The hybrid answers "where do they agree and disagree?"

---

## Quickstart (3 Files)

If you're short on time, start here:

| File | What it gives you |
|------|-------------------|
| `outputs/chatgpt/tables/chatgpt_hybrid_reconciliation.csv` | One row per theme with both pipelines' verdicts, hybrid status, and agreement band. **Treat this as the canonical reconciled view.** |
| `claude/claude_analysis_memo.md` | Narrative findings — scorecard, where Marcus was right/wrong, goalpost analysis |
| `claude/claude_claims_final.jsonl` | Every individual claim with verbatim quotes, scores, and cluster assignment — for spot-checking or drilling into any theme |

---

## Verifiable Corpus Coverage (No Full-Text Upload)

If you need to prove that all posts were processed without publishing copyrighted text, use:

| File | Purpose |
|------|---------|
| `outputs/chatgpt/proof/chatgpt_posts_manifest.csv` | One row per post with date, slug, local path, byte size, and SHA256 hash |
| `outputs/chatgpt/proof/chatgpt_processing_ledger.csv` | One row per post marking automated full-text scan (`review_status=scanned_full_text`) |
| `outputs/chatgpt/proof/chatgpt_coverage_report.json` | Coverage totals and proof-scope caveats |
| `outputs/chatgpt/proof/chatgpt_PROOF_BUNDLE_README.md` | Verification instructions |

Verification command:

```bash
python3 outputs/chatgpt/scripts/chatgpt_verify_proof_bundle.py
```

Expected result: `PASS: proof bundle verified` and `Posts verified: 474`.

---

## How Each Pipeline Works

### Claude Pipeline
1. **Download**: sitemap.xml → 474 posts as clean text (`posts/*.txt`)
2. **Pass 1 — Extraction**: 24 parallel agents, each reading ~20 posts. One JSONL record per claim with: date, slug, verbatim quote, normalized paraphrase, claim type, target, temporal horizon.
3. **Pass 2a — Scoring**: 12 parallel agents scoring each claim for specificity, falsifiability, and outcome status as of 2026-03-02.
4. **Pass 2b — Clustering**: Single agent grouping all 2,218 claims into 54 thematic clusters, detecting goalpost movement within each.
5. **Output**: `claude_claims_final.jsonl` (one file with everything).

Key design choice: *calls it as it sees it*. If the evidence leans one way, the claim gets a verdict rather than "unresolved." This yields higher supported and contradicted rates.

### ChatGPT Pipeline
1. **Extraction**: Canonical claim extraction from posts.
2. **3-tier clustering**: cluster1 → cluster2 → theme3 (164 themes across 11 labels: agi_timeline, hallucination_misinformation, scaling_limits, etc.).
3. **Correctness scoring**: Vendor-balanced sourcing (OpenAI, Google/DeepMind, Anthropic, EU AI Act system cards and documentation). Ambiguous cases downgraded to "unresolved."
4. **Goalpost shift audit**: Horizon drift, certainty drift, and lexical drift tracked across cluster2 transitions.
5. **Output**: `chatgpt_claims_master.csv` (one row per theme with all fields).

Key design choice: *conservative adjudication*. Only marks supported/contradicted when cross-vendor documentation clearly supports it. This yields high unresolved rates but high-confidence verdicts when rendered.

### Hybrid Reconciliation
- Maps each ChatGPT theme3 to the best-fit Claude cluster using label compatibility → target match → date overlap.
- Aggregates Claude's claim-level verdicts within each theme's matched cluster.
- Produces hybrid statuses using both pipelines' inputs.

---

## Decision Rules — Status Definitions

These definitions apply across the dataset. Statuses from each pipeline follow that pipeline's threshold; hybrid statuses synthesize both.

### Source Pipeline Statuses
| Status | Meaning |
|--------|---------|
| **supported** | Evidence as of 2026-03-02 favors the claim |
| **contradicted** | Evidence as of 2026-03-02 contradicts the claim |
| **mixed** | Evidence is genuinely bidirectional — partly right, partly wrong |
| **unresolved** | Insufficient evidence to adjudicate, or claim's timeframe hasn't elapsed (ChatGPT pipeline only) |
| **pending** | Claim's horizon hasn't arrived yet (Claude pipeline only — similar to ChatGPT's "unresolved") |
| **untestable** | Claim is normative, too vague, or structurally unfalsifiable |

### Hybrid Statuses
| Status | Rule |
|--------|------|
| **supported** | ChatGPT = supported AND Claude supported% ≥ 40% |
| **contradicted** | ChatGPT = contradicted AND Claude contradicted% ≥ 10% |
| **lean_supported** | ChatGPT = unresolved AND Claude supported% ≥ 50% AND contradicted% < 10% |
| **lean_contradicted** | ChatGPT = unresolved AND Claude contradicted% ≥ 15% AND supported% < 30% |
| **mixed_or_unresolved** | Everything else |

### Agreement Bands
| Band | Meaning |
|------|---------|
| **high** | Both pipelines agree on direction |
| **medium** | Compatible but different resolution (e.g., one calls it, the other holds as unresolved) |
| **low** | Pipelines disagree on direction |

---

## Key Numbers at a Glance

### Claude (n=2,218 individual claims)
| Status | Count | % of all (n=2,218) | % of assessable (n=1,657) |
|--------|-------|----------|--------------------------|
| Supported | 992 | 44.7% | 59.9% |
| Mixed | 559 | 25.2% | 33.7% |
| Contradicted | 106 | 4.8% | 6.4% |
| Untestable | 388 | 17.5% | — |
| Pending | 173 | 7.8% | — |

### ChatGPT (n=164 themes)
| Status | Count | % of all (n=164) | % of adjudicable (n=43) |
|--------|-------|----------|------------------------|
| Supported | 16 | 9.8% | 37.2% |
| Mixed | 25 | 15.2% | 58.1% |
| Contradicted | 2 | 1.2% | 4.7% |
| Unresolved | 76 | 46.3% | — |
| Untestable | 45 | 27.4% | — |

### Hybrid (n=164 themes, both pipelines combined)
| Status | Count | % (n=164) |
|--------|-------|---|
| Supported | 15 | 9.1% |
| Lean supported | 26 | 15.9% |
| Mixed or unresolved | 115 | 70.1% |
| Lean contradicted | 6 | 3.7% |
| Contradicted | 2 | 1.2% |

Pipeline agreement: **high** on 17 themes, **medium** on 145, **low** on 2.

**Why the numbers look so different**: Claude scored 2,218 individual claims and was willing to render verdicts. ChatGPT scored 164 themes and defaulted to "unresolved" when evidence was ambiguous. When you exclude untestable/unresolved from both, the directional picture converges — both find Marcus mostly right, sometimes wrong, with his worst areas being the AI bubble thesis and some absolute capability claims from 2023.

---

## File Inventory by Question

### "Was Marcus right overall?"
- `outputs/chatgpt/tables/chatgpt_hybrid_reconciliation.csv` — hybrid verdicts per theme
- `claude/claude_analysis_memo.md` — narrative findings with scorecard

### "Was he right about a specific topic?"
- Filter `chatgpt_hybrid_reconciliation.csv` by `theme_label`
- Drill into `claude/claude_claims_final.jsonl` filtering by `cluster_id` for individual claim quotes

### "Did he move the goalposts?"
- `outputs/chatgpt/data/chatgpt_goalpost_shift_audit.csv` — 10 flagged themes with shift type and score
- `outputs/chatgpt/docs/chatgpt_goalpost_shift_summary.md` — narrative
- `claude/claude_clusters.json` — `revision_notes` field per cluster

### "Where do the two pipelines disagree?"
- `chatgpt_hybrid_reconciliation.csv`, filter to `agreement_band = low` (2 rows: both openai_governance)

### "I want to spot-check a specific claim"
- Find the claim in `claude/claude_claims_final.jsonl` (has `slug` field)
- Read the source post in `posts/[date]_[slug].txt`

### "What topics did Claude track that ChatGPT didn't?"
- `outputs/chatgpt/tables/chatgpt_hybrid_orphan_claude_clusters.csv` — 10 orphan clusters (263 claims)

### "What's the macro narrative arc?"
- `outputs/chatgpt/docs/chatgpt_META_NARRATIVE.md` — 5 meta-pillars over time
- `outputs/chatgpt/data/chatgpt_CLAIM_DRIFT_LEDGER.csv` — per-step drift tracking

---

## Complete File Inventory

### Shared
| Path | Description |
|------|-------------|
| `posts/*.txt` | 474 raw post text files (YYYY-MM-DD_slug.txt) |
| `DATASET_GUIDE.md` | This file |

### Claude (`claude/`)
| File | Description |
|------|-------------|
| `claude_claims_final.jsonl` | **Primary output.** 2,218 claims, fully enriched (scored + clustered) |
| `claude_analysis_memo.md` | Narrative analysis of findings |
| `claude_METHODOLOGY.md` | Extraction and scoring methodology |
| `claude_AUDIT_LOG.md` | Step-by-step provenance record |
| `claude_clusters.json` | 54 cluster definitions with revision notes |
| `claude_claims_raw.jsonl` | 2,218 raw claims from pass 1 (before scoring) |
| `claude_claims_scored.jsonl` | 2,218 claims with scoring fields (before clustering) |
| `claude_claims_condensed.jsonl` | Condensed claim list used as clustering input |
| `claude_claim_clusters.jsonl` | Claim-to-cluster mapping |
| `claude_claims_canonical.csv` | One row per cluster with aggregate scorecard |
| `claude_second_pass_audit.csv` | Full claim list with cluster context (CSV) |
| `claude_crosswalk_label_to_cluster.csv` | Crosswalk: ChatGPT labels → Claude cluster candidates |
| `claude_CROSSWALK_NOTES.md` | Crosswalk methodology and caveats |
| `claude_SESSION_HANDOFF.md` | Session handoff from initial build |
| `claude_*.py` | Build scripts (merge_batches, merge_scored, build_final, do_clustering) |
| `batches/batch_*.jsonl` | 24 per-batch pass 1 extraction outputs |
| `pass2_chunks/chunk_*_scored.jsonl` | 12 per-chunk pass 2a scoring outputs |

### ChatGPT (`outputs/chatgpt/`)
| File | Description |
|------|-------------|
| `tables/chatgpt_claims_master.csv` | **Primary output.** 164 themes with all fields |
| `tables/chatgpt_hybrid_reconciliation.csv` | **Hybrid output.** Both pipelines merged per theme |
| `tables/chatgpt_hybrid_claim_bridge.csv` | Mapping audit trail: theme3 → Claude cluster |
| `tables/chatgpt_hybrid_orphan_claude_clusters.csv` | 10 unmapped Claude clusters |
| `tables/chatgpt_top_themes.csv` | Top themes by claim occurrence |
| `tables/chatgpt_goalpost_flagged.csv` | 10 goalpost-shift flagged themes |
| `tables/chatgpt_adjudicable_only.csv` | 43 themes with supported/contradicted/mixed verdicts |
| `tables/chatgpt_qa_spotcheck_20.csv` | 20-theme QA spot-check |
| `docs/chatgpt_FINAL_RESULTS.md` | Summary results |
| `docs/chatgpt_HYBRID_RECONCILIATION.md` | Hybrid methodology and caveats |
| `docs/chatgpt_META_NARRATIVE.md` | Macro narrative arc across 5 pillars |
| `docs/chatgpt_correctness_refined_v2_summary.md` | Correctness scoring methodology |
| `docs/chatgpt_goalpost_shift_summary.md` | Goalpost shift findings |
| `docs/chatgpt_DRIFT_NOTES.md` | Claim drift methodology and aggregate signals |
| `data/chatgpt_correctness_refined_v2_scorecard.csv` | Per-theme correctness with sources |
| `data/chatgpt_goalpost_shift_audit.csv` | Full goalpost audit (164 themes) |
| `data/chatgpt_CLAIM_DRIFT_LEDGER.csv` | Per-step drift between cluster2 pairs |
| `scripts/chatgpt_*.py` | Pipeline scripts (5 in reproducibility order) |

---

## Known Limitations

1. **LLM-as-judge circularity.** Both pipelines used LLMs to evaluate claims *about* LLMs. Claude scoring "LLMs can't reason reliably" as "supported" is an LLM rendering judgment on its own limitations. This is unavoidable but should inform how much weight you place on specific verdicts.

2. **Paywall truncation.** Some subscriber-only posts may have been truncated to their public preview. Claims from these posts represent only the publicly visible portion.

3. **Quote fidelity not spot-checked.** Claude's agents were instructed to copy-paste exact quotes, but LLM extraction may occasionally paraphrase or truncate. Spot-checking against source posts is recommended before publishing any specific quote.

4. **3.4x claim count asymmetry.** Claude extracted 2,218 claims; ChatGPT tracked ~645 claim occurrences. Claude was more inclusive in what counts as a separate claim. Always compare percentages, not raw counts.

5. **10 orphan Claude clusters (263 claims).** Topics Claude tracked that ChatGPT's taxonomy doesn't cover: `gpt4_overhyped`, `ai_academic_integrity`, `ai_coding_overhyped`, `sora_video_unreliable`, `china_ai_competition`, and 5 smaller clusters. These are documented but excluded from the hybrid layer.

6. **Weak mappings.** `self_driving_robotics` (no high-confidence Claude cluster match) and `copyright_ip` (drift contamination in ChatGPT's theme chains) should be treated with extra caution.

7. **"Mixed" and "unresolved" are over-represented.** Claude defaults ambiguous cases to "mixed" (25.2% of claims). ChatGPT defaults to "unresolved" (46.3% of themes). Both are conservative in opposite ways — Claude calls it but hedges; ChatGPT withholds judgment entirely.

8. **Evaluation anchor: 2026-03-02.** All verdicts reflect evidence available as of this date. Future developments will change some assessments, particularly the 173 "pending" claims in Claude's data.

### Confidence Ladder

When using hybrid verdicts, weight them by confidence:

1. **Highest**: Hybrid status with `agreement_band = high` and `bridge_confidence = high`. Both pipelines agree and the mapping is clean.
2. **Medium**: Hybrid `lean_supported` or `lean_contradicted` statuses. One pipeline rendered a verdict; the other held as unresolved but the claim-level data tilts one way.
3. **Lowest**: Rows with `manual_review = yes`, `bridge_confidence = low`, or claims in orphan/unmapped clusters. Use these for exploration, not conclusions.

### What Not to Do

- **Don't treat "unresolved" as "wrong."** Unresolved means insufficient evidence to adjudicate, not that Marcus was incorrect. Nearly half of ChatGPT's themes are unresolved by design.
- **Don't compare raw counts across pipelines.** 992 supported claims (Claude) vs. 16 supported themes (ChatGPT) are not comparable numbers. Use the percentage columns and note the denominator.
- **Don't publish claim-level verdicts without spot-checks.** The `quote` and `status_at_eval` fields are LLM-generated. Pick a random sample, go back to `posts/`, and verify before citing specific claims.

---

## How This Was Built

Built 2026-03-02 in a single session. As-of evaluation date: **2026-03-02** (all verdicts anchored to evidence available on this date). Claude Code (Opus 4.6) and ChatGPT worked the same corpus independently, then collaborated on the hybrid reconciliation with David Goldblatt directing.

For full provenance: `claude/claude_AUDIT_LOG.md` (Claude's step-by-step record), ChatGPT's scripts in `outputs/chatgpt/scripts/` (reproducibility order documented in `chatgpt_FINAL_RESULTS.md`).
