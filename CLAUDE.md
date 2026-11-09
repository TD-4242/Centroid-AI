# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A plugin marketplace (`centroid-ai`) of skills for Centroid CNC12 controls and the TECO F510 VFD,
published for Claude Code, Codex, the Claude app and (piloted, unverified) ChatGPT. Most content is
Markdown skills; the Python under `tools/` validates and packages them, and a few plugin scripts run
on the user's machine. Python 3.12, stdlib only, no package manager.

## Commands

Full check suite (same as CI in `.github/workflows/check.yml`):

    python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && \
    python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t .

- ChatGPT-target warnings (CI runs this too): `python3 tools/check_marketplace.py --profile chatgpt`
- Single test module: `python3 -m unittest tools.tests.test_plcfmt` (run from repo root)
- Copy shared helpers into plugins after editing `shared/`: `python3 tools/sync_shared.py`
- Build upload zips into `dist/`: `python3 tools/export_plugin.py <plugin>` or `--all --stable-name`
  (refuses a dirty tree unless `--allow-dirty`)

The `plcfmt`/`plc_compile` integration tests need Wine plus `CENTROID_AI_TEST_SRC` (a `.src` with
`mpucomp.exe` beside it) and self-skip otherwise.

## Layout and how the pieces fit

- **Two catalogs, two manifests per plugin.** `.claude-plugin/marketplace.json` (Claude) and
  `.agents/plugins/marketplace.json` (Codex) must list the same plugins. Each plugin has
  `.claude-plugin/plugin.json` and a portable `plugin.json` (with `extensions.com.openai`); names
  and `version` must match. Bump `version` in both when a plugin changes. `check_marketplace.py`
  enforces all of this.
- **`shared/*.py` is the source of truth** for `centroid_config.py` (reads/writes
  `~/.centroid-ai/config.json`) and `fetch_manual.py`. Installed plugins can't share files, so these
  are copied into every `plugins/*/scripts/`. Never edit the copies; edit `shared/` and run
  `sync_shared.py`.
- **`manuals.json` per plugin** lists the PDFs its skills cite (URL, expected rev/pages, `pdfOffset`).
  A plugin that cites only web sources (`centroid-api`) has none.
  PDFs are never committed (`.gitignore` blocks `*.pdf`, `*.exe`, `*.plc`); `fetch_manual.py`
  downloads them with consent.
- **`centroid-plc` scripts** wrap Centroid's own compiler: `mpucomp_locate.py` finds `mpucomp.exe`
  (never bundled), `plc_compile.py` runs it (Wine off Windows), `plcfmt.py` formats `.src`. The
  `compile`/`format` skills document exit codes the agent must act on (e.g. exit 3 = ask the user to
  trust a found compiler).
- **Releases**: pushing a `v*` tag runs checks, exports all plugin zips plus `SHA256SUMS.txt`, and
  creates a GitHub release.
- `docs/superpowers/` holds design specs and plans; it is excluded from the link checker.

## Skill authoring rules

Read `docs/authoring.md` before changing skills or adding a plugin (it has the full add-a-plugin
checklist). Key points:

- Generic only: nothing tied to one machine or shop. Paths: mill `c:\cncm`, router `c:\cncr`.
- Every fact cites a manual page, or for a web source its name and page or class (e.g.
  `(API Ref, CNCPipe.Plc)`); uncitable facts are dropped. Citation forms and per-manual page
  offsets are in `docs/authoring.md` - keep that table, `docs/manuals.md` and each `manuals.json` in sync.
- Labels: `Field-verified (CNC12, YYYY-MM)` for uncited field lessons; `**Advisory (not in the manual):**`
  for electrical-safety guidance only.
- Describe current state only - no "previously"/"REMOVED" tombstones.
- Shape: `SKILL.md` plus `reference/*.md` of ~100-250 lines; each knowledge skill ends with the
  standard "Manuals" section, or a "Sources" section when it cites only web sources.
- Cross-plugin skill names must be conditional and carry a manual citation on the same line;
  `check_skill_links.py` enforces this along with link and anchor resolution.
- Adding a plugin also means a `docs/plugins/<name>.md` page and a README table row.
