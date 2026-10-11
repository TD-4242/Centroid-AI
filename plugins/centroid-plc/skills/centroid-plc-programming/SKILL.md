---
name: centroid-plc-programming
description: Use when writing, reading, or debugging Centroid CNC12 PLC stage-language source (.src) or M-code macro-to-PLC interaction on MPU11/ALLIN1DC or Acorn controls - stage/scan execution, IF/THEN/SET/RST syntax, resource types and I/O addressing, the SV_* system-variable catalog, operator-message encoding and plcmsg.txt, the Acorn Wizard-generated PLC, and example PLC projects. To check a .src compiles use the compile skill; to tidy its style use the format skill. Source: CNC12 PLC Programming Manual rev8 07/24/26.
---

# Centroid PLC Programming

## When to use / when not

Use this skill for PLC stage-language (`.src`) programming and macro-to-PLC interaction on
Centroid MPU11-based controls such as the ALLIN1DC, and on the Acorn: stage/scan execution and
syntax, resource types and I/O addressing, the `SV_*` system-variable catalog, operator-message
encoding, the Acorn Wizard-generated PLC program, and official example projects. The language
is the same on every current platform; boards differ only in hardware features (PLC Manual,
PDF p.11).

**Do not use this skill** for hardware wiring or Acorn Wizard configuration pages; see the
board's installation manual, e.g. for the Acorn (Acorn Install ch.5, p.35; ch.6, p.71).

## Language essentials

The PLC source file has two parts. The **definition section** (top) uses `Name IS Resource` to
bind a symbolic name to a hardware or internal resource; any definition after the first
`IF`/`THEN` is a compile-time error (PLC Manual, PDF p.17):

```
EStopOk_I IS INP11   ; PLC Manual, PDF p.17
Lube_O    IS OUT2    ; PLC Manual, PDF p.17
```

The rest of the program is `IF`/`THEN` statements, grouped under Stage lines, that runs top to
bottom every pass. A line holding only a Stage name designates the start of that Stage
(PLC Manual, PDF p.31, p.16). Logic inside a Stage (`STG`/`FSTG`) is skipped entirely while
that Stage is RST (PLC Manual, PDF p.30, p.16). Regular Stages run 50 times per second; Fast
Stages or code outside any Stage run up to 1000 times per second, provided the rest of the
program finishes in under 1ms (PLC Manual, PDF p.13, p.16). `STG1` is SET automatically at
startup (PLC Manual, PDF p.13).

Inputs and Timers are buffered for the whole pass; physical Output state is buffered too, but the
in-program image of the Outputs updates immediately, along with Memory Bits, Words, One-Shots,
Stages and System Variables, so a later line in the same pass sees an earlier line's write
(PLC Manual, PDF p.13).

Every action follows `THEN`, comma-separated: `SET`/`RST` turn a bit-type variable
unconditionally on or off, `(<bit-var>)` coils it to the condition, `<word> = <expr>` assigns a
Word or Timer, and `JMP <stage>` RSTs the current Stage and SETs another (PLC Manual, PDF
p.21-22). There is no `ELSE` keyword; the manual's stated workaround is a second line with the
condition negated by `!` (PLC Manual, PDF p.17). See [syntax.md](reference/syntax.md) for the
statement-form, operator and comment-style reference.

A macro reads PLC resource state through fixed variable ranges (for example `OUT` n at
`#(60000+n)`), and `M94`/`M95` set/reset `SV_M94_M95_1`-`128` for the PLC program to read -- see
[mpu11-allin1dc.md](reference/mpu11-allin1dc.md#macro---plc-access).

## Reference router

| Topic | Reference file |
| --- | --- |
| Statement syntax: `IF`/`THEN`, `SET`/`RST`/`JMP`, coils, Timers, operators, comments, the manual's naming and layout conventions | [reference/syntax.md](reference/syntax.md) |
| Resource types and ranges (`INP`/`OUT`/`MEM`/`STG`/`FSTG`/`T`/`PD`/`W`/`DW`/`FW`/`DFW`), MPU11/ALLIN1DC I/O, jog panel, expansion, debounce, macro<->PLC access (`#(60000+n)`, `M94`/`M95`) | [reference/mpu11-allin1dc.md](reference/mpu11-allin1dc.md) |
| Acorn, Wizard, Custom PLC: universal template, where the generated `.src` lands, Custom PLC before hand-editing, Acorn I/O, PLC Diagnostic/PLC Detective | [reference/acorn.md](reference/acorn.md) |
| An `SV_*` name, its type, direction (CNC->PLC vs. PLC->CNC), or an Appendix H-K bit table | [reference/system-variables.md](reference/system-variables.md) |
| Operator-message encoding (`value = type + 256 x msgNumber`), `plcmsg.txt` format, the manual's worked example | [reference/messages.md](reference/messages.md) |
| Official example PLC projects to crib a pattern from | [reference/examples-index.md](reference/examples-index.md) |

**Tools:** to check that a `.src` compiles, use the `compile` skill; to reformat it into one
consistent style, use the `format` skill.

## Not covered here

- Compiler Errors (PLC Manual, PDF p.52-59).
- Keywords beyond the basic statement forms above: Indexes, Range `..`, DUMP, BTW/WTB, BCD/BIN,
  BITSET/BITRST/BITTST, LSHIFT/RSHIFT, and the math functions (PLC Manual, PDF p.20-28).
- SV and data-type names cannot be used as constant or variable labels (PLC Manual, PDF p.20).
- There are no bitwise operators (PLC Manual, PDF p.21).
- Standard PLC Program Layout, the manual's section-by-section walkthrough (PLC Manual, PDF
  p.30-51).

## Manuals

This skill cites: PLC Manual (CNC12 PLC Programming Manual), Router Manual (CNC12 Router
Operators Manual), Acorn Install (Acorn Installation Manual). PLC Manual citations are PDF
pages; Router Manual and Acorn Install citations are printed pages (PDF page = printed + 1).
Exact wording is in the official PDF. When an answer needs text beyond these references, run
`python3 <plugin>/scripts/fetch_manual.py <id>` with `plc-manual`, `router-manual` or
`acorn-install` (`<plugin>` is this plugin's root directory):

- exit 0: it printed the local PDF path — read the cited page with `pdftotext -layout -f <p> -l <p> <path> -`
  if available, or open the PDF.
- exit 4: not downloaded yet. Ask the user in plain words, e.g. "This is best checked against
  Centroid's <title> (free PDF, about <sizeMB> MB). Want me to download it to
  `~/.centroid-ai/manuals/`? I can also do this automatically from now on, or never ask
  again." Yes → rerun with `--yes`. "Always" → `python3 <plugin>/scripts/centroid_config.py set manuals.autoDownload always`, then rerun. "Never" → set `never`.
  Sizes: PLC Manual about 3 MB, Router Manual about 63 MB, Acorn Install about 16 MB.
- exit 5: the user chose never to download; answer from the references and give the manual and page.
- exit 1: download failed; give the user the printed URL to download by hand.

Download links for every manual: https://github.com/TD-4242/Centroid-AI/blob/main/docs/manuals.md

## Useful resources

- PLC Diagnostic screen (virtual input/output LEDs):
  https://www.centroidcnc.com/centroid_diy/downloads/acorn_documentation/cnc12_PLC_diagnostic_screen.pdf
  (PLC Manual, PDF p.9-10)
- PLC Detective (real-time logic analyzer):
  https://www.centroidcnc.com/downloads/centroid_PLC_detective_quickstart.pdf
  (PLC Manual, PDF p.9-10)
