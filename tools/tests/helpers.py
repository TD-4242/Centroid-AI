"""Fixture builders shared by the tools tests."""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_plugin(root, name, skills=("s1",), version="0.1.0", codex_name=None):
    pdir = Path(root) / "plugins" / name
    write(pdir / ".claude-plugin" / "plugin.json", json.dumps({"name": name, "version": version}))
    write(pdir / "plugin.json", json.dumps({"name": codex_name or name, "version": version}))
    for skill in skills:
        write(pdir / "skills" / skill / "SKILL.md",
              f"---\nname: {skill}\ndescription: test\n---\n# {skill}\n")
    return pdir


def write_catalogs(root, names, codex_names=None):
    root = Path(root)
    write(root / ".claude-plugin" / "marketplace.json", json.dumps({
        "name": "centroid-ai", "owner": {"name": "t"},
        "plugins": [{"name": n, "source": f"./plugins/{n}"} for n in names]}))
    write(root / ".agents" / "plugins" / "marketplace.json", json.dumps({
        "name": "centroid-ai",
        "plugins": [{"name": n, "source": {"source": "local", "path": f"./plugins/{n}"},
                     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                     "category": "Manufacturing"} for n in (codex_names or names)]}))
