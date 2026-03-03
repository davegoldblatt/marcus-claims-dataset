# How To Use This Dataset

## Purpose

This dataset tracks Gary Marcus AI-related claims from Substack, with:
- extracted claims,
- canonical/theme clustering,
- goalpost-shift flags,
- and theme-level correctness adjudication (as-of 2026-03-02).

## Start Here

1. Read `outputs/chatgpt/docs/chatgpt_FINAL_RESULTS.md` for top-line findings.
2. Use `outputs/chatgpt/tables/chatgpt_claims_master.csv` as the master analysis table.
3. Use `outputs/chatgpt/tables/chatgpt_adjudicable_only.csv` for truth-status analysis.
4. Use `outputs/chatgpt/tables/chatgpt_goalpost_flagged.csv` for goalpost-shift review.

## File Map

- `posts/`:
  Raw downloaded Substack post text files.

- `outputs/chatgpt/data/chatgpt_first_pass_claims.csv`:
  Sentence-level extracted claim instances.

- `outputs/chatgpt/data/chatgpt_first_pass_canonical.csv`:
  Deduplicated canonical claims from pass 1.

- `outputs/chatgpt/data/chatgpt_second_pass_clustered_claims.csv`:
  Pass-2 cluster rollups.

- `outputs/chatgpt/data/chatgpt_third_pass_themes.csv`:
  One-level-up Theme3 groups (all).

- `outputs/chatgpt/data/chatgpt_third_pass_themes_signal.csv`:
  Theme3 groups excluding `general_misc`.

- `outputs/chatgpt/data/chatgpt_goalpost_shift_audit.csv`:
  Goalpost-shift scoring and flags.

- `outputs/chatgpt/data/chatgpt_correctness_refined_v2_scorecard.csv`:
  Vendor-balanced, high-precision theme-level correctness labels.

- `outputs/chatgpt/tables/chatgpt_claims_master.csv`:
  Unified theme-level table (theme + goalpost + correctness).

## Recommended Analysis Sequence

1. **Coverage check**:
   Confirm row counts match `outputs/chatgpt/docs/chatgpt_FINAL_RESULTS.md`.

2. **Theme-level analysis**:
   Use `outputs/chatgpt/tables/chatgpt_claims_master.csv`.
   Key columns:
   - `theme_label`, `target_mode`, `claim_type_mode`
   - `claim_occurrences`
   - `goalpost_shift_flag`, `goalpost_shift_score`
   - `status_at_eval`, `confidence`

3. **Goalpost analysis**:
   Filter `goalpost_shift_flag == yes`.
   Review `horizon_shift_type` and `certainty_shift`.

4. **Correctness analysis**:
   Use `outputs/chatgpt/tables/chatgpt_adjudicable_only.csv` for distribution summaries.
   Keep `unresolved` and `untestable` separate from wrong/right rates.

5. **Audit trail**:
   For any theme, use `cluster2_ids` and `source_urls` in `outputs/chatgpt/tables/chatgpt_claims_master.csv`.
   Then drill into `outputs/chatgpt/data/chatgpt_third_pass_theme_members.csv` and source quotes.

## Interpretation Rules

- `supported` does not mean universally true, only supported by current evidence for that theme.
- `contradicted` is reserved for clear conflicts with documented facts.
- `mixed` means explicit bidirectional evidence exists.
- `unresolved` means not enough specificity or deadline closure.
- `untestable` usually maps to normative/prescriptive claims.

## Known Limits

- Theme-level labels can hide claim-level variation.
- Goalpost flags are heuristic, not definitive.
- Some posts are truncated/paywalled.
- Quotes can include noisy context from scraped text.

## Reproducibility

Main scripts:
- `outputs/chatgpt/scripts/chatgpt_first_pass_canonical_extractor.py`
- `outputs/chatgpt/scripts/chatgpt_second_pass_cluster.py`
- `outputs/chatgpt/scripts/chatgpt_third_pass_merge.py`
- `outputs/chatgpt/scripts/chatgpt_goalpost_shift_pass.py`
- `outputs/chatgpt/scripts/chatgpt_correctness_refine_precision.py`

Run order is the same as listed above.
