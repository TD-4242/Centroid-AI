#!/usr/bin/env python3
"""Check that the Claude Code and Codex catalogs, and each plugin's two manifests, agree."""
import argparse
import json
import re
import sys
from pathlib import Path

CLAUDE_CATALOG = Path(".claude-plugin/marketplace.json")
CODEX_CATALOG = Path(".agents/plugins/marketplace.json")
NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)
DEFAULT_MAX_SHORT = 30


def _load(path, problems):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        problems.append(f"missing {path}")
    except json.JSONDecodeError as e:
        problems.append(f"{path}: invalid JSON: {e}")
    return None


def _codex_source(entry):
    src = entry.get("source")
    return src.get("path") if isinstance(src, dict) else src


def _check_plugin(root, name, source):
    problems = []
    if not isinstance(source, str) or not source.startswith("./") or ".." in source:
        return [f"{name}: source {source!r} must be a ./ path inside the repo"]
    pdir = root / source
    if not pdir.is_dir():
        return [f"{name}: source {source} does not exist"]
    manifests = {label: _load(pdir / rel, problems)
                 for label, rel in (("Claude", ".claude-plugin/plugin.json"), ("portable", "plugin.json"))}
    for label, manifest in manifests.items():
        if manifest is not None and manifest.get("name") != name:
            problems.append(f"{name}: {label} manifest name is {manifest.get('name')!r}")
    if all(manifests.values()) and manifests["Claude"].get("version") != manifests["portable"].get("version"):
        problems.append(f"{name}: manifest versions differ")
    skill_files = sorted(pdir.glob("skills/*/SKILL.md"))
    if not skill_files:
        problems.append(f"{name}: no skills/*/SKILL.md")
    for skill_md in skill_files:
        match = NAME_RE.search(skill_md.read_text(encoding="utf-8"))
        folder = skill_md.parent.name
        if not match or match.group(1).strip("\"'") != folder:
            found = match.group(1) if match else None
            problems.append(f"{name}: skills/{folder}/SKILL.md frontmatter name {found!r} != folder")
    return problems


def check_tree(root):
    root = Path(root)
    problems = []
    claude = _load(root / CLAUDE_CATALOG, problems)
    codex = _load(root / CODEX_CATALOG, problems)
    if claude is None or codex is None:
        return problems
    claude_src = {e["name"]: e.get("source") for e in claude.get("plugins", [])}
    codex_src = {e["name"]: _codex_source(e) for e in codex.get("plugins", [])}
    for name in sorted(set(claude_src) ^ set(codex_src)):
        where = "Claude" if name in claude_src else "Codex"
        problems.append(f"plugin {name} is only in the {where} catalog")
    for entry in codex.get("plugins", []):
        for field in ("policy", "category"):
            if field not in entry:
                problems.append(f"Codex entry {entry['name']}: missing {field}")
    for name in sorted(set(claude_src) & set(codex_src)):
        if claude_src[name] != codex_src[name]:
            problems.append(f"{name}: catalogs point at different paths")
        problems += _check_plugin(root, name, claude_src[name])
    return problems


def _short_description(manifest):
    node = manifest
    for key in ("extensions", "com.openai", "interface", "shortDescription"):
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node if isinstance(node, str) else None


def chatgpt_warnings(root, max_short=DEFAULT_MAX_SHORT):
    """Warn for each Codex shortDescription longer than ChatGPT's suggested length (issue #2)."""
    root = Path(root)
    warnings = []
    try:
        catalog = json.loads((root / CODEX_CATALOG).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return warnings  # check_tree reports an unreadable catalog
    for entry in catalog.get("plugins", []):
        try:
            manifest = json.loads((root / _codex_source(entry) / "plugin.json").read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            continue
        short = _short_description(manifest)
        if short is not None and len(short) > max_short:
            warnings.append(f"warning: {entry.get('name')}: shortDescription is {len(short)} chars "
                            f"(ChatGPT target {max_short})")
    return warnings


def _positive_int(text):
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return value


def main(argv):
    parser = argparse.ArgumentParser(description="Check that the catalogs and plugin manifests agree.")
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--profile", choices=["chatgpt"], help="also print warnings for this target")
    parser.add_argument("--max-short", type=_positive_int, default=DEFAULT_MAX_SHORT,
                        help="ChatGPT shortDescription target length (default %(default)s)")
    args = parser.parse_args(argv)
    problems = check_tree(args.root)
    for problem in problems:
        print(problem)
    if args.profile == "chatgpt":
        for warning in chatgpt_warnings(args.root, args.max_short):
            print(warning)
    if problems:
        return 1
    print("OK: catalogs and manifests agree")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
