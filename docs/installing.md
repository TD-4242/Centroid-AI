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
| `mpucomp.path` | path to `mpucomp.exe` or its folder | Remembered compiler location |

Environment variables override the defaults: `CENTROID_AI_HOME` moves the whole `~/.centroid-ai`
folder, and `CENTROID_AI_MANUALS` sets the manuals folder (taking precedence over `manuals.dir`).

Skills ask before downloading or using a compiler and will offer to remember your answer. To
change an answer later, run (`<plugin>` is any installed plugin's folder):

    python3 <plugin>/scripts/centroid_config.py set manuals.autoDownload never
    python3 <plugin>/scripts/centroid_config.py set mpucomp.path /path/to/mpucomp.exe
    python3 <plugin>/scripts/centroid_config.py show

`set <key> null` clears a value. A hand-edited `config.json` that is not valid JSON is reported
by file name; fix or delete it.
