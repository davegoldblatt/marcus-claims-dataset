# Hybrid Reconciliation

## Logic
- Direction: ChatGPT theme3 -> Claude cluster (many-to-one).
- Mapping priority: crosswalk confidence + target compatibility + date overlap (precision-first).
- Low-confidence mappings are retained but marked `manual_review=yes`.
- Orphan/unmapped themes are not force-fit.
- Claude verdict aggregation uses claim-level statuses from `claude_claims_final.jsonl` filtered to theme date window when possible.
- Hybrid status thresholds follow Claude-proposed rules.

## Mapping Summary
- themes processed: 164
- mapped: 160
- mapped_medium_weak_target: 4
- bridge_confidence: high:154, medium:6, low:4
- manual_review rows: 39

## Hybrid Status Summary
- contradicted: 2
- lean_contradicted: 6
- lean_supported: 26
- mixed_or_unresolved: 115
- supported: 15
- agreement_band: low:2, medium:145, high:17

## Caveats
- Crosswalk granularity mismatch remains: 164 theme3 rows vs 54 Claude clusters.
- Shared Claude clusters across multiple labels require target-based disambiguation; marked for manual review.
- `copyright_ip` and `self_driving_robotics` mappings are weaker and should be audited first.
- Percent-based comparison is preferred over raw counts due to extraction density asymmetry.
- Claude orphan clusters (not represented in ChatGPT's 11-label taxonomy) are listed in `outputs/chatgpt/tables/chatgpt_hybrid_orphan_claude_clusters.csv` (10 clusters, 263 claims).
