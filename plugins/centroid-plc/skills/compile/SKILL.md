---
name: compile
description: Use when the user wants to check that a Centroid CNC12 PLC program (.src) compiles - "compile my PLC", "check the .src for errors", before loading a PLC on the machine, or after editing PLC source. Runs Centroid's mpucomp.exe compiler and reports errors and warnings. Does not load anything onto the machine.
---

# Compile-check a Centroid PLC program

Run `python3 <plugin>/scripts/plc_compile.py <file.src>` where `<plugin>` is this plugin's root
(the directory two levels above this file). Add `-v` to list every warning, `-o out.plc` to keep
the compiled program. If the user did not name a file, look for `*.src` in the project; if
there are several, ask which one. On Windows, use `py -3` (or `python`) if `python3` is not found.

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
