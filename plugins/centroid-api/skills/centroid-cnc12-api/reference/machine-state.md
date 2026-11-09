# Machine state: State, Dro, Wcs, Csr, Screen

Source: Centroid API 1.0.0 reference (API Ref). All calls return `CNCPipe.ReturnCode` unless noted
and are `Since v5.24` unless noted; see [connection-and-setup.md](connection-and-setup.md#versions).

What the machine is doing now - positions, motion modes, the running line, feedrate and spindle - and
the work coordinate systems. Reached through `pipe.state`, `pipe.dro`, `pipe.wcs`, `pipe.csr` and
`pipe.screen` (API Ref, CNCPipe).

---

## State: status at a glance

`State` "holds info relating to system state, e.g. move mode, position mode, feedrate, spindle
speed" (API Ref, CNCPipe.State).

### Job and line

| Call | Returns |
| --- | --- |
| `IsJobRunning(out bool job_running)` | Whether a job is currently running. Since v5.40. |
| `GetJobNameCurrent(out string job_name)` | Name of the currently loaded job. |
| `GetFullPathJobNameCurrent(out string job_name)` | Full path of the currently loaded job. |
| `GetCurrentLineInfo(out int line_number, out int program_number, out int stack_level)` | Current line of the executing job. |
| `GetCurrentStackLevelZeroLineInfo(out int line_number, out int program_number)` | Current line of the original job, excluding calls to macros. |
| `GetActiveGCodes(out string[] active_g_codes)` | Currently active modal G- and M-codes. |
| `GetGCodeDisplay(out string[] g_code_display)` | The G-code lines CNC12 usually shows while a job runs. |
| `GetMdiState(out MdiState mdi_state)` | `IN_MDI`, `NOT_IN_MDI` or `UNKNOWN`. |
| `GetFeedHoldState(out FeedHoldState feed_hold_state)` | `FEED_HOLD_ON` (pressed), `FEED_HOLD_OFF` or `UNKNOWN`. |
| `GetJogState(out bool jog_state)` | Whether the user is jogging the machine. |
| `IsAPIRestricted(out bool apiRestricted)` | Whether API calls are restricted (job running, a menu that does not accept calls...). Not every call is restricted. |

A job's line number can also arrive pushed rather than polled: see `JOB_INFO` in
[events-and-ui.md](events-and-ui.md#message-types).

### Motion, feed and spindle

| Call | Returns |
| --- | --- |
| `GetMoveMode(out MoveMode move_mode)` | `RAPID` (G0), `LINEAR` (G1), `CW_ARC` (G2), `CCW_ARC` (G3); `UNKNOWN` means bad communication with the pipe. |
| `GetPositioningMode(out PositioningMode positioning_mode)` | `ABSOLUTE` (G90), `INCREMENTAL` (G91), `UNKNOWN`. |
| `GetFeedrate(out double feedrate)` | The measured feedrate; accounts for the feedrate override knob. |
| `GetFeedrateOverride(out int feedrate_override)` | Feedrate override as a percent between 1 and max (usually 120). |
| `GetSpindleSpeed(out double spindle_speed)` | Current spindle speed. |
| `GetHighRangeSpindleSpeed(Value max_or_min, out double ...)` / `SetHighRangeSpindleSpeed(Value max_or_min, double value)` | Spindle Speed High Range maximum or minimum (`Value.MAX` / `Value.MIN`). |

Enums `CircularInterpolationPlane` (`XY` = G17, `ZX` = G18, `YZ` = G19) and
`CircularInterpolationDirection` (`CLOCKWISE`, `COUNTERCLOCKWISE`) are also declared on `State`
(API Ref, CNCPipe.State).

### Positions

| Call | Returns |
| --- | --- |
| `GetCurrentMachinePosition(out double[] machine_pos)` | Current machine position. |
| `GetCurrentLocalPosition(out double[] local_pos)` | Current WCS position. |
| `GetEncoderPosition(out Int64[] encoder_position)` | Encoder position, "AKA the 'real' motor position". Since v5.40. |

### Units

| Call | Does |
| --- | --- |
| `GetUnitsOfMeasureDefault(out UnitsOfMeasure units)` | Default units: `INCH_UNITS` (G20), `METRIC_UNITS` (G21), `UNKNOWN` (failure to communicate). |
| `SetImperialUnits()` / `SetMetricUnits()` | Set the default unit of measure. |
| `GetUnitsOfMeasureDro(out UnitsOfMeasure units)` | DRO units. |
| `SetDroImperialUnits()` / `SetDroMetricUnits()` | Set the DRO units. |

### Setup and console

| Call | Does |
| --- | --- |
| `GetMachineHomeAtPowerUp(out HomingType homing_type)` / `SetMachineHomeAtPowerUp(HomingType)` | Homing type at power-up: `JOG`, `HOMESWITCH`, `REFMARKHS`, `HOMEINPLACE`, `ABSOLUTEHOME`, `UNKNOWN` (usually an error). |
| `GetConsoleType(out ConsoleTypes consoleType)` / `SetConsoleType(ConsoleTypes)` | `JOGBOARD`, `LEGACY`, `VIRTUAL`, `OFFLINE`, `JOGBOARD_WITH_VCP`. |
| `GetAcornBoardRevision(out int revision)` | Acorn board revision. |
| `GetScreenSize`, `GetMonitorSize`, `GetScreenPosition` | Size and position of the CNC application window and monitor (`out int` pairs). |

The USB-BOB calls on `State` are in [plc-and-io.md](plc-and-io.md#usb-bob-inputs).

## Dro: what the DRO shows

(API Ref, CNCPipe.Dro)

| Call | Returns |
| --- | --- |
| `GetDro(DroCoordinates dro_coordinates, out double[] dro_position)` | DRO readout as numbers. |
| `GetDro(DroCoordinates dro_coordinates, out Tuple<string, string, string>[] dro_strings)` | DRO readout as strings. |
| `SetDroCoordinates(DroCoordinates dro_coordinates)` | Set the DRO coordinates. |

`DroCoordinates`: `DRO_LOCAL` (coordinates from the selected WCS), `DRO_MACHINE` (machine
coordinates), `DRO_DISTANCE_TO_GO` (the Distance-to-Go DRO).

Centroid's example reads one axis's machine position as the second tuple item
(PowerFeed example, PipeManager.cs):

```csharp
var cncDro = new CentroidAPI.CNCPipe.Dro(m_pipe);
Tuple<string, string, string>[] droStrings;
if (cncDro.GetDro(DroCoordinates.DRO_MACHINE, out droStrings) == ReturnCode.SUCCESS)
{
    return droStrings[axis].Item2;   // axis index 0-7
}
```

## Wcs: work coordinate systems and part zero

(API Ref, CNCPipe.Wcs). `WCS` enumerates `WCS_1` to `WCS_18` and `WCS_UNKNOWN`.

| Call | Does |
| --- | --- |
| `GetActiveWcs(out WCS wcs_number)` | Active WCS. |
| `SelectNextWcs()` / `SelectPrevWcs()` | Step the active WCS. |
| `GetWorkpieceOrigin(int axis, out double origin)` | Part zero for the active WCS and an axis. |
| `GetWorkpieceOrigin(int wcs, int axis, out double origin)` | Part zero for a given WCS and axis. |
| `SetWorkpieceOrigin()` | Attempt to set part zero for **all axes** of the active WCS. |
| `SetWorkpieceOrigin(int axis)` | Attempt to set part zero for one axis of the active WCS. |
| `SetWorkpieceOrigin(int wcs, int axis)` | Attempt to set part zero for one axis of a given WCS. |
| `SetWorkpieceLocation(int axis, double location)` | Attempt to set the part location for one axis of the active WCS. |
| `SetWorkpieceLocation(int wcs, int axis, double location)` | Same, for a given WCS. |
| `GetWorkpieceReference(int ret, int axis, out double reference)` / `SetWorkpieceReference(int ret, int axis, double point)` | Reference point from the Return menu in the work coordinate settings. |

The `Set...` calls are documented as "attempt to set" (API Ref, CNCPipe.Wcs); check the return code.

## Csr: coordinate system rotation

(API Ref, CNCPipe.Csr)

| Call | Does |
| --- | --- |
| `GetAngle(out double angle)` / `GetAngle(int wcs, out double csr_angle)` | CSR angle for the active WCS, or a given WCS. |
| `SetAngle(double angle)` / `SetAngle(int wcs, double angle)` | Attempt to set the CSR angle. |
| `DisableCSR()` | Disable the active CSR; it re-enables when a job concludes or when `ReenableCSR` is called. |
| `ReenableCSR()` | Re-enable a disabled CSR; returns an error if `DisableCSR` was never called or a job's conclusion already re-enabled it. |

## Screen: viewport sizes

`Screen.GetViewportInfo(Viewport viewport, out int width, out int height)` returns the size of a
CNC12 viewport: `VIEWPORT_ACTIVE_G_CODES`, `VIEWPORT_DRO`, `VIEWPORT_FKEY` or `VIEWPORT_MESSAGE`
(API Ref, CNCPipe.Screen).
