# Centroid ALLIN1DC

Install, wire, commission and tune a Centroid ALLIN1DC (MPU11) servo controller.

## Install

Claude Code:

    claude plugin install centroid-allin1dc@centroid-ai

Codex: add the marketplace with `codex plugin marketplace add TD-4242/Centroid-AI`, then install **Centroid ALLIN1DC** from the Plugins directory. See [Installing](../installing.md).

## Skills

### `centroid-allin1dc-install`

Installing and commissioning a Centroid ALLIN1DC (MPU11): board hardware, I/O and LED states, cabinet wiring (input voltage, VM/rectifier, E-stop, servo motors, current limiting, limits, lube/coolant/spindle), CNC12 install and bench test, commissioning (encoder, motor and spindle setup, DRO calibration, homing, feedrate and acceleration tuning, backlash, travel limits), recommended servo PID, current and heating parameters, and troubleshooting.

Triggers: When you wire, commission, tune or troubleshoot an ALLIN1DC.

Example prompts:

- "What do the status LEDs on the ALLIN1DC mean?"
- "How do I calibrate the DRO for a servo axis?"
- "My axis faults on following error - how do I tune the PID?"

## Manuals

This plugin cites:

- [ALLIN1DC Installation Manual](../manuals.md) (ALLIN1DC Install)
- [CNC12 PLC Programming Manual](../manuals.md) (PLC Manual)

Download links, revisions and page offsets are in [manuals.md](../manuals.md).

## Requirements

- Python 3.10+ only for the optional manual download.
