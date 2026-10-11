# Installing

The marketplace is named centroid-ai. Each plugin installs on its own; install only the ones
you need.

## Claude Code

Add the marketplace once, then install plugins from it:

    claude plugin marketplace add TD-4242/Centroid-AI
    claude plugin install <name>@centroid-ai

For example `claude plugin install centroid-plc@centroid-ai`. Inside a session, `/plugin` opens
the same browser. Plugin names are listed in the [README](../README.md#plugins).

Update and remove:

    claude plugin marketplace update centroid-ai
    claude plugin uninstall <name>@centroid-ai
    claude plugin marketplace remove centroid-ai

## Codex

    codex plugin marketplace add TD-4242/Centroid-AI

Then install plugins from the Plugins directory in the Codex app. To enable a plugin for one
project, add this to the project's `.codex/config.toml`:

    [plugins."<name>@centroid-ai"]
    enabled = true

Update and remove:

    codex plugin marketplace upgrade centroid-ai
    codex plugin marketplace remove centroid-ai

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
  on Linux or macOS) there, and work only in Claude Code or the Desktop app on that computer.

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

## Requirements

- Python 3.10 or newer for the plugin scripts (manual download, compile, format, settings).
  On Windows, use `py -3` (or `python`) if `python3` is not found.
- Linux and macOS: [Wine](https://www.winehq.org/) to run `mpucomp.exe` for compile and format.
  If it is missing, the scripts print the install command for your system.
- A CNC12 install, or a copy of `mpucomp.exe`, for compile and format. The compiler is Centroid's
  and is not shipped here; see [centroid-plc](plugins/centroid-plc.md#requirements).

The knowledge-only skills need nothing beyond Python (and only for the optional manual download).

## Your settings

Settings live in `~/.centroid-ai/config.json`, shared by every plugin:

| Key | Values | Meaning |
| --- | --- | --- |
| `manuals.autoDownload` | `ask` (default), `always`, `never` | Whether a skill may download a missing manual |
| `manuals.dir` | folder path | Where manuals are stored (default `~/.centroid-ai/manuals/`) |
| `mpucomp.path` | path to `mpucomp.exe` or its folder | Remembered compiler location (used without asking) |
| `mpucomp.trusted` | list of `mpucomp.exe` paths | Compilers you approved after a skill found them by searching; add one with `centroid_config.py trust <path>` |

Environment variables override the defaults: `CENTROID_AI_HOME` moves the whole `~/.centroid-ai`
folder, and `CENTROID_AI_MANUALS` sets the manuals folder (taking precedence over `manuals.dir`).

Skills ask before downloading or using a compiler and will offer to remember your answer. To
change an answer later, run (`<plugin>` is any installed plugin's folder):

    python3 <plugin>/scripts/centroid_config.py set manuals.autoDownload never
    python3 <plugin>/scripts/centroid_config.py set mpucomp.path /path/to/mpucomp.exe
    python3 <plugin>/scripts/centroid_config.py trust /path/to/mpucomp.exe
    python3 <plugin>/scripts/centroid_config.py show

`set <key> null` clears a value. A hand-edited `config.json` that is not valid JSON is reported
by file name; fix or delete it.
