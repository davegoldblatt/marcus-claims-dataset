# Meta Narrative

## Logic
- Unit analyzed: Theme3 rows from `outputs/chatgpt/tables/chatgpt_claims_master.csv`.
- Weighting: `claim_occurrences` per theme.
- Year assignment: theme `first_date` year.
- Abstraction: theme labels mapped to meta pillars (capability limits, AGI trajectory, safety/governance, market cycle, deployment case studies).
- Status view: counts of theme-level `status_at_eval` by pillar.

## Narrative Arc
- 2022: dominant pillars -> safety_governance:26, capability_limits:6, agi_trajectory:1
- 2023: dominant pillars -> safety_governance:199, capability_limits:180, agi_trajectory:100
- 2024: dominant pillars -> capability_limits:33, safety_governance:14, agi_trajectory:11
- 2025: dominant pillars -> capability_limits:18, safety_governance:8, market_cycle:7
- 2026: dominant pillars -> capability_limits:2, safety_governance:2

## Pillar Summary
- safety_governance: occurrences=249, themes=55, supported=0, contradicted=2, mixed=25, unresolved=14, untestable=14
- capability_limits: occurrences=239, themes=73, supported=16, contradicted=0, mixed=0, unresolved=37, untestable=20
- agi_trajectory: occurrences=116, themes=16, supported=0, contradicted=0, mixed=0, unresolved=11, untestable=5
- market_cycle: occurrences=29, themes=10, supported=0, contradicted=0, mixed=0, unresolved=8, untestable=2
- deployment_case_studies: occurrences=12, themes=10, supported=0, contradicted=0, mixed=0, unresolved=6, untestable=4

## Interpretation
- The dominant macro story is persistent capability skepticism (reasoning/hallucination/scaling limits) plus sustained governance/safety focus.
- AGI timeline discussion remains high-volume but mostly unresolved at current evaluation date.
- Market-cycle claims exist but are secondary relative to technical/safety narratives.
