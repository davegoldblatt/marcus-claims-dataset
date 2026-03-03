# One-Level-Up Output (Theme3)

## What This Is

Third-pass synthesis that merges second-pass clusters into broader themes using:
- `target_mode`
- `claim_type_mode`
- topic bucket rules

## Core Files

- `outputs/chatgpt/data/chatgpt_third_pass_themes.csv` (all Theme3 groups)
- `outputs/chatgpt/data/chatgpt_third_pass_theme_members.csv` (Theme3 -> cluster2 mapping)
- `outputs/chatgpt/data/chatgpt_third_pass_themes_signal.csv` (Theme3 excluding `general_misc`)
- `outputs/chatgpt/data/chatgpt_third_pass_report.txt` (run metrics)
- `ANALYSIS_MEMO.md` (narrative summary)
- `THIRD_PASS_LOGIC.md` (method)

## Metrics (current run)

- Input cluster2 rows: **1087**
- Theme3 rows: **186**
- Themes merging >1 cluster2: **108**
- Goalpost candidates: **17**

## Signal-First View

Use `outputs/chatgpt/data/chatgpt_third_pass_themes_signal.csv` first. It removes catch-all `general_misc` and surfaces interpretable themes like:
- `agi_timeline`
- `openai_governance`
- `reasoning_common_sense`
- `regulation_policy`
- `safety_alignment`
- `hallucination_misinformation`
- `scaling_limits`

## Recommended Next Step

For final adjudication (goalposts/repetition), operate on:
1. `outputs/chatgpt/data/chatgpt_third_pass_themes_signal.csv`
2. `outputs/chatgpt/data/chatgpt_third_pass_theme_members.csv`
3. source claims in `first_pass_claims.csv`

This keeps the review focused on substantive themes while preserving full auditability.
