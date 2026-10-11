# Centroid CNC12 Operation

Operate Centroid CNC12 Mill and Router software: menus, jogging, part zero, tool offsets, running jobs, and G/M-code, parameter and message lookup.

## Install

Claude Code:

    claude plugin install centroid-cnc12-ops@centroid-ai

Codex: add the marketplace with `codex plugin marketplace add TD-4242/Centroid-AI`, then install **Centroid CNC12 Operation** from the Plugins directory. See [Installing](../installing.md).

## Skills

### `centroid-cnc12-mill-ops`

Day-to-day operation of CNC12 mill software: F1-F10 softkey menus, jogging with the operator panel, MPG or VCP, part zero (WCS), tool offsets and library, loading and running jobs, canceling and resuming, run-time graphics, power feed and the Utility menu. It does not cover the G/M-code language, Intercon, probing or configuration; it points to the Mill Manual chapters for those.

Triggers: When you ask how to do something at the mill control.

Example prompts:

- "How do I set part zero on a work coordinate system?"
- "How do I resume a job after canceling it?"
- "Where do I enter tool length offsets?"

### `centroid-cnc12-router-ops`

Operating CNC12 Router software on Acorn, AcornSix or Hickory: main screen and menus, machine home, jog panel/MPG/VCP/keyboard shortcuts, part zeros and WCS, offset and tool libraries, running jobs, the Utility menu, plus lookup of any router G-code, M-code, machine parameter or CNC12 message by number.

Triggers: When you ask how to operate the router control, or what a G/M-code, parameter or message number means.

Example prompts:

- "What does M-code M6 do on the router?"
- "What does parameter 100 control?"
- "How do I home the machine and set the Z zero?"

## Manuals

This plugin cites:

- [CNC12 Milling Machine Operators Manual](../manuals.md) (Mill Manual)
- [CNC12 Router Operators Manual](../manuals.md) (Router Manual)
- [Acorn Installation Manual](../manuals.md) (Acorn Install)
- [Acorn Axis Pairing and Squaring](../manuals.md) (Pairing Guide)
- [CNC12 PLC Programming Manual](../manuals.md) (PLC Manual)
- [VCP 2.0 Users Manual](../manuals.md) (VCP Manual)

Download links, revisions and page offsets are in [manuals.md](../manuals.md).

## Requirements

- Python 3.10+ only for the optional manual download.
