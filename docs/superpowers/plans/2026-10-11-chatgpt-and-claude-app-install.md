# ChatGPT and Claude App Install Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document Claude app, Cowork and ChatGPT installs, and ship the tooling (plugin export, ChatGPT length warnings, no-Python fallbacks) a ChatGPT pilot needs.

**Architecture:** Two new stdlib tool features (`tools/export_plugin.py`, a `--profile chatgpt` mode in `tools/check_marketplace.py`), one-paragraph additions to existing skills, and new doc sections. Nothing changes in the catalogs, manifests or shared scripts.

**Tech Stack:** Python ≥ 3.10 stdlib only, `unittest`, git, Markdown, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-11-chatgpt-and-claude-app-install-design.md`

## Global Constraints

> Annotated after final review: Desktop chats run code in a cloud sandbox, so the compile, format and install snippets below were corrected to name Claude Code (including Desktop's Code tab) or Codex. PR #4 review also required bumping every changed plugin to 0.1.1 per `docs/authoring.md` § Version bumps.

- Python ≥ 3.10, stdlib only. Run tests with `python3 -m unittest discover -s tools/tests -t .` from the repo root.
- Comments are 1-2 lines and only clarify confusing code; rationale goes in the commit message.
- Do not shorten any `shortDescription`; do not edit catalogs or plugin manifests.
- Do not edit `shared/*` or `plugins/*/scripts/*` (sync_shared copies must stay identical).
- Before every commit, these all pass: `python3 tools/check_marketplace.py`, `python3 tools/check_skill_links.py`, `python3 tools/sync_shared.py --check`, the unit tests.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Menu steps for the Claude app and ChatGPT are dated "as of 2026-10".
- Never modify the sibling repos `/home/bwarner/github/Acroloc-Centroid` or `/home/bwarner/github/Torchmate-Centroid`.

## Review Focus

1. A plugin name that is a path (`../centroid-a`, `plugins/x`) must be rejected by `export_plugin.py` with exit 2, never zipped — pinned in Task 2 `test_path_like_name_rejected`.
2. Running `export_plugin.py` outside a git checkout must print one error line and exit 2, not a traceback — pinned in Task 2 `test_not_a_git_repo`.
3. Uncommitted edits elsewhere in the repo (README, another plugin) must not block exporting a clean plugin; an untracked new file inside the plugin must — pinned in Task 2 `test_change_outside_plugin_not_dirty` and `test_untracked_file_is_dirty`.
4. A portable `plugin.json` with no `extensions`, or a non-dict `extensions`, must not crash `--profile chatgpt` — pinned in Task 1 `test_missing_or_malformed_extensions_skipped`.
5. `--max-short 0` or a negative value is a usage error (exit 2), not "everything warns" — pinned in Task 1 `test_max_short_must_be_positive`.

---

### Task 1: `check_marketplace.py --profile chatgpt`

**Files:**
- Modify: `tools/check_marketplace.py` (add `argparse`, `DEFAULT_MAX_SHORT`, `chatgpt_warnings`, new `main`)
- Modify: `tools/tests/test_check_marketplace.py` (new test class)
- Modify: `.github/workflows/check.yml` (extra step)

**Interfaces:**
- Produces: `chatgpt_warnings(root, max_short=30) -> list[str]`; CLI `check_marketplace.py [root] [--profile chatgpt] [--max-short N]`. Existing `check_tree(root)` unchanged.

- [ ] **Step 1: Write the failing tests** — append to `tools/tests/test_check_marketplace.py`, above the `if __name__` block. Add `import contextlib` and `import io` to the imports at the top.

```python
def set_short(pdir, short, extensions=None):
    data = {"name": pdir.name, "version": "0.1.0"}
    data["extensions"] = extensions if extensions is not None else {
        "com.openai": {"interface": {"shortDescription": short}}}
    write(pdir / "plugin.json", json.dumps(data))


class ChatGPTProfileTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.pdir = make_plugin(self.root, "centroid-a")
        write_catalogs(self.root, ["centroid-a"])

    def tearDown(self):
        self._tmp.cleanup()

    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cm.main([str(self.root), *args])
        return code, out.getvalue()

    def test_long_short_description_warns(self):
        set_short(self.pdir, "x" * 31)
        self.assertEqual(cm.chatgpt_warnings(self.root),
                         ["warning: centroid-a: shortDescription is 31 chars (ChatGPT target 30)"])

    def test_exactly_at_limit_is_not_warned(self):
        set_short(self.pdir, "x" * 30)
        self.assertEqual(cm.chatgpt_warnings(self.root), [])

    def test_max_short_changes_threshold(self):
        set_short(self.pdir, "x" * 12)
        self.assertEqual(cm.chatgpt_warnings(self.root, max_short=12), [])
        self.assertEqual(cm.chatgpt_warnings(self.root, max_short=11),
                         ["warning: centroid-a: shortDescription is 12 chars (ChatGPT target 11)"])

    def test_missing_or_malformed_extensions_skipped(self):
        self.assertEqual(cm.chatgpt_warnings(self.root), [])  # make_plugin writes no extensions
        set_short(self.pdir, None, extensions="not-a-dict")
        self.assertEqual(cm.chatgpt_warnings(self.root), [])
        set_short(self.pdir, None, extensions={"com.openai": {"interface": {"shortDescription": 7}}})
        self.assertEqual(cm.chatgpt_warnings(self.root), [])

    def test_profile_prints_warnings_and_exits_zero(self):
        set_short(self.pdir, "x" * 40)
        code, out = self.run_main("--profile", "chatgpt")
        self.assertEqual(code, 0)
        self.assertIn("warning: centroid-a: shortDescription is 40 chars (ChatGPT target 30)", out)
        self.assertIn("OK: catalogs and manifests agree", out)

    def test_profile_flag_on_cli_sets_limit(self):
        set_short(self.pdir, "x" * 40)
        code, out = self.run_main("--profile", "chatgpt", "--max-short", "50")
        self.assertEqual(code, 0)
        self.assertNotIn("warning:", out)

    def test_default_run_prints_no_warnings(self):
        set_short(self.pdir, "x" * 40)
        code, out = self.run_main()
        self.assertEqual(code, 0)
        self.assertNotIn("warning:", out)

    def test_profile_still_fails_on_real_problems(self):
        write_catalogs(self.root, ["centroid-a", "centroid-missing"])
        code, _ = self.run_main("--profile", "chatgpt")
        self.assertEqual(code, 1)

    def test_max_short_must_be_positive(self):
        for bad in ("0", "-3"):
            with self.assertRaises(SystemExit) as ctx, contextlib.redirect_stderr(io.StringIO()):
                cm.main([str(self.root), "--profile", "chatgpt", "--max-short", bad])
            self.assertEqual(ctx.exception.code, 2)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tools.tests.test_check_marketplace -v`
Expected: the new tests ERROR with `AttributeError: module 'check_marketplace' has no attribute 'chatgpt_warnings'` (and `main` tests fail on the unknown `--profile` argument); old tests still pass.

- [ ] **Step 3: Implement** — in `tools/check_marketplace.py`:

Add `import argparse` to the imports, and below `NAME_RE`:

```python
DEFAULT_MAX_SHORT = 30
```

Add after `check_tree`:

```python
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
```

Replace `main` with:

```python
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
```

Note: `int("x")` raising `ValueError` inside `_positive_int` is turned into a usage error by argparse already.

- [ ] **Step 4: Run tests and the real repo**

Run: `python3 -m unittest tools.tests.test_check_marketplace -v`
Expected: all PASS.

Run: `python3 tools/check_marketplace.py --profile chatgpt; echo exit=$?`
Expected: six `warning:` lines (every current shortDescription is 80-147 chars), then `OK: catalogs and manifests agree`, `exit=0`.

Run: `python3 tools/check_marketplace.py; echo exit=$?`
Expected: only `OK: catalogs and manifests agree`, `exit=0`.

- [ ] **Step 5: Add the CI step** — in `.github/workflows/check.yml`, directly after `- run: python3 tools/check_marketplace.py`, add:

```yaml
      - run: python3 tools/check_marketplace.py --profile chatgpt
```

- [ ] **Step 6: Run the full suite and commit**

Run: `python3 tools/check_skill_links.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t .`
Expected: all pass.

```bash
git add tools/check_marketplace.py tools/tests/test_check_marketplace.py .github/workflows/check.yml
git commit -m "feat: warn on long ChatGPT shortDescriptions with --profile chatgpt

ChatGPT's Plugin Creator guide suggests a 30-character shortDescription.
Whether that is enforced is unconfirmed (issue #2), so the check only
warns, never fails, and the limit is configurable with --max-short.
CI runs the profile for information.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: `tools/export_plugin.py`

**Files:**
- Create: `tools/export_plugin.py`
- Create: `tools/tests/test_export_plugin.py`
- Modify: `.gitignore` (add `dist/`)

**Interfaces:**
- Produces: `export(root, plugin, out, allow_dirty=False, now=None) -> Path` (raises `ExportError` with `.code` 1 or 2); `main(argv) -> int`; CLI `python3 tools/export_plugin.py <plugin> [--out DIR] [--allow-dirty]`. Task 4's docs use the CLI.

- [ ] **Step 1: Write the failing tests** — create `tools/tests/test_export_plugin.py`:

```python
import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from tools.tests.helpers import make_plugin, write, write_catalogs
import export_plugin as ep

FIXED_NOW = datetime(2026, 10, 11, 12, 0, 0, tzinfo=timezone.utc)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


class ExportPluginTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.out = self.root / "dist"
        self.pdir = make_plugin(self.root, "centroid-a", version="1.2.3")
        write(self.pdir / "scripts" / "x.py", "print(1)\n")
        write_catalogs(self.root, ["centroid-a"])
        write(self.root / ".gitignore", "__pycache__/\n*.pyc\ndist/\n")
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        git(self.root, "config", "commit.gpgsign", "false")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "init")
        self.sha = git(self.root, "rev-parse", "HEAD")
        write(self.pdir / "scripts" / "__pycache__" / "x.cpython-312.pyc", "junk")

    def tearDown(self):
        self._tmp.cleanup()

    def export(self, plugin="centroid-a", **kw):
        return ep.export(self.root, plugin, self.out, now=FIXED_NOW, **kw)

    def names(self, zip_path):
        with zipfile.ZipFile(zip_path) as zf:
            return set(zf.namelist())

    def source(self, zip_path):
        with zipfile.ZipFile(zip_path) as zf:
            return zf.read("centroid-a/SOURCE.txt").decode("utf-8")

    def test_zip_name_and_layout(self):
        path = self.export()
        self.assertEqual(path, self.out / f"centroid-a-1.2.3-{self.sha[:7]}.zip")
        self.assertEqual(self.names(path), {
            "centroid-a/.claude-plugin/plugin.json",
            "centroid-a/plugin.json",
            "centroid-a/skills/s1/SKILL.md",
            "centroid-a/scripts/x.py",
            "centroid-a/SOURCE.txt",
        })

    def test_source_txt_fields(self):
        self.assertEqual(self.source(self.export()), (
            "repository: https://github.com/TD-4242/Centroid-AI\n"
            "plugin: centroid-a\n"
            "version: 1.2.3\n"
            f"commit: {self.sha}\n"
            "exported: 2026-10-11T12:00:00Z\n"
            "dirty: false\n"))

    def test_modified_file_refused(self):
        write(self.pdir / "scripts" / "x.py", "print(2)\n")
        with self.assertRaises(ep.ExportError) as ctx:
            self.export()
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("--allow-dirty", str(ctx.exception))
        self.assertFalse(self.out.exists())

    def test_untracked_file_is_dirty(self):
        write(self.pdir / "skills" / "s1" / "reference" / "new.md", "new\n")
        with self.assertRaises(ep.ExportError) as ctx:
            self.export()
        self.assertEqual(ctx.exception.code, 1)

    def test_allow_dirty_marks_source(self):
        write(self.pdir / "scripts" / "x.py", "print(2)\n")
        path = self.export(allow_dirty=True)
        self.assertIn("dirty: true\n", self.source(path))
        with zipfile.ZipFile(path) as zf:
            self.assertEqual(zf.read("centroid-a/scripts/x.py"), b"print(2)\n")

    def test_change_outside_plugin_not_dirty(self):
        write(self.root / "README.md", "uncommitted\n")
        make_plugin(self.root, "centroid-b")
        self.assertIn("dirty: false\n", self.source(self.export()))

    def test_unknown_plugin(self):
        with self.assertRaises(ep.ExportError) as ctx:
            self.export("nope")
        self.assertEqual(ctx.exception.code, 2)

    def test_path_like_name_rejected(self):
        for name in ("../centroid-a", "plugins/centroid-a", "centroid-a/"):
            with self.assertRaises(ep.ExportError) as ctx:
                self.export(name)
            self.assertEqual(ctx.exception.code, 2)

    def test_plugin_in_only_one_catalog(self):
        make_plugin(self.root, "centroid-b")
        write_catalogs(self.root, ["centroid-a", "centroid-b"], codex_names=["centroid-a"])
        with self.assertRaises(ep.ExportError) as ctx:
            self.export("centroid-b")
        self.assertEqual(ctx.exception.code, 2)

    def test_not_a_git_repo(self):
        shutil.rmtree(self.root / ".git")
        with self.assertRaises(ep.ExportError) as ctx:
            self.export()
        self.assertEqual(ctx.exception.code, 2)

    def test_out_dir_created(self):
        self.out = self.root / "a" / "b"
        self.assertTrue(self.export().is_file())

    def test_main_prints_path(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ep.main(["centroid-a", "--root", str(self.root), "--out", str(self.out)])
        self.assertEqual(code, 0)
        self.assertTrue(Path(out.getvalue().strip()).is_file())

    def test_main_error_is_one_line(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = ep.main(["nope", "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertEqual(len(err.getvalue().strip().splitlines()), 1)
        self.assertTrue(err.getvalue().startswith("error: "))

    def test_main_default_out_is_root_dist(self):
        with contextlib.redirect_stdout(io.StringIO()):
            ep.main(["centroid-a", "--root", str(self.root)])
        self.assertEqual(len(list((self.root / "dist").glob("centroid-a-1.2.3-*.zip"))), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tools.tests.test_export_plugin -v`
Expected: ERROR `ModuleNotFoundError: No module named 'export_plugin'`.

- [ ] **Step 3: Implement** — create `tools/export_plugin.py`:

```python
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


def _files(pdir):
    for path in sorted(pdir.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            yield path


def export(root, plugin, out, allow_dirty=False, now=None):
    """Write <out>/<plugin>-<version>-<shortsha>.zip and return its path.

    Raises ExportError: code 2 for an unknown plugin or a non-git tree, code 1 when
    plugins/<plugin> has uncommitted changes and allow_dirty is false.
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
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / f"{plugin}-{version}-{sha[:7]}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in _files(pdir):
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
```

Then `chmod +x tools/export_plugin.py` and add `dist/` as a new last line of `.gitignore`.

- [ ] **Step 4: Run tests and try it on the real repo**

Run: `python3 -m unittest tools.tests.test_export_plugin -v`
Expected: all PASS.

Run (after committing in Step 5, so the tree is clean): `python3 tools/export_plugin.py centroid-acorn && unzip -l dist/centroid-acorn-*.zip | tail -5 && unzip -p dist/centroid-acorn-*.zip centroid-acorn/SOURCE.txt && rm -r dist`
Expected: the zip path, a listing ending in `centroid-acorn/SOURCE.txt`, the SOURCE.txt with `dirty: false`. `git status --short` shows nothing afterwards.

- [ ] **Step 5: Run the full suite and commit**

Run: `python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t .`
Expected: all pass.

```bash
git add tools/export_plugin.py tools/tests/test_export_plugin.py .gitignore
git commit -m "feat: export a plugin as a zip for chat-app upload

The Claude app accepts uploaded plugin files and ChatGPT's Plugin
Creator may repackage one (issue #2, untested). The zip carries
SOURCE.txt with the commit, and export refuses a plugin folder with
uncommitted changes unless --allow-dirty, so every zip can be traced
back to a commit.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Then run the Step 4 real-repo check.

---

### Task 3: No-Python and local-only lines in the skills

One batch of small, identical-shape text edits. Markdown only.

**Files:**
- Modify (Manuals sections): `plugins/centroid-plc/skills/centroid-plc-programming/SKILL.md`, `plugins/centroid-vcp/skills/centroid-vcp/SKILL.md`, `plugins/centroid-cnc12-ops/skills/centroid-cnc12-mill-ops/SKILL.md`, `plugins/centroid-cnc12-ops/skills/centroid-cnc12-router-ops/SKILL.md`, `plugins/centroid-acorn/skills/centroid-acorn-install/SKILL.md`, `plugins/centroid-allin1dc/skills/centroid-allin1dc-install/SKILL.md`, `plugins/teco-f510/skills/teco-f510/SKILL.md`
- Modify (local-only): `plugins/centroid-plc/skills/compile/SKILL.md`, `plugins/centroid-plc/skills/format/SKILL.md`

**Interfaces:** none.

- [ ] **Step 1: Insert the fallback paragraph in the seven Manuals sections.** In each file, find the `## Manuals` heading, then the first line after it starting `On Windows, use`; insert this paragraph and a blank line directly before that line. Run this script from the repo root (it fails loudly if a file doesn't match):

```bash
python3 - <<'EOF'
from pathlib import Path
FALLBACK = (
    "If you can't run Python here (for example in ChatGPT or Claude web chat), don't run the script:\n"
    "give the user the manual's link from the download-links page named below, or ask them to upload\n"
    "the PDF and read the cited page from it.\n"
    "\n")
files = [
    "plugins/centroid-plc/skills/centroid-plc-programming/SKILL.md",
    "plugins/centroid-vcp/skills/centroid-vcp/SKILL.md",
    "plugins/centroid-cnc12-ops/skills/centroid-cnc12-mill-ops/SKILL.md",
    "plugins/centroid-cnc12-ops/skills/centroid-cnc12-router-ops/SKILL.md",
    "plugins/centroid-acorn/skills/centroid-acorn-install/SKILL.md",
    "plugins/centroid-allin1dc/skills/centroid-allin1dc-install/SKILL.md",
    "plugins/teco-f510/skills/teco-f510/SKILL.md",
]
for f in files:
    p = Path(f)
    text = p.read_text(encoding="utf-8")
    start = text.index("\n## Manuals\n")
    at = text.index("\nOn Windows, use", start) + 1
    assert "can't run Python here" not in text, f
    p.write_text(text[:at] + FALLBACK + text[at:], encoding="utf-8")
    print("updated", f)
EOF
```

Expected: seven `updated` lines. `git diff --stat` shows 7 files, 4 insertions each.

- [ ] **Step 2: Check one result reads right**

Run: `grep -n -B2 -A6 "can't run Python here" plugins/centroid-acorn/skills/centroid-acorn-install/SKILL.md`
Expected: the paragraph sits after the `exit 2:` bullet and its blank line, followed by a blank line, `On Windows, use ...`, a blank line, and `Download links for every manual: https://github.com/TD-4242/Centroid-AI/blob/main/docs/manuals.md`.

- [ ] **Step 3: Add the local-only paragraph to `compile`.** In `plugins/centroid-plc/skills/compile/SKILL.md`, directly after the line `# Compile-check a Centroid PLC program` and its following blank line, insert:

```markdown
This runs Centroid's compiler on the user's own computer, so it needs that computer, with CNC12
(or a copy of `mpucomp.exe`) on it. In a chat app (Claude web or Desktop chat, or ChatGPT) say so
plainly and suggest running it in Claude Code (including the Claude Desktop app's Code tab) or
Codex on that computer.

```

- [ ] **Step 4: Add the local-only paragraph to `format`.** In `plugins/centroid-plc/skills/format/SKILL.md`, directly after the line `# Format a Centroid PLC program` and its following blank line, insert:

```markdown
This runs on the user's own computer and checks its work with Centroid's compiler, so it needs
that computer, with CNC12 (or a copy of `mpucomp.exe`) on it. In a chat app (Claude web or Desktop
chat, or ChatGPT) say so plainly and suggest running it in Claude Code (including the Claude
Desktop app's Code tab) or Codex on that computer.

```

- [ ] **Step 5: Verify and commit**

Run: `python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t .`
Expected: all pass.

Run: `git diff --stat`
Expected: exactly the nine SKILL.md files.

```bash
git add plugins
git commit -m "feat(skills): fall back to links or uploads when Python can't run

In ChatGPT and Claude web chat the skills may not be able to run
fetch_manual.py. Each Manuals section now says to give the manual's
link or ask for the PDF instead, and compile and format say they need
the user's own computer with CNC12 (issue #2, #3).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Install docs and the ChatGPT pilot checklist

**Files:**
- Modify: `docs/installing.md` (two new sections after `## Codex`, before `## Requirements`)
- Create: `docs/chatgpt-pilot.md`
- Modify: `README.md` (intro sentence, Quick install)

**Interfaces:**
- Consumes: Task 2's CLI `python3 tools/export_plugin.py <plugin>` (writes `dist/<plugin>-<version>-<shortsha>.zip`); Task 1's CLI `python3 tools/check_marketplace.py --profile chatgpt`.
- Produces: anchors `docs/installing.md#claude-app-and-cowork` and `docs/installing.md#chatgpt-pilot` (GitHub slugs of the headings below).

- [ ] **Step 1: Add the two sections to `docs/installing.md`.** Insert directly before the line `## Requirements` (leaving one blank line between sections):

````markdown
## Claude app and Cowork

Steps as of 2026-10; the app's menus change often.

**Claude app (web chat or Desktop).** Add the marketplace once: *Customize → Plugins → Add → Add
marketplace → Add from a repository*, and enter `TD-4242/Centroid-AI`. Then install plugins:
*Customize → Plugins → Discover*, choose a plugin, and select *Add*.

**Cowork.** Open the *Cowork* tab, then *Customize*, and follow the same *Plugins* steps.

**Upload a plugin file instead.** You can also upload a plugin you built yourself. From a clone
of this repo:

    python3 tools/export_plugin.py centroid-acorn

It prints the path of the zip it wrote in `dist/`. The zip holds a `SOURCE.txt` recording the
commit it was built from. The plugin folder must have no uncommitted changes; `--allow-dirty`
overrides that and marks the zip.

Notes:

- Plugins need a paid Claude plan: Pro, Max, Team or Enterprise.
- A plugin added in chat is saved to your account, so it also appears in Cowork and in Claude
  Code v2.1.273 or later.
- In web chat the knowledge skills work. Downloading manuals may or may not work, depending on
  the chat's network access, and settings in `~/.centroid-ai/` may not last between chats. When
  a skill can't download a manual it gives you the link or asks you to upload the PDF.
- Compile and format run Centroid's compiler on your own computer, so they need CNC12 (and Wine
  on Linux or macOS) there. Chats in the Claude app, web or Desktop, run code in a cloud sandbox,
  so use Claude Code (including the Desktop app's Code tab) or Codex on that computer instead.

## ChatGPT (pilot)

ChatGPT support is being piloted in [issue #2](https://github.com/TD-4242/Centroid-AI/issues/2);
neither route below is confirmed yet. Steps as of 2026-10.

**Route 1: desktop app with a local marketplace (try this first).** The ChatGPT desktop app reads
a plugin marketplace from `.agents/plugins/marketplace.json` at a repository root, or from
`~/.agents/plugins/marketplace.json`. This repo already has one, so clone it:

    git clone https://github.com/TD-4242/Centroid-AI.git

Open the clone in the desktop app, install a plugin from the Plugins directory, then pick it from
the `@` menu in a chat.

**Route 2: Plugin Creator (proposed, untested).** Export a plugin zip with
`python3 tools/export_plugin.py <name>` and ask Plugin Creator to repackage it with
`create_plugin`. Nobody has tried this yet; report what happens on issue #2.

Compile and format are local-only, as described under
[Claude app and Cowork](#claude-app-and-cowork). If you are helping with the pilot, work through
the [ChatGPT pilot checklist](chatgpt-pilot.md).

````

- [ ] **Step 2: Create `docs/chatgpt-pilot.md`** with exactly:

```markdown
# ChatGPT pilot checklist

For [issue #2](https://github.com/TD-4242/Centroid-AI/issues/2). Try the centroid-acorn and
centroid-cnc12-ops plugins in ChatGPT and record what happens. Install steps:
[ChatGPT (pilot)](installing.md#chatgpt-pilot). Fill in each result, then paste the page into a
comment on the issue.

ChatGPT version and platform:

## 1. Route 1 installs

Clone the repo, open it in the ChatGPT desktop app, and install both plugins from the Plugins
directory.

Result:

## 2. The plugins appear in the `@` menu

Start a chat and type `@`. Note each plugin's name and description as shown, and whether the
description is cut off.

Result:

## 3. Questions load the right reference

Ask each question in a new chat and note which file under `skills/*/reference/` the answer drew
on.

- centroid-acorn: "How do I pair two motors on the Y axis of an Acorn and square the gantry?"
  Expected: `axis-pairing.md`.
- centroid-cnc12-ops: "In CNC12 Router, how do I set part zero for X and Y?" Expected:
  `part-setup.md` in the router skill.

Result:

## 4. Fallback when Python can't run

Ask something the references don't cover in detail, such as "Show me the exact Acorn
Installation Manual text on the Acorn's E-stop wiring." If ChatGPT can't run Python, the skill
should give the manual's download link or ask you to upload the PDF, not fail silently.

Result:

## 5. Is the 30-character description limit enforced?

`python3 tools/check_marketplace.py --profile chatgpt` lists every description over 30
characters (currently all of them). Note whether ChatGPT rejected, truncated or accepted them.

Result:

## 6. Is route 2 needed?

If route 1 worked, say so and skip this. Otherwise try route 2 from the install page and
describe what Plugin Creator did.

Result:

## Next steps

Post the results on issue #2. Shorten the descriptions only if item 5 shows the limit is
enforced; add another install route only if items 1 and 6 show one is needed.
```

- [ ] **Step 3: Update `README.md`.**

Replace the intro's first sentence fragment `help AI coding assistants (Claude Code and Codex) work with` with `help AI assistants (Claude Code, Codex and the Claude app) work with`.

In **Quick install**, replace the line

```
then install plugins from the Plugins directory. Full steps: [docs/installing.md](docs/installing.md).
```

with

```
then install plugins from the Plugins directory.

**Claude app and Cowork:** add the marketplace from *Customize → Plugins*; see
[Claude app and Cowork](docs/installing.md#claude-app-and-cowork). **ChatGPT** is in pilot:
[ChatGPT (pilot)](docs/installing.md#chatgpt-pilot). Full steps: [docs/installing.md](docs/installing.md).
```

- [ ] **Step 4: Verify links and commit**

Run: `python3 tools/check_skill_links.py && python3 tools/check_marketplace.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t .`
Expected: all pass (the link checker validates the new anchors `#claude-app-and-cowork` and `#chatgpt-pilot`).

```bash
git add docs/installing.md docs/chatgpt-pilot.md README.md
git commit -m "docs: Claude app, Cowork and ChatGPT pilot install steps

Closes the documentation part of #3 (Claude app and Cowork, with the
upload alternative, plan and environment notes) and adds the ChatGPT
routes and pilot checklist for #2. Menu steps are dated because both
apps change them often.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Open the PR and update issue #2

Controller task (no implementer subagent); runs after the final whole-branch review is clean.

- [ ] **Step 1: Final checks**

Run: `python3 tools/check_marketplace.py --profile chatgpt && python3 tools/check_skill_links.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t . && git status --short`
Expected: all pass, six warnings, clean tree.

- [ ] **Step 2: Push and open the PR**

```bash
git push -u origin chatgpt-and-claude-app
gh pr create --base main --title "Claude app, Cowork and ChatGPT pilot install" --body-file <scratchpad>/pr-body.md
```

The body summarizes the four changes (docs, export tool, `--profile chatgpt`, skill fallbacks), says `Closes #3` and `Part of #2`, links `docs/chatgpt-pilot.md`, and ends with `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.

- [ ] **Step 3: Comment on issue #2** with the revised scope (approach A: routes documented, export tool and length warning shipped, descriptions unchanged pending the pilot) and a link to the pilot checklist on the PR branch.
