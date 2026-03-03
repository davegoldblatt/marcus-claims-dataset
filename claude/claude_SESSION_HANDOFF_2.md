# Marcus Claims Project — Session Handoff #2

**Date**: 2026-03-02
**Session**: Cleanup, hybrid reconciliation, and publishing (Claude Code, Opus 4.6)
**Operator**: David Goldblatt
**Prior session**: See `claude_SESSION_HANDOFF.md` for the initial build session.

---

## What Was Done This Session

### 1. File Reorganization
- Moved all `claude_*` files into `claude/` subdirectory (keeping prefixes)
- Moved `batches/` and `pass2_chunks/` into `claude/` as subdirectories
- ChatGPT files left for ChatGPT to organize (now in `outputs/chatgpt/`)
- Updated all path references in `claude_SESSION_HANDOFF.md`, `claude_AUDIT_LOG.md`, and `claude_METHODOLOGY.md`

### 2. ChatGPT Pipeline Review
- Read and validated ChatGPT's full output against their review checklist:
  - Master table: 164 rows, status distribution confirmed (76 unresolved, 45 untestable, 25 mixed, 16 supported, 2 contradicted)
  - Vendor-balanced sourcing confirmed (OpenAI 155/164, Google 89/164, Anthropic 89/164, EU AI Act 9/164)
  - Goalpost audit: 10 flagged themes, clean flag threshold (min flagged score=2, max unflagged=1)
  - Abstraction layers (META_NARRATIVE + DRIFT_NOTES) validated
  - All 5 reproducibility scripts confirmed present

### 3. Hybrid Reconciliation — Crosswalk
- Analyzed granularity mismatch: Claude has 54 clusters, ChatGPT has 164 themes across 11 labels
- Corrected mapping direction: theme3 → claude_cluster (many-to-one), not reverse
- Built `claude_crosswalk_label_to_cluster.csv`: 52 rows mapping 11 ChatGPT labels to 44 Claude cluster candidates
  - 26 high-confidence, 16 medium, 10 low
  - 6 shared clusters across multiple labels (need target-based disambiguation)
- Wrote `claude_CROSSWALK_NOTES.md` documenting methodology, coverage, orphans, and caveats
- Identified 10 orphan Claude clusters (263 claims) with no ChatGPT label match

### 4. Hybrid Reconciliation — ChatGPT Built the Bridge
- ChatGPT ingested crosswalk and produced:
  - `chatgpt_hybrid_claim_bridge.csv` — mapping audit trail (164 rows)
  - `chatgpt_hybrid_reconciliation.csv` — hybrid verdicts per theme (164 rows)
  - `chatgpt_HYBRID_RECONCILIATION.md` — method and caveats
  - `chatgpt_hybrid_orphan_claude_clusters.csv` — 10 orphan clusters with verdict distributions
- Claude validated all outputs:
  - 160 mapped + 4 mapped_medium_weak_target
  - Bridge confidence: 154 high, 6 medium, 4 low
  - Hybrid statuses: 15 supported, 26 lean_supported, 115 mixed_or_unresolved, 6 lean_contradicted, 2 contradicted
  - Agreement: 17 high, 145 medium, 2 low
  - The 2 low-agreement rows are both openai_governance (ChatGPT=contradicted, Claude cluster=supported) — correctly resolved to contradicted

### 5. DATASET_GUIDE.md
- Wrote comprehensive meta-doc at project root (~1,900 words)
- Structure: What This Is → Quickstart (3 files) → Both Pipelines → Decision Rules → Key Numbers → File Inventory by Question → Complete Inventory → Limitations + What Not To Do → How Built
- Incorporated ChatGPT's feedback: proof bundle section, denominator labels, confidence ladder, canonical view note
- All 30+ file references verified to exist on disk

### 6. Copyright Research & Proof Bundle
- Researched legality of uploading scraped posts — conclusion: don't upload full-text posts (market substitution, Substack ToS, post-Warhol risk)
- ChatGPT independently reached same conclusion and built a proof bundle:
  - `chatgpt_posts_manifest.csv` (per-post SHA256 + bytes)
  - `chatgpt_processing_ledger.csv` (per-post scan status)
  - `chatgpt_coverage_report.json` (totals)
  - `chatgpt_verify_proof_bundle.py` (verifier)
- Proof bundle added to DATASET_GUIDE.md

### 7. GitHub Publishing
- `git init` with `.gitignore` excluding `posts/`, `final_tables/`, `.DS_Store`, Python artifacts
- Initial commit: 135 files
- Created public repo: https://github.com/davegoldblatt/marcus-claims-dataset
- Pushed to main

---

## Current State

### Repository
- **GitHub**: https://github.com/davegoldblatt/marcus-claims-dataset (public)
- **Local**: `~/Desktop/marcus_scrape/`
- **Entry point**: `DATASET_GUIDE.md`

### Directory Structure
```
marcus_scrape/
├── DATASET_GUIDE.md           ← start here
├── .gitignore
├── claude/                    ← all Claude outputs + intermediates
│   ├── claude_*.md/jsonl/csv/py/json
│   ├── batches/               (24 files)
│   └── pass2_chunks/          (25 files)
├── outputs/chatgpt/           ← all ChatGPT outputs
│   ├── tables/                (8 files, incl. hybrid reconciliation)
│   ├── docs/                  (15 files)
│   ├── data/                  (19 files)
│   ├── scripts/               (12 files)
│   └── proof/                 (4 files)
├── posts/                     ← LOCAL ONLY, not in git (474 .txt files)
└── final_tables/              ← empty, gitignored
```

### Dataset Status: Complete
- Pipeline: done
- Scoring: done
- Clustering: done
- Hybrid reconciliation: done
- Documentation: done
- Published: done

---

## What Could Be Done Next

1. **Narrative analysis** — David mentioned building analysis in vanilla Claude. The dataset is ready; feed it `DATASET_GUIDE.md` + `chatgpt_hybrid_reconciliation.csv` + `claude_analysis_memo.md`.

2. **Spot-check audit** — Pick 20-30 random claims from `claude_claims_final.jsonl`, verify quotes against `posts/`, assess verdict accuracy.

3. **Visualizations** — Claim frequency over time, stacked bars by status/year, goalpost drift timelines.

4. **Event overlay** — Cross-reference claim timelines with major AI events (GPT-4, o1, DeepSeek, GPT-5, EU AI Act milestones).

5. **Tighter clustering** — Collapse Claude's 54 clusters to ~20 macro-themes for cleaner narrative.

---

## Technical Notes

- Python 3.9.6 with bs4 available via `/Users/davidgoldblatt/Desktop/Vibey/.venv/bin/python3`
- `posts/` must be present locally for proof bundle verification and any spot-checking
- The `slug` field in claims data maps directly to post filenames: `posts/YYYY-MM-DD_slug.txt`
- Hybrid reconciliation CSV is the canonical reconciled view per DATASET_GUIDE.md
- All evaluation verdicts anchored to 2026-03-02
