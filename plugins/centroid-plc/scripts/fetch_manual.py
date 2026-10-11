#!/usr/bin/env python3
"""Find a manual from this plugin's manuals.json locally, or download it with the user's consent."""
import argparse
import http.client
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import centroid_config

urlopen = urllib.request.urlopen
# Centroid's server rejects default client user agents.
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/126.0 Safari/537.36",
           "Accept": "application/pdf,*/*"}
DEFAULT_MANIFEST = Path(__file__).resolve().parent.parent / "manuals.json"
PAGE_RE = re.compile(rb"/Type\s*/Page(?![a-zA-Z])")


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=dest.name + ".", suffix=".part", dir=dest.parent)
    part = Path(name)
    try:
        with os.fdopen(fd, "wb") as out, \
                urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as resp:
            shutil.copyfileobj(resp, out)
            expected = resp.headers.get("Content-Length")
        data = part.read_bytes()
        if expected and expected.isdigit() and len(data) != int(expected):
            raise OSError("download was incomplete")
        if not data.startswith(b"%PDF-"):
            raise OSError("the server did not return a PDF")
        if b"%%EOF" not in data.rstrip()[-1024:]:
            raise OSError("download looks truncated")
        if not dest.exists():
            os.replace(part, dest)
    finally:
        part.unlink(missing_ok=True)


def count_pages(path):
    if shutil.which("pdfinfo"):
        r = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, errors="replace")
        match = re.search(r"^Pages:\s+(\d+)", r.stdout, re.MULTILINE)
        if match:
            return int(match.group(1))
    count = len(PAGE_RE.findall(Path(path).read_bytes()))
    return count or None


def _warnings(path, entry):
    expected = entry.get("expectPages")
    pages = count_pages(path) if expected else None
    if expected and pages and pages != expected:
        return [f"note: {entry['title']} has {pages} pages; the skills were written against "
                f"{entry.get('expectRev') or 'an earlier revision'} ({expected} pages), "
                "so page citations may be slightly off."]
    return []


def main(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("id", nargs="?")
    p.add_argument("--yes", action="store_true", help="download without asking")
    p.add_argument("--list", action="store_true")
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = p.parse_args(argv)
    try:
        entries = {e["id"]: e for e in json.loads(args.manifest.read_text(encoding="utf-8"))}
        cfg = centroid_config.load()
        manuals = centroid_config.manuals_dir()
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.list:
        for e in entries.values():
            state = "downloaded" if (manuals / e["file"]).is_file() else "not downloaded"
            print(f"{e['id']}: {e['title']} ({state}) {e['url']}")
        return 0
    entry = entries.get(args.id)
    if entry is None:
        print(f"error: unknown manual {args.id!r}; known: {', '.join(entries)}", file=sys.stderr)
        return 2
    dest = manuals / entry["file"]
    if not dest.is_file():
        mode = cfg["manuals"].get("autoDownload", "ask")
        if not args.yes and mode == "never":
            print(f"{entry['title']} is not downloaded (auto-download is off). URL: {entry['url']}")
            return 5
        if not args.yes and mode != "always":
            size = f"about {entry['sizeMB']} MB" if entry.get("sizeMB") else "size unknown"
            print(f"NEEDS CONSENT: {entry['title']} (free PDF, {size})\n"
                  f"from: {entry['url']}\nto: {dest}")
            return 4
        try:
            download(entry["url"], dest)
        except (OSError, http.client.HTTPException, ValueError) as e:
            print(f"Could not download {entry['title']}: {e}.\n"
                  f"You can download it in a browser from {entry['url']} and save it as {dest}")
            return 1
    for warning in _warnings(dest, entry):
        print(warning, file=sys.stderr)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
