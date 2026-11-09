# Centroid API

Build your own C# or VB.NET app against a running Centroid CNC12 with CentroidAPI.dll: connecting, return codes, machine state, PLC I/O and skinning data, jobs, tools, parameters and inbound messages.

This plugin is for people writing software. If you only operate, configure or program the PLC of a
CNC12 control, you do not need it.

## Install

Claude Code:

    claude plugin install centroid-api@centroid-ai

Codex: add the marketplace with `codex plugin marketplace add TD-4242/Centroid-AI`, then install **Centroid API** from the Plugins directory. See [Installing](../installing.md).

## Skills

### `centroid-cnc12-api`

Writing, reading or debugging an application that talks to a running CNC12 through `CentroidAPI.dll`
(the Centroid API, formerly the Skinning API): connecting a `CNCPipe`, return codes, polling rates
and the five-pipe limit, machine state and positions, PLC inputs/outputs and watch lists, skinning
data words and skin events, loading and running jobs, the tool library, machine parameters and
system variables, inbound CNC12 messages and M0/M200 prompts, drop-in WPF controls, axis
configuration and board/license info.

Triggers: When you ask to write or fix code that uses `CentroidAPI.dll` or a `CNCPipe`.

Example prompts:

- "Write a C# WPF window that shows the X, Y and Z machine position from CNC12."
- "Why does my CentroidAPI call return ERROR_CLIENT_LOCKED?"
- "Send a value from my app to the PLC and read it in the PLC program."

## Sources

The API is documented as web pages, not a PDF, so there is nothing to download:

- Centroid API reference: https://centroidcnc.com/CentroidAPI/ (also installed with CNC12 in
  `CentroidAPIDocumentation`)
- Centroid's CNC App API page: https://www.centroidcnc.com/cnc_app_api.html
- Centroid's example apps: https://github.com/CentroidCNC/CentroidAPI_CSharp_PowerFeed and
  https://github.com/CentroidCNC/CentroidAPI_VBnet_PowerFeed

## Requirements

- To build apps: Windows 10 or 11 (64-bit), Visual Studio, and CNC12 installed (Offline or Standard).
- None for the skill itself.
