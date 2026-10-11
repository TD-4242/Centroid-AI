# TECO F510 VFD

Set up, wire, tune and troubleshoot a TECO-Westinghouse F510 VFD driving a CNC spindle.

## Install

Claude Code:

    claude plugin install teco-f510@centroid-ai

Codex: add the marketplace with `codex plugin marketplace add TD-4242/Centroid-AI`, then install **TECO F510 VFD** from the Plugins directory. See [Installing](../installing.md).

## Skills

### `teco-f510`

The TECO-Westinghouse F510 variable-frequency drive as a CNC spindle: control modes (V/F, SLV, PM SLV), the 24 parameter groups and key spindle parameters, RS-485 Modbus config download and upload, motor nameplate entry and auto-tuning, accel/decel and S-curve, braking resistor and over-voltage prevention, power, control and RS-485 terminals, and fault codes.

Triggers: When you set up, tune, back up or troubleshoot an F510 drive.

Example prompts:

- "What parameters do I set for a 3 HP spindle motor?"
- "The drive shows an OV fault on decel - what do I change?"
- "How do I back up the F510 parameters over RS-485?"

## Manuals

This plugin cites:

- [F510 Instruction Manual](../manuals.md) (F510 Manual)
- [ALLIN1DC Installation Manual](../manuals.md) (ALLIN1DC Install)
- [CNC12 PLC Programming Manual](../manuals.md) (PLC Manual)

Download links, revisions and page offsets are in [manuals.md](../manuals.md).

## Requirements

- Python 3.10+ only for the optional manual download.
