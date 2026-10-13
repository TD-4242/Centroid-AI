# ChatGPT Browser Install and Release Archives Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish per-plugin zips on tagged GitHub Releases and give browser ChatGPT users a README-linked install guide and pilot checklist, with every browser step marked unverified (phase 1 of #2).

**Architecture:** `tools/export_plugin.py` gains `--all` and `--stable-name`; a new tag-triggered workflow runs the checks, exports all plugins and creates the release. Docs add `docs/chatgpt-browser.md`, rewrite `docs/chatgpt-pilot.md` browser-first, and link both from README and `docs/installing.md`.

**Tech Stack:** Python ≥ 3.10 stdlib, `unittest`, git, GitHub Actions, `gh` CLI, Markdown.

**Spec:** `docs/superpowers/specs/2026-10-13-chatgpt-browser-release-design.md`

## Global Constraints

- Python ≥ 3.10, stdlib only. Tests: `python3 -m unittest discover -s tools/tests -t .` from the repo root.
- Comments are 1-2 lines and only clarify confusing code; rationale goes in the commit message.
- Do not change skill content, plugin manifests, catalogs, `shared/*` or `plugins/*/scripts/*`.
- Every browser ChatGPT step stays marked *(unverified)*; the 30-character limit stays unverified.
- Release asset URLs use `https://github.com/TD-4242/Centroid-AI/releases/latest/download/<plugin>.zip`.
- First release tag is `v0.2.0`, pushed only after the maintainer says so (not part of this plan's tasks).
- Before every commit these pass: `python3 tools/check_marketplace.py`, `python3 tools/check_skill_links.py`, `python3 tools/sync_shared.py --check`, the unit tests.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Never modify `/home/bwarner/github/Acroloc-Centroid` or `/home/bwarner/github/Torchmate-Centroid`.

## Review Focus

1. `--all` with one dirty plugin partway through the catalog stops with exit 1 and that plugin's error; zips already written stay — pinned in Task 1 `test_all_stops_on_dirty_plugin`.
2. Re-running `--all --stable-name` into a `dist/` that already holds zips overwrites them rather than failing or appending — pinned in Task 1 `test_stable_name_overwrites_existing_zip`.
3. A plugin listed in only one catalog is skipped by `--all`, not exported and not an error — pinned in Task 1 `test_all_skips_plugin_in_one_catalog`.
4. A plugin listed twice in a catalog is exported once — pinned in Task 1 `test_all_deduplicates`.
5. The release must never upload anything but the zips and `SHA256SUMS.txt`, and must not publish when a check fails — pinned in Task 2 by the explicit asset list and step order, checked by `test_release_workflow_shape` in Task 2.

---

### Task 1: `export_plugin.py --all` and `--stable-name`

**Files:**
- Modify: `tools/export_plugin.py` (new `catalog_plugins`, `export_all`; `export` gains `stable_name`; `main` gains a required mutually exclusive `plugin | --all` and `--stable-name`)
- Modify: `tools/tests/test_export_plugin.py` (new test class)

**Interfaces:**
- Produces: `catalog_plugins(root) -> list[str]`; `export(root, plugin, out, allow_dirty=False, now=None, stable_name=False) -> Path`; `export_all(root, out, allow_dirty=False, now=None, stable_name=False) -> list[Path]`; CLI `export_plugin.py (<plugin> | --all) [--out DIR] [--allow-dirty] [--stable-name]`. Task 2's workflow runs `python3 tools/export_plugin.py --all --stable-name --out dist`.

- [ ] **Step 1: Write the failing tests** — append to `tools/tests/test_export_plugin.py`, above `if __name__ == "__main__":`:

```python
class ExportAllTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.out = self.root / "dist"
        for name in ("centroid-b", "centroid-a"):
            make_plugin(self.root, name, version="1.0.0")
        write_catalogs(self.root, ["centroid-b", "centroid-a"])
        write(self.root / ".gitignore", "__pycache__/\n*.pyc\ndist/\n")
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        git(self.root, "config", "commit.gpgsign", "false")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "init")
        self.sha = git(self.root, "rev-parse", "HEAD")

    def tearDown(self):
        self._tmp.cleanup()

    def test_catalog_plugins_in_catalog_order(self):
        self.assertEqual(ep.catalog_plugins(self.root), ["centroid-b", "centroid-a"])

    def test_all_skips_plugin_in_one_catalog(self):
        make_plugin(self.root, "centroid-c")
        write_catalogs(self.root, ["centroid-b", "centroid-a", "centroid-c"],
                       codex_names=["centroid-b", "centroid-a"])
        self.assertEqual(ep.catalog_plugins(self.root), ["centroid-b", "centroid-a"])

    def test_all_deduplicates(self):
        write_catalogs(self.root, ["centroid-b", "centroid-a", "centroid-b"])
        self.assertEqual(ep.catalog_plugins(self.root), ["centroid-b", "centroid-a"])

    def test_export_all_writes_one_zip_per_plugin(self):
        paths = ep.export_all(self.root, self.out, now=FIXED_NOW)
        self.assertEqual([p.name for p in paths],
                         [f"centroid-b-1.0.0-{self.sha[:7]}.zip", f"centroid-a-1.0.0-{self.sha[:7]}.zip"])
        self.assertTrue(all(p.is_file() for p in paths))

    def test_stable_name(self):
        path = ep.export(self.root, "centroid-a", self.out, now=FIXED_NOW, stable_name=True)
        self.assertEqual(path, self.out / "centroid-a.zip")
        with zipfile.ZipFile(path) as zf:
            self.assertIn("version: 1.0.0\n", zf.read("centroid-a/SOURCE.txt").decode("utf-8"))

    def test_stable_name_overwrites_existing_zip(self):
        write(self.out / "centroid-a.zip", "stale, not a zip")
        path = ep.export(self.root, "centroid-a", self.out, now=FIXED_NOW, stable_name=True)
        with zipfile.ZipFile(path) as zf:
            self.assertIn("centroid-a/SOURCE.txt", zf.namelist())

    def test_all_stops_on_dirty_plugin(self):
        write(self.root / "plugins" / "centroid-a" / "skills" / "s1" / "SKILL.md", "changed\n")
        with self.assertRaises(ep.ExportError) as ctx:
            ep.export_all(self.root, self.out, now=FIXED_NOW, stable_name=True)
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("plugins/centroid-a", str(ctx.exception))
        self.assertTrue((self.out / "centroid-b.zip").is_file())
        self.assertFalse((self.out / "centroid-a.zip").exists())

    def test_main_all_prints_each_path(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ep.main(["--all", "--stable-name", "--root", str(self.root), "--out", str(self.out)])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().splitlines(),
                         [str(self.out / "centroid-b.zip"), str(self.out / "centroid-a.zip")])

    def test_main_all_error_exit_code(self):
        write(self.root / "plugins" / "centroid-a" / "skills" / "s1" / "SKILL.md", "changed\n")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = ep.main(["--all", "--root", str(self.root), "--out", str(self.out)])
        self.assertEqual(code, 1)
        self.assertTrue(err.getvalue().startswith("error: "))

    def test_main_plugin_and_all_is_usage_error(self):
        for argv in (["centroid-a", "--all"], []):
            with self.assertRaises(SystemExit) as ctx, contextlib.redirect_stderr(io.StringIO()):
                ep.main([*argv, "--root", str(self.root)])
            self.assertEqual(ctx.exception.code, 2)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tools.tests.test_export_plugin -v 2>&1 | tail -5`
Expected: the new `ExportAllTest` tests ERROR/FAIL (`AttributeError: ... 'catalog_plugins'`, unexpected keyword `stable_name`, unrecognized `--all`); the existing `ExportPluginTest` tests still pass.

- [ ] **Step 3: Implement** — in `tools/export_plugin.py`:

Add after `_catalog_names`:

```python
def catalog_plugins(root):
    """Plugins listed in both catalogs, in Claude catalog order, each once."""
    root = Path(root)
    try:
        data = json.loads((root / CATALOGS[0]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ExportError(f"cannot read {CATALOGS[0]}: {e}", 2) from e
    others = _catalog_names(root, CATALOGS[1])
    names = [e.get("name") for e in data.get("plugins", []) if isinstance(e, dict)]
    return [n for i, n in enumerate(names) if n in others and n not in names[:i]]
```

Change the `export` signature and zip name:

```python
def export(root, plugin, out, allow_dirty=False, now=None, stable_name=False):
```

and replace

```python
    zip_path = out / f"{plugin}-{version}-{sha[:7]}.zip"
```

with

```python
    zip_path = out / (f"{plugin}.zip" if stable_name else f"{plugin}-{version}-{sha[:7]}.zip")
```

Update the docstring's first line to: `"""Write <out>/<plugin>-<version>-<shortsha>.zip (or <plugin>.zip with stable_name) and return its path.`

Add after `export`:

```python
def export_all(root, out, allow_dirty=False, now=None, stable_name=False):
    """Export every catalog plugin; the first ExportError stops the run, earlier zips stay."""
    return [export(root, name, out, allow_dirty, now, stable_name) for name in catalog_plugins(root)]
```

Replace `main` with:

```python
def main(argv):
    parser = argparse.ArgumentParser(description="Zip plugins for upload to the Claude app or ChatGPT.")
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("plugin", nargs="?", help="plugin name, e.g. centroid-acorn")
    which.add_argument("--all", action="store_true", help="export every plugin in the catalogs")
    parser.add_argument("--out", type=Path, help="output folder (default: dist/ in the repo)")
    parser.add_argument("--allow-dirty", action="store_true",
                        help="export even if a plugin has uncommitted changes")
    parser.add_argument("--stable-name", action="store_true",
                        help="name zips <plugin>.zip instead of <plugin>-<version>-<sha>.zip")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    out = args.out or args.root / "dist"
    try:
        if args.all:
            for path in export_all(args.root, out, args.allow_dirty, stable_name=args.stable_name):
                print(path)
        else:
            print(export(args.root, args.plugin, out, args.allow_dirty, stable_name=args.stable_name))
    except ExportError as e:
        print(f"error: {e}", file=sys.stderr)
        return e.code
    return 0
```

Note: `export_all` builds its list before `main` prints, so on an error no paths are printed even though earlier zips exist; that matches the tests.

- [ ] **Step 4: Run the tests and the real repo**

Run: `python3 -m unittest tools.tests.test_export_plugin -v 2>&1 | tail -3`
Expected: `OK`.

Run (after the Step 5 commit, so the tree is clean): `python3 tools/export_plugin.py --all --stable-name --out /tmp/claude-1001/-home-bwarner-github/218ab847-f8fd-455c-9698-7566514a7be3/scratchpad/dist && ls /tmp/claude-1001/-home-bwarner-github/218ab847-f8fd-455c-9698-7566514a7be3/scratchpad/dist`
Expected: six paths printed, then `centroid-acorn.zip centroid-allin1dc.zip centroid-cnc12-ops.zip centroid-plc.zip centroid-vcp.zip teco-f510.zip`. Delete that scratch `dist` afterwards.

- [ ] **Step 5: Full suite and commit**

Run: `python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t . 2>&1 | tail -1`
Expected: all pass, last line `OK (skipped=4)`.

```bash
git add tools/export_plugin.py tools/tests/test_export_plugin.py
git commit -m "feat: export all plugins with stable zip names

The release workflow needs every plugin zipped in one call, under
names that latest/download links can point at (issue #2). --all
exports each plugin listed in both catalogs in catalog order and
stops at the first error; --stable-name writes <plugin>.zip, with
version and commit still in SOURCE.txt.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Then run the Step 4 real-repo check.

---

### Task 2: Release workflow

**Files:**
- Create: `.github/workflows/release.yml`
- Create: `tools/tests/test_release_workflow.py`

**Interfaces:**
- Consumes: Task 1 CLI `python3 tools/export_plugin.py --all --stable-name --out dist`.
- Produces: on a `v*` tag, a GitHub Release with assets `<plugin>.zip` ×6 and `SHA256SUMS.txt`.

- [ ] **Step 1: Write the failing shape test** — create `tools/tests/test_release_workflow.py`. It reads the YAML as text (PyYAML isn't stdlib) and pins the safety properties:

```python
import unittest

from tools.tests.helpers import REPO

WORKFLOW = REPO / ".github" / "workflows" / "release.yml"


class ReleaseWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_release_workflow_shape(self):
        lines = [line.strip() for line in self.text.splitlines()]
        self.assertIn('tags: ["v*"]', lines)
        self.assertIn("contents: write", lines)
        order = ["tools/check_marketplace.py", "tools/check_skill_links.py",
                 "tools/sync_shared.py --check", "unittest discover",
                 "tools/export_plugin.py --all --stable-name --out dist",
                 "sha256sum *.zip > SHA256SUMS.txt", "gh release create"]
        positions = [self.text.index(step) for step in order]
        self.assertEqual(positions, sorted(positions), "checks must run before export and publish")

    def test_release_uploads_only_zips_and_sums(self):
        create = next(line for line in self.text.splitlines() if "gh release create" in line)
        self.assertIn("dist/*.zip dist/SHA256SUMS.txt", create)
        self.assertNotIn("dist/*", create.replace("dist/*.zip", ""))
        self.assertIn("--notes-file dist/NOTES.md", create)
        self.assertIn("--generate-notes", create)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m unittest tools.tests.test_release_workflow -v 2>&1 | tail -3`
Expected: ERROR `FileNotFoundError: ... release.yml`.

- [ ] **Step 3: Create `.github/workflows/release.yml`** with exactly:

```yaml
name: release
on:
  push:
    tags: ["v*"]
permissions:
  contents: write
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python3 tools/check_marketplace.py
      - run: python3 tools/check_skill_links.py
      - run: python3 tools/sync_shared.py --check
      - run: python3 -m unittest discover -s tools/tests -t . -v
      - run: python3 tools/export_plugin.py --all --stable-name --out dist
      - run: cd dist && sha256sum *.zip > SHA256SUMS.txt
      - name: Publish release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          echo "Download a plugin zip below. Browser ChatGPT install steps (unverified): https://github.com/TD-4242/Centroid-AI/blob/main/docs/chatgpt-browser.md" > dist/NOTES.md
          gh release create "$GITHUB_REF_NAME" dist/*.zip dist/SHA256SUMS.txt --title "$GITHUB_REF_NAME" --notes-file dist/NOTES.md --generate-notes
```

- [ ] **Step 4: Run the tests and parse the YAML**

Run: `python3 -m unittest tools.tests.test_release_workflow -v 2>&1 | tail -3`
Expected: `OK`.

Run: `python3 -c "import yaml; d = yaml.safe_load(open('.github/workflows/release.yml')); print(sorted(d[True]['push']), len(d['jobs']['release']['steps']))"`
Expected: `['tags'] 9` (PyYAML reads the `on` key as `True`). If PyYAML isn't installed, skip this check and say so.

- [ ] **Step 5: Full suite and commit**

Run: `python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t . 2>&1 | tail -1`
Expected: all pass.

```bash
git add .github/workflows/release.yml tools/tests/test_release_workflow.py
git commit -m "ci: publish plugin zips on version tags

A v* tag runs the same checks as CI, exports every plugin under a
stable name, writes SHA256SUMS.txt and creates a GitHub Release with
only those files, so browser users can install without Python or Git
(issue #2). A failing check stops the job before anything is
published. The shape test pins step order and the asset list.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Browser guide, pilot checklist and links

**Files:**
- Create: `docs/chatgpt-browser.md`
- Replace: `docs/chatgpt-pilot.md`
- Modify: `docs/installing.md` (Claude app upload paragraph; ChatGPT section intro)
- Modify: `README.md` (Quick install)

**Interfaces:**
- Consumes: Task 2's release asset names (`<plugin>.zip`, `SHA256SUMS.txt`).
- Produces: `docs/chatgpt-browser.md` with headings `## Install` and `## Troubleshooting` (anchors `#install`, `#troubleshooting`).

- [ ] **Step 1: Create `docs/chatgpt-browser.md`** with exactly:

````markdown
# ChatGPT in the browser

> **Unverified:** these steps have not yet been tested end to end in browser ChatGPT
> ([#2](https://github.com/TD-4242/Centroid-AI/issues/2)). Steps as of 2026-10. Each untested
> step is marked *(unverified)*. Please report what happens on #2.

These plugins answer questions about Centroid CNC12, Acorn and ALLIN1DC controls and the TECO F510
drive, citing the official manuals by page. In the browser they work as knowledge plugins: no
Python, Git or compiler is needed.

## What you need

- A ChatGPT account with access to Plugin Creator. Which plans include it: *(unverified)*.
- A web browser.

## Install

1. **Download a plugin zip.** Start with Centroid Acorn or Centroid CNC12 Operation.

   | Plugin | Download |
   | --- | --- |
   | Centroid Acorn | [centroid-acorn.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-acorn.zip) |
   | Centroid CNC12 Operation | [centroid-cnc12-ops.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-cnc12-ops.zip) |
   | Centroid PLC | [centroid-plc.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-plc.zip) |
   | Centroid VCP | [centroid-vcp.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-vcp.zip) |
   | Centroid ALLIN1DC | [centroid-allin1dc.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-allin1dc.zip) |
   | TECO F510 VFD | [teco-f510.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/teco-f510.zip) |

   All files and checksums ([SHA256SUMS.txt](https://github.com/TD-4242/Centroid-AI/releases/latest/download/SHA256SUMS.txt))
   are on the [Releases page](https://github.com/TD-4242/Centroid-AI/releases). If a link above
   doesn't work, use that page.

2. **Open Plugin Creator** in a new chat and attach the zip *(unverified: how Plugin Creator is
   started in the browser)*.

3. **Paste this prompt**, replacing the three `<...>` values from the table below:

   ```
   Create a private plugin from the attached zip. It holds one plugin folder: skills/<name>/SKILL.md
   files, their reference/*.md files, a plugin.json and a SOURCE.txt.
   - Keep every SKILL.md and reference file word for word, including page citations and safety notes.
   - Name: <plugin name>. Display name: <display name>.
   - Use the description from plugin.json. Only if you require a description of 30 characters or
     fewer, use instead: "<short description>", and tell me that you did.
   - The scripts/ folder holds optional local helpers; include it if you can, skip it if you can't,
     and tell me which.
   - Tell me about any file you could not include and any error, word for word.
   ```

   | Plugin name | Display name | Short description |
   | --- | --- | --- |
   | centroid-acorn | Centroid Acorn | Centroid Acorn setup help |
   | centroid-cnc12-ops | Centroid CNC12 Operation | Centroid CNC12 operation help |
   | centroid-plc | Centroid PLC | Centroid PLC programming help |
   | centroid-vcp | Centroid VCP | Centroid VCP customization |
   | centroid-allin1dc | Centroid ALLIN1DC | Centroid ALLIN1DC setup help |
   | teco-f510 | TECO F510 VFD | TECO F510 spindle VFD help |

   The short descriptions are 30 characters or fewer, for the case where Plugin Creator requires
   that *(unverified whether it does)*.

4. **Install the private plugin** Plugin Creator produces *(unverified)*.

5. **Use it.** Start a new conversation, type `@`, choose the plugin and ask a question, for
   example "How do I pair two motors on the Y axis of an Acorn and square the gantry?"
   *(unverified)*.

## Without a compiler or Python

Knowledge answers work in the browser. When an answer needs a manual's exact wording, the plugin
gives you the manual's download link (all links: [docs/manuals.md](manuals.md)) or asks you to
upload the PDF and then reads the cited page from it.

Compile and format (in Centroid PLC) run Centroid's compiler on your own computer. They need
Claude Code or Codex on the computer with CNC12 and do not work in the browser.

## Updating

Download the newer zip from the [Releases page](https://github.com/TD-4242/Centroid-AI/releases).
Ask Plugin Creator to update your existing private plugin from it *(unverified)*, or remove the
plugin and install it again. `SOURCE.txt` inside a zip shows its version and the commit it was
built from.

## Troubleshooting

In every case, please post the exact message on [#2](https://github.com/TD-4242/Centroid-AI/issues/2).

| Symptom | Try |
| --- | --- |
| Plugin Creator rejects the zip | Unzip it and attach the files instead, or attach only the `SKILL.md` and `reference/*.md` files. |
| "Description too long" | Use the short description from the table in step 3. |
| The plugin isn't in the `@` menu | Start a new conversation; check the plugin is installed and turned on. |
| Answers ignore the plugin's references | Pick the plugin with `@` and ask it to read its reference files. |
| A manual won't download | Use the link the plugin gives, download the PDF yourself and upload it to the chat. |

## Other ways to install

ChatGPT desktop app, Claude app, Claude Code and Codex: see [installing.md](installing.md).
````

- [ ] **Step 2: Replace `docs/chatgpt-pilot.md`** with exactly:

```markdown
# ChatGPT pilot checklist

For [issue #2](https://github.com/TD-4242/Centroid-AI/issues/2), phase 1. Test the Centroid Acorn
and Centroid CNC12 Operation plugins in **browser** ChatGPT, following
[ChatGPT in the browser](chatgpt-browser.md). Fill in each result, copy any error word for word,
then paste this page into a comment on #2.

ChatGPT plan:
Browser:
Date:

## 1. Download

Download `centroid-acorn.zip` and `centroid-cnc12-ops.zip` from the latest release. Optionally check
them against `SHA256SUMS.txt`.

Result:
Exact error (if any):

## 2. Plugin Creator accepts the zip

Attach each zip with the guide's prompt. Note how you started Plugin Creator and what it said
about `scripts/` and any skipped files.

Result:
Exact error (if any):

## 3. The 30-character description limit

Did Plugin Creator require a description of 30 characters or fewer? Did it use the short one?

Result:
Exact error (if any):

## 4. Install

Did the private plugin install? Where did you find the install control?

Result:
Exact error (if any):

## 5. The `@` menu

In a new conversation, type `@`. Note each plugin's name and description as shown, and whether
the description is cut off.

Result:
Exact error (if any):

## 6. Questions load the right reference

Ask each in a new conversation with the plugin picked, and note which reference file the answer
drew on.

- Centroid Acorn: "How do I pair two motors on the Y axis of an Acorn and square the gantry?"
  Expected: `axis-pairing.md`.
- Centroid CNC12 Operation: "In CNC12 Router, how do I set part zero for X and Y?" Expected:
  `part-setup.md` in the router skill.

Result:
Exact error (if any):

## 7. Manual-link fallback

After a cited Acorn answer, ask: "Quote word for word what the Acorn Installation Manual says on
the page your answer cites." Expected: the manual's download link or a request to upload the PDF,
not an invented quote.

Result:
Exact error (if any):

## 8. Uploaded-PDF fallback

Download the Acorn Installation Manual from [docs/manuals.md](manuals.md), upload it to the chat
and repeat item 7. Expected: the quoted text from the cited page.

Result:
Exact error (if any):

## 9. Update

If a newer release exists, update the plugin from its zip as the guide describes. Skip if there is
only one release.

Result:
Exact error (if any):

## Optional: desktop route

The ChatGPT desktop app can read this repo's `.agents/plugins/marketplace.json`; steps are in
[ChatGPT (pilot)](installing.md#chatgpt-pilot). Note whether it worked.

Result:

## Next steps

Post the results on #2. Phase 2 rewrites the browser guide from them and removes the
*(unverified)* marks for what passed. Plugin descriptions are shortened only if item 3 shows the
limit is enforced.
```

- [ ] **Step 3: Edit `docs/installing.md`.**

(a) Replace this paragraph:

```
**Upload a plugin file instead.** You can also upload a plugin you built yourself. From a clone
of this repo:
```

with:

```
**Upload a plugin file instead.** Ready-made zips are on the
[Releases page](https://github.com/TD-4242/Centroid-AI/releases), e.g.
`https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-acorn.zip`. Or build one
from a clone of this repo:
```

(b) Replace:

```
ChatGPT support is being piloted in [issue #2](https://github.com/TD-4242/Centroid-AI/issues/2);
neither route below is confirmed yet. Steps as of 2026-10.
```

with:

```
ChatGPT support is being piloted in [issue #2](https://github.com/TD-4242/Centroid-AI/issues/2);
none of these routes is confirmed yet. Steps as of 2026-10.

**In the browser (Chat/Work):** follow [ChatGPT in the browser](chatgpt-browser.md). It needs no
Python or Git: download a plugin zip from the Releases page and give it to Plugin Creator.
```

- [ ] **Step 4: Edit `README.md`.** Replace:

```
[Claude app and Cowork](docs/installing.md#claude-app-and-cowork). **ChatGPT** is in pilot:
[ChatGPT (pilot)](docs/installing.md#chatgpt-pilot). Full steps: [docs/installing.md](docs/installing.md).
```

with:

```
[Claude app and Cowork](docs/installing.md#claude-app-and-cowork).

**ChatGPT in the browser** (unverified, being piloted): download a plugin zip from
[Releases](https://github.com/TD-4242/Centroid-AI/releases) and follow
[docs/chatgpt-browser.md](docs/chatgpt-browser.md). Desktop app:
[ChatGPT (pilot)](docs/installing.md#chatgpt-pilot). Full steps: [docs/installing.md](docs/installing.md).
```

- [ ] **Step 5: Verify and commit**

Run: `python3 tools/check_skill_links.py && python3 tools/check_marketplace.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t . 2>&1 | tail -1`
Expected: all pass (the link checker covers the new relative links and anchors).

Run: `grep -c "(unverified" docs/chatgpt-browser.md`
Expected: at least 6.

```bash
git add docs/chatgpt-browser.md docs/chatgpt-pilot.md docs/installing.md README.md
git commit -m "docs: ChatGPT browser install guide and browser-first pilot

Issue #2 asks for easy installation in ChatGPT's browser Chat/Work
with no Python or Git. The guide downloads a release zip and hands it
to Plugin Creator with a copy-and-paste prompt; every step is marked
unverified until the phase 2 pilot. The pilot checklist now tests the
browser route end to end for Acorn and CNC12 and records exact errors.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Open the PR and update issue #2

Controller task; runs after the final whole-branch review is clean.

- [ ] **Step 1: Final checks** — `python3 tools/check_marketplace.py --profile chatgpt && python3 tools/check_skill_links.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t . && git status --short`. Expected: all pass, clean tree.
- [ ] **Step 2: Push and open the PR** — `git push -u origin chatgpt-browser-release`, then `gh pr create --base main` with a body summarizing the four changes, saying `Part of #2`, noting that tag `v0.2.0` will be pushed only on the maintainer's go-ahead after merge, and ending with `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
- [ ] **Step 3: Comment on #2** with the PR link, the guide and checklist links, and that phase 2 follows the posted results.
