#!/usr/bin/env python3
"""Find mpucomp.exe, Centroid's PLC compiler, without copying or bundling it."""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import NamedTuple

import centroid_config

EXE = "mpucomp.exe"
CNC12_DIRS = ("cncm", "cncr", "cnct", "cncp")


class Found(NamedTuple):
    path: Path
    origin: str


def find_in(directory):
    directory = Path(directory)
    if not directory.is_dir():
        return None
    for entry in directory.iterdir():
        if entry.name.lower() == EXE and entry.is_file():
            return entry
    return None


def _as_compiler(path):
    path = Path(path).expanduser().resolve()
    return find_in(path) if path.is_dir() else (path if path.is_file() else None)


def _git_root(start):
    for d in [start, *start.parents]:
        if (d / ".git").exists():
            return d
    return None


def locate(src, explicit=None, is_windows=None, wineprefix=None, windows_root=None):
    if explicit:
        hit = _as_compiler(explicit)
        if hit is None:
            raise FileNotFoundError(f"no {EXE} found at {explicit}")
        return Found(hit, "explicit")
    configured = centroid_config.load()["mpucomp"].get("path")
    if configured and (hit := _as_compiler(configured)):
        return Found(hit, "config")
    if src is not None:
        src_dir = Path(src).resolve().parent
        for d in (src_dir, _git_root(src_dir)):
            if d and (hit := find_in(d)):
                return Found(hit, "project")
    if is_windows is None:
        is_windows = os.name == "nt"
    if is_windows:
        base = Path(windows_root) if windows_root else Path("C:/")
    else:
        prefix = wineprefix or Path(os.environ.get("WINEPREFIX") or Path.home() / ".wine")
        base = Path(prefix) / "drive_c"
    for name in CNC12_DIRS:
        if hit := find_in(base / name):
            return Found(hit, "cnc12")
    return None


def main(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--src", type=Path)
    p.add_argument("--compiler")
    args = p.parse_args(argv)
    try:
        found = locate(args.src, explicit=args.compiler)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if found is None:
        return 2
    print(json.dumps({"path": str(found.path), "origin": found.origin}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
