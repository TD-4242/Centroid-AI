# Resources, MPU11/ALLIN1DC I/O and Macro Access

Sources: CNC12 PLC Programming Manual rev8 07/24/26 (PLC Manual), cited by PDF page number;
CNC12 Router Operators Manual (Router Manual), cited by printed page (PDF page = printed + 1).

The resource types, System Variable rules and macro access below apply to every board; the I/O
sections are specific to MPU11-based controls such as the ALLIN1DC. Acorn I/O is in
[acorn.md](acorn.md#acorn-io).

---

## Resource Types

The `IS` keyword in the definition section binds a symbolic name to a hardware or internal
resource, given by its resource type and instance number. Every type has a fixed range
(PLC Manual, PDF p.13):

| Keyword | Type | Instance range | Notes |
|---------|------|----------------|-------|
| `INP` | Physical input bit | `INP1`-`INP1312` | Buffered at the start of each pass; the same value reads throughout the pass. |
| `OUT` | Physical output bit | `OUT1`-`OUT1312` | The in-program image updates immediately; a later line in the same pass sees the value an earlier line wrote. |
| `MEM` | Internal memory bit | `MEM1`-`MEM1024` | Not wired to hardware; updates immediately, like Outputs. |
| `STG` | Stage bit | `STG1`-`STG256` | `STG1` is SET at startup. Logic inside a Stage is skipped entirely while that Stage is RST (PLC Manual, PDF p.16). |
| `FSTG` | Fast stage bit | `FSTG1`-`FSTG256` | Behaves like `STG` but runs up to 1000 times/s instead of 50, provided the rest of the program finishes under 1ms (PLC Manual, PDF p.16). |
| `T` | Timer | `T1`-`T128` | `T1`-`T64` before CNC12 v4.22. Counts up in milliseconds to the stored value, then evaluates true until RST (PLC Manual, PDF p.15). Buffered at the start of the pass like Inputs. |
| `PD` | One-shot (positive differential) | `PD1`-`PD256` | SET on the coil line's rising edge; the same line's condition must go false to RST it before it can trigger again (PLC Manual, PDF p.15). |
| `W` | 32-bit signed integer word | `W1`-`W128` | `W1`-`W88` "available for PLC Detective and G-code variables". |
| `DW` | 64-bit signed integer | `DW1`-`DW128` | `DW1`-`DW22` available for PLC Detective and G-code variables. |
| `FW` | 32-bit floating-point word | `FW1`-`FW128` | `FW1`-`FW44` available for PLC Detective and G-code variables[^fw-typo]. |
| `DFW` | 64-bit floating-point word | `DFW1`-`DFW128` | `DFW1`-`DFW22` available for PLC Detective and G-code variables. |

[^fw-typo]: PDF p.13 prints this range as `FW1-FDW44`, an evident typo; the Router Manual's
    macro-variable table (§11.2.16, p.205, `98001-98044 FW1-FW44`) gives `FW1`-`FW44`.

Manual examples of the addressing form (PLC Manual, PDF p.14, p.17); the statement form is in
[syntax.md](syntax.md#1-definition--name-is-resource):

```
EStopOk_I    IS INP11   ; PLC Manual, PDF p.17
Lube_O       IS OUT2    ; PLC Manual, PDF p.17
Error_Code_W IS W10     ; PLC Manual, PDF p.14
Aux10Key_I   IS JPI18   ; PLC Manual, PDF p.14
```

## ALLIN1DC I/O

- The ALLIN1DC has 16 inputs and 9 outputs usable in the PLC program; its MPG header adds 14
  inputs and 3 outputs usable as general I/O in a customized program, though a PLC1616ADD card
  is typically the better choice (PLC Manual, PDF p.121).
- Inputs 1-6 are dedicated to limit switches: inputs 1-2 belong to axis 1, 3-4 to axis 2, 5-6
  to axis 3. The drive firmware stops motion in the tripped direction regardless of CNC software
  limit-switch setup (PLC Manual, PDF p.121). The example program names them
  `Ax1_MinusLimitOk` (`INP1`) through `Ax3_PlusLimitOk` (`INP6`) (PLC Manual, PDF p.65-66).
- Each ALLIN1DC reserves 16 inputs and 16 outputs, but only 16 inputs and 9 outputs are
  accessible through hardware, so outputs 10-16 are not accessible through hardware. All 16
  inputs can be configured in banks of 4 for 5, 12 or 24VDC, sourcing or sinking. A PLCADD1616
  expansion board's inputs begin at input 17 (PLC Manual, PDF p.64-67, p.121).
- Outputs 1-7 are SPST relays and outputs 8-9 are SPDT relays (PLC Manual, PDF p.64).
- The single 12-bit analog input is mapped to `INP241`-`INP252`, LSB = `INP241`, configurable
  for 0-5V, 0-10V, -5 to +5V or -10 to +10V (PLC Manual, PDF p.64).
- The 12-bit 0-10VDC analog output is mapped to `OUT241`-`OUT252`. `SV_PC_DAC_SPINDLE_SPEED` is
  a 16-bit value (0-65535) that the PLC must convert to the 12-bit range 0-4095
  (PLC Manual, PDF p.65, p.67).

The manual refers to the ALLIN1DC installation manual for the schematic and I/O map (PLC
Manual, PDF p.121).

## MPU11 onboard I/O

`INP769`-`INP784` are the MPU11 onboard inputs, generally used for MPG and probing (PLC Manual,
PDF p.31, p.66). The example program's header lists 4 high-speed inputs `INP769`-`INP772` for
probe/TT1 functions, 3 auxiliary inputs `INP784`-`INP786`, 11 inputs for MPG increment and axis
selection, and 2 auxiliary outputs `OUT770`-`OUT771` (PLC Manual, PDF p.64). Its definitions
(PLC Manual, PDF p.66-67):

```
MechanicalProbe       IS INP769
DSPProbe              IS INP770
ProbeDetect           IS INP771
ProbeAux              IS INP772
MPG_Inc_X_1           IS INP773    ; INP774 = x10, INP775 = x100
MPG_AXIS_1            IS INP776    ; through MPG_AXIS_8 IS INP783
MPG_LED_OUT           IS OUT769
```

## Jog panel I/O

`JPI1`-`JPI256` and `JPO1`-`JPO256` are shorthand for `INP1057`-`INP1312` and
`OUT1057`-`OUT1312`; Appendix B maps each jog-panel key and LED, e.g. Spindle Auto/Man is
`JPI2`/`INP1058` and `JPO2`/`OUT1058` (PLC Manual, PDF p.99).

## PLC expansion

miniPLC expansion boards add I/O in slots of 16: a slot's first I/O number is slot x 16 + 1 and
its last is 15 higher. There are 16 debounceable and 32 non-debounceable slots, numbered 0-47. On
the ALLIN1DC, expansion starts at slots 1 and 16, because the onboard I/O fills the first slot
of each kind. After powering on with the boards attached, `mpu_info.txt` in the `cncm` or `cnct`
directory lists the I/O ranges and the board each belongs to. Plug miniPLC devices in only with
the drive powered off (PLC Manual, PDF p.122).

## Debounce and inversion

PLC inputs are debounced 1.5 ms and jog-panel inputs 18 ms by default; no inputs are inverted
by default. Custom debounce values must be set on every MPU11 boot, so `InitialStage` is the
usual place. Use Debounce Time 2 or greater for a custom time: Time 1 is the default for most
inputs and Time 0 is fixed at 0. Input 770 (DSP probe) defaults to 0 and must not be changed
(PLC Manual, PDF p.44).

| System Variables | Scan rate | Applies to |
|---|---|---|
| `SV_PLC_DEBOUNCE_1`-`_64` | 62.5 µs | PLC inputs |
| `SV_JOG_LINK_DEBOUNCE_1`-`_32` | 750 µs | Jog panel inputs |
| `SV_LOCAL_DEBOUNCE_1`-`_13` | 62.5 µs | MPU11 onboard inputs |

(PLC Manual, PDF p.44)

## Bus checking

MPU11 systems use a DriveBus (fibers 4 and 5, or Drive Communication wiring) for motor control
and a PLCBus (fibers 1 and 3) for I/O. The ALLIN1DC has an MPU11 on board, so it shows no fiber
connections, but both buses are still used and should be checked; a few checks per second from
a Timer-triggered Stage is enough (PLC Manual, PDF p.34). A PLC executor fault
(`SV_PLC_FAULT_STATUS`) can only be reset by rebooting the MPU11 (PLC Manual, PDF p.33).

## System Variables (SV)

System Variables are predefined `SV_` names, not numbered like `INP`/`OUT`. Appendix D splits
them into two write-direction tables:

- **CNC Software Write-Controlled, 1-bit Boolean System Variables (CNC → PLC)** — includes the
  128 bits `SV_M94_M95_1`-`SV_M94_M95_128` that `M94`/`M95` set and reset from G/M-code programs
  (PLC Manual, PDF p.104).
- **PLC Write-Controlled, 1-bit boolean system variables (PLC → CNC)** (PLC Manual, PDF p.113).

> The name does not reliably signal direction: `SV_PLC_BUS_ONLINE` and `SV_PLC_IO2_ONLINE` are
> both CNC-written despite the `SV_PLC_` prefix, and are listed in the CNC → PLC table (PLC
> Manual, PDF p.104). Direction is determined by which Appendix D table an SV is listed in.

The full catalog is [system-variables.md](system-variables.md).

## Naming-suffix convention

The manual suggests `SCREAMING_SNAKE_CASE` ending `_C` for Constants and `PascalCase` with a
type suffix for resources: `_I`, `_O`, `_M`, `_W`, `_DW`, `_FW`, `_DFW`, `_T`, `_PD`, `Stage`
or `_STG`, `_FSTG`. It is a suggestion, not a compiler rule: "Whether you put an underscore
between the name and type... is up to you" (PLC Manual, PDF p.30). The full table is in
[syntax.md](syntax.md#programming-conventions).

## Macro <-> PLC Access

### Reading PLC resource state from a macro

A macro reads PLC resource state through fixed variable ranges; all are read-only from a macro
(Router Manual §11.2.16, p.205):

| PLC resource | Macro variable range | Formula |
|---|---|---|
| `INP` 1-1312 | `#50001`-`#51312` | `#(50000+n)` |
| `OUT` 1-1312 | `#60001`-`#61312` | `#(60000+n)` |
| `MEM` 1-1024 | `#70001`-`#71024` | `#(70000+n)` |
| `T` 1-128 status bit | `#90001`-`#90128` | `#(90000+n)` |
| `STG` 1-256 status bit | `#93001`-`#93256` | `#(93000+n)` |
| `FSTG` 1-256 status bit | `#94001`-`#94256` | `#(94000+n)` |
| `W` 1-88 | `#96001`-`#96088` | `#(96000+n)` |
| `DW` 1-22 | `#97001`-`#97022` | `#(97000+n)` |
| `FW` 1-44 | `#98001`-`#98044` | `#(98000+n)` |
| `DFW` 1-22 | `#99001`-`#99022` | `#(99000+n)` |

(Router Manual §11.2.16, p.205)

### Triggering PLC actions with M94/M95

`M94 /n` sets, and `M95 /n` resets, one of 128 system-variable bits `SV_M94_M95_1`-
`SV_M94_M95_128` that the PLC program reads (Router Manual §13.28, p.290). Multiple bits can be
listed on one line, e.g. `M94 /5/6` (Router Manual §13.28, p.290). Requests 1-5, 15 and 16 are
controlled by the default actions of M3, M4, M5, M6, M7, M8, M9, M10, M11 and M39; overriding one
of those requires a custom M-function (Router Manual §13.28, p.290).

To add a custom M-code, pick an unused `M94`/`M95` bit, name it after the M-code, and create an
`mfuncXXX.mac` file with the matching number; the PLC program checks that bit for SET/RST
(PLC Manual, PDF p.61). The manual's M3 macro skips itself while searching or backplotting, sets
the spindle-direction bits, then reads Output `OUT1058` (`JPO2`, Auto Spindle) as `#61058`
(PLC Manual, PDF p.61):

```
IF #4202 || #4201 THEN GOTO 200
M95 /2 ; turn off CCW spindle
M94 /1 ;turn on CW spindle

;if AutoSpindle i.e. OUT1058 (a.k.a. JPO2) is set, exit the Macro
IF #61058 THEN GOTO 200
```
