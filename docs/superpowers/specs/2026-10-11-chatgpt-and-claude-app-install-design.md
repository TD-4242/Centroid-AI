# ChatGPT and Claude app install — design

Date: 2026-10-11. Issues: #3 (Claude app and Cowork), #2 (ChatGPT). Branch: `chatgpt-and-claude-app`.

## Goal

Let users install the Centroid AI plugins in the Claude app (web chat, Desktop, Cowork) and try
them in ChatGPT, without weakening the existing Claude Code and Codex installs. For #2 this PR
follows approach A, agreed on the issue: document the routes, ship the tooling a pilot needs, and
build more only where the pilot shows a gap. #3 is closed by this PR; #2 stays open until the
pilot results are in.

## Non-goals

- Shortening any `shortDescription`. That waits for the pilot to show the 30-character limit is
  enforced.
- A second catalog or a separate export tree for ChatGPT.
- Changing skill content beyond the fallback lines in section 5. Citations and safety notes stay
  as they are.
- Running compile or format anywhere but a local machine.

## 1. Claude app and Cowork docs (#3)

`docs/installing.md` gets a **Claude app and Cowork** section after Codex:

- **Claude app (web chat or Desktop):** *Customize → Plugins → Add → Add marketplace → Add from a
  repository*, enter `TD-4242/Centroid-AI`; then *Customize → Plugins → Discover*, choose a plugin,
  *Add*.
- **Cowork:** open the *Cowork* tab, then *Customize* and the same *Plugins* steps.
- **Upload alternative:** upload a plugin file you built. The zip from `tools/export_plugin.py`
  (section 3) is such a file.
- **Notes:**
  - Plugins need a paid plan: Pro, Max, Team or Enterprise.
  - A plugin added in chat is saved to your account, so it also appears in Cowork and in Claude
    Code v2.1.273 or later.
  - In web chat the knowledge skills work. Downloading manuals may or may not work, depending on
    the sandbox's network access; settings in `~/.centroid-ai/` may not persist between chats.
  - Compile and format need a local machine with CNC12 (and Wine on Linux or macOS), so they
    work only in Claude Code or the Desktop app on that machine.

README.md's **Quick install** gets one line pointing to this section.

## 2. ChatGPT docs (#2)

`docs/installing.md` gets a **ChatGPT (pilot)** section after the Claude app:

- **Route 1, desktop app from a local marketplace (try first).** The ChatGPT desktop app reads
  `.agents/plugins/marketplace.json` from a repository root (or `~/.agents/plugins/marketplace.json`).
  Clone this repo, open it in the app, install a plugin from the Plugins directory, and select it
  from the `@` menu.
- **Route 2, Plugin Creator (proposed, untested).** Export a plugin zip (section 3) and ask
  Plugin Creator to repackage it with `create_plugin`.
- Compile and format are local-only, as in section 1.
- A link to the pilot checklist.

New `docs/chatgpt-pilot.md`: a checklist for the maintainer, limited to the centroid-acorn and
centroid-cnc12-ops plugins. Each item has a result line to fill in:

1. Route 1 installs the plugin.
2. The plugin appears in the `@` menu.
3. A typical question loads the right reference file (one example question per plugin).
4. With Python unavailable, the skill falls back to the manual link or an uploaded PDF.
5. Whether the 30-character `shortDescription` limit is enforced, and what happens if it is.
6. Whether route 2 is needed at all.

The page ends with what to do next: post results on #2; shorten descriptions only if item 5 says
the limit is enforced.

## 3. `tools/export_plugin.py`

```
python3 tools/export_plugin.py <plugin> [--out DIR] [--allow-dirty]
```

- `<plugin>` must be a folder under `plugins/` that is listed in both catalogs; otherwise exit 2
  with a one-line error.
- Writes `<out>/<plugin>-<version>-<shortsha>.zip`; `--out` defaults to `dist/`, which is added to
  `.gitignore`. `<version>` comes from the plugin's `.claude-plugin/plugin.json`.
- The zip's top-level folder is `<plugin>/`, holding the plugin's files minus `__pycache__/` and
  `*.pyc`, plus `<plugin>/SOURCE.txt`:

  ```
  repository: https://github.com/TD-4242/Centroid-AI
  plugin: <plugin>
  version: <version>
  commit: <full sha>
  exported: <UTC ISO-8601 timestamp>
  dirty: <true|false>
  ```

- If the working tree has uncommitted changes under `plugins/<plugin>/`, it refuses (exit 1, one
  line saying so) unless `--allow-dirty` is given; then `dirty: true`.
- Prints the zip path on success (exit 0). Stdlib only (`zipfile`, `subprocess` for git).
- Tests in `tools/tests/test_export_plugin.py` against a temporary git repo: contents and layout,
  `SOURCE.txt` fields, `__pycache__` excluded, dirty refusal and `--allow-dirty`, unknown plugin.

## 4. `check_marketplace.py --profile chatgpt`

```
python3 tools/check_marketplace.py --profile chatgpt [--max-short N]
```

- Without `--profile` the checker behaves exactly as now.
- With `--profile chatgpt` it runs the normal checks, then prints
  `warning: <plugin>: shortDescription is <n> chars (ChatGPT target <N>)` for each plugin whose
  root `plugin.json` `extensions.com.openai.interface.shortDescription` exceeds `N` (default 30).
  Warnings never change the exit code.
- CI runs the profile as an extra step; it passes while printing the warnings.
- Tests cover: default run unchanged, warnings printed with exit 0, `--max-short` changes the
  threshold, a description at exactly `N` is not warned.

## 5. Fallbacks in the skills

- Each of the seven `## Manuals` sections (centroid-plc-programming, centroid-vcp, both
  cnc12-ops skills, centroid-acorn-install, centroid-allin1dc-install, teco-f510) gets one line,
  before the "On Windows" line:

  > If you can't run Python here (for example in ChatGPT or Claude web chat), don't run the
  > script: give the user the manual's link from the download-links page named below, or ask them to upload
  > the PDF and read the cited page from it.

- The `compile` and `format` skills each get one line near the top: they need the user's own
  computer with CNC12 installed, so in a web chat explain that and suggest running them in
  Claude Code or Codex on that machine.
- After editing, `sync_shared.py --check`, `check_skill_links.py` and the tests still pass.

## Delivery

One PR from `chatgpt-and-claude-app` to `main`. The body says "Closes #3" and "Part of #2". After
opening it, comment on #2 with the revised scope and the pilot checklist link.

## Risks

- Claude app and ChatGPT menu paths change often; the docs date their instructions
  ("as of 2026-10") so stale steps are recognisable.
- Route 2 is untested by design; the docs say so plainly.
