# Centroid PLC

Write, read and debug Centroid CNC12 PLC programs (MPU11/ALLIN1DC and Acorn), and compile-check or format .src files with Centroid's own compiler.

## Install

Claude Code:

    claude plugin install centroid-plc@centroid-ai

Codex: add the marketplace with `codex plugin marketplace add TD-4242/Centroid-AI`, then install **Centroid PLC** from the Plugins directory. See [Installing](../installing.md).

## Skills

### `centroid-plc-programming`

Writing, reading and debugging CNC12 PLC stage-language `.src` programs on MPU11/ALLIN1DC and Acorn controls: stage and scan execution, `IF`/`THEN`/`SET`/`RST` syntax, resource types and I/O addressing, the `SV_*` system-variable catalog, operator-message encoding and `plcmsg.txt`, the Acorn Wizard-generated PLC, and example PLC projects.

Triggers: When you ask about PLC source, a `.src` file, system variables or macro-to-PLC interaction.

Example prompts:

- "What does SV_STOP do?"
- "Add a PLC message for a low air pressure fault."
- "Why is my stage never running?"

### `compile`

Checks that a `.src` compiles by running Centroid's own `mpucomp.exe` and reporting errors and warnings. Loads nothing onto the machine.

Triggers: When you say "compile my PLC", "check the .src for errors", or before loading a PLC on the machine.

Example prompts:

- "Compile my PLC and tell me what is wrong."
- "Check plc/mill.src for errors before I load it."

### `format`

Tidies a `.src` into one consistent style (aligned `Name IS Resource` definitions, keyword case, comment spacing, continuation alignment). Changes are kept only if the compiled program is proven identical.

Triggers: When you ask to tidy, reformat or check the style of a PLC file.

Example prompts:

- "Format my PLC source, but show me the diff first."
- "Does this .src need reformatting?"

## Commands

In Claude Code the `compile` and `format` skills are also slash commands:

    /centroid-plc:compile path/to/file.src [-v]
    /centroid-plc:format path/to/file.src

- `compile`: `-v` lists every warning; `-o out.plc` keeps the compiled program. Exit 0 compiled, 1 compile errors, 2 setup problem (no compiler, no Wine, no source file), 3 compiler found in a CNC12 folder and needs your OK.
- `format`: checks by default and prints the diff it would make (exit 1 if a change is pending, 0 if already formatted); `--fix` rewrites the file, but only after compiling before and after and proving the program is identical, otherwise it restores the original (exit 2). `--no-verify` skips that proof. Naming findings are advice and are never auto-changed. Formatting a Wizard-generated Acorn file warns that the Wizard may regenerate it.

### Finding the compiler

Both look for `mpucomp.exe` in this order and stop at the first hit:

1. `--compiler <path>` (the file or its folder). A bad path is an error, not a fallback.
2. `mpucomp.path` in `~/.centroid-ai/config.json`.
3. Next to the `.src` file, then at the git repository root.
4. The CNC12 folders `C:\cncm`, `C:\cncr`, `C:\cnct`, `C:\cncp` (on Linux and macOS the same folders under `$WINEPREFIX/drive_c`, default `~/.wine/drive_c`).

A compiler found in a CNC12 folder is used only after you confirm, and you can have the location remembered. The compiler is never copied; it always runs from where it is installed.

## Manuals

This plugin cites:

- [CNC12 PLC Programming Manual](../manuals.md) (PLC Manual)
- [CNC12 Router Operators Manual](../manuals.md) (Router Manual)
- [Acorn Installation Manual](../manuals.md) (Acorn Install)

Download links, revisions and page offsets are in [manuals.md](../manuals.md).

## Requirements

- Python 3.10+.
- `compile` and `format` need Centroid's `mpucomp.exe` (not shipped here): it comes with CNC12, usually in `C:\cncm` (mill) or `C:\cncr` (router). The free CNC12 download from centroidcnc.com includes it.
- Linux and macOS also need Wine to run it. `format --fix --no-verify` works without a compiler but skips the safety check.
