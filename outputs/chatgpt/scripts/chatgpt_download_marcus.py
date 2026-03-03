#!/usr/bin/env python3
"""
Download all Gary Marcus Substack posts as clean text files.
1. Fetch sitemap.xml
2. Extract all /p/ post URLs with dates
3. Download each post HTML
4. Strip to clean text via BeautifulSoup
5. Save as YYYY-MM-DD_slug.txt in ./posts/
"""

import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup

BASE = "https://garymarcus.substack.com"
SITEMAP_URL = f"{BASE}/sitemap.xml"
OUTPUT_DIR = Path(__file__).parent / "posts"
DELAY = 1.0  # seconds between requests to be polite

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def get_post_urls_from_sitemap():
    """Parse sitemap.xml and return list of (date, url, slug) for posts."""
    xml_text = fetch(SITEMAP_URL)
    # Strip namespace for easier parsing
    xml_text = re.sub(r'\s+xmlns="[^"]+"', "", xml_text, count=1)
    root = ET.fromstring(xml_text)

    posts = []
    for url_elem in root.findall(".//url"):
        loc = url_elem.findtext("loc", "")
        lastmod = url_elem.findtext("lastmod", "")
        if "/p/" in loc:
            slug = loc.split("/p/")[-1].rstrip("/")
            date = lastmod[:10] if lastmod else "unknown"
            posts.append((date, loc, slug))

    # Sort by date
    posts.sort(key=lambda x: x[0])
    return posts


def html_to_text(html):
    """Extract article text from Substack post HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Try to find the article body
    article = (
        soup.find("div", class_="body")
        or soup.find("div", class_="post-content")
        or soup.find("article")
        or soup.find("div", class_="available-content")
    )
    if not article:
        article = soup

    # Get title
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Get subtitle
    subtitle_tag = soup.find("h3", class_="subtitle")
    subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else ""

    # Get date from meta or page
    date_tag = soup.find("time")
    date_str = date_tag.get_text(strip=True) if date_tag else ""

    # Remove script/style tags
    for tag in article.find_all(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Get body text
    body = article.get_text(separator="\n", strip=True)

    # Compose output
    parts = []
    if title:
        parts.append(f"TITLE: {title}")
    if subtitle:
        parts.append(f"SUBTITLE: {subtitle}")
    if date_str:
        parts.append(f"DATE: {date_str}")
    parts.append("")
    parts.append(body)

    return "\n".join(parts)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching sitemap...")
    posts = get_post_urls_from_sitemap()
    print(f"Found {len(posts)} posts")

    # Check which are already downloaded
    existing = set(f.stem for f in OUTPUT_DIR.glob("*.txt"))

    downloaded = 0
    skipped = 0
    errors = 0

    for i, (date, url, slug) in enumerate(posts):
        filename = f"{date}_{slug}"
        if filename in existing:
            skipped += 1
            continue

        print(f"[{i+1}/{len(posts)}] {date} {slug[:60]}...", end=" ", flush=True)

        try:
            html = fetch(url)
            text = html_to_text(html)
            out_path = OUTPUT_DIR / f"{filename}.txt"
            out_path.write_text(text, encoding="utf-8")
            downloaded += 1
            print(f"OK ({len(text)} chars)")
        except Exception as e:
            errors += 1
            print(f"ERROR: {e}")

        time.sleep(DELAY)

    print(f"\nDone. Downloaded: {downloaded}, Skipped (existing): {skipped}, Errors: {errors}")
    print(f"Files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
