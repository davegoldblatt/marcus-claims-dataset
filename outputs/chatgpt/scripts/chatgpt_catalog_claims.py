#!/usr/bin/env python3
"""Extract and catalog AI-related claims from downloaded Marcus Substack posts.

Outputs:
- claims_raw.csv: one row per extracted claim sentence
- claims_canonical.csv: deduplicated claims with first/last date and source counts
- extraction_report.txt: run summary and caveats
"""

from __future__ import annotations

import csv
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
RAW_OUT = ROOT / "claims_raw.csv"
CANON_OUT = ROOT / "claims_canonical.csv"
REPORT_OUT = ROOT / "extraction_report.txt"

BASE_URL = "https://garymarcus.substack.com/p/"

AI_KEYWORDS = re.compile(
    r"\b(ai|agi|gpt|chatgpt|llm|large language model|machine learning|deep learning|"
    r"neural|transformer|model|robot|autonomous|self-driving|misinformation|"
    r"alignment|hallucination|safety|automation)\b",
    re.IGNORECASE,
)

# Heuristic markers that a sentence is a claim/opinion/prediction.
CLAIM_MARKERS = re.compile(
    r"\b("
    r"i think|i believe|i expect|i predict|i suspect|i worry|i doubt|i argue|i contend|"
    r"i see|i am concerned|i'm concerned|i remain concerned|"
    r"we think|we believe|we expect|we predict|we need|"
    r"will|won't|cannot|can't|should|must|need to|likely|unlikely|"
    r"is not enough|are not enough|isn'?t enough|aren'?t enough"
    r")\b",
    re.IGNORECASE,
)

SKIP_PREFIXES = (
    "subscribe",
    "share",
    "paid subscribers",
    "restack",
    "listen now",
    "gift a subscription",
)

SKIP_PHRASES = (
    "gary marcus is",
    "his most recent book",
    "this substack is reader-supported",
    "thanks for reading",
    "subscribe now",
    "gift a subscription",
    "reposts",
    "likes",
    "become a paid subscriber",
)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"(])")


@dataclass
class Claim:
    date: str
    slug: str
    title: str
    url: str
    category: str
    claim_text: str
    evidence_excerpt: str
    file_path: str


def normalize_whitespace(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[\t\r]+", " ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()


def parse_file(path: Path) -> tuple[str, str, str, str]:
    m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+)\.txt$", path.name)
    if m:
        date, slug = m.group(1), m.group(2)
    else:
        date, slug = "unknown", path.stem

    title = ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    body_lines = []
    for line in lines:
        if line.startswith("TITLE:"):
            title = line.split(":", 1)[1].strip()
            continue
        if line.startswith("SUBTITLE:") or line.startswith("DATE:"):
            continue
        body_lines.append(line)

    body = normalize_whitespace("\n".join(body_lines))
    url = BASE_URL + slug
    return date, slug, title, body


def sentence_candidates(text: str) -> Iterable[str]:
    # Flatten paragraphs to aid sentence segmentation.
    text = text.replace("\n", " ")
    text = normalize_whitespace(text)
    for sent in SENTENCE_SPLIT.split(text):
        s = normalize_whitespace(sent)
        if len(s) < 40 or len(s) > 450:
            continue
        low = s.lower()
        if any(low.startswith(p) for p in SKIP_PREFIXES):
            continue
        if any(phrase in low for phrase in SKIP_PHRASES):
            continue
        yield s


def categorize(sentence: str) -> str:
    s = sentence.lower()
    if re.search(r"\b(will|expect|predict|soon|future|decade|century)\b", s):
        return "forecast"
    if re.search(r"\b(risk|harm|danger|unsafe|safety|suicide|misinformation|cybercrime)\b", s):
        return "risk"
    if re.search(r"\b(regulat|law|policy|govern|ban|oversight)\b", s):
        return "policy"
    if re.search(r"\b(cannot|can't|not enough|won't|fails?|failure|wrong)\b", s):
        return "limitation"
    if re.search(r"\b(need|should|must|neurosymbolic|reasoning|common sense)\b", s):
        return "prescription"
    return "other"


def canonicalize(sentence: str) -> str:
    s = sentence.lower()
    s = re.sub(r"https?://\S+", "", s)
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_claims() -> list[Claim]:
    claims: list[Claim] = []
    files = sorted(POSTS_DIR.glob("*.txt"))
    for p in files:
        date, slug, title, body = parse_file(p)
        if not body:
            continue

        for sent in sentence_candidates(body):
            if not AI_KEYWORDS.search(sent):
                continue
            if not CLAIM_MARKERS.search(sent):
                continue

            claims.append(
                Claim(
                    date=date,
                    slug=slug,
                    title=title,
                    url=BASE_URL + slug,
                    category=categorize(sent),
                    claim_text=sent,
                    evidence_excerpt=sent[:280],
                    file_path=str(p),
                )
            )
    return claims


def write_outputs(claims: list[Claim], file_count: int) -> None:
    with RAW_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "date",
                "slug",
                "title",
                "url",
                "category",
                "claim_text",
                "evidence_excerpt",
                "file_path",
            ]
        )
        for c in sorted(claims, key=lambda x: (x.date, x.slug, x.claim_text)):
            w.writerow(
                [
                    c.date,
                    c.slug,
                    c.title,
                    c.url,
                    c.category,
                    c.claim_text,
                    c.evidence_excerpt,
                    c.file_path,
                ]
            )

    grouped: dict[str, list[Claim]] = defaultdict(list)
    for c in claims:
        grouped[canonicalize(c.claim_text)].append(c)

    with CANON_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "canonical_id",
                "canonical_claim",
                "canonical_norm",
                "category",
                "first_date",
                "last_date",
                "occurrences",
                "source_posts",
                "source_urls",
                "example_url",
            ]
        )
        for canon, items in sorted(grouped.items(), key=lambda kv: (len(kv[1]), kv[0]), reverse=True):
            if not canon:
                continue
            dates = sorted(x.date for x in items if x.date != "unknown")
            first_date = dates[0] if dates else "unknown"
            last_date = dates[-1] if dates else "unknown"
            source_posts = sorted({x.slug for x in items})
            source_urls = sorted({x.url for x in items})
            categories = [x.category for x in items]
            cat = max(set(categories), key=categories.count)
            representative = sorted(items, key=lambda x: (x.date, len(x.claim_text)))[0].claim_text
            canon_id = hashlib.sha1(canon.encode("utf-8")).hexdigest()[:12]
            w.writerow(
                [
                    canon_id,
                    representative,
                    canon,
                    cat,
                    first_date,
                    last_date,
                    len(items),
                    ";".join(source_posts),
                    ";".join(source_urls),
                    items[0].url,
                ]
            )

    # Basic quality diagnostics
    very_short = [p for p in POSTS_DIR.glob("*.txt") if p.stat().st_size < 500]
    with REPORT_OUT.open("w", encoding="utf-8") as f:
        f.write("Gary Marcus claims extraction report\n")
        f.write(f"Run timestamp: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Files scanned: {file_count}\n")
        f.write(f"Claims extracted (raw): {len(claims)}\n")
        f.write(f"Canonical claim groups: {len(grouped)}\n")
        f.write(f"Very short files (<500 bytes): {len(very_short)}\n")
        if very_short:
            f.write("Potentially truncated/paywalled posts:\n")
            for p in sorted(very_short)[:50]:
                f.write(f"- {p.name}\n")
        f.write("\nCaveat: heuristic extraction can miss implicit claims and include false positives.\n")


def main() -> None:
    if not POSTS_DIR.exists():
        raise SystemExit(f"Missing posts dir: {POSTS_DIR}")

    files = sorted(POSTS_DIR.glob("*.txt"))
    claims = extract_claims()
    write_outputs(claims, file_count=len(files))

    print(f"Scanned {len(files)} files")
    print(f"Wrote {RAW_OUT}")
    print(f"Wrote {CANON_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(f"Extracted {len(claims)} raw claims")


if __name__ == "__main__":
    main()
