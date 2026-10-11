# Centroid VCP

Customize the Centroid CNC12 Virtual Control Panel: buttons, skins, graphics, LED states and PLC-wired actions.

## Install

Claude Code:

    claude plugin install centroid-vcp@centroid-ai

Codex: add the marketplace with `codex plugin marketplace add TD-4242/Centroid-AI`, then install **Centroid VCP** from the Plugins directory. See [Installing](../installing.md).

## Skills

### `centroid-vcp`

Customizing a CNC12 Virtual Control Panel: moving, creating and deleting buttons; button XML/SVG and graphics; LED colors and image swaps; logos, borders, backgrounds and hover/touch effects; wiring a button to a skin event, macro, app or PLC bit; big buttons and live PLC-word displays; and diagnosing a VCP that will not load.

Triggers: When you ask to change or debug a VCP layout, button or LED.

Example prompts:

- "Move the Cycle Start button to the right column."
- "Make a button light up green when a PLC bit is on."
- "My VCP will not load after I edited a button - why?"

## Manuals

This plugin cites:

- [VCP 2.0 Users Manual](../manuals.md) (VCP Manual)
- [Acorn Installation Manual](../manuals.md) (Acorn Install)
- [CNC12 PLC Programming Manual](../manuals.md) (PLC Manual)

Download links, revisions and page offsets are in [manuals.md](../manuals.md).

## Requirements

- Python 3.10+ only for the optional manual download.
