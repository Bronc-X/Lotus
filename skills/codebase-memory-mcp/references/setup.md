# Code graph setup

Use only for requested installation or repair. Inspect the current installation before changing it. Auto-indexing is optional and requires setup scope; use limits appropriate to the repository.


```powershell
python -m venv "$env:USERPROFILE\.codebase-memory-mcp-venv"
& "$env:USERPROFILE\.codebase-memory-mcp-venv\Scripts\python.exe" -m pip install --upgrade pip codebase-memory-mcp
& "$env:USERPROFILE\.codebase-memory-mcp-venv\Scripts\codebase-memory-mcp.exe" install
& "$env:USERPROFILE\.codebase-memory-mcp-venv\Scripts\codebase-memory-mcp.exe" config set auto_index true
& "$env:USERPROFILE\.codebase-memory-mcp-venv\Scripts\codebase-memory-mcp.exe" config set auto_index_limit 50000
```

Verify:

```powershell
& "$env:USERPROFILE\.codebase-memory-mcp-venv\Scripts\codebase-memory-mcp.exe" config list
```

Expected config:

```text
auto_index = true
auto_index_limit = 50000
```

If `install` says indexes must be rebuilt, confirm only when the listed paths
are under the tool's own cache directory, such as
`~/.cache/codebase-memory-mcp/`.
