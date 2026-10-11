# Acorn: Wizard-Generated PLC and I/O

Sources: CNC12 PLC Programming Manual rev8 07/24/26 (PLC Manual), cited by PDF page number;
Acorn Installation Manual (Acorn Install) and CNC12 Router Operators Manual (Router Manual),
cited by printed page (PDF page = printed + 1).

---

## Same language, Wizard-generated program

Centroid's PLC programming language is the same across all current platforms — Oak, Allin1DC,
MPU11, Acorn, AcornSix and Hickory — with differences between them coming only from the board's
hardware feature set, not the language itself (PLC Manual, PDF p.11).

Acorn and AcornSix CNC12 use a control-configuration Wizard that creates the PLC program for the
control based on the Input/Output selections made in the Wizard's input and output menus. The
Wizard builds a "custom" PLC program by drag-and-drop assigning a list of canned PLC functions to
inputs and outputs, using the user's selections (PLC Manual, PDF p.6-8).

## Files

The Acorn Wizard uses a Universal Template PLC source program to build the custom Acorn PLC
program. The manual gives the template's path as:

```
cncm\resources\wizard\default\plc\acorn_universal_template.src
```

(PLC Manual, PDF p.8)

Source code for the Wizard-generated PLC program appears in the root `cncm` or `cnct` directory,
for example `acorn_mill_plc.src` (PLC Manual, PDF p.8). The manual shows only the mill example,
with the mill's `cncm` directory prefix; it does not show a router example. CNC12 Router's
install directory is `c:\cncr` (Router Manual §1.8, p.13), not `c:\cncm` — no manual page gives
the router-specific generated-PLC filename or confirms whether `cnct` applies to it, so none is
stated here.

## Custom PLC: hand-editing safely

Before hand-editing an Acorn PLC program, turn off the Wizard's automatic PLC program generation
so the Wizard does not overwrite the edit. The "Custom PLC" in-use setting is in the Wizard
Preferences menu (PLC Manual, PDF p.8); selecting it tells the Wizard not to overwrite a custom
PLC program (Acorn Install §6.19, p.98).

Before editing, make a `report.zip` ("create report" in the CNC12 utility menu) and keep a copy
in case the change needs to be reverted (PLC Manual, PDF p.11). Compile an edited source with
`mpucomp.exe ProgramName.src mpu.plc`; the output file must be named exactly `mpu.plc`
(lowercase), which is the name CNC software looks for and loads (PLC Manual, PDF p.11). After a
successful compile, power the system off completely and back on for the change to take full
effect (PLC Manual, PDF p.12). To compile-check a `.src` without loading it, use the `compile`
skill.

## Acorn I/O

The Acorn has 8 physical inputs. They are sourcing 24VDC: the Acorn supplies +24VDC at the input
pin, and an external switch or sensor must sink it to `COM` to activate it — the "contact
closure to ground (COM)" method (Acorn Install §5.2, p.44). The Acorn has 8 relay outputs; each
output toggles one SPDT relay (Acorn Install §5.3, p.45).

> App D describes the same outputs differently: 8 open-collector drivers normally drive an
> external 8-relay board over ribbon cable (Acorn Install App D, p.126). Its I/O map lists these
> as the `H10` outputs, with output type `Open Collector`, not relay (Acorn Install App D, p.129).

The PLC Manual's own I/O appendix (App E) documents ALLIN1DC, DC3IOB, GPIO4D and PLC-expansion
I/O ranges but has no Acorn entry (PLC Manual, PDF p.121-123). No manual page states which
`INPn`/`OUTn` a given Acorn screw terminal maps to: the Acorn Wizard assigns the PLC `INP`/`OUT`
number for each function from the choices made in its input and output menus, rather than using
a fixed table (PLC Manual, PDF p.6). Resource types and their ranges are the same as on every
board — see [mpu11-allin1dc.md](mpu11-allin1dc.md#resource-types).

## Tools

- **PLC Diagnostic screen** (virtual input/output LEDs):
  `https://www.centroidcnc.com/centroid_diy/downloads/acorn_documentation/cnc12_PLC_diagnostic_screen.pdf`
  (PLC Manual, PDF p.9-10)
- **PLC Detective** (real-time logic analyzer):
  `https://www.centroidcnc.com/downloads/centroid_PLC_detective_quickstart.pdf`
  (PLC Manual, PDF p.9-10)

## Board identification

`SV_DRIVE_TYPE_x` (1-8) / `SV_?_AXIS_DRIVE_TYPE` reports the type of drive connected to each
axis — see the
[Axis validity, drive status, and power](system-variables.md#axis-validity-drive-status-and-power)
row for its values, including `13 = ACORN` and `24 = ACORNSIX` (PLC Manual, PDF p.110).

[Appendix H](system-variables.md#appendix-h-cyclone--mcu-status-sv-information)'s
`SV_PC_CYCLONE_STATUS_x` bit tables print columns for MPU13 (Hickory), MPU12 (AcornSix) and
MPU11 (MPU11, ALLIN1DC, OAK) — there is no column for the original Acorn (PLC Manual, PDF p.128).
