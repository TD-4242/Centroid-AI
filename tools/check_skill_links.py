#!/usr/bin/env python3
"""Report broken links, unknown skill names and uncited cross-plugin skill names in the docs."""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SKILL_RE = re.compile(r"`((?:centroid|teco)-[a-z0-9-]+)`")
CITATION_RE = re.compile(r"\([^()]*\bp\.\s*\d+[^()]*\)")
EXTERNAL = ("http://", "https://", "mailto:")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _doc_files(root):
    files = sorted((root / "plugins").glob("**/*.md"))
    files += sorted(p for p in (root / "docs").glob("**/*.md")
                    if "superpowers" not in p.relative_to(root / "docs").parts)
    if (root / "README.md").is_file():
        files.append(root / "README.md")
    return files


def _skill_owners(root):
    """Map every skill name to its plugin; plugin names map to themselves."""
    owners = {}
    for skill_md in (root / "plugins").glob("*/skills/*/SKILL.md"):
        owners[skill_md.parent.name] = skill_md.parents[2].name
    if (root / "plugins").is_dir():
        for plugin in (root / "plugins").iterdir():
            if plugin.is_dir():
                owners.setdefault(plugin.name, plugin.name)
    return owners


def _slug(heading):
    # GitHub's rule: link text only, lowercase, drop punctuation but - and _, spaces to -.
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"[^\w\- ]", "", text.lower())
    return text.replace(" ", "-")


def _anchors(path, cache):
    if path not in cache:
        seen, anchors, in_fence = {}, set(), False
        for line in path.read_text(encoding="utf-8").splitlines():
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            match = None if in_fence else HEADING_RE.match(line)
            if match:
                slug = _slug(match.group(1))
                count = seen.get(slug, 0)
                seen[slug] = count + 1
                anchors.add(slug if count == 0 else f"{slug}-{count}")
        cache[path] = anchors
    return cache[path]


def _plugin_of(root, path):
    parts = path.relative_to(root).parts
    return parts[1] if len(parts) > 2 and parts[0] == "plugins" else None


def check_tree(root):
    root = Path(root)
    owners = _skill_owners(root)
    misses, anchor_cache = [], {}
    for path in _doc_files(root):
        rel_path = path.relative_to(root).as_posix()
        here = _plugin_of(root, path)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for target in LINK_RE.findall(line):
                if target.startswith(EXTERNAL):
                    continue
                file_part, _, anchor = target.partition("#")
                linked = (path.parent / file_part) if file_part else path
                if not linked.exists():
                    misses.append(f"{rel_path}:{lineno}: broken link {target}")
                elif anchor and linked.suffix == ".md" and anchor not in _anchors(linked, anchor_cache):
                    misses.append(f"{rel_path}:{lineno}: broken anchor {target}")
            for name in SKILL_RE.findall(line):
                owner = owners.get(name)
                if owner is None:
                    misses.append(f"{rel_path}:{lineno}: unknown skill {name}")
                elif here and owner != here and owner != name and not CITATION_RE.search(line):
                    misses.append(f"{rel_path}:{lineno}: cross-plugin skill {name} needs a manual "
                                  "citation on the same line")
    return misses


def main(argv):
    root = Path(argv[0]) if argv else Path(__file__).resolve().parent.parent
    files = _doc_files(root)
    if not files:
        print(f"error: {root} has no Markdown files to check", file=sys.stderr)
        return 2
    misses = check_tree(root)
    for miss in misses:
        print(miss)
    if misses:
        return 1
    print(f"OK: {len(files)} files checked")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
