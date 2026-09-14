# gstack browser runtime

Locate the existing executable; do not derive it from an unrelated project directory:
- Project installation: <repo>/.agents/skills/gstack/browse/dist/browse
- User installation: <user-skills>/gstack/browse/dist/browse
- Managed upstream: <user-home>/.gstack/repos/gstack/browse/dist/browse

Use the executable form that exists on the current platform, including .exe where appropriate. If unavailable, use a supported host browser or report the missing runtime; install/build it only within requested setup scope.

Assign the verified executable to B in the shell. Core commands:

```text
"$B" goto <url>
"$B" snapshot -i
"$B" click @e3
"$B" fill @e4 <value>
"$B" snapshot -D
"$B" text
"$B" console
"$B" network
"$B" screenshot <output-path>
"$B" status
```

Refs come from the latest snapshot and expire on navigation. Do not guess them.
Consult the installed version's help for responsive views, uploads, dialogs, PDF, tabs, state persistence, and CSS inspection only when needed.
State persists between calls. Do not export cookies or stop a shared browser as routine cleanup.
