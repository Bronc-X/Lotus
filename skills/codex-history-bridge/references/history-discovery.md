# History discovery

The inspector uses `CODEX_HOME` or the current user’s `.codex` directory. Use `--home` only for a known alternate history root and `--db` only for a confirmed state database. Do not create a database because the current directory is empty.

Use the returned task ID with the host’s task-reading tool; open the task only when the user asks. Keep the source-provided title.

If title search fails:

1. Narrow by the supplied project directory, task ID, provider, archive state, or known handoff index.
2. For full-text search, scan only the already-located session files and cap output length.
3. Confirm the Windows user, `CODEX_HOME`, archive locations, and known backups.
4. Inspect the installed Codex version and actual `thread_history_*.sqlite` schema before assuming a legacy layout.

A missing history file does not by itself prove message loss; newer versions may page history differently. Other accounts, devices, and cloud-only records are outside the evidence of this local workflow.
