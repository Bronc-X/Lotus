---
name: codebase-memory-mcp
description: 用已有代码图谱查询跨文件调用链、依赖或影响面；或按要求配置索引。
metadata:
  homepage: https://github.com/DeusData/codebase-memory-mcp
---

# Codebase memory MCP
Use graph tools for structural queries; use literal search for filenames and exact strings.
For installation or configuration repair only, read [references/setup.md](references/setup.md). A query does not authorize enabling global auto-indexing or reinstalling software.
## Query
- Discover available tools and indexed project names; do not guess normalized identifiers.
- Check index freshness before trusting results. Index only the repository in scope when needed.
- Choose the smallest useful index mode; `fast` is suitable for connectivity checks.
- Query the relevant call path, dependencies, architecture, or snippets. Read source before editing; graph output can be stale.
- Keep generated indexes in the tool's cache unless the user requests a shared artifact.
This is a stdio MCP server, not a detached web service. If unavailable, fall back to search and file reads; setup is a separate requested action.
