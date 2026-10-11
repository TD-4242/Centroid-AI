#!/usr/bin/env python3
"""Zip one plugin, with a SOURCE.txt naming the commit it came from, for upload to a chat app."""
import argparse
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO_URL = "https://github.com/TD-4242/Centroid-AI"
FORBIDDEN_SUFFIXES = (".exe", ".plc", ".pyc")
CATALOGS = (Path(".claude-plugin/marketplace.json"), Path(".agents/plugins/marketplace.json"))


class ExportError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def _git(root, *args):
    try:
        result = subprocess.run(["git", "-C", str(root), *args],
                                capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        raise ExportError(f"git {args[0]} failed in {root}; run this from a git checkout of the repo", 2) from e
    return result.stdout.strip()


def _catalog_names(root, rel):
    try:
        data = json.loads((root / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ExportError(f"cannot read {rel}: {e}", 2) from e
    return {entry.get("name") for entry in data.get("plugins", []) if isinstance(entry, dict)}


def _files(root, plugin):
    """Tracked plus untracked-but-unignored files; refuses symlinks and compiled binaries."""
    listing = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", f"plugins/{plugin}")
    files = []
    for rel in sorted(set(filter(None, listing.split("\0")))):
        path = root / rel
        if path.is_symlink():
            raise ExportError(f"{rel} is a symlink; replace it with a real file to export", 2)
        if not path.is_file():
            continue  # tracked but deleted in the working tree
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or "__pycache__" in path.parts:
            raise ExportError(f"{rel} must not be shipped; remove it from git to export", 2)
        files.append(path)
    return files


def export(root, plugin, out, allow_dirty=False, now=None):
    """Write <out>/<plugin>-<version>-<shortsha>.zip and return its path.

    Raises ExportError: code 2 for an unknown plugin, a non-git tree, an --out inside the
    plugin, or a symlink or compiled binary in it; code 1 when plugins/<plugin> has
    uncommitted changes and allow_dirty is false.
    """
    root = Path(root)
    if not all(plugin in _catalog_names(root, rel) for rel in CATALOGS):
        raise ExportError(f"unknown plugin {plugin!r}: it must be listed in both catalogs", 2)
    pdir = root / "plugins" / plugin
    try:
        version = json.loads((pdir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError) as e:
        raise ExportError(f"cannot read the version of {plugin}: {e}", 2) from e
    sha = _git(root, "rev-parse", "HEAD")
    dirty = bool(_git(root, "status", "--porcelain", "--", f"plugins/{plugin}"))
    if dirty and not allow_dirty:
        raise ExportError(f"plugins/{plugin} has uncommitted changes; commit them or pass --allow-dirty", 1)
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    source = (f"repository: {REPO_URL}\nplugin: {plugin}\nversion: {version}\n"
              f"commit: {sha}\nexported: {stamp}\ndirty: {str(dirty).lower()}\n")
    out = Path(out)
    if out.resolve().is_relative_to(pdir.resolve()):
        raise ExportError(f"--out {out} is inside plugins/{plugin}; choose a folder outside it", 2)
    files = _files(root, plugin)
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / f"{plugin}-{version}-{sha[:7]}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, f"{plugin}/{path.relative_to(pdir).as_posix()}")
        zf.writestr(f"{plugin}/SOURCE.txt", source)
    return zip_path


def main(argv):
    parser = argparse.ArgumentParser(description="Zip one plugin for upload to the Claude app or ChatGPT.")
    parser.add_argument("plugin", help="plugin name, e.g. centroid-acorn")
    parser.add_argument("--out", type=Path, help="output folder (default: dist/ in the repo)")
    parser.add_argument("--allow-dirty", action="store_true",
                        help="export even if the plugin has uncommitted changes")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        path = export(args.root, args.plugin, args.out or args.root / "dist", args.allow_dirty)
    except ExportError as e:
        print(f"error: {e}", file=sys.stderr)
        return e.code
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
