# Centroid-AI Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `centroid-ai` plugin marketplace: six installable Claude Code / Codex plugins carrying the generic Centroid CNC12 skills and PLC compile/format tooling extracted from the Acroloc-Centroid and Torchmate-Centroid repos.

**Architecture:** One repo, two catalogs (`.claude-plugin/marketplace.json` for Claude Code, `.agents/plugins/marketplace.json` for Codex) pointing at `plugins/<name>/`. Each plugin has a Claude manifest, a portable root `plugin.json` for Codex, `skills/`, `manuals.json` and `scripts/`. Shared helpers live once in `shared/` and are copied into plugins by `tools/sync_shared.py`; repo checkers in `tools/` keep catalogs, manifests, links and copies consistent.

**Tech Stack:** Python 3.10+ stdlib only (scripts and tests, `unittest`), Markdown skills, JSON manifests, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-10-centroid-ai-marketplace-design.md`

**Source repos (read-only, never modify):** `/home/bwarner/github/Acroloc-Centroid` (abbrev. **AC**) and `/home/bwarner/github/Torchmate-Centroid` (abbrev. **TM**). Skills are under `.claude/skills/`.

## Global Constraints

- Python scripts: stdlib only, Python ≥ 3.10, run on Windows, Linux and macOS; no Bash dependency.
- Tests: `unittest`; run all with `python3 -m unittest discover -s tools/tests -t . -v` from the repo root.
- Marketplace name `centroid-ai`; owner `{"name": "Bill Warner", "url": "https://github.com/TD-4242"}`; every plugin `version` `0.1.0`, `license` `MIT`, `homepage`/`repository` `https://github.com/TD-4242/Centroid-AI`, author `{"name": "Bill Warner"}`.
- Never commit vendor binaries (`mpucomp.exe`) or vendor PDFs. `.gitignore` excludes `*.pdf`, `*.exe`, `__pycache__/`.
- Skills are generic: `grep -rniE 'acroloc|torchmate|this repo|this machine|series 10|Centroid-Acroloc-ALLIN1DC|acorn_router_plc' plugins/` must print nothing.
- No tombstones in skills ("previously", "used to", "REMOVED").
- Comments: 1–2 lines, only where code is confusing; rationale goes in commit messages.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Work on branch `spec/marketplace-design` (already holds the spec); never push without asking.
- Shared user state: `~/.centroid-ai/` (override `CENTROID_AI_HOME`); manuals dir `~/.centroid-ai/manuals/` (override `CENTROID_AI_MANUALS` or config `manuals.dir`).

### Plugin manifest templates (used by Tasks 9–14)

`plugins/<name>/.claude-plugin/plugin.json`:

```json
{
  "name": "<name>",
  "version": "0.1.0",
  "description": "<description>",
  "author": { "name": "Bill Warner" },
  "homepage": "https://github.com/TD-4242/Centroid-AI",
  "repository": "https://github.com/TD-4242/Centroid-AI",
  "license": "MIT",
  "keywords": [<keywords>]
}
```

`plugins/<name>/plugin.json` (portable, read by Codex):

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "<name>",
  "version": "0.1.0",
  "description": "<description>",
  "author": { "name": "Bill Warner" },
  "homepage": "https://github.com/TD-4242/Centroid-AI",
  "repository": "https://github.com/TD-4242/Centroid-AI",
  "license": "MIT",
  "keywords": [<keywords>],
  "extensions": {
    "com.openai": {
      "interface": {
        "displayName": "<displayName>",
        "shortDescription": "<description>",
        "category": "Manufacturing"
      }
    }
  }
}
```

Catalog entries — append to `plugins` in `.claude-plugin/marketplace.json`:

```json
{ "name": "<name>", "source": "./plugins/<name>", "description": "<description>", "category": "manufacturing" }
```

and to `plugins` in `.agents/plugins/marketplace.json`:

```json
{ "name": "<name>", "source": { "source": "local", "path": "./plugins/<name>" },
  "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" }, "category": "Manufacturing" }
```

### Plugin values

| name | displayName | description | keywords |
| --- | --- | --- | --- |
| `centroid-plc` | Centroid PLC | Write, read and debug Centroid CNC12 PLC programs (MPU11/ALLIN1DC and Acorn), and compile-check or format .src files with Centroid's own compiler. | `"centroid","cnc12","plc","mpu11","acorn"` |
| `centroid-vcp` | Centroid VCP | Customize the Centroid CNC12 Virtual Control Panel: buttons, skins, graphics, LED states and PLC-wired actions. | `"centroid","cnc12","vcp"` |
| `centroid-cnc12-ops` | Centroid CNC12 Operation | Operate Centroid CNC12 Mill and Router software: menus, jogging, part zero, tool offsets, running jobs, and G/M-code, parameter and message lookup. | `"centroid","cnc12","mill","router"` |
| `centroid-acorn` | Centroid Acorn | Install, wire, configure and troubleshoot a Centroid Acorn controller, including the Acorn Wizard and axis pairing and squaring. | `"centroid","acorn","install"` |
| `centroid-allin1dc` | Centroid ALLIN1DC | Install, wire, commission and tune a Centroid ALLIN1DC (MPU11) servo controller. | `"centroid","allin1dc","mpu11","install"` |
| `teco-f510` | TECO F510 VFD | Set up, wire, tune and troubleshoot a TECO-Westinghouse F510 VFD driving a CNC spindle. | `"teco","f510","vfd","spindle"` |

### Manuals (for `manuals.json`, Tasks 9–14, and `docs/manuals.md`)

All URLs verified 200 `application/pdf` on 2026-10-10. `pdfOffset`: PDF page = cited page + offset (0 where skills cite PDF pages directly).

| id | plugin | title | citeAs | url | file | expectRev | expectPages | pdfOffset | sizeMB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plc-manual` | centroid-plc | CNC12 PLC Programming Manual | PLC Manual | https://www.centroidcnc.com/centroid_diy/downloads/centroid_plc_programming_manual.pdf | centroid_plc_programming_manual.pdf | rev8 07/24/26 | 132 | 0 | 3 |
| `vcp-manual` | centroid-vcp | VCP 2.0 Users Manual | VCP Manual | https://www.centroidcnc.com/centroid_diy/downloads/centroid_vcp_users_manual.pdf | centroid_vcp_users_manual.pdf | rev28 | 64 | 0 | 12 |
| `mill-manual` | centroid-cnc12-ops | CNC12 Milling Machine Operators Manual | Mill Manual | https://www.centroidcnc.com/centroid_diy/downloads/operator_manuals/centroid-cnc12-mill-operator-manual.pdf | centroid-cnc12-mill-operator-manual.pdf | CNC12 V5.4+ | 506 | 1 | 57 |
| `router-manual` | centroid-cnc12-ops | CNC12 Router Operators Manual | Router Manual | https://www.centroidcnc.com/centroid_diy/downloads/operator_manuals/centroid-cnc12-router-operator-manual.pdf | centroid-cnc12-router-operator-manual.pdf | CNC12 V5.42+ | 511 | 1 | 63 |
| `acorn-install` | centroid-acorn | Acorn Installation Manual | Acorn Install | https://www.centroidcnc.com/centroid_diy/downloads/acorn_documentation/centroid_acorn_install_manual.pdf | centroid_acorn_install_manual.pdf | rev6 | 138 | 1 | 16 |
| `pairing-guide` | centroid-acorn | Acorn Axis Pairing and Squaring | Pairing Guide | https://www.centroidcnc.com/centroid_diy/downloads/acorn_documentation/paired_axes_acorn_user_guide.pdf | paired_axes_acorn_user_guide.pdf | rev19 | 41 | 0 | 21 |
| `allin1dc-install` | centroid-allin1dc | ALLIN1DC Installation Manual | ALLIN1DC Install | https://www.centroidcnc.com/downloads/centroid_allin1dc_install_manual.pdf | centroid_allin1dc_install_manual.pdf | rev22 | null | 0 | null |
| `plcexp1616` | centroid-allin1dc | PLCEXP1616 Users Manual | PLCEXP1616 Manual | https://www.centroidcnc.com/centroid_diy/downloads/centroid_plcexp1616_users_manual.pdf | centroid_plcexp1616_users_manual.pdf | null | 7 | 0 | 1 |
| `f510-manual` | teco-f510 | F510 Instruction Manual | F510 Manual | https://www.tecowestinghouse.com/Manuals/F510_instruction_manual.pdf | teco-f510-instruction-manual.pdf | TECO-F510IM Ver 01 2017.12 | 438 | 0 | 13 |

`manuals.json` entry shape (JSON `null` where the table says null):

```json
{ "id": "plc-manual", "title": "CNC12 PLC Programming Manual", "citeAs": "PLC Manual",
  "url": "https://www.centroidcnc.com/centroid_diy/downloads/centroid_plc_programming_manual.pdf",
  "file": "centroid_plc_programming_manual.pdf", "expectRev": "rev8 07/24/26",
  "expectPages": 132, "pdfOffset": 0, "sizeMB": 3 }
```

### SKILL.md "Manuals" section (every knowledge skill, Tasks 10–14)

```markdown
## Manuals

This skill cites: <citeAs (title)>, ... Exact wording is in the official PDF. When an answer
needs text beyond these references, run `python3 <plugin>/scripts/fetch_manual.py <id>`
(`<plugin>` is this plugin's root directory):

- exit 0: it printed the local PDF path — read the cited page with `pdftotext -layout -f <p> -l <p> <path> -`
  if available, or open the PDF.
- exit 4: not downloaded yet. Ask the user in plain words, e.g. "This is best checked against
  Centroid's <title> (free PDF, about <sizeMB> MB). Want me to download it to
  `~/.centroid-ai/manuals/`? I can also do this automatically from now on, or never ask
  again." Yes → rerun with `--yes`. "Always" → `python3 <plugin>/scripts/centroid_config.py set manuals.autoDownload always`, then rerun. "Never" → set `never`.
- exit 5: the user chose never to download; answer from the references and give the manual and page.
- exit 1: download failed; give the user the printed URL to download by hand.

Download links for every manual: https://github.com/TD-4242/Centroid-AI/blob/main/docs/manuals.md
```

## Review Focus

1. A user types a compiler path that does not exist, or pastes the CNC12 folder instead of the `.exe` — expect a clear "not found at <path>" message (no silent fallback to another compiler), and a folder is searched for `mpucomp.exe`. (Task 6)
2. The CNC12 folder under Wine holds `MPUCOMP.EXE` (different case) — expect it to be found on case-sensitive filesystems. (Task 6)
3. Centroid's server returns an HTML error page instead of a PDF — expect download failure exit 1, no partial or bogus file left in the manuals dir. (Task 4)
4. `~/.centroid-ai/config.json` is hand-edited into invalid JSON — expect a one-line error naming the file, not a traceback. (Task 3)
5. `format --fix` runs on a Wizard-generated Acorn `.src` — expect the Wizard-overwrite warning on stderr before anything is written. (Task 8)

---

## File Structure

```
.claude-plugin/marketplace.json        Claude Code catalog
.agents/plugins/marketplace.json       Codex catalog
.github/workflows/check.yml            CI
.gitignore
README.md  LICENSE.md
docs/installing.md  docs/manuals.md  docs/authoring.md  docs/plugins/<plugin>.md
shared/centroid_config.py              user config read/write + manuals dir
shared/fetch_manual.py                 find/download a manual from manuals.json
plugins/<plugin>/.claude-plugin/plugin.json
plugins/<plugin>/plugin.json
plugins/<plugin>/manuals.json
plugins/<plugin>/scripts/              synced shared/*.py (+ centroid-plc tools)
plugins/<plugin>/skills/<skill>/SKILL.md, reference/*.md
plugins/centroid-plc/scripts/mpucomp_locate.py   compiler search
plugins/centroid-plc/scripts/plc_compile.py      compile-check any .src
plugins/centroid-plc/scripts/plcfmt.py           formatter + compile gate
tools/check_marketplace.py  tools/check_skill_links.py  tools/sync_shared.py
tools/tests/test_*.py
```

---

### Task 1: Repo scaffold and marketplace checker

**Files:**
- Create: `.gitignore`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `tools/check_marketplace.py`, `tools/__init__.py`, `tools/tests/__init__.py`, `tools/tests/helpers.py`
- Test: `tools/tests/test_check_marketplace.py`

**Interfaces:**
- Produces: `check_marketplace.check_tree(root: Path) -> list[str]` (problem strings, empty = OK); CLI `python3 tools/check_marketplace.py [root]` exit 0/1; `tools/tests/helpers.py` with `make_plugin(root: Path, name: str, skills=("s1",), version="0.1.0", codex_name=None)` and `write_catalogs(root: Path, names: list[str])` used by later tests.

- [ ] **Step 1: Scaffold**

`.gitignore`:
```
__pycache__/
*.pyc
*.pdf
*.exe
*.plc
.superpowers/
```

`.claude-plugin/marketplace.json`:
```json
{
  "name": "centroid-ai",
  "description": "Generic Centroid CNC12 skills and PLC tools for Claude Code and Codex",
  "owner": { "name": "Bill Warner", "url": "https://github.com/TD-4242" },
  "plugins": []
}
```

`.agents/plugins/marketplace.json`:
```json
{
  "name": "centroid-ai",
  "interface": { "displayName": "Centroid AI" },
  "plugins": []
}
```

`tools/__init__.py` and `tools/tests/__init__.py`: empty (tests import `tools.tests.helpers`). `tools/tests/helpers.py`:
```python
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
```

- [ ] **Step 2: Write the failing tests** — `tools/tests/test_check_marketplace.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import make_plugin, write, write_catalogs
import check_marketplace as cm


class CheckMarketplaceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_consistent_tree_passes(self):
        make_plugin(self.root, "centroid-a")
        write_catalogs(self.root, ["centroid-a"])
        self.assertEqual(cm.check_tree(self.root), [])

    def test_plugin_only_in_one_catalog(self):
        make_plugin(self.root, "centroid-a")
        make_plugin(self.root, "centroid-b")
        write_catalogs(self.root, ["centroid-a", "centroid-b"], codex_names=["centroid-a"])
        self.assertIn("plugin centroid-b is only in the Claude catalog", cm.check_tree(self.root))

    def test_manifest_name_mismatch(self):
        make_plugin(self.root, "centroid-a", codex_name="other")
        write_catalogs(self.root, ["centroid-a"])
        self.assertTrue(any("portable manifest name is 'other'" in p for p in cm.check_tree(self.root)))

    def test_version_mismatch(self):
        pdir = make_plugin(self.root, "centroid-a")
        write(pdir / "plugin.json", json.dumps({"name": "centroid-a", "version": "0.2.0"}))
        write_catalogs(self.root, ["centroid-a"])
        self.assertTrue(any("versions differ" in p for p in cm.check_tree(self.root)))

    def test_missing_source_dir(self):
        write_catalogs(self.root, ["centroid-a"])
        self.assertTrue(any("does not exist" in p for p in cm.check_tree(self.root)))

    def test_plugin_without_skills(self):
        make_plugin(self.root, "centroid-a", skills=())
        write_catalogs(self.root, ["centroid-a"])
        self.assertIn("centroid-a: no skills/*/SKILL.md", cm.check_tree(self.root))

    def test_skill_frontmatter_name_must_match_folder(self):
        pdir = make_plugin(self.root, "centroid-a")
        write(pdir / "skills" / "s1" / "SKILL.md", "---\nname: wrong\ndescription: x\n---\n")
        write_catalogs(self.root, ["centroid-a"])
        self.assertTrue(any("frontmatter name 'wrong'" in p for p in cm.check_tree(self.root)))

    def test_codex_entry_missing_policy(self):
        make_plugin(self.root, "centroid-a")
        write_catalogs(self.root, ["centroid-a"])
        path = self.root / ".agents" / "plugins" / "marketplace.json"
        data = json.loads(path.read_text())
        del data["plugins"][0]["policy"]
        path.write_text(json.dumps(data))
        self.assertIn("Codex entry centroid-a: missing policy", cm.check_tree(self.root))

    def test_invalid_json_reported(self):
        write(self.root / ".claude-plugin" / "marketplace.json", "{nope")
        write(self.root / ".agents" / "plugins" / "marketplace.json", "{}")
        self.assertTrue(any("invalid JSON" in p for p in cm.check_tree(self.root)))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m unittest tools.tests.test_check_marketplace -v`
Expected: ERROR `ModuleNotFoundError: No module named 'check_marketplace'`

- [ ] **Step 4: Implement** — `tools/check_marketplace.py`:

```python
#!/usr/bin/env python3
"""Check that the Claude Code and Codex catalogs, and each plugin's two manifests, agree."""
import json
import re
import sys
from pathlib import Path

CLAUDE_CATALOG = Path(".claude-plugin/marketplace.json")
CODEX_CATALOG = Path(".agents/plugins/marketplace.json")
NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)


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


def main(argv):
    root = Path(argv[0]) if argv else Path(__file__).resolve().parent.parent
    problems = check_tree(root)
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print("OK: catalogs and manifests agree")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 5: Run tests** — `python3 -m unittest tools.tests.test_check_marketplace -v` → all PASS. Also `python3 tools/check_marketplace.py` → `OK` (empty catalogs).

- [ ] **Step 6: Commit**

```bash
git add .gitignore .claude-plugin .agents tools
git commit -m "Add marketplace catalogs and consistency checker"
```

---

### Task 2: Skill link checker

**Files:**
- Create: `tools/check_skill_links.py` (generalized from TM `tools/check_skill_links.py`)
- Test: `tools/tests/test_check_skill_links.py`

**Interfaces:**
- Consumes: `tools/tests/helpers.py` (`write`, `make_plugin`).
- Produces: `check_skill_links.check_tree(root: Path) -> list[str]`; CLI exit 0 OK / 1 misses / 2 nothing to check.

Rules: checks `plugins/**/*.md`, `docs/**/*.md` except `docs/superpowers/`, and `README.md`. Broken relative links and anchors fail (unchanged GitHub slug logic). A backticked name matching `` `(centroid|teco)-[a-z0-9-]+` `` must be a known skill or plugin. Inside `plugins/<p>/`, naming a skill from another plugin requires a page citation on the same line — a parenthetical containing `p.<digits>`.

- [ ] **Step 1: Write the failing tests** — `tools/tests/test_check_skill_links.py`:

```python
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import make_plugin, write
import check_skill_links as csl


class CheckSkillLinksTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.a = make_plugin(self.root, "centroid-a", skills=("centroid-alpha",))
        self.b = make_plugin(self.root, "centroid-b", skills=("centroid-beta",))

    def tearDown(self):
        self._tmp.cleanup()

    def skill(self, plugin_dir, skill, text):
        write(plugin_dir / "skills" / skill / "SKILL.md",
              f"---\nname: {skill}\ndescription: t\n---\n{text}")

    def test_clean_tree(self):
        write(self.a / "skills/centroid-alpha/reference/r.md", "# Ref Head\n")
        self.skill(self.a, "centroid-alpha", "See [r](reference/r.md#ref-head) and `centroid-alpha`.\n")
        self.assertEqual(csl.check_tree(self.root), [])

    def test_broken_link_and_anchor(self):
        write(self.a / "skills/centroid-alpha/reference/r.md", "# Ref\n")
        self.skill(self.a, "centroid-alpha", "[x](reference/missing.md)\n[y](reference/r.md#nope)\n")
        misses = csl.check_tree(self.root)
        self.assertTrue(any("broken link reference/missing.md" in m for m in misses))
        self.assertTrue(any("broken anchor reference/r.md#nope" in m for m in misses))

    def test_unknown_skill_name(self):
        self.skill(self.a, "centroid-alpha", "See `centroid-cnc12-gmcodes`.\n")
        self.assertTrue(any("unknown skill centroid-cnc12-gmcodes" in m for m in csl.check_tree(self.root)))

    def test_plugin_names_are_known(self):
        write(self.root / "README.md", "Install `centroid-a`.\n")
        self.assertEqual(csl.check_tree(self.root), [])

    def test_cross_plugin_reference_needs_citation(self):
        self.skill(self.a, "centroid-alpha", "Use `centroid-beta` for that.\n")
        self.assertTrue(any("cross-plugin skill centroid-beta" in m for m in csl.check_tree(self.root)))

    def test_cross_plugin_reference_with_citation_ok(self):
        self.skill(self.a, "centroid-alpha",
                   "If installed, use `centroid-beta`; otherwise see (VCP Manual p.44).\n")
        self.assertEqual(csl.check_tree(self.root), [])

    def test_specs_are_not_checked(self):
        write(self.root / "docs/superpowers/specs/x.md", "`centroid-nope` [x](gone.md)\n")
        self.assertEqual(csl.check_tree(self.root), [])

    def test_fenced_code_headings_are_not_anchors(self):
        write(self.root / "docs/a.md", "```\n# Not A Heading\n```\n# Real\n")
        write(self.root / "docs/b.md", "[x](a.md#not-a-heading) [y](a.md#real)\n")
        misses = csl.check_tree(self.root)
        self.assertEqual(len(misses), 1)
        self.assertIn("a.md#not-a-heading", misses[0])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure** — `python3 -m unittest tools.tests.test_check_skill_links -v` → ModuleNotFoundError.

- [ ] **Step 3: Implement** — `tools/check_skill_links.py`:

```python
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
    for plugin in (root / "plugins").glob("*/"):
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
```

- [ ] **Step 4: Run tests** — `python3 -m unittest tools.tests.test_check_skill_links -v` → all PASS.

- [ ] **Step 5: Commit**

```bash
git add tools
git commit -m "Add skill link checker with cross-plugin citation rule"
```

---

### Task 3: Shared user config

**Files:**
- Create: `shared/centroid_config.py`
- Test: `tools/tests/test_centroid_config.py`

**Interfaces:**
- Produces: `home() -> Path`, `config_path() -> Path`, `load() -> dict` (raises `ValueError` on bad JSON), `set_value(key: str, value) -> None`, `manuals_dir() -> Path`, `AUTO_DOWNLOAD = ("ask", "always", "never")`. CLI: `centroid_config.py show | get <key> | set <key> <value>` (`null` → None); exit 2 with one-line message on bad config/arguments.

- [ ] **Step 1: Write the failing tests** — `tools/tests/test_centroid_config.py`:

```python
import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import REPO, write
sys.path.insert(0, str(REPO / "shared"))
import centroid_config as cc


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name) / "home"
        self._env = dict(os.environ)
        os.environ["CENTROID_AI_HOME"] = str(self.home)
        os.environ.pop("CENTROID_AI_MANUALS", None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def test_defaults_without_file(self):
        cfg = cc.load()
        self.assertEqual(cfg["manuals"]["autoDownload"], "ask")
        self.assertIsNone(cfg["mpucomp"]["path"])

    def test_set_then_load_round_trip(self):
        cc.set_value("mpucomp.path", "C:/cncr/mpucomp.exe")
        self.assertEqual(cc.load()["mpucomp"]["path"], "C:/cncr/mpucomp.exe")
        self.assertEqual(cc.load()["manuals"]["autoDownload"], "ask")

    def test_rejects_bad_auto_download(self):
        with self.assertRaises(ValueError):
            cc.set_value("manuals.autoDownload", "sometimes")

    def test_manuals_dir_precedence(self):
        self.assertEqual(cc.manuals_dir(), self.home / "manuals")
        cc.set_value("manuals.dir", str(Path(self._tmp.name) / "cfg"))
        self.assertEqual(cc.manuals_dir(), Path(self._tmp.name) / "cfg")
        os.environ["CENTROID_AI_MANUALS"] = str(Path(self._tmp.name) / "env")
        self.assertEqual(cc.manuals_dir(), Path(self._tmp.name) / "env")

    def test_invalid_json_is_one_line_error(self):
        write(self.home / "config.json", "{broken")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(cc.main(["show"]), 2)
        self.assertIn("config.json is not valid JSON", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_cli_set_null(self):
        cc.main(["set", "mpucomp.path", "X"])
        cc.main(["set", "mpucomp.path", "null"])
        self.assertIsNone(cc.load()["mpucomp"]["path"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure** — `python3 -m unittest tools.tests.test_centroid_config -v` → ModuleNotFoundError.

- [ ] **Step 3: Implement** — `shared/centroid_config.py`:

```python
#!/usr/bin/env python3
"""Read and write ~/.centroid-ai/config.json, shared by every Centroid-AI plugin."""
import copy
import json
import os
import sys
from pathlib import Path

DEFAULTS = {"manuals": {"autoDownload": "ask", "dir": None}, "mpucomp": {"path": None}}
AUTO_DOWNLOAD = ("ask", "always", "never")


def home():
    return Path(os.environ.get("CENTROID_AI_HOME") or Path.home() / ".centroid-ai")


def config_path():
    return home() / "config.json"


def load():
    cfg = copy.deepcopy(DEFAULTS)
    try:
        data = json.loads(config_path().read_text(encoding="utf-8"))
    except FileNotFoundError:
        return cfg
    except json.JSONDecodeError as e:
        raise ValueError(f"{config_path()} is not valid JSON ({e.msg}, line {e.lineno}); "
                         "fix or delete it") from None
    for section, values in data.items():
        if isinstance(values, dict) and isinstance(cfg.get(section), dict):
            cfg[section].update(values)
        else:
            cfg[section] = values
    return cfg


def set_value(key, value):
    if key == "manuals.autoDownload" and value not in AUTO_DOWNLOAD:
        raise ValueError(f"manuals.autoDownload must be one of {', '.join(AUTO_DOWNLOAD)}")
    section, _, name = key.partition(".")
    if not name:
        raise ValueError(f"key must look like section.name, got {key!r}")
    cfg = load()
    cfg.setdefault(section, {})[name] = value
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def manuals_dir():
    env = os.environ.get("CENTROID_AI_MANUALS")
    if env:
        return Path(env).expanduser()
    configured = load()["manuals"].get("dir")
    return Path(configured).expanduser() if configured else home() / "manuals"


def main(argv):
    try:
        if argv[:1] == ["show"]:
            print(json.dumps(load(), indent=2))
        elif len(argv) == 2 and argv[0] == "get":
            section, _, name = argv[1].partition(".")
            print(json.dumps(load().get(section, {}).get(name)))
        elif len(argv) == 3 and argv[0] == "set":
            set_value(argv[1], None if argv[2] == "null" else argv[2])
        else:
            print("usage: centroid_config.py show | get <key> | set <key> <value>", file=sys.stderr)
            return 2
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests** → all PASS.

- [ ] **Step 5: Commit**

```bash
git add shared tools/tests
git commit -m "Add shared user config helper"
```

---

### Task 4: Manual fetcher

**Files:**
- Create: `shared/fetch_manual.py`
- Test: `tools/tests/test_fetch_manual.py`

**Interfaces:**
- Consumes: `centroid_config.load()`, `centroid_config.manuals_dir()` (same directory import).
- Produces: CLI `fetch_manual.py <id> [--yes] [--manifest PATH]` / `fetch_manual.py --list [--manifest PATH]`. Exit 0 = prints local PDF path (warnings on stderr); 4 = needs consent (prints title, sizeMB, url, destination); 5 = user set never (prints title + url); 1 = download failed (prints url to fetch by hand); 2 = usage/unknown id/bad config. Module functions `count_pages(path: Path) -> int | None`, `download(url: str, dest: Path) -> None`; module attribute `urlopen` (patchable).

Default manifest: `Path(__file__).resolve().parent.parent / "manuals.json"` (plugin root when run from `plugins/<p>/scripts/`).

- [ ] **Step 1: Write the failing tests** — `tools/tests/test_fetch_manual.py`:

```python
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import REPO, write
sys.path.insert(0, str(REPO / "shared"))
import centroid_config
import fetch_manual as fm

PDF = b"%PDF-1.7\n1 0 obj << /Type /Pages >>\n2 0 obj << /Type /Page >>\n3 0 obj << /Type /Page >>\n"


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class FetchManualTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self._env = dict(os.environ)
        os.environ["CENTROID_AI_HOME"] = str(tmp / "home")
        os.environ.pop("CENTROID_AI_MANUALS", None)
        self.manifest = write(tmp / "manuals.json", json.dumps([{
            "id": "m1", "title": "Test Manual", "citeAs": "Test", "url": "https://example.com/m1.pdf",
            "file": "m1.pdf", "expectRev": None, "expectPages": 2, "pdfOffset": 0, "sizeMB": 1}]))
        self.dest = tmp / "home" / "manuals" / "m1.pdf"
        self._urlopen = fm.urlopen
        self.requests = []

    def tearDown(self):
        fm.urlopen = self._urlopen
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def serve(self, body):
        def fake(request, timeout=None):
            self.requests.append(request)
            return FakeResponse(body)
        fm.urlopen = fake

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fm.main([*args, "--manifest", str(self.manifest)])
        return code, out.getvalue(), err.getvalue()

    def test_existing_file_prints_path(self):
        write(self.dest, "%PDF-")
        code, out, _ = self.run_cli("m1")
        self.assertEqual((code, out.strip()), (0, str(self.dest)))

    def test_ask_mode_requests_consent_without_network(self):
        self.serve(PDF)
        code, out, _ = self.run_cli("m1")
        self.assertEqual(code, 4)
        self.assertIn("Test Manual", out)
        self.assertEqual(self.requests, [])

    def test_never_mode(self):
        centroid_config.set_value("manuals.autoDownload", "never")
        code, out, _ = self.run_cli("m1")
        self.assertEqual(code, 5)
        self.assertIn("https://example.com/m1.pdf", out)

    def test_yes_downloads_with_browser_headers(self):
        self.serve(PDF)
        code, out, _ = self.run_cli("m1", "--yes")
        self.assertEqual(code, 0)
        self.assertEqual(self.dest.read_bytes(), PDF)
        self.assertIn("Mozilla", self.requests[0].get_header("User-agent"))

    def test_always_mode_downloads(self):
        centroid_config.set_value("manuals.autoDownload", "always")
        self.serve(PDF)
        self.assertEqual(self.run_cli("m1")[0], 0)

    def test_html_error_page_is_rejected_and_removed(self):
        self.serve(b"<html>blocked</html>")
        code, out, _ = self.run_cli("m1", "--yes")
        self.assertEqual(code, 1)
        self.assertFalse(self.dest.exists())
        self.assertEqual(list(self.dest.parent.glob("*")), [])
        self.assertIn("https://example.com/m1.pdf", out)

    def test_page_count_mismatch_warns_but_succeeds(self):
        self.serve(PDF + b"4 0 obj << /Type /Page >>\n")
        code, _, err = self.run_cli("m1", "--yes")
        self.assertEqual(code, 0)
        self.assertIn("citations may be slightly off", err)

    def test_unknown_id(self):
        self.assertEqual(self.run_cli("nope")[0], 2)

    def test_list(self):
        code, out, _ = self.run_cli("--list")
        self.assertEqual(code, 0)
        self.assertIn("m1", out)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure** — `python3 -m unittest tools.tests.test_fetch_manual -v` → ModuleNotFoundError.

- [ ] **Step 3: Implement** — `shared/fetch_manual.py`:

```python
#!/usr/bin/env python3
"""Find a manual from this plugin's manuals.json locally, or download it with the user's consent."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
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
    part = dest.with_name(dest.name + ".part")
    try:
        with urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as resp, \
                open(part, "wb") as out:
            shutil.copyfileobj(resp, out)
        with open(part, "rb") as f:
            if f.read(5) != b"%PDF-":
                raise OSError("the server did not return a PDF")
        os.replace(part, dest)
    finally:
        if part.exists():
            part.unlink()


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
        except OSError as e:
            print(f"Could not download {entry['title']}: {e}.\n"
                  f"You can download it in a browser from {entry['url']} and save it as {dest}")
            return 1
    for warning in _warnings(dest, entry):
        print(warning, file=sys.stderr)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

Note: `urllib.error.URLError` is a subclass of `OSError`, so network failures land in the exit-1 branch.

- [ ] **Step 4: Run tests** → all PASS. (If `pdfinfo` is installed it will fail to parse the fake PDF; `count_pages` then falls back to the regex — confirm `test_page_count_mismatch_warns_but_succeeds` passes on this machine, which has `pdfinfo`.)

- [ ] **Step 5: Commit**

```bash
git add shared tools/tests
git commit -m "Add consent-gated manual fetcher"
```

---

### Task 5: Shared-file sync

**Files:**
- Create: `tools/sync_shared.py`
- Test: `tools/tests/test_sync_shared.py`

**Interfaces:**
- Produces: `sync_shared.sync(root: Path, check: bool) -> list[str]` (drifted/copied paths); CLI `sync_shared.py [--check] [root]` — `--check` exits 1 listing drifted copies; without it copies and exits 0. `SHARED = ("centroid_config.py", "fetch_manual.py")`.

- [ ] **Step 1: Write the failing tests** — `tools/tests/test_sync_shared.py`:

```python
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import make_plugin, write
import sync_shared


class SyncSharedTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for name in sync_shared.SHARED:
            write(self.root / "shared" / name, f"# {name}\n")
        self.plugin = make_plugin(self.root, "centroid-a")

    def tearDown(self):
        self._tmp.cleanup()

    def test_check_reports_missing_copies(self):
        drift = sync_shared.sync(self.root, check=True)
        self.assertIn("plugins/centroid-a/scripts/fetch_manual.py", drift)
        self.assertFalse((self.plugin / "scripts").exists())

    def test_sync_then_check_is_clean(self):
        sync_shared.sync(self.root, check=False)
        self.assertEqual((self.plugin / "scripts" / "fetch_manual.py").read_text(), "# fetch_manual.py\n")
        self.assertEqual(sync_shared.sync(self.root, check=True), [])

    def test_check_detects_edited_copy(self):
        sync_shared.sync(self.root, check=False)
        write(self.plugin / "scripts" / "centroid_config.py", "# edited\n")
        self.assertEqual(sync_shared.sync(self.root, check=True),
                         ["plugins/centroid-a/scripts/centroid_config.py"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure** → ModuleNotFoundError.

- [ ] **Step 3: Implement** — `tools/sync_shared.py`:

```python
#!/usr/bin/env python3
"""Copy shared/*.py helpers into every plugin's scripts/ (installed plugins cannot share files)."""
import shutil
import sys
from pathlib import Path

SHARED = ("centroid_config.py", "fetch_manual.py")


def sync(root, check):
    root = Path(root)
    changed = []
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
```

- [ ] **Step 4: Run tests** → all PASS.

- [ ] **Step 5: Commit**

```bash
git add tools
git commit -m "Add shared helper sync tool"
```

---

### Task 6: Compiler locator

**Files:**
- Create: `plugins/centroid-plc/scripts/mpucomp_locate.py`
- Test: `tools/tests/test_mpucomp_locate.py`

**Interfaces:**
- Consumes: `centroid_config.load()` (synced into the same `scripts/` dir in Task 9; for tests, `shared/` is on `sys.path`).
- Produces: `Found = NamedTuple(path: Path, origin: str)` with origin in `"explicit" | "config" | "project" | "cnc12"`; `locate(src: Path | None, explicit: str | None = None, is_windows: bool | None = None, wineprefix: Path | None = None, windows_root: Path | None = None) -> Found | None` (raises `FileNotFoundError` when `explicit` is given but holds no compiler); `find_in(directory: Path) -> Path | None` (case-insensitive); `CNC12_DIRS = ("cncm", "cncr", "cnct", "cncp")`. CLI prints JSON `{"path", "origin"}` exit 0, or exit 2 when not found.

- [ ] **Step 1: Write the failing tests** — `tools/tests/test_mpucomp_locate.py`:

```python
import os
import sys
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import REPO, write
sys.path.insert(0, str(REPO / "shared"))
sys.path.insert(0, str(REPO / "plugins" / "centroid-plc" / "scripts"))
import centroid_config
import mpucomp_locate as ml


class LocateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.t = Path(self._tmp.name)
        self._env = dict(os.environ)
        os.environ["CENTROID_AI_HOME"] = str(self.t / "home")
        self.project = self.t / "proj"
        (self.project / ".git").mkdir(parents=True)
        self.src = write(self.project / "plc" / "my.src", "x")
        self.wine = self.t / "wine"
        self.kw = dict(is_windows=False, wineprefix=self.wine)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def exe(self, path):
        return write(path, "MZ")

    def test_nothing_found(self):
        self.assertIsNone(ml.locate(self.src, **self.kw))

    def test_next_to_source_is_project(self):
        exe = self.exe(self.project / "plc" / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, **self.kw), ml.Found(exe, "project"))

    def test_repo_root_is_project(self):
        exe = self.exe(self.project / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, **self.kw), ml.Found(exe, "project"))

    def test_wine_cnc12_folder_needs_confirmation_origin(self):
        exe = self.exe(self.wine / "drive_c" / "cncr" / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, **self.kw), ml.Found(exe, "cnc12"))

    def test_windows_cnc12_folder(self):
        exe = self.exe(self.t / "C" / "cncm" / "mpucomp.exe")
        found = ml.locate(self.src, is_windows=True, windows_root=self.t / "C")
        self.assertEqual(found, ml.Found(exe, "cnc12"))

    def test_uppercase_exe_found(self):
        exe = self.exe(self.wine / "drive_c" / "cncm" / "MPUCOMP.EXE")
        self.assertEqual(ml.locate(self.src, **self.kw).path, exe)

    def test_config_beats_project(self):
        cfg_exe = self.exe(self.t / "elsewhere" / "mpucomp.exe")
        self.exe(self.project / "mpucomp.exe")
        centroid_config.set_value("mpucomp.path", str(cfg_exe))
        self.assertEqual(ml.locate(self.src, **self.kw), ml.Found(cfg_exe, "config"))

    def test_explicit_beats_everything(self):
        exe = self.exe(self.t / "x" / "mpucomp.exe")
        self.exe(self.project / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, explicit=str(exe), **self.kw), ml.Found(exe, "explicit"))

    def test_explicit_folder_is_searched(self):
        exe = self.exe(self.t / "cncr" / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, explicit=str(self.t / "cncr"), **self.kw).path, exe)

    def test_explicit_missing_raises_not_falls_through(self):
        self.exe(self.project / "mpucomp.exe")
        with self.assertRaises(FileNotFoundError) as ctx:
            ml.locate(self.src, explicit=str(self.t / "typo.exe"), **self.kw)
        self.assertIn("typo.exe", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure** → ModuleNotFoundError.

- [ ] **Step 3: Implement** — `plugins/centroid-plc/scripts/mpucomp_locate.py`:

```python
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
    path = Path(path).expanduser()
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
```

- [ ] **Step 4: Run tests** → all PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/centroid-plc/scripts/mpucomp_locate.py tools/tests/test_mpucomp_locate.py
git commit -m "Add mpucomp.exe locator"
```

---

### Task 7: PLC compile-check script

**Files:**
- Create: `plugins/centroid-plc/scripts/plc_compile.py` (Python port of AC/TM `compile.sh`)
- Test: `tools/tests/test_plc_compile.py`

**Interfaces:**
- Consumes: `mpucomp_locate.locate`, `mpucomp_locate.Found`.
- Produces:
  - `Result = NamedTuple(ok: bool, errors: list[str], warnings: list[str], summary: list[str])`
  - `parse_log(log: str, returncode: int) -> Result`
  - `build_command(compiler: Path, src_name: str, out_plc: str, is_windows: bool) -> list[str]`
  - `compile_src(src: Path, compiler: Path, out: Path | None = None, runner=subprocess.run, is_windows: bool | None = None) -> Result` (raises `SetupError` if Wine missing on non-Windows)
  - `class SetupError(RuntimeError)`; constants `NOT_FOUND_HELP`, `wine_help() -> str`
  - CLI `plc_compile.py <file.src> [-v] [-o OUT] [--compiler PATH]` — exit 0 compiled, 1 compile errors, 2 setup problem (no source / no compiler / no Wine; friendly text on stdout), 3 compiler found in a CNC12 folder and needs the user's OK (prints `CONFIRM COMPILER: <path>`).

- [ ] **Step 1: Write the failing tests** — `tools/tests/test_plc_compile.py`:

```python
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import REPO, write
sys.path.insert(0, str(REPO / "shared"))
sys.path.insert(0, str(REPO / "plugins" / "centroid-plc" / "scripts"))
import mpucomp_locate
import plc_compile as pc

OK_LOG = "Compiling...\nWarning: unused X\nWarning: unused Y\nCompilation successful\nProgram size: 1234\n"
BAD_LOG = "Error Line 12: unknown symbol Foo\nCompilation failed\n"


class ParseTest(unittest.TestCase):
    def test_success(self):
        r = pc.parse_log(OK_LOG, 0)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.warnings), 2)
        self.assertEqual(r.summary, ["Compilation successful", "Program size: 1234"])

    def test_failure(self):
        r = pc.parse_log(BAD_LOG, 0)
        self.assertFalse(r.ok)
        self.assertIn("Error Line 12: unknown symbol Foo", r.errors)

    def test_nonzero_exit_without_error_text_shows_whole_log(self):
        r = pc.parse_log("weird crash\n", 3)
        self.assertFalse(r.ok)
        self.assertEqual(r.errors, ["weird crash"])

    def test_command_windows_and_wine(self):
        exe = Path("/c/mpucomp.exe")
        self.assertEqual(pc.build_command(exe, "a.src", "o.plc", True), [str(exe), "-w", "a.src", "o.plc"])
        self.assertEqual(pc.build_command(exe, "a.src", "o.plc", False)[:2], ["wine", str(exe)])


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.src = write(t / "my.src", "x")
        self.exe = write(t / "mpucomp.exe", "MZ")
        self._env = dict(os.environ)
        os.environ["CENTROID_AI_HOME"] = str(t / "home")
        self._locate, self._run, self._which = pc.locate, pc.RUNNER, pc.shutil.which
        pc.shutil.which = lambda name: "/usr/bin/wine"

    def tearDown(self):
        pc.locate, pc.RUNNER, pc.shutil.which = self._locate, self._run, self._which
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = pc.main([str(self.src), *args])
        return code, out.getvalue()

    def fake_run(self, log, rc=0):
        def run(cmd, **kw):
            self.cmd, self.kw = cmd, kw
            return subprocess.CompletedProcess(cmd, rc, stdout=log, stderr="")
        pc.RUNNER = run

    def test_success_reports_warning_count(self):
        self.fake_run(OK_LOG)
        code, out = self.cli()
        self.assertEqual(code, 0)
        self.assertIn("Warnings: 2", out)
        self.assertEqual(self.kw["cwd"], self.src.resolve().parent)

    def test_compile_error_exit_1(self):
        self.fake_run(BAD_LOG)
        code, out = self.cli()
        self.assertEqual(code, 1)
        self.assertIn("Error Line 12", out)

    def test_not_found_prints_friendly_help(self):
        pc.locate = lambda *a, **k: None
        code, out = self.cli()
        self.assertEqual(code, 2)
        self.assertIn("Centroid's PLC compiler", out)
        self.assertIn("C:\\cncr", out)

    def test_cnc12_hit_needs_confirmation(self):
        pc.locate = lambda *a, **k: mpucomp_locate.Found(Path("/w/drive_c/cncr/mpucomp.exe"), "cnc12")
        code, out = self.cli()
        self.assertEqual(code, 3)
        self.assertIn("CONFIRM COMPILER: /w/drive_c/cncr/mpucomp.exe", out)

    def test_missing_wine_explained(self):
        if os.name == "nt":
            self.skipTest("Wine is not used on Windows")
        pc.shutil.which = lambda name: None
        code, out = self.cli("--compiler", str(self.exe))
        self.assertEqual(code, 2)
        self.assertIn("Wine", out)

    def test_missing_source(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            self.assertEqual(pc.main([str(self.src) + ".nope"]), 2)


class RealCompilerTest(unittest.TestCase):
    """Set CENTROID_AI_TEST_SRC to a .src whose folder (or repo) holds mpucomp.exe."""

    def test_real_source_compiles(self):
        src = os.environ.get("CENTROID_AI_TEST_SRC")
        if not src:
            self.skipTest("CENTROID_AI_TEST_SRC not set")
        found = mpucomp_locate.locate(Path(src))
        if found is None:
            self.skipTest("no mpucomp.exe next to the test source")
        self.assertTrue(pc.compile_src(Path(src), found.path).ok)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure** → ModuleNotFoundError.

- [ ] **Step 3: Implement** — `plugins/centroid-plc/scripts/plc_compile.py`:

```python
#!/usr/bin/env python3
"""Compile-check a Centroid CNC12 PLC .src with mpucomp.exe (natively on Windows, via Wine elsewhere)."""
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

from mpucomp_locate import locate

RUNNER = subprocess.run
FAILED_RE = re.compile(r"Compilation failed|^Error|Error Line", re.IGNORECASE | re.MULTILINE)

NOT_FOUND_HELP = """\
To check your PLC program for errors I need mpucomp.exe, Centroid's PLC compiler. It's the
same program CNC12 uses to build your PLC when you load it on the machine. It comes with every
CNC12 install, but it can't be shipped with these tools.

Where to look: on your control PC it's usually in C:\\cncm (mill) or C:\\cncr (router). If you
copied your CNC12 folder to this computer, look there. If you don't have CNC12 here, the free
CNC12 download from centroidcnc.com includes it.

Paste the path to mpucomp.exe (or its folder), or skip compiling for now."""


class SetupError(RuntimeError):
    pass


class Result(NamedTuple):
    ok: bool
    errors: list
    warnings: list
    summary: list


def wine_help():
    if platform.system() == "Darwin":
        install = "brew install --cask wine-stable"
    elif shutil.which("dnf"):
        install = "sudo dnf install wine"
    else:
        install = "sudo apt install wine"
    return ("mpucomp.exe is a Windows program. On this computer it runs through Wine, a free "
            "tool that runs Windows programs on Linux and macOS, and Wine isn't installed.\n"
            f"Install it with:  {install}\nthen try again.")


def parse_log(log, returncode):
    lines = [l.strip() for l in log.splitlines() if l.strip()]
    failed = returncode != 0 or bool(FAILED_RE.search(log))
    errors = [l for l in lines if re.search(r"Error|Compilation failed", l, re.IGNORECASE)]
    if failed and not errors:
        errors = lines
    warnings = [l for l in lines if re.match(r"Warning:", l, re.IGNORECASE)]
    summary = [l for l in lines if re.search(r"Compilation successful|Program size", l, re.IGNORECASE)]
    return Result(not failed, errors, warnings, summary)


def build_command(compiler, src_name, out_plc, is_windows):
    cmd = [str(compiler), "-w", src_name, out_plc]
    return cmd if is_windows else ["wine", *cmd]


def compile_src(src, compiler, out=None, runner=None, is_windows=None):
    runner = runner or RUNNER
    if is_windows is None:
        is_windows = os.name == "nt"
    if not is_windows and shutil.which("wine") is None:
        raise SetupError(wine_help())
    src = Path(src).resolve()
    fd, tmp = tempfile.mkstemp(suffix=".plc")
    os.close(fd)
    try:
        env = dict(os.environ, WINEDEBUG="-all")
        r = runner(build_command(compiler, src.name, tmp, is_windows), cwd=src.parent,
                   capture_output=True, text=True, errors="replace", env=env)
        result = parse_log((r.stdout or "") + (r.stderr or ""), r.returncode)
        if result.ok and out:
            shutil.copyfile(tmp, out)
        return result
    finally:
        os.unlink(tmp)


def main(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("src", type=Path)
    p.add_argument("-v", "--verbose", action="store_true", help="print every warning")
    p.add_argument("-o", "--output", type=Path, help="keep the compiled program here")
    p.add_argument("--compiler", help="path to mpucomp.exe or its folder")
    args = p.parse_args(argv)
    if not args.src.is_file():
        print(f"error: PLC source {args.src} not found")
        return 2
    try:
        found = locate(args.src, explicit=args.compiler)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}")
        return 2
    if found is None:
        print(NOT_FOUND_HELP)
        return 2
    if found.origin == "cnc12":
        print(f"CONFIRM COMPILER: {found.path}")
        return 3
    print(f"Compiling {args.src.name} with {found.path} ...")
    try:
        result = compile_src(args.src, found.path, args.output)
    except SetupError as e:
        print(e)
        return 2
    if not result.ok:
        print("\n".join(result.errors))
        print("ERROR: compilation failed")
        return 1
    print("\n".join(result.summary))
    print(f"Warnings: {len(result.warnings)}")
    if args.verbose and result.warnings:
        print("----\n" + "\n".join(result.warnings) + "\n----")
    if args.output:
        print(f"Wrote compiled program to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests** → all PASS; then `CENTROID_AI_TEST_SRC=/home/bwarner/github/Torchmate-Centroid/acorn_router_plc.src python3 -m unittest tools.tests.test_plc_compile -v` → `test_real_source_compiles` PASS (Wine and the repo-local `mpucomp.exe` are present on this machine).

- [ ] **Step 5: Commit**

```bash
git add plugins/centroid-plc/scripts/plc_compile.py tools/tests/test_plc_compile.py
git commit -m "Add cross-platform PLC compile-check script"
```

---

### Task 8: Port the PLC formatter

**Files:**
- Create: `plugins/centroid-plc/scripts/plcfmt.py` (from AC `tools/plcfmt.py`)
- Create: `tools/tests/test_plcfmt.py` (from AC `tools/test_plcfmt.py`)

**Interfaces:**
- Consumes: `plc_compile.compile_src`, `plc_compile.SetupError`, `plc_compile.NOT_FOUND_HELP`, `mpucomp_locate.locate`.
- Produces: `plcfmt.verify_compile_identical(path, original, formatted, compiler: Path)`; `plcfmt.run(path, fix, verify, compiler=None)`; `plcfmt.looks_wizard_generated(text: str) -> bool`; `plcfmt._compile(src_path, out_plc, compiler)`; CLI `plcfmt.py <file.src> [--fix|--check] [--no-verify] [--compiler PATH]` exit 0 clean/applied, 1 check found pending reformat, 2 error, 3 compiler needs confirmation.

- [ ] **Step 1: Copy both files**

```bash
cp /home/bwarner/github/Acroloc-Centroid/tools/plcfmt.py plugins/centroid-plc/scripts/plcfmt.py
cp /home/bwarner/github/Acroloc-Centroid/tools/test_plcfmt.py tools/tests/test_plcfmt.py
```

- [ ] **Step 2: Adapt the test file first (failing tests)**

In `tools/tests/test_plcfmt.py`:
1. Replace the import block (`sys.path.insert(...)` / `import plcfmt` / `REPO = ...`) with:
   ```python
   import unittest
   from pathlib import Path
   REPO = Path(__file__).resolve().parents[2]
   sys.path.insert(0, str(REPO / "shared"))
   sys.path.insert(0, str(REPO / "plugins" / "centroid-plc" / "scripts"))
   import plcfmt
   import mpucomp_locate
   TEST_SRC = os.environ.get("CENTROID_AI_TEST_SRC")
   ```
2. Replace `class Skip(Exception): pass` with `Skip = unittest.SkipTest`.
3. Fix the module docstring: run with `python3 -m unittest tools.tests.test_plcfmt`, integration tests need `CENTROID_AI_TEST_SRC`.
4. Delete `test_verify_refuses_non_canonical_filename` and add:
   ```python
   def test_verify_compiles_the_given_file():
       seen = []
       orig_compile, orig_fp = plcfmt._compile, plcfmt.plc_fingerprint
       plcfmt._compile = lambda src, out, compiler: seen.append(os.path.basename(src))
       plcfmt.plc_fingerprint = lambda p: ((), "A", "B")
       try:
           with tempfile.TemporaryDirectory() as td:
               p = os.path.join(td, "any_name.src")
               with open(p, "wb") as f:
                   f.write(b"if a then b\r\n")
               plcfmt.verify_compile_identical(p, "if a then b\r\n", "IF a THEN b\r\n", Path("x.exe"))
       finally:
           plcfmt._compile, plcfmt.plc_fingerprint = orig_compile, orig_fp
       assert seen == ["any_name.src", "any_name.src"]

   def test_wizard_detection():
       assert plcfmt.looks_wizard_generated("; DO NOT MODIFY\r\n; #wizardregion Date\r\n")
       assert not plcfmt.looks_wizard_generated("; plain program\r\n")

   def test_fix_on_wizard_file_warns_before_writing():
       with tempfile.TemporaryDirectory() as td:
           p = os.path.join(td, "acorn.src")
           with open(p, "wb") as f:
               f.write(b"; #wizardregion Date\r\nif a then b\r\n")
           err = io.StringIO()
           with contextlib.redirect_stderr(err):
               assert plcfmt.main(["--fix", "--no-verify", p]) == 0
           assert "Acorn Wizard" in err.getvalue()

   def test_fix_without_compiler_refuses_and_explains():
       orig = plcfmt.locate
       plcfmt.locate = lambda *a, **k: None
       try:
           with tempfile.TemporaryDirectory() as td:
               p = os.path.join(td, "x.src")
               with open(p, "wb") as f:
                   f.write(b"if a then b\r\n")
               out = io.StringIO()
               with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                   assert plcfmt.main(["--fix", p]) == 2
               assert open(p, "rb").read() == b"if a then b\r\n"
               assert "--no-verify" in out.getvalue()
       finally:
           plcfmt.locate = orig
   ```
   (add `import contextlib`, `import io` at the top if not already imported).
5. In `test_gate_reverts_when_fingerprint_extraction_fails`: make it `def fake_compile(src, out, compiler):`, use `p = os.path.join(td, "x.src")` instead of `plcfmt.SRC`, delete the two lines that write `compile.sh`, and pass `Path("x.exe")` as the fourth argument to `verify_compile_identical`.
6. Replace `test_main_reports_gate_error_cleanly` with:
   ```python
   def test_main_reports_gate_error_cleanly():
       # RuntimeError surfaces as exit code 2, not a traceback
       orig = plcfmt._compile
       def failing(src, out, compiler):
           raise RuntimeError("compile failed")
       plcfmt._compile = failing
       try:
           with tempfile.TemporaryDirectory() as td:
               exe = os.path.join(td, "mpucomp.exe")
               open(exe, "wb").close()
               p = os.path.join(td, "other-name.src")
               with open(p, "wb") as f:
                   f.write(b"if a then b\r\n")
               assert plcfmt.main(["--fix", "--compiler", exe, p]) == 2
               assert open(p, "rb").read() == b"if a then b\r\n"   # nothing written
       finally:
           plcfmt._compile = orig
   ```
7. Replace `_compiler_available` and `_copy_repo` with:
   ```python
   def _test_source():
       if not TEST_SRC:
           raise Skip("CENTROID_AI_TEST_SRC not set")
       found = mpucomp_locate.locate(Path(TEST_SRC))
       if found is None:
           raise Skip("no mpucomp.exe next to the test source")
       return found.path

   def _copy_src(td):
       target = os.path.join(td, os.path.basename(TEST_SRC))
       shutil.copyfile(TEST_SRC, target)
       return target
   ```
   and in the three integration tests use `compiler = _test_source()`, `target = _copy_src(td)` and pass `compiler` to `verify_compile_identical`.
8. Below the existing `_run()` runner, add the hook so `unittest` discovery runs the plain test functions:
   ```python
   def load_tests(loader, tests, pattern):
       suite = unittest.TestSuite()
       for name in sorted(n for n in globals() if n.startswith("test_") and callable(globals()[n])):
           suite.addTest(unittest.FunctionTestCase(globals()[name]))
       return suite
   ```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m unittest tools.tests.test_plcfmt -v`
Expected: FAIL/ERROR in the new and adapted tests (`looks_wizard_generated` missing, `_compile` signature mismatch).

- [ ] **Step 4: Adapt `plcfmt.py`**

1. Module docstring first lines: `"""Format a Centroid CNC12 PLC .src to one canonical style.` and `--fix verifies the compiled program is unchanged using mpucomp.exe."""` (drop the Acroloc filename and `./compile.sh`).
2. Delete `SRC = "Centroid-Acroloc-ALLIN1DC.src"`.
3. Add after the imports:
   ```python
   from mpucomp_locate import locate
   from plc_compile import NOT_FOUND_HELP, SetupError, compile_src

   WIZARD_MARK = "#wizardregion"
   WIZARD_WARNING = ("warning: this looks like an Acorn Wizard-generated PLC. The Wizard rewrites "
                     "it unless its Custom PLC preference is set, which discards hand edits.")


   def looks_wizard_generated(text):
       return WIZARD_MARK in text
   ```
4. Replace `_compile` with:
   ```python
   def _compile(src_path, out_plc, compiler):
       result = compile_src(src_path, compiler, out=out_plc)
       if not result.ok:
           raise RuntimeError("compile failed:\n  " + "\n  ".join(result.errors[-8:]))
   ```
5. `verify_compile_identical(path, original, formatted, compiler)`: delete the `SRC` filename refusal and the `compile.sh` existence check; replace `_compile(cwd, before)` / `_compile(cwd, after)` with `_compile(path, before, compiler)` / `_compile(path, after, compiler)`; drop the now-unused `cwd` variable.
6. `run(path, fix, verify, compiler=None)`: at the top, after `original = read_src(path)`, add
   ```python
   if looks_wizard_generated(original):
       sys.stderr.write(WIZARD_WARNING + "\n")
   ```
   and call `verify_compile_identical(path, original, formatted, compiler)`.
7. `main`: make `file` a required positional; add `p.add_argument("--compiler", help="path to mpucomp.exe or its folder")`; before calling `run`, when `args.fix and not args.no_verify`:
   ```python
   try:
       found = locate(Path(args.file), explicit=args.compiler)
   except FileNotFoundError as e:
       sys.stderr.write("error: %s\n" % e)
       return 2
   if found is None:
       print(NOT_FOUND_HELP)
       print("\nTo format without the compiled-program check, rerun with --no-verify "
             "(the change will not be verified).")
       return 2
   if found.origin == "cnc12":
       print("CONFIRM COMPILER: %s" % found.path)
       return 3
   compiler = found.path
   ```
   else `compiler = None`; then `return run(args.file, fix=args.fix, verify=not args.no_verify, compiler=compiler)`, and add `SetupError` to the caught exceptions. Add `from pathlib import Path` to the imports.

- [ ] **Step 5: Run tests**

Run: `python3 -m unittest tools.tests.test_plcfmt -v` → all PASS, integration tests SKIP.
Run: `CENTROID_AI_TEST_SRC=/home/bwarner/github/Acroloc-Centroid/Centroid-Acroloc-ALLIN1DC.src python3 -m unittest tools.tests.test_plcfmt -v` → integration tests PASS (gate holds on real source, reverts on SET→RST and INP1→INP2).

- [ ] **Step 6: Commit**

```bash
git add plugins/centroid-plc/scripts/plcfmt.py tools/tests/test_plcfmt.py
git commit -m "Port PLC formatter: any .src, shared compiler, Wizard warning"
```

---

### Task 9: Package the centroid-plc plugin with compile and format skills

**Files:**
- Create: `plugins/centroid-plc/.claude-plugin/plugin.json`, `plugins/centroid-plc/plugin.json`, `plugins/centroid-plc/manuals.json`, `plugins/centroid-plc/skills/compile/SKILL.md`, `plugins/centroid-plc/skills/format/SKILL.md`
- Modify: both catalogs; `plugins/centroid-plc/scripts/` (synced copies)

**Interfaces:**
- Consumes: Tasks 1, 4–8 scripts; manifest templates and plugin values (Global Constraints).
- Produces: installable `centroid-plc` plugin (knowledge skill added in Task 10).

- [ ] **Step 1: Manifests and catalog entries** — fill the templates with the `centroid-plc` row; append both catalog entries. `manuals.json` = `[ <plc-manual entry> ]` from the Manuals table.

- [ ] **Step 2: Sync shared scripts** — `python3 tools/sync_shared.py` → `updated: plugins/centroid-plc/scripts/centroid_config.py`, `... fetch_manual.py`.

- [ ] **Step 3: Write `skills/compile/SKILL.md`**

```markdown
---
name: compile
description: Use when the user wants to check that a Centroid CNC12 PLC program (.src) compiles - "compile my PLC", "check the .src for errors", before loading a PLC on the machine, or after editing PLC source. Runs Centroid's mpucomp.exe compiler and reports errors and warnings. Does not load anything onto the machine.
---

# Compile-check a Centroid PLC program

Run `python3 <plugin>/scripts/plc_compile.py <file.src>` where `<plugin>` is this plugin's root
(the directory two levels above this file). Add `-v` to list every warning, `-o out.plc` to keep
the compiled program. If the user did not name a file, look for `*.src` in the project; if
there are several, ask which one.

## Reading the result

| Exit | Meaning | What to do |
| --- | --- | --- |
| 0 | Compiled | Report the warning count; offer `-v` if there are warnings. |
| 1 | Compile errors | Show the errors with their line numbers and help fix them. |
| 2 | Setup problem | Show the script's message as-is - it is written for the user (no compiler, no Wine, or no source file). |
| 3 | Compiler found in a CNC12 folder | Ask: "I found Centroid's PLC compiler at `<path>`. Use it from there? I can remember this location." Yes → rerun with `--compiler <path>`. "Remember" → also run `python3 <plugin>/scripts/centroid_config.py set mpucomp.path <path>`. |

## When the compiler isn't found (exit 2)

The message explains what `mpucomp.exe` is and where it usually lives. Be patient and
friendly: the user may not know what a compiler is. Help them look - offer to search likely
folders they name, accept a folder instead of the exact file, and when they give a path rerun
with `--compiler <path>`. Offer to remember it with
`python3 <plugin>/scripts/centroid_config.py set mpucomp.path <path>`. Never copy
`mpucomp.exe` anywhere; it always runs from where it is installed. If they want to skip
compiling, say plainly that the program has not been checked.
```

- [ ] **Step 4: Write `skills/format/SKILL.md`**

```markdown
---
name: format
description: Use when the user wants to tidy or reformat a Centroid CNC12 PLC .src file into one consistent style (aligned "Name IS Resource" definitions, keyword case, comment spacing, continuation alignment), or check whether it needs reformatting. Applies changes only after proving the compiled program is unchanged.
---

# Format a Centroid PLC program

1. Check first: `python3 <plugin>/scripts/plcfmt.py <file.src>` (`<plugin>` is this plugin's
   root). Exit 1 prints the diff it would make; exit 0 means already formatted. Naming findings
   on stderr are advice only and are never auto-changed.
2. Show the user a summary of the diff and ask before applying.
3. Apply: `python3 <plugin>/scripts/plcfmt.py --fix <file.src>`. It compiles before and after
   and keeps the change only if the compiled program is identical; otherwise it restores the
   original and exits 2.

Exit 3 and the compiler-not-found message work exactly as in the `compile` skill: ask before
using a compiler found in a CNC12 folder, rerun with `--compiler <path>`, and help a user who
doesn't know what `mpucomp.exe` is.

**No compiler available:** offer `--fix --no-verify` only after telling the user the change
will not be checked against the compiled program, and only if they agree.

**Acorn Wizard warning on stderr:** tell the user the Acorn Wizard regenerates this file unless
its Custom PLC preference is set (see the Acorn section of `centroid-plc-programming`), so
formatting it may be pointless. Continue only if they want to.

Files must be ASCII with CRLF line endings, as CNC12 writes them; the script reports otherwise.
```

- [ ] **Step 5: Verify**

Run: `python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t . -v`
Expected: all OK except exactly one `check_skill_links` miss, `unknown skill centroid-plc-programming` in `skills/format/SKILL.md`, which Task 10 resolves. Any other miss is a defect. Commit:

```bash
git add plugins/centroid-plc .claude-plugin .agents
git commit -m "Package centroid-plc plugin with compile and format skills"
```

---

### Task 10: Merged `centroid-plc-programming` skill

**Files:**
- Create: `plugins/centroid-plc/skills/centroid-plc-programming/SKILL.md` and `reference/{syntax,system-variables,messages,mpu11-allin1dc,acorn,examples-index}.md`

**Sources:** AC and TM `.claude/skills/centroid-plc-programming/`. TM cites PLC Manual **rev8 07/24/26** (132 pp, `TM/docs/official/centroid_plc_programming_manual.pdf`); AC cites an older revision (139 pp, `AC/docs/official/centroid_plc_programming_manual.pdf`), so AC page numbers are **not** valid against rev8.

- [ ] **Step 1: Start from TM** — copy TM `SKILL.md`, `reference/syntax.md`, `system-variables.md`, `messages.md`; copy TM `reference/acorn-plc.md` to `reference/acorn.md`; copy AC `reference/examples-index.md`.

- [ ] **Step 2: Fold in AC-only facts** — for each of `syntax.md`, `system-variables.md`, `messages.md`, run `diff AC/... TM/...`. For each fact present only in AC: find it in rev8 with `pdftotext -layout TM/docs/official/centroid_plc_programming_manual.pdf - | grep -n '<keyword>'` and the page via `pdftotext -layout -f N -l N`; add it with a rev8 `(PLC Manual, PDF p.N)` citation. If rev8 does not contain it, drop it (or keep it only with a `Field-verified (CNC12, YYYY-MM)` label if AC already labeled it so). Where AC and TM disagree, TM (rev8) wins.

- [ ] **Step 3: Write `reference/mpu11-allin1dc.md`** — from AC `reference/resources.md`: the MPU11/ALLIN1DC resource ranges and I/O addressing, re-cited against rev8. Remove every Acroloc-specific item (ATC, bins, `; Acroloc` tags, specific INP/OUT assignments of that mill). 100–250 lines.

- [ ] **Step 4: Rewrite `SKILL.md`** — frontmatter:
  ```
  name: centroid-plc-programming
  description: Use when writing, reading, or debugging Centroid CNC12 PLC stage-language source (.src) or M-code macro-to-PLC interaction on MPU11/ALLIN1DC or Acorn controls - stage/scan execution, IF/THEN/SET/RST syntax, resource types and I/O addressing, the SV_* system-variable catalog, operator-message encoding and plcmsg.txt, the Acorn Wizard-generated PLC, and example PLC projects. To check a .src compiles use the compile skill; to tidy its style use the format skill. Source: CNC12 PLC Programming Manual rev8 07/24/26.
  ```
  Body: when to use / when not; essentials (from TM); a reference router table with one row per reference file, including "MPU11/ALLIN1DC I/O → `reference/mpu11-allin1dc.md`" and "Acorn, Wizard, Custom PLC → `reference/acorn.md`"; a "Tools" line naming the `compile` and `format` skills; the **Manuals** section (Global Constraints template) for `plc-manual`; useful resources. Delete AC's line "Points to centroid-plc-programming…" style self-references and any "this repo" wording.

- [ ] **Step 5: Verify**

```bash
python3 tools/check_skill_links.py
python3 tools/check_marketplace.py
grep -rniE 'acroloc|torchmate|this repo|this machine|series 10|Centroid-Acroloc-ALLIN1DC|acorn_router_plc' plugins/centroid-plc || echo CLEAN
wc -l plugins/centroid-plc/skills/centroid-plc-programming/reference/*.md
```
Expected: checkers OK, `CLEAN`, each reference ≲ 250 lines (`system-variables.md` is an index and exempt).

- [ ] **Step 6: Commit** — `git add plugins/centroid-plc && git commit -m "Add merged centroid-plc-programming skill (MPU11 and Acorn)"` with a body listing which AC-only facts were added and which were dropped as uncitable in rev8.

---

### Task 11: centroid-vcp plugin

**Files:**
- Create: `plugins/centroid-vcp/{.claude-plugin/plugin.json,plugin.json,manuals.json}`, `plugins/centroid-vcp/skills/centroid-vcp/SKILL.md`, `reference/{actions,advanced,button-anatomy,skin-and-grid,troubleshooting,visual-states}.md`
- Modify: both catalogs; `scripts/` via sync

- [ ] **Step 1: Manifests, catalogs, `manuals.json`** (`vcp-manual`), `python3 tools/sync_shared.py`.
- [ ] **Step 2: Copy TM `centroid-vcp/` (rev28 base).**
- [ ] **Step 3: Fold in AC-only facts** — `diff` each AC/TM file pair. Keep an AC-only fact only if it is generic and cited (re-verify its page against `TM/docs/official/centroid_vcp_users_manual.pdf`, rev28) or carries a `Field-verified` label. Drop: "this-machine skin/buttons live in the acroloc-s10 skill", "this repo's resources/vcp", retro skin / `vcpgen` mentions.
- [ ] **Step 4: SKILL.md** — keep TM frontmatter name; description ends `Generic to the Centroid VCP. Source: VCP 2.0 Users Manual rev28 plus labeled field-verified notes.`; references to the PLC skill become `if the centroid-plc plugin is installed, see `centroid-plc-programming`; otherwise (PLC Manual, PDF p.N)`; add the **Manuals** section.
- [ ] **Step 5: Verify** — same commands as Task 10 Step 5 with `plugins/centroid-vcp`.
- [ ] **Step 6: Commit** — `git commit -m "Add centroid-vcp plugin (merged VCP skill)"`.

---

### Task 12: centroid-cnc12-ops plugin

**Files:**
- Create: `plugins/centroid-cnc12-ops/{.claude-plugin/plugin.json,plugin.json,manuals.json}`, `skills/centroid-cnc12-mill-ops/` (from AC `centroid-cnc12-operating/`), `skills/centroid-cnc12-router-ops/` (from TM)
- Modify: both catalogs; `scripts/` via sync

- [ ] **Step 1: Manifests, catalogs, `manuals.json`** (`mill-manual`, `router-manual`), sync.
- [ ] **Step 2: Copy** AC `centroid-cnc12-operating/` → `skills/centroid-cnc12-mill-ops/`; set frontmatter `name: centroid-cnc12-mill-ops`. Copy TM `centroid-cnc12-router-ops/` unchanged.
- [ ] **Step 3: Remove dangling pointers** — `grep -rn 'centroid-cnc12-gmcodes\|centroid-cnc12-config\|centroid-cnc12-intercon-probing' plugins/centroid-cnc12-ops`. For each hit, look the topic up in `AC/docs/official/centroid-cnc12-mill-operator-manual.pdf` (PDF page = printed + 1; `pdftotext -layout AC/docs/official/centroid-cnc12-mill-operator-manual.pdf - | grep -n '<code or topic>'`) and replace the pointer with `(Mill Manual §<section>, p.<printed page>)`. For a G/M code also in the router index, `centroid-cnc12-router-ops/reference/g-code-index.md` may be named as well (same plugin, no citation required). Update the mill SKILL.md "NOT for" line to cite manual chapters instead of missing skills.
- [ ] **Step 4: Manuals sections** in both SKILL.md files; replace the router skill's link to `docs/official/centroid-cnc12-router-operator-manual.md` (TM-only stub) with the Manuals section.
- [ ] **Step 5: Verify** — Task 10 Step 5 commands with `plugins/centroid-cnc12-ops`, plus `grep -rn 'gmcodes\|cnc12-config\|intercon-probing' plugins/ || echo CLEAN`.
- [ ] **Step 6: Commit** — `git commit -m "Add centroid-cnc12-ops plugin (mill and router operation)"`; body states the number of dangling pointers replaced.

---

### Task 13: centroid-acorn and centroid-allin1dc plugins

**Files:**
- Create: `plugins/centroid-acorn/…` with `skills/centroid-acorn-install/` (from TM); `plugins/centroid-allin1dc/…` with `skills/centroid-allin1dc-install/` (from AC)
- Modify: both catalogs; `scripts/` via sync

- [ ] **Step 1: Manifests, catalogs, `manuals.json`** (`acorn-install`, `pairing-guide`; `allin1dc-install`, `plcexp1616`), sync.
- [ ] **Step 2: Copy skills.** Rewrite mentions of skills now in other plugins (`centroid-plc-programming`, `centroid-vcp`, `centroid-cnc12-*`) to the conditional form with a manual citation on the same line; a `centroid-cnc12-operating` mention becomes `centroid-cnc12-mill-ops`. Remove machine references found by the global grep.
- [ ] **Step 3: Manuals sections** in both SKILL.md files.
- [ ] **Step 4: Verify** — Task 10 Step 5 commands with both plugin dirs.
- [ ] **Step 5: Commit** — `git commit -m "Add centroid-acorn and centroid-allin1dc install plugins"`.

---

### Task 14: teco-f510 plugin

**Files:**
- Create: `plugins/teco-f510/…` with `skills/teco-f510/` (from AC)
- Modify: both catalogs; `scripts/` via sync

- [ ] **Step 1: Manifests, catalogs, `manuals.json`** (`f510-manual`), sync.
- [ ] **Step 2: Copy skill**; in the description replace "Generic to the F510 — this-machine settings live in the acroloc-s10 skill." with "Generic to the F510."; remove the other machine references the global grep finds.
- [ ] **Step 3: Manuals section.**
- [ ] **Step 4: Verify** — Task 10 Step 5 commands with `plugins/teco-f510`.
- [ ] **Step 5: Commit** — `git commit -m "Add teco-f510 VFD plugin"`.

---

### Task 15: README, docs and license

**Files:**
- Create: `README.md`, `LICENSE.md`, `docs/installing.md`, `docs/manuals.md`, `docs/authoring.md`, `docs/plugins/{centroid-plc,centroid-vcp,centroid-cnc12-ops,centroid-acorn,centroid-allin1dc,teco-f510}.md`

- [ ] **Step 1: `README.md`**

```markdown
# Centroid AI

Skills and tools that help AI coding assistants (Claude Code and Codex) work with Centroid
CNC12 controls: PLC programming, the Virtual Control Panel, CNC12 operation, Acorn and
ALLIN1DC installation, and the TECO F510 spindle drive. Everything is generic - nothing here
is tied to one machine. Not affiliated with Centroid or TECO-Westinghouse.

## Quick install

**Claude Code**

    claude plugin marketplace add TD-4242/Centroid-AI
    claude plugin install centroid-plc@centroid-ai

**Codex**

    codex plugin marketplace add TD-4242/Centroid-AI

then install plugins from the Plugins directory. Full steps: [docs/installing.md](docs/installing.md).

## Plugins

| Plugin | What it does | Skills / commands |
| --- | --- | --- |
| [centroid-plc](docs/plugins/centroid-plc.md) | <centroid-plc description> | `centroid-plc-programming`, `/centroid-plc:compile`, `/centroid-plc:format` |
| [centroid-vcp](docs/plugins/centroid-vcp.md) | <description> | `centroid-vcp` |
| [centroid-cnc12-ops](docs/plugins/centroid-cnc12-ops.md) | <description> | `centroid-cnc12-mill-ops`, `centroid-cnc12-router-ops` |
| [centroid-acorn](docs/plugins/centroid-acorn.md) | <description> | `centroid-acorn-install` |
| [centroid-allin1dc](docs/plugins/centroid-allin1dc.md) | <description> | `centroid-allin1dc-install` |
| [teco-f510](docs/plugins/teco-f510.md) | <description> | `teco-f510` |

## Official manuals

The skills cite Centroid's and TECO's manuals by page; the PDFs are not included. Skills offer
to download them for you, or get them yourself from [docs/manuals.md](docs/manuals.md).

## Contributing

Skill conventions: [docs/authoring.md](docs/authoring.md). Run the checks before a PR:

    python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && \
    python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t .

## License

MIT for the skills, scripts and docs in this repo; see [LICENSE.md](LICENSE.md).
```
Replace each `<description>` with the exact description from the Plugin values table.

- [ ] **Step 2: `docs/installing.md`** — sections: *Claude Code* (`claude plugin marketplace add TD-4242/Centroid-AI`; `claude plugin install <name>@centroid-ai`; in-session `/plugin`; update with `claude plugin marketplace update centroid-ai`; remove with `claude plugin uninstall <name>@centroid-ai` / `claude plugin marketplace remove centroid-ai`); *Codex* (`codex plugin marketplace add TD-4242/Centroid-AI`; install from the Plugins directory; enable per project with `[plugins."<name>@centroid-ai"] enabled = true` in `.codex/config.toml`; `codex plugin marketplace upgrade centroid-ai`; `codex plugin marketplace remove centroid-ai`); *Requirements* (Python 3.10+ for scripts; Wine on Linux/macOS for compile/format; CNC12 install or a copy of `mpucomp.exe`); *Your settings* (`~/.centroid-ai/config.json` keys, `CENTROID_AI_HOME`, `CENTROID_AI_MANUALS`, how to change answers with `centroid_config.py set`).

- [ ] **Step 3: `docs/manuals.md`** — intro (skills cite these; not redistributed; Centroid serves only the latest revision so citations may drift), then the Manuals table from Global Constraints rendered as: Manual (title, linked to URL) · Cite as · Revision written against · Pages · PDF page = cited page + offset · Used by (plugin links). Then a "Downloading by hand" section with the curl form:
  ```bash
  curl -fL -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36' \
    -H 'Accept: application/pdf,*/*' -o ~/.centroid-ai/manuals/<file> <url>
  ```

- [ ] **Step 4: `docs/authoring.md`** — the eight conventions from the spec's "Skill content migration › Conventions" verbatim, the cross-plugin reference rule, the citation table (cite-as + PDF offset per manual), how to add a plugin (manifest templates, both catalog entries, `manuals.json`, `sync_shared.py`, checks), and version bumps (bump `version` in both manifests).

- [ ] **Step 5: `docs/plugins/<name>.md` × 6** — each: `# <displayName>`; description; install lines for Claude Code (`claude plugin install <name>@centroid-ai`) and Codex; `## Skills` with, per skill, what it covers (from its SKILL.md description), when it triggers, and 2–3 example prompts (e.g. for `centroid-plc-programming`: "What does SV_STOP do?", "Add a PLC message for a low air pressure fault", "Why is my stage never running?"); for `centroid-plc` a `## Commands` section with `/centroid-plc:compile path/to/file.src [-v]` and `/centroid-plc:format path/to/file.src` usage plus compiler lookup order; `## Manuals` linking the relevant `docs/manuals.md` rows; `## Requirements`.

- [ ] **Step 6: `LICENSE.md`**

```markdown
# License

## Original work - MIT License

Copyright (c) 2026 Bill Warner

The skills, scripts, documentation and tooling in this repository are licensed under the MIT
License:

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software
> and associated documentation files (the "Software"), to deal in the Software without
> restriction, including without limitation the rights to use, copy, modify, merge, publish,
> distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
> Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or
> substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
> INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
> PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
> ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
> ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

## Third-party documentation and software

The skills summarize and cite manuals published by Centroid Corporation and TECO-Westinghouse
Motor Company. Those manuals and Centroid's software (including `mpucomp.exe`) are not
included in this repository and remain the property of their owners. Centroid, CNC12, Acorn,
ALLIN1DC, TECO and F510 are trademarks of their respective owners. This project is not
affiliated with or endorsed by them.
```

- [ ] **Step 7: Verify** — `python3 tools/check_skill_links.py` (now also covers README and docs) → OK.
- [ ] **Step 8: Commit** — `git add README.md LICENSE.md docs && git commit -m "Add README, install guide, manuals list, authoring guide and plugin pages"`.

---

### Task 16: CI and end-to-end verification

**Files:**
- Create: `.github/workflows/check.yml`

- [ ] **Step 1: Workflow**

```yaml
name: check
on: [push, pull_request]
jobs:
  check:
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
```

- [ ] **Step 2: Full local check**

```bash
python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && \
python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t . -v
claude plugin validate .
for p in plugins/*/; do claude plugin validate "$p"; done
```
Expected: all OK; each `claude plugin validate` ends `✔ Validation passed`.

- [ ] **Step 3: Real compiler against both source repos**

```bash
python3 plugins/centroid-plc/scripts/plc_compile.py /home/bwarner/github/Acroloc-Centroid/Centroid-Acroloc-ALLIN1DC.src
(cd /home/bwarner/github/Acroloc-Centroid && ./compile.sh)
python3 plugins/centroid-plc/scripts/plc_compile.py /home/bwarner/github/Torchmate-Centroid/acorn_router_plc.src
(cd /home/bwarner/github/Torchmate-Centroid && ./compile.sh)
python3 plugins/centroid-plc/scripts/plcfmt.py /home/bwarner/github/Acroloc-Centroid/Centroid-Acroloc-ALLIN1DC.src; echo "exit $?"
```
Expected: each `plc_compile.py` result (success, warning count) matches the corresponding `compile.sh`; `plcfmt.py` check mode exits 0 or 1 without error and writes nothing (`git -C /home/bwarner/github/Acroloc-Centroid status --short` unchanged).

- [ ] **Step 4: Install locally in Claude Code**

```bash
claude plugin marketplace add ./
for p in centroid-plc centroid-vcp centroid-cnc12-ops centroid-acorn centroid-allin1dc teco-f510; do
  claude plugin install "$p@centroid-ai"; done
claude plugin list
```
Expected: all six `✔ enabled`. Then in a fresh `claude -p` session per plugin, ask one sample prompt from its `docs/plugins/<name>.md` and confirm the intended skill loads (e.g. `claude -p "Using the centroid-plc compile skill, compile /home/bwarner/github/Torchmate-Centroid/acorn_router_plc.src"`). Afterwards remove the local registration so it does not shadow the GitHub one: `claude plugin marketplace remove centroid-ai`.

- [ ] **Step 5: Codex** — `which codex`; if absent (it is absent on this machine as of 2026-10-10), record in the final report that Codex install was not exercised locally and the Codex catalog was checked only by `check_marketplace.py`.

- [ ] **Step 6: Commit**

```bash
git add .github
git commit -m "Add CI workflow"
```

- [ ] **Step 7: Report** — summarize results of Steps 2–5 to the user and ask whether to push the branch and open a PR to `TD-4242/Centroid-AI`.
