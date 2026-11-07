"""Check the three host installations in isolated homes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib

spec = importlib.util.spec_from_file_location("install_profile", Path(__file__).with_name("install-profile.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
profile = json.loads(module.PROFILE.read_text(encoding="utf-8"))
menu = set(profile["skills"]["slashEntries"])
assert "gstack" in menu and "image-2" not in menu and "copy-editing" not in menu
assert not any(name.startswith("gstack-") for name in menu)
assert len(profile["plugins"]["codex"]) == 11

with tempfile.TemporaryDirectory(prefix="lotus-profile-test-") as temporary:
    home = Path(temporary)
    for host, (dirname, rules, _) in module.HOSTS.items():
        target = home / dirname
        private = target / "skills/toni-voice/runtime.json"
        private.parent.mkdir(parents=True)
        private.write_text('{"private": "sentinel"}', encoding="utf-8")
        old_rules = target / rules
        old_rules.write_text("existing rules", encoding="utf-8")
        unrelated = target / "skills/my-private-skill/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("private skill", encoding="utf-8")
        if host != "codex":
            alias = target / "skills/ship/SKILL.md"
            alias.parent.mkdir(parents=True)
            alias.write_text("---\nname: ship\ndescription: Existing upstream alias\n---\nRuntime reference", encoding="utf-8")
        if host == "codex":
            (target / "config.toml").write_text('model = "keep-model"\n'
                '[mcp_servers.private]\ncommand = "keep-command"\n'
                '[plugins."custom@example"]\nenabled = false\n'
                '[[skills.config]]\nname = "my-private-skill"\nenabled = true\n'
                '[plugins."visualize@openai-bundled"]\nenabled = false\n', encoding="utf-8")
        preview = module.install(host, home, True)
        assert preview["changedFiles"] > 0 and old_rules.read_text() == "existing rules"
        result = module.install(host, home)
        assert result["slashEntries"] == len(menu)
        assert private.read_text() == '{"private": "sentinel"}'
        assert unrelated.read_text() == "private skill"
        assert old_rules.read_bytes() == (module.ROOT / "core/AGENTS.md").read_bytes()
        assert len(list((target / "backups").glob("lotus-profile-*"))) == 1
        assert any(p.read_text() == "existing rules" for p in (target / "backups").rglob(rules))
        for name in menu:
            assert (target / "skills" / name / "SKILL.md").is_file(), name
        if host == "codex":
            config = tomllib.loads((target / "config.toml").read_text())
            assert config["model"] == "keep-model"
            assert config["mcp_servers"]["private"]["command"] == "keep-command"
            assert config["plugins"]["custom@example"]["enabled"] is False
            assert config["plugins"]["visualize@openai-bundled"]["enabled"] is True
            rows = config["skills"]["config"]
            assert any(r.get("name") == "my-private-skill" and r["enabled"] for r in rows)
            for name in ["gstack-office-hours", "image-2"]:
                assert any(r.get("path", "").endswith(f"/{name}/SKILL.md") and not r["enabled"] for r in rows)
        else:
            assert "user-invocable: false" in (target / "skills/ship/SKILL.md").read_text(encoding="utf-8")
            assert "user-invocable: true" in (target / "skills/gstack/SKILL.md").read_text(encoding="utf-8")
            assert "user-invocable: false" in (target / "skills/gstack-ship/SKILL.md").read_text(encoding="utf-8")
            assert "disable-model-invocation: true" in (target / "skills/image-2/SKILL.md").read_text(encoding="utf-8")
        assert module.install(host, home)["changedFiles"] == 0, f"Non-idempotent installation: {host}"
        print(f"PASS {host}: {len(menu)} slash entries; backup, private files, and repeat install verified")

print("Profile installation tests passed")
