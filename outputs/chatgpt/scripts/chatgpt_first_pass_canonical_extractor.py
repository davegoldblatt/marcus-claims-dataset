#!/usr/bin/env python3
"""First-pass canonical claim extraction for Gary Marcus Substack corpus.

Outputs:
- first_pass_claims.csv: extracted claim instances (sentence-level)
- first_pass_canonical.csv: canonicalized/deduplicated claim groups
- first_pass_report.txt: extraction diagnostics
"""

from __future__ import annotations

import csv
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
CLAIMS_OUT = ROOT / "first_pass_claims.csv"
CANON_OUT = ROOT / "first_pass_canonical.csv"
REPORT_OUT = ROOT / "first_pass_report.txt"

BASE_URL = "https://garymarcus.substack.com/p/"
EVAL_DATE = "2026-03-02"

AI_KEYWORDS = re.compile(
    r"\b(ai|agi|llm|llms|gpt|chatgpt|claude|gemini|large language model|"
    r"machine learning|deep learning|neural|transformer|self-driving|autonomous|"
    r"hallucination|alignment|safety|misinformation|chatbot|model)\b",
    re.IGNORECASE,
)

CLAIM_MARKERS = re.compile(
    r"\b(i think|i believe|i expect|i predict|i worry|i suspect|i doubt|"
    r"i argue|i contend|i maintain|"
    r"will|won't|cannot|can't|should|must|need to|likely|unlikely|"
    r"is not|are not|isn't|aren't|"
    r"never|always|impossible|possible|"
    r"at risk|danger|harm)\b",
    re.IGNORECASE,
)

MEASURABLE_MARKERS = re.compile(
    r"\b(reliable|accuracy|benchmark|hallucinat|error|safety|risk|"
    r"reason|common sense|truthful|deployment|adoption|revenue|profit|"
    r"bubble|burst|crash|fail|succeed|regulat|law|ban|timeline)\b",
    re.IGNORECASE,
)

POLICY_MARKERS = re.compile(r"\b(should|must|need to|regulat|law|policy|ban|oversight|govern)\b", re.IGNORECASE)
PREDICT_MARKERS = re.compile(r"\b(will|won't|soon|future|decade|year|by\s+\d{4}|in\s+\d{4})\b", re.IGNORECASE)
CAUSAL_MARKERS = re.compile(r"\b(cause|lead to|drives?|results? in|because|therefore|hence)\b", re.IGNORECASE)

TECH_MARKERS = re.compile(
    r"\b(reason|common sense|semantics|symbolic|neurosymbolic|hallucinat|"
    r"scaling|architecture|transformer|training|inference|alignment)\b",
    re.IGNORECASE,
)
MARKET_MARKERS = re.compile(r"\b(bubble|market|valuation|revenue|profit|business model|scam|winter)\b", re.IGNORECASE)
CAPABILITY_MARKERS = re.compile(r"\b(can't|cannot|unable|reliable|works?|fails?|not near|nowhere near|solve)\b", re.IGNORECASE)

SKIP_PHRASES = (
    "this substack is reader-supported",
    "thanks for reading",
    "subscribe now",
    "gift a subscription",
    "restack",
    "reposts",
    "likes",
    "his most recent book",
    "gary marcus is",
    "(@garymarcus), scientist, bestselling author, and entrepreneur",
    "scientist, bestselling author, and entrepreneur",
    "marcus on ai",
)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"(])")
YEAR_RE = re.compile(r"\b(20\d{2})\b")
SKIP_PREFIX_RE = re.compile(r"^(subscribe|share|listen now|gift a subscription)\b", re.IGNORECASE)

TARGET_RULES = [
    ("openai", re.compile(r"\bopenai|sam altman\b", re.IGNORECASE)),
    ("google", re.compile(r"\bgoogle|deepmind|demis\b", re.IGNORECASE)),
    ("meta", re.compile(r"\bmeta|zuckerberg\b", re.IGNORECASE)),
    ("microsoft", re.compile(r"\bmicrosoft|bing\b", re.IGNORECASE)),
    ("tesla", re.compile(r"\btesla|fsd|full self-driving|autopilot|elon\b", re.IGNORECASE)),
    ("anthropic", re.compile(r"\banthropic|claude\b", re.IGNORECASE)),
    ("agi", re.compile(r"\bagi|artificial general intelligence\b", re.IGNORECASE)),
    ("llms", re.compile(r"\bllm|large language model|gpt|chatgpt|gemini\b", re.IGNORECASE)),
    ("regulation", re.compile(r"\bregulat|law|policy|oversight|government\b", re.IGNORECASE)),
    ("ai_safety", re.compile(r"\balignment|safety|harm|risk|misinformation|cybercrime\b", re.IGNORECASE)),
]


@dataclass
class Claim:
    claim_id: str
    claim_date: str
    slug: str
    title: str
    url: str
    quote: str
    canonical_claim: str
    canonical_norm: str
    category: str
    claim_type: str
    falsifiability_tier: str
    target: str
    horizon_type: str
    horizon_value: str
    evaluation_date: str
    source_file: str


def normalize_ws(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[\t\r]+", " ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()


def parse_post(path: Path) -> tuple[str, str, str, str, str]:
    m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+)\.txt$", path.name)
    if m:
        claim_date, slug = m.group(1), m.group(2)
    else:
        claim_date, slug = "unknown", path.stem

    title = ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    body_lines = []
    for ln in lines:
        if ln.startswith("TITLE:"):
            title = ln.split(":", 1)[1].strip()
            continue
        if ln.startswith("SUBTITLE:") or ln.startswith("DATE:"):
            continue
        body_lines.append(ln)

    body = normalize_ws("\n".join(body_lines))
    url = BASE_URL + slug
    return claim_date, slug, title, url, body


def iter_sentences(text: str):
    flat = normalize_ws(text.replace("\n", " "))
    for s in SENTENCE_SPLIT.split(flat):
        s = normalize_ws(s)
        if len(s) < 35 or len(s) > 500:
            continue
        low = s.lower()
        if SKIP_PREFIX_RE.search(s):
            continue
        if any(p in low for p in SKIP_PHRASES):
            continue
        if "@" in s and "reposts" in low and "likes" in low:
            continue
        yield s


def infer_target(sentence: str) -> str:
    for name, rx in TARGET_RULES:
        if rx.search(sentence):
            return name
    return "general_ai"


def infer_category(sentence: str) -> str:
    if POLICY_MARKERS.search(sentence):
        return "policy"
    if MARKET_MARKERS.search(sentence):
        return "industry_market"
    if CAPABILITY_MARKERS.search(sentence):
        return "capability"
    if PREDICT_MARKERS.search(sentence):
        return "prediction"
    if TECH_MARKERS.search(sentence):
        return "technical_assessment"
    return "technical_assessment"


def infer_claim_type(sentence: str) -> str:
    if POLICY_MARKERS.search(sentence):
        return "normative"
    if CAUSAL_MARKERS.search(sentence):
        return "causal"
    if PREDICT_MARKERS.search(sentence):
        return "predictive"
    return "descriptive"


def infer_horizon(sentence: str) -> tuple[str, str]:
    m = YEAR_RE.search(sentence)
    if m:
        return "explicit_date", f"{m.group(1)}-12-31"

    s = sentence.lower()
    if "within a decade" in s or "next decade" in s:
        return "relative", "within_10_years"
    if "this decade" in s:
        return "relative", "this_decade"
    if "in your lifetime" in s or "in our lifetime" in s:
        return "relative", "within_lifetime"
    if "soon" in s or "near term" in s:
        return "relative", "near_term"
    return "none", ""


def canonicalize(sentence: str) -> str:
    s = sentence.lower()
    s = re.sub(r"\bi\s+(think|believe|expect|predict|suspect|worry|argue|contend)\b", "", s)
    s = re.sub(r"https?://\S+", "", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def infer_falsifiability_tier(sentence: str, claim_type: str, target: str, horizon_type: str) -> str:
    if claim_type == "normative":
        return "tier_3"

    score = 0
    if target != "general_ai" or AI_KEYWORDS.search(sentence):
        score += 1
    if MEASURABLE_MARKERS.search(sentence) or CAPABILITY_MARKERS.search(sentence):
        score += 1
    if horizon_type != "none":
        score += 1
    if re.search(r"\b(\d+|reliably|at scale|most|all|none|always|never)\b", sentence, re.IGNORECASE):
        score += 1

    if score >= 3:
        return "tier_1"
    if score == 2:
        return "tier_2"
    return "tier_3"


def extract_claims() -> list[Claim]:
    claims: list[Claim] = []
    cid = 1
    for post in sorted(POSTS_DIR.glob("*.txt")):
        claim_date, slug, title, url, body = parse_post(post)
        for sentence in iter_sentences(body):
            if not AI_KEYWORDS.search(sentence):
                continue
            if not CLAIM_MARKERS.search(sentence):
                continue

            category = infer_category(sentence)
            claim_type = infer_claim_type(sentence)
            target = infer_target(sentence)
            horizon_type, horizon_value = infer_horizon(sentence)
            canonical_norm = canonicalize(sentence)
            tier = infer_falsifiability_tier(sentence, claim_type, target, horizon_type)

            if len(canonical_norm) < 20:
                continue

            claims.append(
                Claim(
                    claim_id=f"claim_{cid:05d}",
                    claim_date=claim_date,
                    slug=slug,
                    title=title,
                    url=url,
                    quote=sentence,
                    canonical_claim=sentence,
                    canonical_norm=canonical_norm,
                    category=category,
                    claim_type=claim_type,
                    falsifiability_tier=tier,
                    target=target,
                    horizon_type=horizon_type,
                    horizon_value=horizon_value,
                    evaluation_date=EVAL_DATE,
                    source_file=str(post),
                )
            )
            cid += 1
    return claims


def write_claim_instances(claims: list[Claim]) -> None:
    with CLAIMS_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "claim_id",
                "claim_date",
                "slug",
                "title",
                "url",
                "quote",
                "canonical_claim",
                "canonical_norm",
                "category",
                "claim_type",
                "falsifiability_tier",
                "target",
                "horizon_type",
                "horizon_value",
                "evaluation_date",
                "source_file",
            ]
        )
        for c in sorted(claims, key=lambda x: (x.claim_date, x.slug, x.claim_id)):
            w.writerow(
                [
                    c.claim_id,
                    c.claim_date,
                    c.slug,
                    c.title,
                    c.url,
                    c.quote,
                    c.canonical_claim,
                    c.canonical_norm,
                    c.category,
                    c.claim_type,
                    c.falsifiability_tier,
                    c.target,
                    c.horizon_type,
                    c.horizon_value,
                    c.evaluation_date,
                    c.source_file,
                ]
            )


def write_canonical(claims: list[Claim]) -> None:
    grouped: dict[str, list[Claim]] = defaultdict(list)
    for c in claims:
        grouped[c.canonical_norm].append(c)

    with CANON_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "cluster_id",
                "canonical_norm",
                "representative_claim",
                "category_mode",
                "claim_type_mode",
                "falsifiability_tier_mode",
                "target_mode",
                "first_date",
                "last_date",
                "occurrences",
                "source_posts",
                "source_urls",
                "supporting_claim_ids",
            ]
        )

        for norm, items in sorted(grouped.items(), key=lambda kv: (len(kv[1]), kv[0]), reverse=True):
            if not norm:
                continue
            dates = sorted([x.claim_date for x in items if x.claim_date != "unknown"])
            first_date = dates[0] if dates else "unknown"
            last_date = dates[-1] if dates else "unknown"
            posts = sorted({x.slug for x in items})
            urls = sorted({x.url for x in items})
            ids = sorted({x.claim_id for x in items})

            def mode(vals: list[str]) -> str:
                counts = defaultdict(int)
                for v in vals:
                    counts[v] += 1
                return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

            rep = sorted(items, key=lambda x: (x.claim_date, len(x.quote)))[0].quote
            cluster_id = "cluster_" + hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]

            w.writerow(
                [
                    cluster_id,
                    norm,
                    rep,
                    mode([x.category for x in items]),
                    mode([x.claim_type for x in items]),
                    mode([x.falsifiability_tier for x in items]),
                    mode([x.target for x in items]),
                    first_date,
                    last_date,
                    len(items),
                    ";".join(posts),
                    ";".join(urls),
                    ";".join(ids),
                ]
            )


def write_report(claims: list[Claim]) -> None:
    canon_rows = sum(1 for _ in open(CANON_OUT, "r", encoding="utf-8")) - 1
    tiny_files = [p.name for p in POSTS_DIR.glob("*.txt") if p.stat().st_size < 500]

    by_cat = defaultdict(int)
    by_tier = defaultdict(int)
    for c in claims:
        by_cat[c.category] += 1
        by_tier[c.falsifiability_tier] += 1

    with REPORT_OUT.open("w", encoding="utf-8") as f:
        f.write("First-pass canonical extraction report\n")
        f.write(f"Run timestamp: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Posts scanned: {len(list(POSTS_DIR.glob('*.txt')))}\n")
        f.write(f"Claim instances: {len(claims)}\n")
        f.write(f"Canonical clusters: {canon_rows}\n")
        f.write(f"Evaluation date anchor: {EVAL_DATE}\n")
        f.write("\nCategory counts:\n")
        for k in sorted(by_cat):
            f.write(f"- {k}: {by_cat[k]}\n")
        f.write("\nFalsifiability tier counts:\n")
        for k in sorted(by_tier):
            f.write(f"- {k}: {by_tier[k]}\n")
        f.write(f"\nVery short post files (<500 bytes): {len(tiny_files)}\n")
        if tiny_files:
            for name in sorted(tiny_files)[:50]:
                f.write(f"- {name}\n")
        f.write("\nCaveat: deterministic heuristics; includes false positives/negatives.\n")


def main() -> None:
    if not POSTS_DIR.exists():
        raise SystemExit(f"Missing posts directory: {POSTS_DIR}")

    claims = extract_claims()
    write_claim_instances(claims)
    write_canonical(claims)
    write_report(claims)

    print(f"Wrote {CLAIMS_OUT}")
    print(f"Wrote {CANON_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(f"Claim instances: {len(claims)}")


if __name__ == "__main__":
    main()
