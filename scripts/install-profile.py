"""Install the versioned Lotus slash-menu profile for one host (Python 3.11+)."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles/local-latest.json"
HOSTS = {"codex": (".codex", "AGENTS.md", "CODEX_HOME"),
         "claude-code": (".claude", "CLAUDE.md", "CLAUDE_CONFIG_DIR"),
         "dsh-next": (".dsh", "AGENTS.md", "DSH_HOME")}


def menu_policy(text: str, enabled: bool, internal: bool) -> str:
    """Claude Code and DSH use frontmatter, rather than Codex settings."""
    if not text.startswith("---\n"):
        raise ValueError("Skill is missing YAML frontmatter")
    end = text.index("\n---", 4)
    front, body = text[4:end], text[end:]
    for key, value in (("user-invocable", enabled),
                       ("disable-model-invocation", not enabled and not internal)):
        line = f"{key}: {str(value).lower()}"
        pattern = rf"(?m)^{key}:.*$"
        front = re.sub(pattern, line, front) if re.search(pattern, front) else front + "\n" + line
    return "---\n" + front + body


def codex_settings(text: str, host_root: Path, states: dict[str, bool], profile: dict) -> str:
    """Replace matching skill selectors and plugin switches; preserve other TOML."""
    original = tomllib.loads(text)
    disabled = set(profile["skills"]["disabled"])
    paths = {(host_root / "skills" / name / "SKILL.md").as_posix().casefold()
             for name in states}
    chunks = re.split(r"(?m)(?=^\[)", text)
    kept = []
    plugin_states = dict(profile["plugins"]["codex"])
    for chunk in chunks:
        if chunk.startswith("[[skills.config]]"):
            row = tomllib.loads(chunk)["skills"]["config"][0]
            path = str(row.get("path", "")).replace("\\", "/").casefold()
            if path in paths or row.get("name") in disabled:
                continue
        if chunk.startswith("[plugins."):
            parsed = tomllib.loads(chunk).get("plugins", {})
            key = next(iter(parsed), None)
            if key in plugin_states:
                value = str(plugin_states.pop(key)["enabled"]).lower()
                if re.search(r"(?m)^enabled\s*=", chunk):
                    chunk = re.sub(r"(?m)^enabled\s*=.*$", "enabled = " + value, chunk)
                else:
                    chunk = chunk.rstrip() + "\nenabled = " + value + "\n\n"
        kept.append(chunk)
    output = "".join(kept).rstrip() + "\n\n"
    for key, row in plugin_states.items():
        output += f"[plugins.{json.dumps(key)}]\nenabled = {str(row['enabled']).lower()}\n\n"
    for name, enabled in sorted(states.items()):
        path = (host_root / "skills" / name / "SKILL.md").as_posix()
        output += f"[[skills.config]]\npath = {json.dumps(path)}\nenabled = {str(enabled).lower()}\n\n"
    for name in sorted(disabled - states.keys()):
        output += f"[[skills.config]]\nname = {json.dumps(name)}\nenabled = false\n\n"
    result = tomllib.loads(output)
    for key in original.keys() - {"skills", "plugins"}:
        if result.get(key) != original[key]:
            raise ValueError(f"Unrelated Codex setting changed: {key}")
    return output


def install(host: str, home: Path | None = None, dry_run: bool = False) -> dict:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    dirname, rules, envvar = HOSTS[host]
    host_root = home / dirname if home else Path(os.environ.get(envvar, str(Path.home() / dirname)))
    host_root = host_root.absolute()
    menu = set(profile["skills"]["slashEntries"])
    internal = set(profile["skills"]["internal"])
    writes: dict[Path, bytes] = {}
    states = {}
    for source in sorted((ROOT / "skills").iterdir()):
        if source.is_dir() and (source / "SKILL.md").is_file():
            files = [(p, p.relative_to(source)) for p in source.rglob("*") if p.is_file()]
        elif source.is_file() and source.suffix == ".md":
            if source.stem not in menu | internal:
                continue
            files = [(source, Path("SKILL.md"))]
        else:
            continue
        name = source.stem if source.is_file() else source.name
        states[name] = name in menu
        for path, relative in files:
            if any(part in {"__pycache__", "node_modules", ".git", ".venv"} for part in relative.parts):
                continue
            if path.name in {"runtime.local.json", "runtime.json", "voice.json", ".env", "runtime.conf"}:
                continue
            data = path.read_bytes()
            if relative == Path("SKILL.md") and host != "codex":
                text = data.decode("utf-8-sig").replace("\r\n", "\n")
                data = menu_policy(text, states[name], name in internal).encode("utf-8")
            writes[host_root / "skills" / name / relative] = data
    for source in sorted((ROOT / "adapters/gstack").rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(ROOT / "adapters/gstack")
        name = relative.parts[0]
        states[name] = name in menu
        data = source.read_bytes()
        if source.name == "SKILL.md" and host != "codex":
            data = menu_policy(data.decode("utf-8-sig").replace("\r\n", "\n"),
                               states[name], name in internal).encode("utf-8")
        writes[host_root / "skills" / relative] = data
    for name in profile["skills"]["disabled"]:
        if name.startswith("gstack-"):
            if host == "codex":
                if (host_root / "skills" / name / "SKILL.md").is_file():
                    states[name] = False
            else:
                alias = host_root / "skills" / name.removeprefix("gstack-") / "SKILL.md"
                if alias.is_file():
                    text = alias.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
                    writes[alias] = menu_policy(text, False, True).encode("utf-8")
    writes[host_root / rules] = (ROOT / "core/AGENTS.md").read_bytes()
    if host == "codex":
        config = host_root / "config.toml"
        text = config.read_text(encoding="utf-8-sig") if config.exists() else ""
        writes[config] = codex_settings(text, host_root, states, profile).encode("utf-8")
    missing = menu - states.keys()
    if missing:
        raise ValueError(f"Slash entries missing from package: {sorted(missing)}")
    changed = {p: data for p, data in writes.items() if not p.is_file() or p.read_bytes() != data}
    # Reject redirected targets before writing or backing up any file.
    checked = set()
    for path in changed:
        for parent in (path, *path.parents):
            if parent in checked:
                continue
            checked.add(parent)
            if parent.is_symlink() or getattr(parent, "is_junction", lambda: False)():
                raise ValueError(f"Linked installation target: {parent}")
    backup = host_root / "backups" / ("lotus-profile-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    if not dry_run:
        for path in changed:
            if path.is_file():
                saved = backup / path.relative_to(host_root)
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(path.read_bytes())
        for path, data in changed.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if path.read_bytes() != data:
                raise OSError(f"Verification failed: {path}")
    return {"host": host, "root": str(host_root), "slashEntries": len(menu),
            "changedFiles": len(changed), "dryRun": dry_run}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, choices=HOSTS)
    parser.add_argument("--home", type=Path, help="Override the user home for an isolated installation")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.host, args.home, args.dry_run), ensure_ascii=False))
    except (OSError, ValueError, KeyError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        sys.exit(1)
