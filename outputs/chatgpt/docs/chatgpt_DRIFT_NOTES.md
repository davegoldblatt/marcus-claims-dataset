# Drift Notes

## Logic
- Unit analyzed: sequential cluster2 members within each Theme3.
- Horizon drift compares `horizon_values` specificity and timeline direction.
- Certainty drift compares hedge vs strong-assertion wording in representative quotes.
- Lexical drift = 1 - Jaccard(token overlap) between consecutive quotes.
- Drift score per step: +1 horizon loosen/push/change, +1 softened certainty, +1 high lexical drift (>0.65).

## Aggregate Drift Signals
- total transitions: 450
- horizon drift counts: stable:342, more_specific:52, less_specific:51, deadline_pushed_out:4, deadline_pulled_in:1
- certainty drift counts: stable:370, changed:68, hardened:7, softened:5

## Highest-Drift Themes
- theme3_8546265138f1 | self_driving_robotics | clusters=2 | avg_step_drift=2.00
- theme3_8e4a7ba67b7e | safety_alignment | clusters=2 | avg_step_drift=2.00
- theme3_df801cea5953 | agi_timeline | clusters=2 | avg_step_drift=2.00
- theme3_e0bf578dbd19 | openai_governance | clusters=2 | avg_step_drift=2.00
- theme3_c5056806d534 | agi_timeline | clusters=4 | avg_step_drift=1.67
- theme3_1171c23b8fe5 | openai_governance | clusters=3 | avg_step_drift=1.50
- theme3_2cc418f5064a | scaling_limits | clusters=5 | avg_step_drift=1.50
- theme3_7e94375ad3bc | regulation_policy | clusters=3 | avg_step_drift=1.50
- theme3_d9446e6d7328 | hallucination_misinformation | clusters=3 | avg_step_drift=1.50
- theme3_64bd8b6d3a0f | agents_reliability | clusters=6 | avg_step_drift=1.40
- theme3_315a8368ec1c | scaling_limits | clusters=4 | avg_step_drift=1.33
- theme3_35dcaa96810a | safety_alignment | clusters=4 | avg_step_drift=1.33
- theme3_a708e869f9a5 | hallucination_misinformation | clusters=7 | avg_step_drift=1.33
- theme3_03bbb277b41d | copyright_ip | clusters=8 | avg_step_drift=1.29
- theme3_0572199dc099 | reasoning_common_sense | clusters=8 | avg_step_drift=1.29
- theme3_1229d1997f18 | market_hype_bubble | clusters=8 | avg_step_drift=1.29
- theme3_051f3b425aa5 | reasoning_common_sense | clusters=9 | avg_step_drift=1.25
- theme3_0fb5a9767582 | reasoning_common_sense | clusters=13 | avg_step_drift=1.25
- theme3_172e5150cd97 | scaling_limits | clusters=5 | avg_step_drift=1.25
- theme3_9afbf59166e9 | copyright_ip | clusters=9 | avg_step_drift=1.25
- theme3_aa23f30fb332 | safety_alignment | clusters=5 | avg_step_drift=1.25
- theme3_fa38c07be4e7 | safety_alignment | clusters=5 | avg_step_drift=1.25
- theme3_3c553598e33f | agi_timeline | clusters=40 | avg_step_drift=1.23
- theme3_5bb7238346d7 | reasoning_common_sense | clusters=6 | avg_step_drift=1.20
- theme3_e8ec12058b83 | agi_timeline | clusters=6 | avg_step_drift=1.20

## How To Use
- Start with rows where `drift_score >= 2` in `outputs/chatgpt/data/chatgpt_CLAIM_DRIFT_LEDGER.csv`.
- Manually inspect the `from_quote` -> `to_quote` transitions for genuine goalpost movement vs topic branching.
