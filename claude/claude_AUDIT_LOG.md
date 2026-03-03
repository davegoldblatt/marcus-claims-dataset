# Marcus Claims Extraction — Audit Log

**Generated**: 2026-03-02
**Operator**: Claude Opus 4.6 via Claude Code, directed by David Goldblatt
**Methodology**: See `claude_METHODOLOGY.md`

---

## Step 1: Corpus Download

**Date**: 2026-03-02
**Script**: `download_marcus.py`
**Method**:
1. Fetched `https://garymarcus.substack.com/sitemap.xml`
2. Extracted all 474 URLs containing `/p/` (post pages) with `lastmod` dates
3. Downloaded each post's HTML via `urllib.request` with 1-second polite delay
4. Stripped HTML to clean text using BeautifulSoup (`html.parser` backend)
5. Saved as `posts/YYYY-MM-DD_slug.txt`

**Result**: 474 posts downloaded, 0 errors
**Date range**: 2022-05-29 through 2026-03-01
**Storage**: `../posts/*.txt`
**Limitations**: Downloaded as unauthenticated visitor. Subscriber-only posts may be truncated to their public preview. Content reflects what was publicly accessible as of 2026-03-02.

---

## Step 2: Pass 1 — Raw Claim Extraction

**Date**: 2026-03-02
**Method**: LLM-based extraction (Claude Opus 4.6) via 24 parallel agents
**Batch size**: 20 posts per batch (final batch: 14 posts)
**Batches**: aa through ax, processed in chronological order

### Extraction prompt (summary)
Each agent received:
- The same system prompt defining what counts as a "claim" (testable proposition about AI)
- Four claim types: descriptive, predictive, causal, normative
- Inclusion/exclusion rules (see METHODOLOGY.md)
- Output schema: JSONL with fields `claim_date`, `slug`, `trigger`, `quote`, `claim`, `type`, `target`, `horizon_type`, `horizon_value`
- Instructions to err on the side of inclusion

### Batch results

| Batch | Date range | Posts | Claims |
|-------|-----------|-------|--------|
| aa | 2022-05 – 2023-02 | 20 | 104 |
| ab | 2023-02 | 20 | 97 |
| ac | 2023-02 – 2023-03 | 20 | 95 |
| ad | 2023-03 – 2023-08 | 20 | 115 |
| ae | 2023-08 – 2023-10 | 20 | 78 |
| af | 2023-10 – 2023-11 | 20 | 63 |
| ag | 2023-11 – 2023-12 | 20 | 63 |
| ah | 2024-01 – 2024-02 | 20 | 97 |
| ai | 2024-01 – 2024-03 | 20 | 77 |
| aj | 2024-03 – 2024-04 | 20 | 89 |
| ak | 2024-04 – 2024-06 | 20 | 61 |
| al | 2024-06 – 2024-08 | 20 | 102 |
| am | 2024-08 – 2024-11 | 20 | 116 |
| an | 2024-11 – 2025-01 | 20 | 119 |
| ao | 2025-01 – 2025-02 | 20 | 109 |
| ap | 2025-02 – 2025-03 | 20 | 76 |
| aq | 2025-03 – 2025-04 | 20 | 81 |
| ar | 2025-04 – 2025-05 | 20 | 101 |
| as | 2025-05 – 2025-07 | 20 | 121 |
| at | 2025-07 – 2025-09 | 20 | 102 |
| au | 2025-09 – 2025-11 | 20 | 84 |
| av | 2025-11 – 2026-01 | 20 | 115 |
| aw | 2026-01 – 2026-02 | 20 | 70 |
| ax | 2026-02 – 2026-03 | 14 | 83 |
| **Total** | | **474** | **2,218** |

### Merge step
**Script**: `claude_merge_batches.py`
**Method**:
1. Read all 24 batch JSONL files in alphabetical order (which is chronological)
2. Stripped any `id` fields that agents may have added
3. Sorted all 2,218 claims by `claim_date` then `slug` for stable ordering
4. Assigned sequential IDs: `claim_0001` through `claim_2218`
5. Wrote to `claude_claims_raw.jsonl`

**Output**: `./claude_claims_raw.jsonl` — 2,218 lines, one JSON object per line

### Aggregate statistics

**By claim type:**
| Type | Count | % |
|------|-------|---|
| descriptive | 1,376 | 62.0% |
| predictive | 496 | 22.4% |
| normative | 191 | 8.6% |
| causal | 155 | 7.0% |

**By horizon type:**
| Horizon | Count | % |
|---------|-------|---|
| none | 2,076 | 93.6% |
| explicit_date | 96 | 4.3% |
| relative | 46 | 2.1% |

**By year:**
| Year | Claims |
|------|--------|
| 2022 | 12 |
| 2023 | 593 |
| 2024 | 638 |
| 2025 | 799 |
| 2026 | 176 |

**Top 15 targets:**
| Target | Count |
|--------|-------|
| AI regulation | 53 |
| LLMs | 48 |
| OpenAI | 44 |
| AGI timeline | 27 |
| generative AI | 22 |
| GPT-5 | 21 |
| LLM hallucinations | 19 |
| LLM reliability | 19 |
| AI research direction | 17 |
| Sora | 17 |
| LLM scaling | 16 |
| AI scaling | 16 |
| LLM limitations | 16 |
| AGI | 16 |
| neurosymbolic AI | 15 |

**Posts contributing claims**: 437 of 474 posts (92.2%)
**Posts with no claims**: 37 (7.8%) — skipped for being stubs, obituaries, non-AI content, April Fools jokes, pure link posts, or containing only rhetorical questions

### Known issues and limitations

1. **Batch consistency**: 24 independent agents processed batches without seeing each other's output. Claim extraction threshold may vary slightly between batches.
2. **Trigger attribution**: The `trigger` field requires world knowledge. Obvious triggers (product launches, news events) are captured; subtler ones (specific tweets, private conversations) may be missed or described inconsistently across batches.
3. **Target normalization**: Targets were free-text, not drawn from a controlled vocabulary. The same concept may appear as "LLMs", "large language models", "LLM limitations", "LLM reliability", etc. Pass 2 should normalize.
4. **Paywalled content**: Some posts may have been truncated. Claims from truncated posts represent only the publicly visible portion.
5. **Quote fidelity**: Agents were instructed to copy-paste exact quotes. However, LLM-based extraction may occasionally paraphrase slightly or truncate long quotes. Spot-checking against source posts is recommended.
6. **Feb 2023 spike**: 241 claims in Feb 2023 reflects Marcus importing many pre-Substack essays when he launched the newsletter, not a sudden burst of writing.

---

## Step 3: Pass 2a — Per-Claim Scoring

**Date**: 2026-03-02
**Method**: LLM-based scoring (Claude Opus 4.6) via 12 parallel agents
**Input**: `claude_claims_raw.jsonl` split into 12 chunks of ~200 claims each
**Fields added**: specificity, falsifiability, evaluation_date (fixed: 2026-03-02), status_at_eval

### Chunk results

| Chunk | Claims | Supported | Mixed | Contradicted | Untestable | Pending |
|-------|--------|-----------|-------|-------------|------------|---------|
| 00 | 200 | 77 | 65 | 18 | 21 | 19 |
| 01 | 200 | 86 | 73 | 9 | 30 | 2 |
| 02 | 200 | 87 | 49 | 15 | 44 | 5 |
| 03 | 200 | 95 | 58 | 8 | 30 | 9 |
| 04 | 200 | 60 | 54 | 25 | 48 | 13 |
| 05 | 200 | 63 | 65 | 21 | 41 | 10 |
| 06 | 200 | 102 | 56 | 2 | 27 | 13 |
| 07 | 200 | 106 | 40 | 1 | 36 | 17 |
| 08 | 200 | 129 | 22 | 1 | 25 | 23 |
| 09 | 200 | 89 | 44 | 2 | 40 | 25 |
| 10 | 200 | 96 | 25 | 4 | 42 | 33 |
| 11 | 18 | 2 | 7 | 0 | 4 | 4 |
| **Total** | **2,218** | **992** | **559** | **106** | **388** | **173** |

### Aggregate statistics

**Specificity**: high 389 (17.5%), med 1,049 (47.3%), low 780 (35.2%)
**Falsifiability**: yes 281 (12.7%), partial 1,520 (68.5%), no 417 (18.8%)

**Status by year**:
| Year | n | Supported | Mixed | Contradicted | Untestable | Pending |
|------|---|-----------|-------|-------------|------------|---------|
| 2022 | 12 | 33% | 42% | 0% | 17% | 8% |
| 2023 | 593 | 42% | 31% | 7% | 16% | 4% |
| 2024 | 638 | 38% | 29% | 8% | 19% | 5% |
| 2025 | 799 | 51% | 20% | 1% | 17% | 11% |
| 2026 | 176 | 49% | 14% | 2% | 20% | 14% |

**Status by claim type**:
| Type | n | Supported | Mixed | Contradicted | Untestable | Pending |
|------|---|-----------|-------|-------------|------------|---------|
| descriptive | 1,376 | 56% | 29% | 5% | 10% | 1% |
| predictive | 496 | 33% | 22% | 7% | 6% | 31% |
| causal | 155 | 35% | 34% | 3% | 26% | 3% |
| normative | 191 | 2% | 2% | 1% | 95% | 1% |

**106 contradicted claims**: Concentrated in (1) absolute "LLMs can't do X" claims from 2023 refuted by reasoning models, (2) repeated bubble-burst/WeWork predictions for OpenAI, (3) capability plateau claims contradicted by o1/o3.

### Merge step
**Script**: `claude_merge_scored.py`
**Output**: `./claude_claims_scored.jsonl` — 2,218 lines with all original + 4 scoring fields

### Known issues
1. **Scorer knowledge cutoff**: Agents use knowledge through early 2026 to evaluate claims. Events after March 2026 could change some assessments.
2. **"Mixed" as catch-all**: The "mixed" category may be over-represented — it's the default when evidence is ambiguous, which covers a wide range of partial correctness.
3. **Normative claims**: 95% of normative claims scored "untestable" by design. These are policy recommendations, not empirical claims.
4. **Chunk 00 retry**: Original agent failed to write output; re-launched successfully.

---

## Step 4: Pass 2b — Clustering & Revision Linking

**Date**: 2026-03-02
**Method**: Single LLM agent (Claude Opus 4.6) processing full condensed claim set (576KB)
**Input**: `claude_claims_condensed.jsonl` (2,218 claims, id + date + claim + type + target + status + horizon)

### Results
- **54 clusters** identified (53 thematic + 1 miscellaneous)
- **2,132 claims (96.1%)** assigned to thematic clusters
- **86 claims (3.9%)** in miscellaneous
- **18 clusters** have manually enriched revision notes documenting goalpost movement

### Top clusters by size
| Cluster | Claims | Supported% | Contradicted% |
|---------|--------|-----------|--------------|
| ai_needs_regulation | 164 | 31.1% | 1.2% |
| ai_roi_disappointing | 132 | 38.6% | 6.8% |
| llms_lack_world_models | 124 | 30.6% | 4.0% |
| hallucination_unsolvable | 120 | 56.7% | 5.8% |
| scaling_wont_reach_agi | 106 | 42.5% | 2.8% |
| openai_wont_stay_dominant | 87 | 40.2% | 12.6% |
| deepfakes_threaten_democracy | 79 | 62.0% | 1.3% |
| ai_copyright_infringement | 72 | 62.5% | 2.8% |
| genai_bubble_will_burst | 63 | 11.1% | 27.0% |

### Goalpost detection findings
1. "LLMs can't reason" → softened to "can't reason reliably" after o1/o3
2. "Scaling won't reach AGI" → hardened over time (opposite of goalpost movement)
3. "GenAI bubble will burst" → escalated dollar figures each year without crash materializing
4. "GPT-5 will disappoint" → consistent, no drift, largely vindicated
5. "AI ROI disappointing" → updated figures each year (repetition, not goalpost movement)

### Output files
- `claude_clusters.json` — 54 cluster definitions with revision notes
- `claude_claim_clusters.jsonl` — 2,218 claim-to-cluster assignments
- `claude_claims_final.jsonl` — fully enriched claims (scored + clustered)
- `claude_claims_canonical.csv` — one row per cluster with aggregate stats
- `claude_second_pass_audit.csv` — full claim list with cluster context
- `claude_analysis_memo.md` — narrative analysis of findings

---

## File inventory

All Claude outputs live in `claude/` under the project root (`~/Desktop/marcus_scrape/claude/`).

| File | Description |
|------|-------------|
| `claude_METHODOLOGY.md` | Full methodology documentation |
| `claude_AUDIT_LOG.md` | This file — step-by-step record of what was done |
| `claude_merge_batches.py` | Batch merge script |
| `claude_merge_scored.py` | Scored chunk merge script |
| `claude_build_final.py` | Final output build script |
| `claude_do_clustering.py` | Clustering helper script |
| `batches/batch_*.jsonl` | 24 per-batch extraction outputs |
| `pass2_chunks/chunk_*_scored.jsonl` | 12 scored chunk outputs |
| `claude_claims_raw.jsonl` | Merged pass 1 output: 2,218 claims with sequential IDs |
| `claude_claims_scored.jsonl` | Merged pass 2a output: 2,218 claims with scoring fields |
| `claude_claims_final.jsonl` | Fully enriched: scored + clustered |
| `claude_claims_condensed.jsonl` | Condensed claim list used for clustering |
| `claude_clusters.json` | 54 cluster definitions with revision notes |
| `claude_claim_clusters.jsonl` | Claim-to-cluster mapping (2,218 lines) |
| `claude_claims_canonical.csv` | One row per cluster with aggregate scorecard |
| `claude_second_pass_audit.csv` | Full claim list with cluster context (CSV for spreadsheet use) |
| `claude_analysis_memo.md` | Narrative analysis memo |
| `claude_SESSION_HANDOFF.md` | Session handoff document |

Shared corpus: `../posts/*.txt` (474 raw post text files, at project root)
