# First-Pass Canonical Claim Logic (Implemented)

This document is the executable logic spec for `outputs/chatgpt/scripts/chatgpt_first_pass_canonical_extractor.py`.
It describes what the current code actually does.

## Scope

- Corpus: `./posts/*.txt` (474 files)
- Date parsed from filename: `YYYY-MM-DD_slug.txt`
- Evaluation anchor date written to each row: `2026-03-02`

## Output Artifacts

- `./first_pass_claims.csv`
  - One extracted claim instance per row (sentence-level)
- `./first_pass_canonical.csv`
  - Canonical deduplicated groups by normalized proposition text
- `./first_pass_report.txt`
  - Counts by category/tier and truncation diagnostics

## Claim Inclusion Logic

A sentence is included as a claim instance only if all are true:

1. Sentence length is between 35 and 500 characters.
2. Sentence does not match skip filters (boilerplate/subscription/social metadata).
3. Sentence matches AI keyword filter (e.g., `ai`, `agi`, `llm`, `gpt`, `chatgpt`, `transformer`, `self-driving`, `alignment`, `misinformation`).
4. Sentence matches claim marker filter (e.g., `will`, `won't`, `cannot`, `can't`, `should`, `must`, `need to`, `likely`, `i think`, `i believe`, `i predict`).

## Skip/Exclusion Logic

The extractor drops sentences when they contain subscription/author boilerplate, including:

- "this substack is reader-supported"
- "thanks for reading"
- "subscribe now"
- "gift a subscription"
- "restack"
- "reposts"
- "likes"
- "his most recent book"
- "gary marcus is"
- "scientist, bestselling author, and entrepreneur"

Also skipped:

- Sentences starting with `subscribe`, `share`, `listen now`, or `gift a subscription`
- Social metadata-like lines containing `@` plus `reposts` and `likes`

## Field Derivation (first_pass_claims.csv)

- `claim_id`: sequential (`claim_00001`, ...)
- `claim_date`: from filename prefix
- `slug`: from filename suffix
- `title`: from `TITLE:` header if present
- `url`: `https://garymarcus.substack.com/p/{slug}`
- `quote`: extracted sentence (verbatim)
- `canonical_claim`: same as `quote` in this pass
- `canonical_norm`: lowercase normalized proposition text (punctuation stripped, some first-person hedges removed)
- `category`: one of
  - `policy`
  - `industry_market`
  - `capability`
  - `prediction`
  - `technical_assessment`
- `claim_type`: one of
  - `normative`
  - `causal`
  - `predictive`
  - `descriptive`
- `falsifiability_tier`: one of `tier_1`, `tier_2`, `tier_3`
- `target`: heuristic target label (e.g., `openai`, `google`, `tesla`, `agi`, `llms`, `regulation`, `ai_safety`, fallback `general_ai`)
- `horizon_type`: `explicit_date | relative | none`
- `horizon_value`: extracted value (e.g., `2030-12-31`, `within_10_years`, `within_lifetime`, `near_term`) else empty
- `evaluation_date`: fixed `2026-03-02`
- `source_file`: absolute source path

## Category Logic

Priority order:

1. If policy markers present -> `policy`
2. Else if market markers present -> `industry_market`
3. Else if capability markers present -> `capability`
4. Else if prediction markers present -> `prediction`
5. Else if technical markers present -> `technical_assessment`
6. Else -> `technical_assessment`

## Claim Type Logic

Priority order:

1. `normative` if policy markers present
2. `causal` if causal connectors present
3. `predictive` if future/timeline markers present
4. Else `descriptive`

## Temporal/Horizon Logic

- `explicit_date`: first detected year `20XX` converted to `20XX-12-31`
- `relative`: phrases like `within a decade`, `next decade`, `this decade`, `in your lifetime`, `soon`, `near term`
- `none`: no temporal phrase found

## Falsifiability Tier Logic

- `tier_3` directly if `claim_type == normative`
- Otherwise score 4 binary checks:
  1. Has identifiable subject/target
  2. Has measurable predicate markers (reliability/error/risk/reasoning/etc.)
  3. Has temporal horizon (`horizon_type != none`)
  4. Has threshold-like wording (`most`, `all`, `never`, `at scale`, numbers, etc.)

Score mapping:

- 3-4 -> `tier_1`
- 2 -> `tier_2`
- 0-1 -> `tier_3`

## Canonical Grouping Logic (first_pass_canonical.csv)

- Group key: exact `canonical_norm` string
- `cluster_id`: `cluster_` + first 12 chars of SHA1(`canonical_norm`)
- Representative sentence: earliest-date, shorter quote from cluster
- `occurrences`: number of grouped claim instances
- `first_date` / `last_date`: date range of grouped instances
- `source_posts`, `source_urls`, `supporting_claim_ids`: semicolon-delimited lists
- Mode fields (`*_mode`) computed for category/type/tier/target

## Known Limitations

- Deterministic regex heuristics, not semantic reading
- Can miss implicit claims or sarcasm without explicit markers
- Can over-split closely related propositions into separate clusters
- Truncated/paywalled posts reduce recoverable claims
- `trigger_event` is not yet populated in this pass

## Current Run Snapshot (as generated)

- Claim instances: 1151
- Canonical clusters: 1137
- Date range: 2022-05-29 to 2026-03-01

