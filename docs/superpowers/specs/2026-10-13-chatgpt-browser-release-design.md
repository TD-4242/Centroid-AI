# ChatGPT browser install and release archives — design

Date: 2026-10-13. Issue: #2 (phase 1 of 2). Branch: `chatgpt-browser-release`.

## Goal

Make the informational skills easy to install in ChatGPT's browser Chat/Work interface, with no
Python, Git or compiler on the user's side. Per the issue owner's comment of 2026-10-11, desktop or
Codex installs alone do not satisfy #2.

The work is split in two phases (agreed 2026-10-13):

- **Phase 1 (this design):** tagged GitHub Releases carrying one zip per plugin, a README-linked
  browser guide with a copy-and-paste Plugin Creator prompt, and a browser-first pilot checklist.
  Every browser step is marked unverified.
- **Phase 2 (separate PR):** the maintainer runs the checklist for Acorn and CNC12 in browser
  ChatGPT and posts the results, verbatim errors included, on #2. The guide is then rewritten from
  those results and the unverified marks are removed for what passed.

## Non-goals

- Changing skill content, manifest descriptions or catalogs. The ≤30-character descriptions live
  only in the guide's prompt table.
- Removing `scripts/` from the zips. Skills already fall back when Python can't run (PR #4).
- Claiming any browser step works before phase 2.

## 1. `export_plugin.py` additions

```
python3 tools/export_plugin.py (<plugin> | --all) [--out DIR] [--allow-dirty] [--stable-name]
```

- `--all` exports every plugin listed in both catalogs, in catalog order, and prints one zip path
  per line. `<plugin>` and `--all` are mutually exclusive; one is required (argparse usage error,
  exit 2, otherwise). With `--all`, the first failure stops the run with that plugin's error and
  exit code; zips already written stay.
- `--stable-name` names the zip `<plugin>.zip` instead of `<plugin>-<version>-<shortsha>.zip`.
  `SOURCE.txt` is unchanged and still records version and commit.
- Everything else (dirty check, refusing symlinks, binaries and `--out` inside a plugin) is
  unchanged and applies to each plugin.
- New tests: `--all` writes one zip per catalog plugin and prints each path; `--all` stops on a
  dirty plugin with exit 1; `--stable-name` file name; `<plugin>` with `--all` is a usage error;
  neither given is a usage error.

## 2. Release workflow

New `.github/workflows/release.yml`:

- Trigger: `push` of tags matching `v*`. `permissions: contents: write`.
- Steps on `ubuntu-latest`, Python 3.12:
  1. `actions/checkout@v4`.
  2. The same checks as `check.yml`: `check_marketplace.py`, `check_skill_links.py`,
     `sync_shared.py --check`, the unit tests.
  3. `python3 tools/export_plugin.py --all --stable-name --out dist`.
  4. `cd dist && sha256sum *.zip > SHA256SUMS.txt`.
  5. Write `dist/NOTES.md` holding the header line below, then run
     `gh release create "$GITHUB_REF_NAME" dist/*.zip dist/SHA256SUMS.txt --title "$GITHUB_REF_NAME"
     --notes-file dist/NOTES.md --generate-notes` (gh appends the generated notes after the file).
  `GH_TOKEN: ${{ github.token }}` in the step's env.
- A failing check stops the job before anything is published.
- The tag is the marketplace release number (first: `v0.2.0`). Plugin versions are independent.
- Header line: `Download a plugin zip below. Browser ChatGPT install steps (unverified):
  https://github.com/TD-4242/Centroid-AI/blob/main/docs/chatgpt-browser.md`.

The workflow has no unit tests. It is reviewed by eye, and proven by the first real tag push, which
needs the maintainer's go-ahead.

## 3. Browser guide: `docs/chatgpt-browser.md`

Linked from README Quick install and from `docs/installing.md`'s ChatGPT section. Content:

- **Status banner:** "Unverified: these steps have not yet been tested end to end in browser
  ChatGPT ([#2](https://github.com/TD-4242/Centroid-AI/issues/2)). Steps as of 2026-10." Each
  untested step carries *(unverified)*.
- **Prerequisites:** a ChatGPT account with access to Plugin Creator (which plans include it:
  unverified); a web browser. No Python, Git or compiler.
- **Steps:**
  1. Download the plugin's zip. Table of all six plugins with direct links
     `https://github.com/TD-4242/Centroid-AI/releases/latest/download/<plugin>.zip`, plus a link to
     the Releases page and `SHA256SUMS.txt`. Start with centroid-acorn or centroid-cnc12-ops.
  2. Open a new chat, start Plugin Creator *(unverified how it is invoked in the browser)*, attach
     the zip, paste the prompt.
  3. Install the private plugin Plugin Creator produces *(unverified)*.
  4. Start a new conversation, type `@`, choose the plugin, ask a question *(unverified)*.
- **Plugin Creator prompt** (one code block; the user fills two placeholders from the table):

  ```
  Create a private plugin from the attached zip. It holds one plugin folder: skills/*/SKILL.md
  files, their reference/*.md files, a plugin.json and a SOURCE.txt.
  - Keep every SKILL.md and reference file word for word, including page citations and safety notes.
  - Name: <plugin name>. Display name: <display name>.
  - Use the description from plugin.json. Only if you require a description of 30 characters or
    fewer, use instead: "<short description>", and tell me that you did.
  - The scripts/ folder holds optional local helpers; include it if you can, skip it if you can't,
    and tell me which.
  - Tell me about any file you could not include and any error, word for word.
  ```

- **Prompt table:**

  | Plugin | Display name | Short description (≤30) |
  | --- | --- | --- |
  | centroid-acorn | Centroid Acorn | Centroid Acorn setup help |
  | centroid-cnc12-ops | Centroid CNC12 Operation | Centroid CNC12 operation help |
  | centroid-plc | Centroid PLC | Centroid PLC programming help |
  | centroid-vcp | Centroid VCP | Centroid VCP customization |
  | centroid-allin1dc | Centroid ALLIN1DC | Centroid ALLIN1DC setup help |
  | teco-f510 | TECO F510 VFD | TECO F510 spindle VFD help |

- **Using it without a compiler:** knowledge answers work in the browser. When an answer needs
  the manual's exact text, the skill gives the link (also in [docs/manuals.md](manuals.md))
  or asks you to upload the PDF and reads the cited page. Compile and format need Claude Code or
  Codex on the computer with CNC12; they do not work in the browser.
- **Updating:** download the newer zip from Releases; ask Plugin Creator to update the existing
  private plugin from it *(unverified)*, or remove the plugin and install again. `SOURCE.txt`
  inside the zip shows its version and commit.
- **Troubleshooting** (symptom → what to try; each ends "post the exact error on #2"):
  zip rejected (try unzipping and attaching the files, or attach `SKILL.md` and the references
  only); description too long (use the table's short description); plugin not under `@` (new
  conversation, check it is installed and enabled); answer ignores the references (name the plugin
  with `@`, ask it to read its reference files); manual download fails (use the link or upload the
  PDF).
- **Other routes:** link to [installing.md#chatgpt-pilot](installing.md#chatgpt-pilot) for
  the desktop route.

## 4. Pilot checklist rewrite: `docs/chatgpt-pilot.md`

Browser first, for centroid-acorn and centroid-cnc12-ops. Header asks for ChatGPT plan, browser
and date. Items, each with `Result:` and `Exact error (if any):` lines:

1. Download both zips from the latest release; `SHA256SUMS.txt` matches (optional).
2. Plugin Creator accepts the zip with the guide's prompt; how it was started.
3. Whether the 30-character limit was enforced, and the exact message.
4. The private plugin installs.
5. It appears under `@` in a new conversation; name and description as shown.
6. Reference question per plugin (existing questions: Acorn axis pairing → `axis-pairing.md`;
   CNC12 Router part zero → router `part-setup.md`).
7. Manual-link fallback: "Quote word for word what the Acorn Installation Manual says on the page
   your answer cites." Expect a download link or a request to upload the PDF.
8. Uploaded-PDF fallback: upload the Acorn Installation Manual PDF and repeat 7; expect the quoted
   text.
9. Update: install a newer release zip over the existing plugin (skip if only one release exists).

Optional final section: the desktop route (existing route 1 steps). Next steps: post results on #2;
phase 2 updates the guide.

## 5. Small additions

- README Quick install: a "ChatGPT in the browser" line linking `docs/chatgpt-browser.md`, marked
  unverified.
- `docs/installing.md`:
  - ChatGPT section: link the browser guide first.
  - Claude app "Upload a plugin file instead": add that ready-made zips are on the Releases page
    (`releases/latest/download/<plugin>.zip`), before the `export_plugin.py` route.

## Delivery

One PR from `chatgpt-browser-release`, body "Part of #2". After merge, ask the maintainer before
pushing tag `v0.2.0` (publishes the first release). Then comment on #2 with the guide and checklist
links.

## Risks

- Plugin Creator's browser behaviour is unknown; the guide's steps may be wrong until phase 2. The
  banner and *(unverified)* marks say so.
- `releases/latest/download/...` links 404 until the first release exists; the guide notes the
  Releases page as the fallback.
