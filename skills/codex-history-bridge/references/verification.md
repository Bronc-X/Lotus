# Verification and rollback

After a scoped provider or config change:

1. Parse the resulting TOML and run the installed version’s configuration check when available.
2. Sample an affected old task through the actual resume interface and distinguish “loaded” from “sent a new model request.”
3. Reopen the task and verify the selected provider persists if persistence is claimed.
4. Only when the user authorized continuing the task, verify a model reply and the intended destination host.
5. On failure, classify configuration, authentication, network, or history-format causes. Roll back only the changed provider/default fields from the backup after checking for newer unrelated edits.

Preserve task IDs, archive state, and history content. Report the number of records found, the resolved provider mapping, files changed, private backup location, checks run, and the highest verified stage.

The bundled workflow was originally validated on one Windows repair involving missing provider aliases. Treat that as precedent, not proof for every Codex version or third-party service.
