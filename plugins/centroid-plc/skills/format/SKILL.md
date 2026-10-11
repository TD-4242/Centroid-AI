---
name: format
description: Use when the user wants to tidy or reformat a Centroid CNC12 PLC .src file into one consistent style (aligned "Name IS Resource" definitions, keyword case, comment spacing, continuation alignment), or check whether it needs reformatting. Applies changes only after proving the compiled program is unchanged.
---

# Format a Centroid PLC program

This runs on the user's own computer and checks its work with Centroid's compiler, so it needs
that computer, with CNC12 (or a copy of `mpucomp.exe`) on it. In a chat app (Claude web or Desktop
chat, or ChatGPT) say so plainly and suggest running it in Claude Code (including the Claude
Desktop app's Code tab) or Codex on that computer.

On Windows, use `py -3` (or `python`) if `python3` is not found.

1. Check first: `python3 <plugin>/scripts/plcfmt.py <file.src>` (`<plugin>` is this plugin's
   root). Exit 1 prints the diff it would make; exit 0 means already formatted. Naming findings
   on stderr are advice only and are never auto-changed.
2. Show the user a summary of the diff and ask before applying.
3. Apply: `python3 <plugin>/scripts/plcfmt.py --fix <file.src>`. It compiles before and after
   and keeps the change only if the compiled program is identical; otherwise it restores the
   original and exits 2.

Exit 3 and the compiler-not-found message work exactly as in the `compile` skill: ask before
using a compiler found in this project or a CNC12 folder, run `centroid_config.py trust <path>`
once they approve and rerun, and help a user who doesn't know what `mpucomp.exe` is.

**No compiler available:** offer `--fix --no-verify` only after telling the user the change
will not be checked against the compiled program, and only if they agree.

**Acorn Wizard warning on stderr:** tell the user the Acorn Wizard regenerates this file unless
its Custom PLC preference is set (see the Acorn section of `centroid-plc-programming`), so
formatting it may be pointless. Continue only if they want to.

Files must be ASCII with CRLF line endings, as CNC12 writes them; the script reports otherwise.
