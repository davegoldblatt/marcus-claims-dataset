# Marcus Claims Project — Session Handoff

**Date**: 2026-03-02
**Session**: Initial build session (Claude Code, Opus 4.6)
**Operator**: David Goldblatt

---

## What This Project Is

A systematic extraction and analysis of every testable AI claim Gary Marcus has made on his Substack (https://garymarcus.substack.com/), spanning May 2022 through March 2026. The goal is to build a structured, auditable dataset that can answer: what did he claim, was he right, did he move the goalposts, and what are his recurring themes?

ChatGPT is running a parallel analysis on the same corpus. All files are tagged with `claude_` or `chatgpt_` prefixes to keep them separate. The raw `posts/` directory is shared.

---

## What Was Done This Session

### Step 1: Corpus Download
- Wrote `claude_download_marcus.py` (actually originally `download_marcus.py` — ChatGPT may have moved/renamed it, the version on disk is `chatgpt_download_marcus.py` now, but the posts were downloaded by Claude)
- Fetched sitemap.xml → extracted 474 post URLs → downloaded each as HTML → stripped to clean text via BeautifulSoup
- **Output**: `posts/*.txt` — 474 files, `YYYY-MM-DD_slug.txt` format

### Step 2: Pass 1 — Raw Claim Extraction
- Split 474 posts into 24 batches of 20
- Launched 24 parallel agents, each reading its batch and extracting claims as structured JSONL
- Each claim has: claim_date, slug, trigger, quote (verbatim), claim (normalized paraphrase), type (descriptive/predictive/causal/normative), target, horizon_type, horizon_value
- Merged all batches with sequential IDs via `claude_merge_batches.py`
- **Output**: `claude_claims_raw.jsonl` — 2,218 claims, `claim_0001` through `claim_2218`

### Step 3: Pass 2a — Per-Claim Scoring
- Split 2,218 claims into 12 chunks of ~200
- Launched 12 parallel agents scoring each claim on:
  - specificity (high/med/low)
  - falsifiability (yes/partial/no) using 4-point checklist
  - status_at_eval (supported/contradicted/mixed/pending/untestable) as of 2026-03-02
- Merged via `claude_merge_scored.py`
- **Output**: `claude_claims_scored.jsonl` — 2,218 claims with scoring fields added

### Step 4: Pass 2b — Clustering & Revision Linking
- Created condensed claim list (`claude_claims_condensed.jsonl`, 576KB)
- Single agent read all 2,218 claims and identified 54 clusters (53 thematic + 1 miscellaneous)
- Assigned every claim to exactly one cluster
- Detected goalpost movement / revision chains within clusters
- Built final output files via `claude_build_final.py`
- **Outputs**:
  - `claude_clusters.json` — 54 cluster definitions with revision notes
  - `claude_claim_clusters.jsonl` — claim-to-cluster mapping
  - `claude_claims_final.jsonl` — fully enriched (scored + clustered)
  - `claude_claims_canonical.csv` — one row per cluster with aggregate scorecard
  - `claude_second_pass_audit.csv` — full claim list with cluster context (CSV)
  - `claude_analysis_memo.md` — narrative findings

---

## Key Findings

### Overall Scorecard (2,218 claims)
| Status | Count | % |
|--------|-------|---|
| Supported | 992 | 44.7% |
| Mixed | 559 | 25.2% |
| Untestable | 388 | 17.5% |
| Pending | 173 | 7.8% |
| Contradicted | 106 | 4.8% |

### Excluding untestable + pending (empirically assessable only)
- Supported: 59.9%
- Mixed: 33.8%
- Contradicted: 6.4%

### Where he was right (>60% supported)
- Musk AI hypocrisy (65.5%)
- OpenAI untrustworthy (64.3%)
- Copyright infringement (62.5%)
- Deepfakes threaten democracy (62.0%)
- GPT-5 disappointing (60.0%)
- Hallucination unsolvable (56.7%)

### Where he was wrong (>10% contradicted)
- GenAI bubble will burst (27.0% contradicted — his worst cluster)
- GPT-4 overhyped (16.4%)
- OpenAI won't stay dominant (12.6%)

### Goalpost movement detected
1. "LLMs can't reason" → softened to "can't reason reliably" (genuine goalpost shift)
2. "Scaling won't reach AGI" → hardened over time (opposite of goalpost movement)
3. "GenAI bubble will burst" → escalating dollar figures without crash materializing
4. "GPT-5 will disappoint" → consistent, no drift, vindicated
5. "AI ROI disappointing" → updated figures, same thesis

### His accuracy improved over time
| Year | Supported | Contradicted |
|------|-----------|-------------|
| 2023 | 42% | 7% |
| 2024 | 38% | 8% |
| 2025 | 51% | 1% |
| 2026 | 49% | 2% |

---

## File Inventory

Root: `~/Desktop/marcus_scrape/`

### Shared
| File | Description |
|------|-------------|
| `posts/*.txt` | 474 raw post text files |

### Claude outputs — `claude/` (all prefixed `claude_`)
| File | Description |
|------|-------------|
| `claude/claude_METHODOLOGY.md` | Extraction and analysis methodology |
| `claude/claude_AUDIT_LOG.md` | Step-by-step provenance record |
| `claude/claude_analysis_memo.md` | Narrative analysis of findings |
| `claude/claude_claims_raw.jsonl` | 2,218 raw claims from pass 1 |
| `claude/claude_claims_scored.jsonl` | 2,218 claims with scoring fields |
| `claude/claude_claims_final.jsonl` | 2,218 claims fully enriched (scored + clustered) |
| `claude/claude_claims_condensed.jsonl` | Condensed claim list used for clustering |
| `claude/claude_clusters.json` | 54 cluster definitions with revision notes |
| `claude/claude_claim_clusters.jsonl` | Claim-to-cluster mapping |
| `claude/claude_claims_canonical.csv` | One row per cluster with aggregate scorecard |
| `claude/claude_second_pass_audit.csv` | Full claim list with cluster context (CSV) |
| `claude/claude_merge_batches.py` | Script: merge pass 1 batches |
| `claude/claude_merge_scored.py` | Script: merge pass 2a scored chunks |
| `claude/claude_build_final.py` | Script: build final output files |
| `claude/claude_do_clustering.py` | Script: clustering helper |
| `claude/claude_SESSION_HANDOFF.md` | This file |

### Claude intermediate working files
| Directory | Description |
|-----------|-------------|
| `claude/batches/batch_*.jsonl` | 24 per-batch pass 1 extraction outputs |
| `claude/pass2_chunks/chunk_*_scored.jsonl` | 12 per-chunk pass 2a scoring outputs |

### ChatGPT outputs (prefixed `chatgpt_`)
Separate directory managed by ChatGPT. See `outputs/chatgpt/` and any `chatgpt_*` files.

---

## What Could Be Done Next

1. **Compare Claude vs ChatGPT outputs**: Both ran the same pipeline on the same corpus. How do the claim counts, scorecards, and cluster structures differ? Where do they agree/disagree on whether Marcus was right?

2. **Spot-check quote fidelity**: Pick 20-30 random claims, go back to the source posts, verify the quotes are verbatim and the paraphrases are faithful.

3. **Deep-dive on contradicted claims**: The 106 contradicted claims are the most interesting. Are any of them unfairly scored? Are there claims scored "mixed" that should be "contradicted" or vice versa?

4. **Publish-ready visualization**: The cadence/repetition data and scorecard data would make great charts. Claim frequency over time per cluster, stacked bar of supported/mixed/contradicted by year, etc.

5. **Cross-reference with events timeline**: Overlay major AI events (GPT-4 launch, o1 release, DeepSeek, GPT-5) on the claim timeline to see how Marcus's output responds to the news cycle.

6. **Run pass 2b with stricter clustering**: 54 clusters may be too granular. Could collapse to ~20 macro-themes for a cleaner narrative.

---

## Technical Notes for Next Session

- Python 3.9.6 with bs4 available via `/Users/davidgoldblatt/Desktop/Vibey/.venv/bin/python3`
- All JSONL files are one JSON object per line, UTF-8
- CSV files use standard comma delimiter with header row
- The `claude_claims_final.jsonl` file is the "one file to rule them all" — every claim with every field from both passes plus cluster assignment
- Cluster IDs are descriptive snake_case strings, not numeric
- Claim IDs are sequential: `claim_0001` through `claim_2218`
