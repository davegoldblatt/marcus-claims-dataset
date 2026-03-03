# Label-Level Crosswalk: ChatGPT Theme Labels → Claude Clusters

**Date**: 2026-03-02
**Purpose**: First-pass mapping to enable hybrid reconciliation between Claude (claim-level, 2,218 claims in 54 clusters) and ChatGPT (theme-level, 164 themes in 11 labels).

**File**: `claude_crosswalk_label_to_cluster.csv`

---

## How to Use This Crosswalk

1. For each ChatGPT theme3 row, look up its `theme_label` in this crosswalk.
2. The crosswalk returns a list of candidate Claude clusters, ranked by `match_confidence` (high/medium/low).
3. To refine from label-level to theme3-level, use `target_mode` and date overlap to pick the best-fit Claude cluster for each theme3.
4. Aggregate Claude claim-level verdicts within the matched cluster, filtered to the theme3's date range and target.

**Mapping direction**: theme3 → claude_cluster (many-to-one). Multiple theme3s will map to the same Claude cluster.

---

## Coverage Summary

| Metric | Count |
|--------|-------|
| ChatGPT theme labels | 11 |
| Claude clusters mapped (appear in crosswalk) | 44 of 54 |
| Claude clusters orphaned (no ChatGPT label match) | 10 |
| Total crosswalk rows | 52 |
| High-confidence mappings | 27 |
| Medium-confidence mappings | 16 |
| Low-confidence mappings | 9 |

---

## Label-Level Mapping Overview

### Clean 1:1 Matches (high confidence, single dominant cluster)
| ChatGPT Label | Primary Claude Cluster | Claude Claims |
|---------------|----------------------|---------------|
| `copyright_ip` | `ai_copyright_infringement` | 72 |
| `agents_reliability` | `llm_agents_premature` | 35 |

### Clean 1:few Matches (high confidence, 2-3 strong candidates)
| ChatGPT Label | Primary Claude Clusters | Combined Claims |
|---------------|------------------------|-----------------|
| `hallucination_misinformation` | `hallucination_unsolvable` + `deepfakes_threaten_democracy` | 199 |
| `market_hype_bubble` | `genai_bubble_will_burst` + `ai_roi_disappointing` + `ai_hype_cycle_parallels` | 204 |
| `openai_governance` | `openai_untrustworthy` + `openai_wont_stay_dominant` + `altman_overpromises` | 158 |
| `regulation_policy` | `ai_needs_regulation` + `industry_self_regulation_fails` | 195 |
| `scaling_limits` | `scaling_wont_reach_agi` + `ai_needs_new_paradigm` + `ai_progress_not_linear` | 155 |

### Broad Labels (many Claude clusters, needs theme3-level refinement)
| ChatGPT Label | High-confidence Clusters | Total Candidates |
|---------------|------------------------|------------------|
| `reasoning_common_sense` (23 themes) | 5 clusters (290 claims) | 9 clusters |
| `safety_alignment` (21 themes) | 4 clusters (77 claims) | 9 clusters |
| `agi_timeline` (16 themes) | 2 clusters (60 claims) | 5 clusters |

### Weak Match
| ChatGPT Label | Best Claude Cluster | Confidence | Note |
|---------------|-------------------|------------|------|
| `self_driving_robotics` (10 themes) | `musk_ai_hypocrisy` | medium | Claude has no dedicated self-driving cluster. Tesla/Musk overlap is partial. Some claims likely in `miscellaneous`. |

---

## Orphaned Claude Clusters (No ChatGPT Label Match)

These 10 Claude clusters (263 total claims) have no natural home in ChatGPT's 11-label taxonomy. They represent topics Claude tracked that ChatGPT's theme structure doesn't surface:

| Claude Cluster | Claims | Possible ChatGPT Affinity | Note |
|---------------|--------|--------------------------|------|
| `gpt4_overhyped` | 61 | `scaling_limits` or `openai_governance` | Could split across both; GPT-4 is both a capability and an OpenAI story |
| `ai_academic_integrity` | 40 | `hallucination_misinformation` | Plagiarism/fake research is misinfo-adjacent but ChatGPT doesn't have this category |
| `ai_coding_overhyped` | 38 | `reasoning_common_sense` or `agents_reliability` | Code reliability is a capability claim; ChatGPT may have absorbed into reasoning |
| `sora_video_unreliable` | 34 | `hallucination_misinformation` or `scaling_limits` | Video generation failures; ChatGPT has no media-generation label |
| `china_ai_competition` | 32 | `regulation_policy` | Geopolitics; ChatGPT may have absorbed into regulation or excluded |
| `ai_image_gen_unreliable` | 17 | `hallucination_misinformation` | Image generation failures; similar to sora_video |
| `ai_job_disruption_overhyped` | 17 | `market_hype_bubble` | Job displacement is hype-adjacent |
| `lecun_criticism` | 12 | `reasoning_common_sense` or `scaling_limits` | Person-specific; ChatGPT doesn't have person-focused labels |
| `hinton_criticism` | 9 | `safety_alignment` | Person-specific |
| `ai_scientists_overstate` | 3 | `market_hype_bubble` | Scientist behavior; very small cluster |

**Recommendation**: For the hybrid pass, these 263 claims should be flagged as `bridge_status = unmapped_orphan` rather than force-fit. They represent genuine analytical divergence between the pipelines — topics that one tracked explicitly and the other absorbed or excluded.

---

## Known Caveats

1. **copyright_ip drift contamination**: ChatGPT's `copyright_ip` theme3 drift chains contain quotes about AI architecture, chip investments, and neurosymbolic AI that aren't about copyright. Some theme3 rows under this label may map poorly to Claude's `ai_copyright_infringement` cluster. Flag these for manual review.

2. **Shared clusters across labels**: Some Claude clusters appear as candidates for multiple ChatGPT labels:
   - `need_hybrid_neurosymbolic` → `agi_timeline` (low) + `reasoning_common_sense` (medium) + `scaling_limits` (medium)
   - `llms_unreliable_for_critical_apps` → `agents_reliability` (low) + `safety_alignment` (medium) + `self_driving_robotics` (low)
   - `scaling_wont_reach_agi` → `agi_timeline` (medium) + `scaling_limits` (high)
   - `industry_self_regulation_fails` → `openai_governance` (low) + `regulation_policy` (high)

   When a theme3 maps to one of these shared clusters, use `target_mode` to disambiguate.

3. **Claim count asymmetry**: Claude extracted 2,218 individual claims; ChatGPT tracked 645 claim occurrences across 164 themes. This ~3.4x ratio means Claude was more inclusive in what counts as a "claim." The aggregation step should normalize (use percentages, not raw counts).

4. **self_driving_robotics is the weakest link**: No high-confidence Claude cluster match exists. Consider leaving this label as `bridge_confidence = low` across the board and noting it in the reconciliation doc.

---

## Next Steps

1. **ChatGPT takes this crosswalk** and refines to theme3-level using target_mode + date overlap.
2. For each theme3, select the single best-fit Claude cluster (or mark unmapped).
3. Aggregate Claude claim verdicts per theme3 (filtered to matched cluster + date range).
4. Compute hybrid status and agreement bands per the thresholds agreed above.
5. Output: `chatgpt_hybrid_claim_bridge.csv`, `chatgpt_hybrid_reconciliation.csv`, `chatgpt_HYBRID_RECONCILIATION.md`.
