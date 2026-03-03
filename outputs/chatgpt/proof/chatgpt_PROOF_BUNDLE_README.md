# ChatGPT Proof Bundle

Generated: 2026-03-03T00:44:32+00:00

## Purpose
This bundle provides verifiable evidence that the local `posts/` corpus was fully processed without publishing copyrighted post text.

## Files
- `chatgpt_posts_manifest.csv`: deterministic per-post manifest (`sha256`, byte size, URL, slug, date).
- `chatgpt_processing_ledger.csv`: per-post processing ledger for this run (`review_status=scanned_full_text`).
- `chatgpt_coverage_report.json`: aggregate coverage and scope limits.

## Verification
From the project root:

```bash
python3 outputs/chatgpt/scripts/chatgpt_verify_proof_bundle.py
```

A successful run confirms:
1. Hashes match all files currently on disk.
2. Manifest/ledger row counts match.
3. Coverage report totals are internally consistent.

## Important Scope Note
This proof bundle verifies corpus coverage and deterministic processing. It does **not** prove human qualitative review quality.
