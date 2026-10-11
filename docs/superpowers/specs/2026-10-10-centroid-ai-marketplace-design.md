# Centroid-AI plugin marketplace — design

Date: 2026-10-10. Status: approved in brainstorming, pending spec review.

## Goal

A public plugin marketplace (`TD-4242/Centroid-AI`) that packages the generic Centroid CNC12
AI skills and PLC tooling currently living in two machine repos (`Acroloc-Centroid`,
`Torchmate-Centroid`) so any Centroid CNC12 user can install them in **Claude Code** or
**Codex**.

Success means:

- `claude plugin marketplace add TD-4242/Centroid-AI` then `claude plugin install <p>@centroid-ai`
  works for every plugin, and `codex plugin marketplace add TD-4242/Centroid-AI` lists the same
  plugins for install.
- The README lists each plugin with a one-line description and a link to a detail page.
- Every skill is generic (no machine content), sourced, and free of dangling pointers.

## Non-goals

- Machine-specific content stays in its repo: `acroloc-s10`, `tools/vcpgen.py`, PLC source,
  macros, VCP skins.
- The two source repos are not modified. (Optional later follow-up: each deletes its generic
  skill copies and installs from the marketplace.)
- No vendor binaries (`mpucomp.exe`) or vendor PDFs are redistributed.
- No new knowledge skills (e.g. a mill G/M-code skill); the existing Acroloc spec
  `2026-08-08-centroid-cnc12-gmcodes-skill-design.md` can be picked up here later.

## Platform facts this design relies on (verified 2026-10-10)

| Concern | Claude Code | Codex |
| --- | --- | --- |
| Marketplace file | `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json` (also reads the Claude file as legacy) |
| Plugin manifest | `<plugin>/.claude-plugin/plugin.json` | portable `<plugin>/plugin.json` with `extensions.com.openai` (`.codex-plugin/plugin.json` is only a fallback) |
| Skills | `<plugin>/skills/<name>/SKILL.md` | same |
| Commands | a skill is invocable as `/<plugin>:<skill>` | no separate command type; skills are invoked by name |
| Add marketplace | `claude plugin marketplace add TD-4242/Centroid-AI` | `codex plugin marketplace add TD-4242/Centroid-AI` |
| Install | `claude plugin install <name>@centroid-ai` | Plugins directory in the app; enable via `.codex/config.toml` |

Sources: code.claude.com/docs/en/plugin-marketplaces, developers.openai.com/codex/plugins/build.

Consequence: "commands" are implemented as **skills with bundled scripts**, which gives one
source for both tools.

## Plugins (grouping by topic)

| Plugin | Skills | Origin |
| --- | --- | --- |
| `centroid-plc` | `centroid-plc-programming` (merged), `compile`, `format` | both repos + Acroloc `compile.sh`/`plcfmt.py` |
| `centroid-vcp` | `centroid-vcp` (merged) | both repos |
| `centroid-cnc12-ops` | `centroid-cnc12-mill-ops`, `centroid-cnc12-router-ops` | Acroloc `centroid-cnc12-operating` (renamed), Torchmate |
| `centroid-acorn` | `centroid-acorn-install` | Torchmate |
| `centroid-allin1dc` | `centroid-allin1dc-install` | Acroloc |
| `teco-f510` | `teco-f510` | Acroloc |

All plugins start at version `0.1.0`. Marketplace name: `centroid-ai`.

## Repository layout

```
Centroid-AI/
├── .claude-plugin/marketplace.json
├── .agents/plugins/marketplace.json
├── .github/workflows/check.yml
├── README.md
├── LICENSE.md
├── docs/
│   ├── installing.md          # Claude Code + Codex: add, install, update, remove
│   ├── manuals.md             # every cited manual: cite-as, URL, expected rev/pages, offset
│   ├── authoring.md           # skill conventions (below)
│   ├── plugins/<plugin>.md    # one detail page per plugin
│   └── superpowers/specs/     # design history
├── shared/                    # canonical copies of cross-plugin helper scripts
│   ├── centroid_config.py
│   └── fetch_manual.py
├── plugins/<plugin>/
│   ├── .claude-plugin/plugin.json
│   ├── plugin.json            # portable manifest (Codex)
│   ├── manuals.json
│   ├── scripts/               # synced copies of shared/ + plugin-specific scripts
│   └── skills/<skill>/{SKILL.md, reference/*.md}
└── tools/
    ├── check_skill_links.py   # generalized from Torchmate; walks plugins/
    ├── check_marketplace.py
    ├── sync_shared.py
    └── tests/
```

### Manifests and catalogs

- Each plugin's two manifests carry the same `name`, `version`, `description`, `author`,
  `homepage`, `repository`, `license` (`MIT`), `keywords`. The portable root `plugin.json`
  adds `"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"` and
  `extensions.com.openai.interface` (`displayName`, `shortDescription`, `category`).
- The two marketplace files list the same plugins. Claude entries use
  `"source": "./plugins/<name>"`; Codex entries use
  `{"source": "local", "path": "./plugins/<name>"}`, `policy: {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}`, and a
  `category`; the Codex catalog also has `interface.displayName`.
- `tools/check_marketplace.py` fails when: the catalogs' plugin sets differ; an entry name
  differs from its manifest `name`; the two manifests of a plugin disagree on name or version;
  a `source` path does not exist; a plugin has no skills.

## Shared user config and the manuals

`~/.centroid-ai/config.json` (created on first write; one file for all plugins and projects):

```json
{ "manuals": { "autoDownload": "ask", "dir": null }, "mpucomp": { "path": null } }
```

`autoDownload` is `ask` (default), `always`, or `never`. The manuals directory defaults to
`~/.centroid-ai/manuals/`, overridden by `manuals.dir` or env `CENTROID_AI_MANUALS`.

### manuals.json (per plugin)

```json
[{ "id": "plc-manual", "title": "CNC12 PLC Programming Manual", "citeAs": "PLC Manual",
   "url": "https://www.centroidcnc.com/…/centroid_plc_programming_manual.pdf",
   "file": "centroid_plc_programming_manual.pdf",
   "expectRev": "rev8 07/24/26", "expectPages": null, "pdfOffset": 0 }]
```

Initial set: PLC Programming Manual (`centroid-plc`); VCP 2.0 Users Manual (`centroid-vcp`);
CNC12 Mill and Router Operator Manuals (`centroid-cnc12-ops`); Acorn Installation Manual and
Acorn Axis Pairing and Squaring guide (`centroid-acorn`); ALLIN1DC Installation Manual and
PLCEXP1616 Users Manual (`centroid-allin1dc`); F510 Instruction Manual (`teco-f510`).
URLs, revisions and page counts are taken from the source repos' skills and `docs/official/`
stubs during implementation and each URL is checked to resolve.

### Download flow

`scripts/fetch_manual.py <id> [--yes]` resolves the manual from `manuals.json`, then:

1. If the file exists in the manuals dir, print its path and exit 0.
2. Otherwise the calling skill consults `autoDownload`:
   - `always` → download.
   - `never` → answer from reference files, citing manual and page.
   - `ask` → ask the user in plain language, e.g. *"This answer is best checked against
     Centroid's CNC12 PLC Programming Manual (free PDF, ~4 MB). Want me to download it to
     `~/.centroid-ai/manuals/`? I can also do this automatically from now on, or never ask
     again."* — and saves an "always"/"never" answer to config.
3. Download with a browser User-Agent and `Accept: application/pdf` (Centroid rejects default
   agents), to a temp file then rename. Verify it is a PDF.
4. Compare page count / revision to `expectPages` / `expectRev` where determinable
   (`pdfinfo` if present, else a stdlib `/Type /Page` count); on mismatch warn that page
   citations may be slightly off. Never fail on a mismatch.

Every SKILL.md has a short "Manuals" section stating this behaviour and listing its manuals.
`docs/manuals.md` lists all manuals with direct download links for users who prefer to fetch
them by hand.

### Shared code

Installed plugins are copied individually, so they cannot share files at runtime. Canonical
helpers live in `shared/`; `tools/sync_shared.py` copies them into each plugin's `scripts/`;
`sync_shared.py --check` (in CI) fails on drift. All scripts are Python 3 stdlib only, so they
run on the Windows control PC, Linux and macOS without Bash.

## `centroid-plc` tooling skills

Scripts in `plugins/centroid-plc/scripts/`:

- `mpucomp_locate.py` — finds the compiler.
- `plc_compile.py <file.src> [-v] [-o out.plc] [--compiler PATH]` — Python port of
  `compile.sh` for any `.src`: runs `mpucomp.exe -w <src> <tmp.plc>` natively on Windows or via
  `wine` (with `WINEDEBUG=-all`) elsewhere, run from the `.src` directory; reports errors,
  "Compilation successful/Program size" and a warning count. Exit 0 ok, 1 compile failed,
  2 setup problem (no compiler / no wine / no source), 3 compiler needs user confirmation.
- `plcfmt.py <file.src> [--fix] [--no-verify] [--compiler PATH]` — Acroloc formatter
  generalized to any `.src`; its fingerprint gate (MPU program words + checksums C2 and C4)
  calls `plc_compile.py` instead of `./compile.sh`.

### Locating mpucomp.exe (first match wins)

1. `--compiler PATH`
2. `mpucomp.path` in config
3. Project: next to the `.src`, then the git repo root
4. CNC12 install folders: `C:\cncm`, `C:\cncr`, `C:\cnct`, `C:\cncp`; on Linux/macOS the same
   under `$WINEPREFIX/drive_c/` (default `~/.wine/drive_c/`)

Hits from 1–3 are used silently. A hit from 4 returns exit 3 with the path; the skill asks
*"I found Centroid's PLC compiler at `C:\cncr\mpucomp.exe`. Use it from there? I can remember
this location."* and on yes reruns with `--compiler` (saving to config if asked). The compiler
is always run in place, never copied.

### When nothing is found

The skill explains before asking, in plain language:

> To check your PLC program for errors I need **`mpucomp.exe`**, Centroid's PLC compiler. It's
> the same program CNC12 uses to build your PLC when you load it on the machine. It comes with
> every CNC12 install, but I can't ship it with these tools.
>
> **Where to look:** on your control PC it's usually in `C:\cncm` (mill) or `C:\cncr` (router).
> If you copied your CNC12 folder to this computer, look there. If you don't have CNC12 here,
> the free CNC12 download from centroidcnc.com includes it.
>
> You can paste the path, drag the file in, or tell me to skip compiling for now.

Missing Wine on Linux/macOS gets a similar plain explanation (what Wine is, why it is needed,
the install command for the detected OS).

### format safeguards

- Default is check mode (diff + findings). `--fix` writes only if the compiled fingerprint is
  unchanged; otherwise the original bytes are restored.
- Without a compiler, `format` shows the diff but applies it only if the user explicitly
  accepts `--no-verify` after a warning.
- If the source looks Acorn Wizard-generated, warn that the Wizard overwrites hand edits unless
  Custom PLC is set, pointing to the `centroid-plc-programming` Acorn reference.

## Skill content migration

### Conventions (`docs/authoring.md`, from Torchmate `CLAUDE.md`)

1. Generic — no machine content.
2. Sourced — every fact cites document and section/page; uncitable facts are dropped.
3. `Field-verified (CNC12, YYYY-MM)` label for board-agnostic lessons no manual states.
4. `**Advisory (not in the manual):**` label for electrical-safety guidance only.
5. No dangling pointers (enforced by `check_skill_links.py`).
6. Current state — no tombstones.
7. Shape — `SKILL.md` (frontmatter, when to use / not, essentials, reference router, manuals,
   resources) plus `reference/*.md` of roughly 100–250 lines; index files exempt.
8. Paths — mill `c:\cncm`, router `c:\cncr`.

Plus the page-citation table (cite-as and PDF-page offset per manual), kept in sync with
`docs/manuals.md`.

### Cross-plugin references

A skill may name skills in its own plugin freely. A skill in another plugin is named
conditionally with a manual fallback — *"if the `centroid-vcp` plugin is installed, use
`centroid-vcp`; otherwise see (VCP Manual p.44)"*. `check_skill_links.py` resolves names
against the whole repo and requires a manual citation on the same line for cross-plugin names.

### Per skill

- **`centroid-plc-programming`** (merge): `SKILL.md` routes by controller.
  `reference/syntax.md`, `system-variables.md`, `messages.md` merged; on conflicting facts the
  text citing PLC Manual rev8 wins, single-copy facts kept if cited.
  `reference/mpu11-allin1dc.md` from Acroloc `resources.md` minus Acroloc specifics;
  `reference/acorn.md` from Torchmate `acorn-plc.md`; `reference/examples-index.md` from
  Acroloc. Description covers both controllers and mentions `compile` / `format`.
- **`centroid-vcp`** (merge): Torchmate (rev28, generic) is the base; add cited generic facts
  only present in Acroloc; drop "this-machine skin lives in acroloc-s10" and
  "this repo's resources/vcp" lines.
- **`centroid-cnc12-mill-ops`**: Acroloc `centroid-cnc12-operating` renamed. Every pointer to
  the non-existent `centroid-cnc12-gmcodes`, `-config`, `-intercon-probing` becomes a Mill
  Operator Manual chapter/page citation (or a conditional pointer to
  `centroid-cnc12-router-ops`'s G/M index where the code is shared).
- **`centroid-cnc12-router-ops`, `centroid-acorn-install`, `centroid-allin1dc-install`,
  `teco-f510`**: copied; machine references removed; manuals sections added.

## README and plugin pages

`README.md`:

1. One-paragraph intro (what this is, who it is for, not affiliated with Centroid or TECO).
2. Quick install for Claude Code and Codex (3–4 commands), linking `docs/installing.md`.
3. Plugin table: **Plugin** (linked to `docs/plugins/<name>.md`) · **What it does** (one line)
   · **Skills / commands**.
4. Official manuals: one sentence plus link to `docs/manuals.md`.
5. Contributing (link `docs/authoring.md`) and license.

`docs/plugins/<name>.md`: summary; install line for both tools; each skill with what it covers,
when it triggers, and 2–3 example prompts; commands with usage (for `centroid-plc`); manuals
used with links; requirements (Python 3, Wine where relevant).

## Licensing

`LICENSE.md`: original work (skills, scripts, docs) under MIT, copyright Bill Warner. A
notice that the skills summarize and cite Centroid and TECO documentation, that no vendor
manuals or binaries are included, and that trademarks belong to their owners.

## Verification

- `python3 tools/check_skill_links.py` and `python3 tools/check_marketplace.py` exit 0.
- `python3 tools/sync_shared.py --check` exits 0.
- Tool tests pass (`plcfmt` tests ported; new tests for the locator search order using fake
  directory trees, for `plc_compile` output parsing, and for `fetch_manual` cache/config
  behaviour without network). Compiler-dependent tests self-skip without `mpucomp`/Wine.
- `claude plugin validate .` passes.
- Local install of every plugin in Claude Code from the working tree; if Codex is available
  on this machine, add the marketplace there too. One sample prompt per skill confirms it
  triggers.
- `plc_compile.py` and `plcfmt.py` (check mode) run against both source repos' `.src` files
  with the repo-local `mpucomp.exe`, matching `compile.sh` results.
- CI (`.github/workflows/check.yml`) runs the checkers and tests on push and PR.
