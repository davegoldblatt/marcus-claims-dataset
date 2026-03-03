# Second-Pass Cluster Logic (Implemented)

This spec reflects the actual behavior of `outputs/chatgpt/scripts/chatgpt_second_pass_cluster.py`.

## Input

- `first_pass_claims.csv` (1151 claim instances in current run)

## Outputs

- `second_pass_clustered_claims.csv` (cluster-level rollups)
- `second_pass_cluster_members.csv` (claim-level cluster membership)
- `second_pass_cluster_report.txt` (run diagnostics)

## Clustering Method

1. Claims are blocked by `target` (e.g., `openai`, `llms`, `agi`, `general_ai`).
2. Within each target block, each claim is compared to existing clusters.
3. Similarity uses a weighted score between claim pairs:
   - token-set Jaccard on normalized text (65%)
   - character trigram Dice similarity (35%)
4. Candidate merge requires:
   - similarity above type-specific threshold
   - lexical overlap of at least one non-generic token, or a non-empty horizon value

## Thresholds by claim_type

- `causal`: 0.32
- `predictive`: 0.34
- `descriptive`: 0.38
- `normative`: 0.40

## Cluster-level fields

- `cluster2_id`: deterministic hash from target block + seed claim
- `theme_label`: top non-generic tokens across member claims
- `first_date`, `last_date`, `occurrences`, `distinct_posts`
- `horizon_values`: semicolon-separated set of horizon values in cluster
- `goalpost_shift_candidate`: `yes` if cluster has 3+ claims and 2+ distinct horizon values
- `representative_quote`: earliest, shorter quote in the cluster
- `supporting_claim_ids`, `source_urls`

## Notes

- This is still conservative; semantic paraphrases can remain in separate clusters.
- Clustering quality depends on first-pass normalization quality.
- `goalpost_shift_candidate` is a heuristic pre-flag, not final adjudication.

