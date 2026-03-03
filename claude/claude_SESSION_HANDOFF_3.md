# Marcus Claims Project — Session Handoff #3

**Date**: 2026-03-03
**Session**: Data analysis, essay development, and GitHub updates (Claude Code, Opus 4.6)
**Operator**: David Goldblatt
**Prior sessions**: See `claude_SESSION_HANDOFF.md` (build), `claude_SESSION_HANDOFF_2.md` (cleanup/reconciliation/publishing)

---

## What Was Done This Session

### 1. Deep Data Analysis
- Extracted top takeaways from the dataset, identifying the central thesis: Marcus understood the technology better than he understood the market
- Identified five analytical threads: technical/market split, escalation asymmetry, institutional criticism as his best work, falsifiability pattern, one-big-idea problem
- Verified year-by-year accuracy (assessable denominator): 2023=52.7%, 2024=50.0%, 2025=71.0%, 2026=75.7%
- Verified quarterly cadence data: hallucination cluster steady (5-14/quarter), bubble cluster escalating (0→0→0→1→6→14→6→7→3→5→15→4)
- Discovered and verified claim age vs accuracy table (recency bias): claims 12+ months old stabilize at ~52% supported, ~8-9% contradicted

### 2. Non-Intuitive Findings
- **Specificity inverts expectations**: high-specificity claims 77.8% supported vs low-specificity 42.7%. Being more specific makes him MORE accurate, not less.
- **60% is driven by description, not prediction**: 77.6% of supported claims are descriptive (observing what IS). Predictive claims specifically: 52.6% supported, with 24.2% contradicted in 2024 (his worst year for predictions).
- **2024 predictive bloodbath**: 23 of 37 contradicted predictions came from just two clusters (bubble: 10, OpenAI dominance: 5). Failure extremely concentrated.
- **2025 predictive recovery**: contradicted rate dropped from 24.2% to 2.8%. Genuine adaptation.
- **Musk accuracy**: 84.4% supported, 1 contradicted claim out of 32 assessable across 4 years.
- **Bubble cluster worse than reported**: 41.46% contradicted against assessable claims (canonical CSV uses total denominator showing 27%).

### 3. Essay Development
- Wrote `claude_essay_brief.md` — analytical brief for essay writing with five threads, key numbers, guardrails
- Collaborated with another Claude instance and ChatGPT on essay structure (7-beat outline → revised to 5 sections)
- Reviewed multiple essay drafts, providing feedback on:
  - Year-by-year numbers (corrected denominator from total to assessable)
  - 2024 dip as most interesting year (not steady improvement)
  - Claim age table verification (all numbers confirmed exact)
  - Recency bias acknowledgment ("Score one for Gary?")
  - Tightening from 3,500 to ~2,800 words
  - "Permission to wait" as the essay's strongest closing line
- Pulled two specific claims for inline examples: claim_1127 (Superalignment 20% compute, supported) and claim_0996 ("bubble will burst within 12 months," contradicted)

### 4. GitHub Updates
- Created README.md with findings-first structure (not a data catalog)
- Committed and pushed: README.md, claude_essay_brief.md, claude_SESSION_HANDOFF_2.md
- Pipeline names: "Claude Code" and "Codex (ChatGPT)" in README

### 5. Cross-LLM Collaboration
- Received and evaluated ChatGPT's critique of initial analysis (agreed on evidence-first framing, pushed back on overcautious tone)
- Received and evaluated another Claude instance's full 7-beat essay outline and full draft
- Provided corrections: year-by-year numbers, 2024 dip, cadence data precision, recency bias caveat
- Flagged methodology inconsistency (Codex/Claude Code vs Claude/ChatGPT in endnote)

---

## Key Data Points Verified This Session

| Finding | Value | Source |
|---------|-------|--------|
| Overall supported (assessable) | 59.9% (992/1657) | claims_final.jsonl |
| Overall contradicted (assessable) | 6.4% (106/1657) | claims_final.jsonl |
| 2024 contradiction rate (assessable) | 11.2% | claims_final.jsonl by year |
| 2024 predictive contradiction rate | 24.2% (23/95) | claims_final.jsonl filtered |
| 2025 predictive contradiction rate | 2.8% (3/107) | claims_final.jsonl filtered |
| High-specificity supported rate | 77.8% (277/356) | claims_final.jsonl |
| Low-specificity supported rate | 42.7% (184/431) | claims_final.jsonl |
| Bubble contradicted (assessable) | 41.46% (17/41) | claims_final.jsonl |
| Bubble contradicted (total) | 27.0% (17/63) | claims_canonical.csv |
| Musk claims supported | 84.4% (27/32) | claims_final.jsonl |
| Claim age 0-6mo supported | 69.5% | claims_final.jsonl |
| Claim age 12-24mo supported | 52.3% | claims_final.jsonl |
| Claim age 36+mo supported | 50.9% | claims_final.jsonl |
| Descriptive % of supported claims | 77.6% (770/992) | claims_final.jsonl |

---

## Current State

### Repository
- **GitHub**: https://github.com/davegoldblatt/marcus-claims-dataset (public)
- **Local**: `~/Desktop/marcus_scrape/`
- **Latest commit**: `c8c9db0` — README, essay brief, session handoff 2

### Essay Status
- Draft is near-final (~2,800 words, 5 sections)
- Being written in a separate Claude conversation
- Title: "The Most Expensive Kind of Correct"
- All data claims in essay verified against dataset
- Charts referenced but not yet generated: marcus_accuracy_by_year, marcus_best_worst_clusters, marcus_falsifiability_breakdown, marcus_volume_hallucination_vs_bubble

### Files Created This Session
| File | Description |
|------|-------------|
| `README.md` | GitHub landing page with key findings |
| `claude/claude_essay_brief.md` | Analytical brief for essay writing |
| `claude/claude_SESSION_HANDOFF_3.md` | This file |

---

## What Could Be Done Next

1. **Generate charts** — Four charts referenced in essay need to be created: accuracy by year (stacked bar), best/worst clusters (horizontal bar), falsifiability breakdown (donut/bar), hallucination vs bubble volume over time (two-line).

2. **Spot-check claims** — Pick 10-20 claims from `claude_claims_final.jsonl`, verify quotes against `posts/`, assess verdict accuracy. Especially worth checking the contradicted bubble claims and supported institutional claims used as essay examples.

3. **Push session handoff 3** — This file isn't committed yet.

4. **Denominator consistency** — The canonical CSV uses total claims as denominator; the essay analysis uses assessable. Consider adding an assessable-denominator version of `claude_claims_canonical.csv` to avoid confusion.

---

## Technical Notes

- Python 3.9.6 via `/Users/davidgoldblatt/Desktop/Vibey/.venv/bin/python3`
- `claim_date` is the date field in claims_final.jsonl (not `date`)
- Assessable = total - untestable - pending (n=1,657 of 2,218)
- The canonical CSV denominators differ from the essay's denominators — always specify which you're using
- Bubble cluster: 27% contradicted (total denom) vs 41.46% contradicted (assessable denom) — both are correct, different bases
