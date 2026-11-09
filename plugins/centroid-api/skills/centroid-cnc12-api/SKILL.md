---
name: centroid-cnc12-api
description: "Use when writing, reading or debugging a C# or VB.NET application that talks to a running Centroid CNC12 through CentroidAPI.dll (the Centroid API, formerly the Skinning API) - connecting a CNCPipe, return codes, polling rates and the five-pipe limit, reading DRO, state and WCS, PLC inputs/outputs and watch lists, skinning data words and skin events, loading and running jobs, the tool library, machine parameters and system variables, inbound CNC12 messages and M0/M200 prompts, drop-in user controls, axis configuration and board/license info. Generic to CNC12 on Acorn, AcornSix, Hickory, Oak and Allin1DC. Source: Centroid API reference 1.0.0, Centroid's API page and its example apps."
---

# Centroid CNC12 API (CentroidAPI.dll)

## When to use / when not

Use this skill to **build your own application against CNC12** with the Centroid API: a custom
operator screen, a power-feed or probing helper, a status display, or a bridge to other software.
The API, formerly the Skinning API, builds custom CNC applications on any of Centroid's control
boards (Allin1DC, Oak, Hickory, Acorn and AcornSix), running alongside CNC12 or replacing its UI
(App API page). The CNC12 VCP, Wizards and PLC Diagnostic Tool are API instances too
(App API page).

**Do not use this skill** for the PLC logic that *reads* what an app sends - skinning data words
and skin events as `SV_*` system variables:
if the centroid-plc plugin is installed, see `centroid-plc-programming`; otherwise (PLC Manual, PDF p.106, p.110).

**Do not use this skill** for editing the Virtual Control Panel's skin and button files:
if the centroid-vcp plugin is installed, see `centroid-vcp`; otherwise (VCP Manual p.36).

**Do not use this skill** for operating CNC12 or for G/M-code meaning - only for calling it from code.

## Essentials

### What it is

The API is not network-based: it works entirely through method calls exposed by a DLL, relies on
return codes rather than exceptions, and its calls are synchronous (App API page). Only VB.NET and
C# are officially supported, in Console, WinForms and WPF projects (App API page). The API is free;
a CNC12 "Pro" license is the recommended minimum to use it effectively (App API page).

Requirements (App API page): CNC12 installed (Offline or Standard), Visual Studio, and a 64-bit
Windows 10 or 11 development PC. A Centroid control board is optional but recommended; the
**Offline install is limited - no jogging or `skin_event` calls** - and fits basic development
and testing only.

### Connect

Reference `CentroidAPI.dll` from the root of the CNC12 install (`c:\cncm` for mill) and add
`using CentroidAPI;` (API Ref, Getting Started). One `CNCPipe` is one API connection; its
sub-objects (`axis`, `dro`, `state`, `plc`, `job`, `tool`, ...) carry the calls
(API Ref, CNCPipe). Centroid's own example asks the user on every failed attempt - Yes rebuilds the
pipe, No exits - so the loop waits on the dialog rather than spinning
(API Ref, Axis Data example):

```csharp
cnc12_pipe = new CNCPipe();
while (!cnc12_pipe.IsConstructed())
{
    MessageBoxResult selection = MessageBox.Show(messageBoxText, messageBoxTitle, messageBoxType);
    switch (selection)
    {
        case MessageBoxResult.Yes: cnc12_pipe = new CNCPipe(); break;
        case MessageBoxResult.No:  Environment.Exit(0);        break;
    }
}
returnCode = cnc12_pipe.axis.GetLabel(CNCPipe.Axes.AXIS_1, out char label);
```

Each `new CNCPipe()` waits up to its `timeout` seconds, 1 by default (API Ref, CNCPipe).

CNC12 must be running and finished initializing before the pipe connects (API Ref, Axis Data
example). Reconnecting after CNC12 restarts is in
[connection-and-setup.md](reference/connection-and-setup.md).

### Rules every app follows

- **Check the `ReturnCode` before using an `out` value.** Almost every call returns
  `CNCPipe.ReturnCode`. `SUCCESS` means no errors occurred; `ERROR_EXPERIMENTAL_FEATURE` also
  indicates success but makes no guarantee the call keeps working that way (API Ref, CNCPipe). All
  31 codes are in [connection-and-setup.md](reference/connection-and-setup.md#return-codes).
- **Poll at 10-50 ms** for real-time data (DRO, I/O, machine status) and **50-500 ms** for basic
  status; rates faster than 10 ms are not recommended (App API page).
- **Budget the five pipes.** CNC12 allows up to 5 simultaneous `CNCPipe` instances, shared with the
  VCP, Wizards, PLC Diagnostic Tool and user apps; calls block, so a single thread is recommended
  (App API page).
- **Read many bits with a watch list.** `SetWatchList` once, then `GetWatchList`, is the recommended
  way to read multiple I/O and memory bits (App API page);
  see [plc-and-io.md](reference/plc-and-io.md#watch-lists).

### It can move the machine

Calls such as `job.RunCommand`, `plc.SetSkinEventState` and `plc.SetIoForceState` act on the
machine. Centroid's example app warns that it moves the X axis and that your machine may move if
you develop on the PC connected to the control board (PowerFeed example, README), and its
skin-event cycle-start helper is labeled "Use with Caution. Operators should have to press cycle
start to begin machine motion." (PowerFeed example, PipeManager.cs).

## API map

| Sub-object | What it does | Reference |
| --- | --- | --- |
| `CNCPipe` itself | Construct, connect, return codes, events, build revisions | [connection-and-setup.md](reference/connection-and-setup.md) |
| `state`, `dro`, `wcs`, `csr`, `screen` | Machine status, positions, active G-codes, feedrate and spindle, part zeros, CSR angles | [machine-state.md](reference/machine-state.md) |
| `plc` | Inputs, outputs, memory bits, watch lists, PLC words, skinning data words, skin events, forcing | [plc-and-io.md](reference/plc-and-io.md) |
| `job`, `tool`, `parameter` | Load and run jobs and commands, tool library, machine parameters and system variables | [jobs-tools-parameters.md](reference/jobs-tools-parameters.md) |
| `inbound_communications`, `message_window` | Messages pushed from CNC12, answering M0/M200-style prompts, the message window, drop-in WPF user controls | [events-and-ui.md](reference/events-and-ui.md) |
| `axis`, `system` | Axis motor and jog configuration, board type, license, expansion devices, reports | [axis-and-system.md](reference/axis-and-system.md) |

Each C# class has a `VB_` twin (`VB_Axis`, `VB_Plc`, `VB_State`, ...) described as the Visual Basic
version of the same class (API Ref, CNCPipe).

## Reference router

| Reference file | Look here when... |
| --- | --- |
| [reference/connection-and-setup.md](reference/connection-and-setup.md) | Starting a project, referencing the DLL, connecting and reconnecting, decoding a return code, checking which CNC12 version added a call, deprecated calls, or using the community Python wrapper |
| [reference/machine-state.md](reference/machine-state.md) | Reading positions, feedrate, spindle speed, active G-codes, the running line, MDI and feed-hold state, units, or getting and setting part zeros and CSR angles |
| [reference/plc-and-io.md](reference/plc-and-io.md) | Reading or forcing PLC bits, watching many bits, reading PLC words, sending values to the PLC through skinning data words, pressing a skin event, or reading USB-BOB inputs |
| [reference/jobs-tools-parameters.md](reference/jobs-tools-parameters.md) | Loading or running a job or G-code line, cancelling or continuing, part counts, the tool library, machine parameters, or `#` system variables |
| [reference/events-and-ui.md](reference/events-and-ui.md) | Reacting to messages CNC12 pushes (DRO updates, job info, shutdown, M2xx prompts), writing to the message window, or using the DRO/G-code user controls |
| [reference/axis-and-system.md](reference/axis-and-system.md) | Reading or changing axis motor, jog, limit and scale settings, or getting board type, serial number, license and plugin unlocks, expansion devices, or creating a report |

## Sources

This skill cites:

- **API Ref** - Centroid API 1.0.0 reference, "Centroid API for C# and VB.Net":
  https://centroidcnc.com/CentroidAPI/ . Cited by class or page, e.g. `(API Ref, CNCPipe.Plc)`.
  The same documentation ships with every CNC12 install in a `CentroidAPIDocumentation` folder -
  `c:\cncm\CentroidAPIDocumentation` for mill, `c:\cncr\CentroidAPIDocumentation` for router
  (App API page). **When working on a control PC, prefer the installed copy: it matches the
  installed CNC12 version.**
- **App API page** - Centroid's "CNC App API" FAQ: https://www.centroidcnc.com/cnc_app_api.html
- **PowerFeed example** - Centroid's C# example app:
  https://github.com/CentroidCNC/CentroidAPI_CSharp_PowerFeed (VB.NET twin:
  https://github.com/CentroidCNC/CentroidAPI_VBnet_PowerFeed).
- **fca1 wrapper** - the community Python wrapper the App API page names, cited only for its own
  claims and labeled unofficial: https://github.com/fca1/cnc_centroid_skinning

The API reference is web pages, not a PDF; there is nothing to download for it. If a page is not
reachable, give the user the URL above. The two manuals this skill also cites are under Manuals.

## Useful resources

From the App API page:

- Centroid API Technical Support Forum, the primary source of API support:
  https://centroidcncforum.com/viewforum.php?f=72
- CNC12 software downloads: https://centroidcnc.com/centroid_diy/centroid_cnc_software_downloads.html
- Visual Studio editions: https://visualstudio.microsoft.com/vs/compare/
- CNC PC requirements: https://centroidcnc.com/cnc_pc_performance_requirements.html

## Manuals

Besides its web sources, this skill cites: PLC Manual (CNC12 PLC Programming Manual) and VCP Manual
(VCP 2.0 Users Manual), for the PLC and VCP side of skinning data words and skin events. PLC Manual
citations are PDF pages; VCP Manual citations are printed pages, which equal PDF pages. Exact wording is in the official PDF. When an answer needs text beyond these
references, run `python3 <plugin>/scripts/fetch_manual.py <id>` with `plc-manual` or
`vcp-manual` (`<plugin>` is this plugin's root directory):

- exit 0: it printed the local PDF path — read the cited page with `pdftotext -layout -f <p> -l <p> <path> -`
  if available, or open the PDF.
- exit 4: not downloaded yet. Ask the user in plain words, e.g. "This is best checked against
  the CNC12 PLC Programming Manual (free PDF, about 3 MB). Want me to download it to
  the folder it printed after `to:`? I can also do this automatically from now on, or never ask
  again." Yes → rerun with `--yes`. "Always" → `python3 <plugin>/scripts/centroid_config.py set manuals.autoDownload always`, then rerun. "Never" → set `never`.
- exit 5: the user chose never to download; answer from the references and give the manual and page.
- exit 1: download failed; give the user the printed URL to download by hand.
- exit 2: show the printed error line to the user as-is (bad settings file or unknown manual id).

If you can't run Python here (for example in ChatGPT or Claude web chat), don't run the script:
give the user the manual's link from the download-links page named below, or ask them to upload
the PDF and read the cited page from it.

On Windows, use `py -3` (or `python`) if `python3` is not found.

Download links for every manual: https://github.com/TD-4242/Centroid-AI/blob/main/docs/manuals.md
