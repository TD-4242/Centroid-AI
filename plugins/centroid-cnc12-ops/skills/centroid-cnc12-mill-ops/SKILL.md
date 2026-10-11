---
name: centroid-cnc12-mill-ops
description: Use when operating Centroid CNC12 mill software: jogging axes, using the operator panel/MPG/VCP, navigating the F1–F10 softkey menus, setting part zero (WCS), managing tool offsets/library, loading and running jobs, canceling or resuming a job, run-time graphics, power feed, and the Utility menu. NOT for the G/M-code language (Mill Manual Ch 12-13), Intercon (Ch 10), probing/digitizing (Ch 8-9), or configuration/parameters/messages (Ch 15-16).
---

# Centroid CNC12 Mill Operating

## When to use / when not

Use this skill for **day-to-day operation** of Centroid **CNC12** mill software: navigating the
main-screen menus (F1–F10), jogging and operating the machine via the operator panel, MPG, or
Virtual Control Panel (VCP), setting part zeros and work coordinate systems, managing the tool
offset and tool library, and loading, running, canceling, or resuming jobs. The reference is the
official **CNC12 Milling Machine Operators Manual** (CNC12 V.5.4+) — generic across all
supported controllers (Acorn, AcornSix, Hickory, Oak, Allin1DC, MPU11, M400, M39).

**Do not use this skill for:**
- **G/M-code language** (syntax, parameters, modal groups, canned cycles) — (Mill Manual Ch 12, p.238; Ch 13, p.275)
- **Intercon** conversational programming — (Mill Manual Ch 10, p.108); **digitizing** — (Mill Manual Ch 8, p.86);
  **probing** — (Mill Manual Ch 9, p.98)
- **Software configuration**, machine parameters, or error/status messages — (Mill Manual Ch 15, p.305; Ch 16, p.430)
- **M-code macro** (`mfunc*.mac`) authoring — (Mill Manual §11.3, p.203; §13.2, p.276)
- **PLC stage-language** (`.src`) — if the centroid-plc plugin is installed,
  see `centroid-plc-programming`; otherwise (PLC Manual, PDF p.13)

## Essentials

The CNC12 main screen has five key areas:

- **DRO** — real-time axis position display with load meters (bars) beneath each axis label.
  A **Distance-to-Go** sub-display below the DRO shows remaining travel for the current move
  (toggle with **Ctrl+D**).
- **Status Window** — shows the active job filename, tool number, feed-rate override, spindle
  speed, and feed-hold state. While a job runs, also shows Part Count, Part #, and Part Time.
- **Message Window** — newest messages at the bottom; scroll with arrow keys. The lowest
  (prompt) line shows control prompts (e.g., "Press CYCLE START to start job" on power-up).
- **Options Window** — the active F-key softkey choices for the current screen. Pressing a
  function key selects that option.
- **User Window** — context-sensitive area: G-code lines during a job run; data-entry fields
  for part zeros, tool library, and digitizing/probing.

**Machine home** must be set at startup before running any job. On machines with home/limit
switches, press **CYCLE START** to auto-home (runs `c:\cncm\cncm.hom`). On machines without
switches, jog each axis to the home position manually, then press **CYCLE START**.

**F1–F10 main-screen menu map:**

| F-key | Menu | Purpose |
|---|---|---|
| **F1** | Setup | Part zeros, tool offsets, config, feed settings |
| **F2** | Load Job | Load a job file from disk |
| **F3** | MDI | Run a single G/M-code line immediately |
| **F4** | Run | Start, search, resume, and control job execution |
| **F5** | CAM | Open Intercon conversational programmer |
| **F6** | Edit | Open the current job in a G-code text editor |
| **F7** | Utility | Backup/restore, options, diagnostics, file management |
| **F8** | Graph | Graph the toolpath of the loaded program |
| **F9** | Digitize | Touch-probe digitizing (purchased option only) |
| **F10** | Shut Down | Park, power off, or exit the control software |

## Reference router

| Reference file | Use when the question is about |
|---|---|
| `reference/interface.md` | screen layout, DRO, conventions, machine home, the F1–F10 menu map |
| `reference/operator-panel.md` | jogging, MPG, spindle/coolant/feed controls, VCP, keyboard jog & shortcuts |
| `reference/part-setup.md` | part zero, WCS, coordinate-system rotation, transformed WCS |
| `reference/tool-setup.md` | offset library, tool library, tool-life management, laser setup |
| `reference/running-jobs.md` | running, canceling, resuming jobs; run-time graphics; power feed; utility menu |

## Manuals

This skill cites: Mill Manual (CNC12 Milling Machine Operators Manual), PLC Manual (CNC12 PLC
Programming Manual). Mill Manual citations, including bare `(p.N)` in the reference files, are
printed pages (PDF page = printed + 1); PLC Manual citations are PDF pages. Exact wording is in the
official PDF. When an answer needs text beyond these references, run
`python3 <plugin>/scripts/fetch_manual.py <id>` with `mill-manual` or `plc-manual` (`<plugin>` is
this plugin's root directory):

- exit 0: it printed the local PDF path — read the cited page with `pdftotext -layout -f <p> -l <p> <path> -`
  if available, or open the PDF.
- exit 4: not downloaded yet. Ask the user in plain words, e.g. "This is best checked against
  the CNC12 Milling Machine Operators Manual (free PDF, about 57 MB). Want me to download it to
  the folder it printed after `to:`? I can also do this automatically from now on, or never ask
  again." Yes → rerun with `--yes`. "Always" → `python3 <plugin>/scripts/centroid_config.py set manuals.autoDownload always`, then rerun. "Never" → set `never`.
- exit 5: the user chose never to download; answer from the references and give the manual and page.
- exit 1: download failed; give the user the printed URL to download by hand.
- exit 2: show the printed error line to the user as-is (bad settings file or unknown manual id).

On Windows, use `py -3` (or `python`) if `python3` is not found.

Download links for every manual: https://github.com/TD-4242/Centroid-AI/blob/main/docs/manuals.md

Community forum (free CNC technical support): https://centroidcncforum.com/
