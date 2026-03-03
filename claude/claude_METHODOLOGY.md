# Marcus Claims Extraction — Methodology

## Goal

Build a canonical, structured dataset of every testable claim Gary Marcus has made about AI on his Substack (garymarcus.substack.com), spanning May 2022 through March 2026. Then analyze for patterns: repetition, goalpost movement, falsifiability, and outcomes.

## Corpus

- **Source**: 474 Substack posts downloaded as plain text files
- **Location**: `../posts/YYYY-MM-DD_slug.txt` (shared corpus at project root)
- **Coverage**: 2022-05-29 through 2026-03-01
- **Limitations**: Some subscriber-only posts may be truncated. Downloaded content is what was publicly accessible as of 2026-03-02.

---

## Pass 1: Raw Claim Extraction

### What counts as a "claim"

A claim is a **testable proposition about AI** — not every sentence, not rhetorical questions, not summaries of others' positions (unless Marcus explicitly endorses them).

#### Four claim types:

| Type | Definition | Example form |
|------|-----------|--------------|
| **Descriptive** | How AI systems are or behave now | "LLMs are unreliable for X" |
| **Predictive** | What will happen by some time | "AGI won't arrive in most people's lifetimes" |
| **Causal** | X leads to / causes Y | "Scaling-only approaches lead to failure on reasoning" |
| **Normative** | What should be done | "We need federal law against AI impersonation" |

#### What to include:
- Marcus's own assertions (stated as his position)
- Claims he explicitly endorses from others ("X is right that...")
- Implied claims strong enough to paraphrase (e.g., a sarcastic headline that clearly asserts something)

#### What to exclude:
- Rhetorical questions without a clear implied answer
- Pure reporting of others' positions without endorsement
- Personal anecdotes, obituaries, non-AI content
- Meta-commentary about his own blog/writing
- Links or quotes presented neutrally for reader consideration

### Output schema (one JSON object per claim):

```json
{
  "id": "claim_0001",
  "claim_date": "2023-02-16",
  "slug": "agi-will-not-happen-in-your-lifetime",
  "trigger": "ChatGPT hype cycle / general industry optimism",
  "quote": "Exact quote from the post, verbatim",
  "claim": "Normalized paraphrase: AGI will not arrive in most people's lifetimes",
  "type": "predictive",
  "target": "AGI",
  "horizon_type": "relative",
  "horizon_value": "within_lifetime"
}
```

#### Field definitions:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Sequential unique ID: `claim_NNNN` |
| `claim_date` | string | ISO date of the post: `YYYY-MM-DD` |
| `slug` | string | Post slug from filename |
| `trigger` | string | What event/announcement prompted the post, if identifiable. "none" if it's self-initiated. |
| `quote` | string | Exact verbatim quote from the post. Keep it tight — the specific sentence(s) containing the claim. |
| `claim` | string | Normalized paraphrase. Should be a standalone sentence that captures the proposition. |
| `type` | enum | One of: `descriptive`, `predictive`, `causal`, `normative` |
| `target` | string | What the claim is about: a company (OpenAI, Google, Tesla), technology (LLMs, AGI, self-driving), concept (scaling, hallucination), or domain (regulation, safety) |
| `horizon_type` | enum | `explicit_date` (claim references a specific date/year), `relative` (claim uses relative timeframe like "within a decade"), `none` (no temporal bound) |
| `horizon_value` | string or null | The timeframe if applicable: `"2030-12-31"`, `"within_10_years"`, `"within_lifetime"`, or `null` |

### Extraction rules:

1. **One claim per object.** If a single quote contains multiple distinct claims, split them.
2. **Prefer direct quotes.** The `quote` field should be copy-pasted from the post, not paraphrased.
3. **Normalize in `claim` field.** The paraphrase should be context-free — understandable without reading the post.
4. **Be conservative with `trigger`.** Only assign a trigger if the post clearly responds to a specific event. Don't guess.
5. **Don't editorialize.** Pass 1 is extraction only. No judgment on correctness, specificity, or falsifiability.

### Output file:

`./claude_claims_raw.jsonl` — one JSON object per line, sequential IDs starting at `claim_0001`.

---

## Pass 2: Analysis & Scoring

Performed on `claude_claims_raw.jsonl` without re-reading the original posts.

### Per-claim scoring:

| Field | Type | Description |
|-------|------|-------------|
| `specificity` | enum | `high` (specific system, measurable outcome, timeframe), `med` (some specifics but vague on others), `low` (broad/unfalsifiable) |
| `falsifiability` | enum | `yes` (clear subject + measurable predicate + timeframe + threshold), `partial` (missing one or two of those), `no` (pure value judgment or too vague) |
| `evaluation_date` | string | Fixed anchor: `2026-03-02` |
| `status_at_eval` | enum | `pending` (not yet testable), `supported` (evidence favors claim), `contradicted` (evidence contradicts), `mixed` (evidence is ambiguous), `untestable` (can't be evaluated as stated) |
| `time_to_resolution_days` | int or null | Days from `claim_date` to resolution, if resolved |
| `revision_of_claim_id` | string or null | If this claim is a restatement/revision of an earlier claim, link to that claim's ID |
| `cluster_id` | string | Thematic cluster: e.g., `scaling_skepticism`, `agi_timeline`, `hallucination_persistent`, `regulation_needed` |

### Falsifiability checklist (applied per claim):

1. Is there a **clear subject** (what system/technology)?
2. Is there a **measurable predicate** (what outcome)?
3. Is there a **timeframe** (by when)?
4. Is there a **threshold** (how much counts)?

Score: 4/4 = `yes`, 2-3/4 = `partial`, 0-1/4 = `no`.

### Clustering rules:

- Claims are grouped by **proposition**, not by topic. Two claims about LLMs go in different clusters if one is about hallucination and the other is about reasoning.
- A cluster represents a single canonical claim that Marcus makes repeatedly (possibly with variations).
- Cluster IDs are descriptive: `scaling_wont_reach_agi`, `llms_cant_reason`, `ai_bubble_will_burst`, etc.

### Timeline analyses (aggregate):

1. **Survival curve**: How long do claims stay unresolved? Distribution of `time_to_resolution_days`.
2. **Drift tracking**: Per cluster, does `horizon_value` get pushed forward over time? This is the goalpost movement metric.
3. **Cadence**: Repetition rate by quarter/year per cluster. Which claims does he hammer hardest?
4. **Regime shifts**: Do claim patterns change around key events? (ChatGPT launch Nov 2022, GPT-4 Mar 2023, GPT-5, etc.)
5. **Scorecard**: For resolved claims — what's his hit rate? By type, by target, by specificity level.

### Output files:

- `./claude_claims_scored.jsonl` — enriched version of `claude_claims_raw.jsonl` with pass 2 fields added
- `./claude_claims_canonical.csv` — deduplicated canonical claims with cluster rollups
- `./claude_second_pass_audit.csv` — goalpost shifts, repetition patterns, outcome tracking
- `./claude_analysis_memo.md` — narrative summary of findings

---

## Known Limitations & Consistency Risks

This extraction is LLM-based (Claude, processing posts in parallel batches). It is a strong first draft, not ground truth. The following fields have known consistency risks:

### Reliable (deterministic or near-deterministic):
- `id` — sequential, assigned post-extraction
- `claim_date` — parsed from filename, deterministic
- `slug` — parsed from filename, deterministic
- `quote` — copy-pasted from source text
- `type` — four clear categories, low ambiguity for most claims

### Moderately reliable (judgment calls, but constrained):
- `claim` — normalized paraphrase. Different agents may word these differently, but the underlying proposition should be the same
- `target` — usually obvious, but some claims touch multiple targets. Extractor picks the primary one.
- `horizon_type` / `horizon_value` — reliable when Marcus uses explicit dates or timeframes ("by 2030", "within a decade"). Unreliable when timeframes are implied or vague ("anytime soon", "not yet"). Extractor defaults to `none`/`null` when unsure rather than guessing.

### Least reliable (requires world knowledge or subjective judgment):
- `trigger` — requires knowing what event a post responds to. Obvious triggers (GPT-4 launch, Bing Sydney incident) will be caught. Subtler ones (a specific tweet, an industry report) may be missed or described inconsistently across batches. Extractor uses `"none"` when not clearly identifiable rather than speculating.
- **Inclusion/exclusion boundary** — whether a given sentence is a "claim" vs. rhetoric is a judgment call. Different batches may have slightly different thresholds. The extraction prompt instructs agents to err on the side of inclusion (extract it, let pass 2 filter).

### Deferred to pass 2 (not attempted in pass 1):
- `revision_of_claim_id` — requires cross-referencing the full claim set
- `cluster_id` — requires seeing all claims first
- `specificity`, `falsifiability`, `status_at_eval` — scoring/judgment
- `time_to_resolution_days` — requires outcome assessment
- All timeline analyses (survival curves, drift tracking, cadence, regime shifts)

### Batch consistency:
- Posts are processed in chronological batches of ~15-20 by parallel agents
- Each agent receives the same extraction prompt and schema
- IDs are assigned sequentially after all batches complete (not during extraction) to avoid gaps/collisions
- Agents do not see each other's output — there is no cross-batch deduplication in pass 1

---

## Process Notes

- Pass 1 is performed by reading posts in batches (~15-20 posts per batch) and extracting claims into per-batch output files, then merged into `claude_claims_raw.jsonl` with sequential IDs.
- Pass 2 is performed entirely from `claude_claims_raw.jsonl` without re-reading posts.
- All Claude outputs live in `claude/` under the project root (`~/Desktop/marcus_scrape/claude/`).
- Results should be treated as a strong first draft, not ground truth. Spot-checking against original posts is recommended for any claim used in a published analysis.
- Batches are processed in chronological order.
