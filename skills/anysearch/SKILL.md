---
name: anysearch
description: Search current web facts, news, and structured identifiers such as stocks, CVEs, DOIs, IATA codes, or patents.
metadata:
  version: 2.2.0
  authors:
    - AnySearch Team
  credentials:
    - name: ANYSEARCH_API_KEY
      required: false
      description: Optional API key; the service can bootstrap a temporary key.
---

# AnySearch

Use AnySearch for routine current web/news lookup and typed vertical identifiers. Use `agent-reach` for supplied URLs, GitHub-native retrieval, transcripts, RSS, platform-native social/video content, or selective Exa semantic discovery. One information need gets one primary route; use the second only after the first fails or is clearly off-target.

## Route

- If `runtime.conf` exists, use its stored command directly.
- For first-time setup, platform selection, and credentials: read [README.md](README.md) and [SECURITY.md](SECURITY.md).
- For vertical domains, batch input, sub-domain parameters, or output schemas: read [scripts/shared/doc_spec.md](scripts/shared/doc_spec.md).

Do not read setup documentation before every search.

## Basic execution

Choose the available wrapper for the current platform:

```text
python scripts/anysearch_cli.py search --query "..."
pwsh -File scripts/anysearch_cli.ps1 search --query "..."
bash scripts/anysearch_cli.sh search --query "..."
node scripts/anysearch_cli.js search --query "..."
```

Use one query when one query can answer the request. Batch search is for independent questions and consumes one search per item. Discover a vertical domain’s required parameters before its first use, then reuse known valid parameters while the local spec remains current.

## Credentials and results

- Keep keys in environment variables or the local ignored `.env`; never commit or print them.
- If the service returns a replacement key, continue the current request with it in memory. Save it only when the user asks or the local setup contract authorizes persistence.
- Treat snippets as leads. For claims requiring attribution, fetch the supporting page and cite the primary source where possible.
- If the primary route produces no relevant result, report the gap and choose the next appropriate route; do not duplicate searches merely to increase source count.

Completion means the requested facts or identifiers are returned with appropriate source evidence, or the attempted route and evidence gap are stated accurately.
