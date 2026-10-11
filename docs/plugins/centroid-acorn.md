# Centroid Acorn

Install, wire, configure and troubleshoot a Centroid Acorn controller, including the Acorn Wizard and axis pairing and squaring.

## Install

Claude Code:

    claude plugin install centroid-acorn@centroid-ai

Codex: add the marketplace with `codex plugin marketplace add TD-4242/Centroid-AI`, then install **Centroid Acorn** from the Plugins directory. See [Installing](../installing.md).

## Skills

### `centroid-acorn-install`

Installing and commissioning a Centroid Acorn: kit and board I/O, LEDs, bench test, Windows/CNC12 install and license, cabinet wiring (inputs, outputs, E-stop, step/dir drives, home and limit switches, spindle), every Acorn Wizard page including Custom PLC, software and hardware axis pairing with auto-squaring, motion tuning, backlash, travel limits, and symptom-to-fix troubleshooting.

Triggers: When you wire, configure or troubleshoot an Acorn machine.

Example prompts:

- "How do I wire an E-stop to the Acorn?"
- "Walk me through the Wizard page for homing."
- "My paired gantry axes will not square - what should I check?"

## Manuals

This plugin cites:

- [Acorn Installation Manual](../manuals.md) (Acorn Install)
- [Acorn Axis Pairing and Squaring](../manuals.md) (Pairing Guide)
- [CNC12 PLC Programming Manual](../manuals.md) (PLC Manual)
- [CNC12 Router Operators Manual](../manuals.md) (Router Manual)

Download links, revisions and page offsets are in [manuals.md](../manuals.md).

## Requirements

- Python 3.10+ only for the optional manual download.
