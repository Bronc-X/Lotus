"""Read-only local Codex history inventory. Python 3.11+; no dependencies."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
import tomllib
from urllib.parse import urlsplit


def inspect(home, query="", provider=None, limit=12, database=None):
    result = {"home": str(home), "errors": []}
    config = {}
    try:
        config = tomllib.loads((home / "config.toml").read_text(encoding="utf-8"))
        result["config_parse"] = "ok"
    except (OSError, ValueError):
        result["config_parse"] = "failed"
        result["errors"].append("Config missing or invalid; contents withheld.")
    result["default_provider"] = config.get("model_provider", "openai") if result["config_parse"] == "ok" else None
    result["providers"] = {}
    definitions = config.get("model_providers", {})
    for name, definition in definitions.items():
        if not isinstance(definition, dict):
            continue
        try:
            host = urlsplit(definition.get("base_url", "")).hostname
        except (ValueError, TypeError):
            host = None
        result["providers"][name] = {
            "host": host,
            "requires_openai_auth": definition.get("requires_openai_auth", False),
            "credential_configured": any(k in definition for k in ("env_key", "experimental_bearer_token", "auth")),
        }
    try:
        auth = json.loads((home / "auth.json").read_text(encoding="utf-8"))
        result["auth_mode"] = auth.get("auth_mode", "unknown")
    except (OSError, ValueError):
        result["auth_mode"] = "unavailable"
    if database:
        db_path = Path(database).resolve()
    else:
        candidates = list(home.glob("state_*.sqlite"))
        if len(candidates) != 1:
            result["errors"].append("Expected one state database; supply --db after checking the active version.")
            return result
        db_path = candidates[0]
    result["database"] = str(db_path)
    db = sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True, timeout=5)
    try:
        db.execute("PRAGMA query_only=ON")
        columns = {row[1] for row in db.execute("PRAGMA table_info(threads)")}
        required = {"id", "model_provider", "title", "cwd", "rollout_path", "archived", "updated_at"}
        if not required <= columns:
            result["errors"].append("Unsupported threads schema; inspect installed app interfaces before proceeding.")
            return result
        result["provider_counts"] = dict(db.execute("SELECT model_provider, COUNT(*) FROM threads GROUP BY model_provider"))
        # Definition lookup cannot resolve reserved provider IDs or project layers.
        known_builtin = {"openai", "ollama", "lmstudio", "amazon-bedrock"}
        result["providers_to_check"] = sorted(set(result["provider_counts"]) - set(definitions) - known_builtin)
        filters, params = [], []
        if query:
            filters.append("(instr(lower(id),lower(?))>0 OR instr(lower(title),lower(?))>0 OR instr(lower(cwd),lower(?))>0)")
            params.extend([query] * 3)
        if provider:
            filters.append("model_provider=?")
            params.append(provider)
        where = " WHERE " + " AND ".join(filters) if filters else ""
        result["match_count"] = db.execute("SELECT COUNT(*) FROM threads" + where, params).fetchone()[0]
        fields = "id,title,cwd,model_provider,archived,rollout_path"
        rows = db.execute("SELECT " + fields + " FROM threads" + where + " ORDER BY updated_at DESC LIMIT ?", params + [limit])
        result["threads"] = []
        for tid, title, cwd, model_provider, archived, rollout in rows:
            result["threads"].append({"id": tid, "title": title[:180], "cwd": cwd, "provider": model_provider,
                                      "archived": bool(archived), "rollout_exists": bool(rollout) and Path(rollout).is_file()})
        result["note"] = "Global config only; project overrides and live thread settings require separate verification. Missing rollout may use paginated history."
    finally:
        db.close()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    parser.add_argument("--db", type=Path)
    parser.add_argument("--query", default="")
    parser.add_argument("--provider")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    try:
        result = inspect(args.home.resolve(), args.query, args.provider, args.limit, args.db)
    except (OSError, sqlite3.Error, TypeError, AttributeError):
        result = {"errors": ["Unable to inspect local history; check paths, access and schema. No data was modified."]}
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
