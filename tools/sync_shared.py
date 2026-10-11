#!/usr/bin/env python3
"""Copy shared/*.py helpers into every plugin's scripts/ (installed plugins cannot share files)."""
import shutil
import sys
from pathlib import Path

SHARED = ("centroid_config.py", "fetch_manual.py")


def sync(root, check):
    root = Path(root)
    changed = []
    if not (root / "plugins").is_dir():
        return changed
    for plugin in sorted(p for p in (root / "plugins").iterdir() if p.is_dir()):
        for name in SHARED:
            src, dst = root / "shared" / name, plugin / "scripts" / name
            if dst.is_file() and dst.read_bytes() == src.read_bytes():
                continue
            changed.append(dst.relative_to(root).as_posix())
            if not check:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
    return changed


def main(argv):
    check = "--check" in argv
    rest = [a for a in argv if a != "--check"]
    root = Path(rest[0]) if rest else Path(__file__).resolve().parent.parent
    changed = sync(root, check)
    for path in changed:
        print(("out of date: " if check else "updated: ") + path)
    return 1 if check and changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
