# Preview setup
Resolve commands relative to this skill directory; run project helper commands from the target project.
- Inspect the Xcode project/workspace, scheme, bundle ID, and existing scripts/ios-preview helpers.
- Install/update using `scripts/install-ios-codex-preview.sh` only when needed.
- Start with `scripts/ios-preview/start-all.sh --daemon`; stop with `scripts/ios-preview/stop.sh`.
- Open the configured loopback URL (default http://127.0.0.1:3200).
- Run `scripts/ios-preview/health.sh`. Confirm server and watcher ownership, a fresh screenshot, and a rendered browser frame; /status alone is insufficient.
- For hot reload checks, use task-scoped reversible changes and restore test-only edits.
Projects under Documents may be blocked by macOS TCC when launched through LaunchAgents. Prefer the project lifecycle scripts; disable a stale agent only after matching its plist, process, and project to this task.
Do not retry architecture-incompatible serve-sim repeatedly on Intel Macs. The compatibility preview polls simctl screenshots.
