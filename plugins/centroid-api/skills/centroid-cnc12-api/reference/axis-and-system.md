# Axis configuration and system information

Source: Centroid API 1.0.0 reference (API Ref), classes `CNCPipe.Axis` and `CNCPipe.Sys`, and the
Getting Some Axis Data example (API Ref, Axis Data example). Calls return `CNCPipe.ReturnCode` and
are `Since v5.24` unless noted. Reached through `pipe.axis` and `pipe.system` (API Ref, CNCPipe).

---

## Axis: motor, jog, limit and scale settings

Every call takes a `CNCPipe.Axes` value, `AXIS_1` to `AXIS_8`; an axis outside 1-8 returns
`ERROR_INVALID_AXIS` (API Ref, CNCPipe).

**These setters change the machine's configuration.** The Axis Data example points to where the
same values live in CNC12: Motor Parameters at **F1 > F3 > F2 > F2** and Jog Parameters at
**F1 > F3 > F2 > F1** from the Main Menu (API Ref, Axis Data example). A configuration that cannot
be saved or sent returns `ERROR_SAVE_CONFIGURATION`, `ERROR_SEND_SETUPS` or `ERROR_SEND_PID_SETUPS`
(API Ref, CNCPipe).

### Get / set pairs

| Get | Set | Value |
| --- | --- | --- |
| `GetLabel(Axes, out char label)` | `SetLabel(Axes, char label)` | Axis label. The example accepts `A B C N W X Y Z`. |
| `GetAccelTime(Axes, out double accel_time)` | `SetAccelTime(Axes, double time)` | Acceleration time. |
| `GetDeadstartVelocity(Axes, out double)` | `SetDeadstartVelocity(Axes, double velocity)` | Deadstart velocity. |
| `GetDeltaVMax(Axes, out double)` | `SetDeltaVMax(Axes, double)` | Delta Vmax. |
| `GetRate(Axes, Rate jog_rate, out double rate)` | `SetRate(Axes, Rate rate_type, double rate)` | A rate from `Rate` (below). |
| `GetLashComp(Axes, out double)` | `SetLashComp(Axes, double value)` | Lash compensation. |
| `GetScrewPitch(Axes, out double)` | `SetScrewPitch(Axes, double value)` | Screw pitch. |
| `GetCountsPerTurn(Axes, out double)` | `SetCountsPerTurn(Axes, double value)` | Motor counts per turn (steps per rev). |
| `GetAxisReversal(Axes, out bool)` | `SetAxisReversal(Axes, bool)` | Axis direction reversed. |
| `GetLimit(Axes, Direction, out double)` | `SetLimit(Axes, Direction, double)` | Axis limit; inches or millimeters per the machine unit configuration. |
| `GetHomeLimit(Axes, Direction, out double)` | `SetHomeLimit(Axes, Direction, double)` | Home limit; inches or millimeters per the machine unit configuration. |
| `GetTravelLimit(Axes, Direction, out double)` | `SetTravelLimit(Axes, Direction, double)` | Travel limit in a direction. |
| `GetScalesEnable(Axes, out bool)` | `SetScalesEnable(Axes, bool)` | Scaling enabled. |
| `GetScalesInput(Axes, out int encoder_number)` | `SetScalesInput(Axes, int)` | Encoder input that scales the axis. |
| `GetScalesCounts(Axes, out double)` | `SetScalesCounts(Axes, double)` | Counts the axis is scaled by. |
| `GetScalesVelocity(Axes, out double)` | `SetScalesVelocity(Axes, double)` | Scaling velocity. |
| `GetScalesDeadband(Axes, out int)` | `SetScalesDeadband(Axes, int)` | Scaling deadband. |

`Direction` is `PLUS` or `MINUS` (API Ref, CNCPipe.Axis).

`Rate` values: `MAX`, `SLOW_JOG`, `FAST_JOG` (**Acorn only**), `FAST_JOG_MINUS`, `FAST_JOG_PLUS`,
`FAST_JOG_PLUS_PROBE`, `FAST_JOG_MINUS_PROBE`, `SLOW_JOG_PROBE`, `HOME_JOG` (API Ref, CNCPipe.Axis).

### Motor power

`GetPower(Axes, out MotorPower power_state)` returns `RELEASED` or `POWERED`. **The default state is
`POWERED` in the event of an error code** - check the return code before trusting the value
(API Ref, CNCPipe.Axis).

### The documented example

From the Axis Data example (API Ref, Axis Data example):

```csharp
returnCode = cnc12_pipe.axis.GetTravelLimit(CNCPipe.Axes.AXIS_1, CNCPipe.Axis.Direction.PLUS,
                                            out double travel_limit);

bool isValid = double.TryParse(TextBoxSetAxis1TravelLimit.Text, out double value);
if (isValid)
{
    returnCode = cnc12_pipe.axis.SetTravelLimit(CNCPipe.Axes.AXIS_1, CNCPipe.Axis.Direction.PLUS, value);
}
```

The example validates input before every `Set` call - a label against the allowed list, a number
with `double.TryParse` - and stores each `ReturnCode`.

## Sys: board, software and license

(API Ref, CNCPipe.Sys)

### Identity

| Call | Returns |
| --- | --- |
| `GetMachineType(out MachineTypes machine)` | `ACORN`, `ACORNSIX`, `HICKORY`, `OAK`, `ALLINONEDC`, `EMULATOR` or `UNKNOWN`. |
| `GetSerialNumber(out string serialNumber)` | Serial number of the connected board. |
| `GetSystemIdentifier(out long identifier)` | System ID of the connected machine. |
| `GetUnlockVersion(out UnlockVersions unlocks)` | Software unlock: `FREE_`, `PRO_`, `ULTIMATE_` or `ULTIMATE_PLUS_` combined with `MILL`, `LATHE`, `ROUTER`, `PLASMA` or `LASER` (e.g. `PRO_MILL`), or `UNKNOWN`. |
| `GetHighestLicenseVersion(out LicenseVersion highestVersion)` | Highest version of the loaded license file: `PreVersionedLicense` or `V540`. Since v5.40. |
| `double LicenseVersionToDouble(LicenseVersion)` | The license version as a number. |
| `GetPluginUnlocked(Plugins plugin, out bool pluginUnlocked)` | Whether a licensed plugin is unlocked: `HARDWARE_KEY`, `ATC`, `CNC12_C`, `ENGINE_BLOCK`, `AUTO_PORT_CHAMBER`, `MILLWRITE`. Since v5.40.05. |

`State.GetAcornBoardRevision(out int revision)` gives the Acorn board revision
(API Ref, CNCPipe.State).

### Expansion devices

| Call | Returns |
| --- | --- |
| `GetPLCEXP1616NumberofDevices(out int)` | Number of PLCEXP1616 devices connected. |
| `GetECAT1616NumberOfDevices(out int)` | Number of ECAT1616 devices connected. |
| `GetEther1616DeviceInfo(out List<Ether1616Device> devices)` | Every valid, attached Ether1616 device. |
| `IsENCEXP12Connected(out bool)` | Whether an ENCEXP12 is connected to the AcornSix board. |

An `Ether1616Device` has `IP` (`IPAddress`) and `DeviceNumber` (`int?`), "the determining factor of
where the IO starts at in the PLC (e.g. Device 0 starts at 33 and has a jumper on 'A0')"
(API Ref, CNCPipe.Sys.Ether1616Device).

### Actions

| Call | Does |
| --- | --- |
| `ExitSoftware()` | Closes the CNC software gracefully. |
| `ImportLicense(string licensePath)` | Imports a license into CNC12. Failures: `ERROR_LICENSE_GENERAL_FAILURE`, `ERROR_LICENSE_MISMATCHED_VERSIONS`, `ERROR_LICENSE_MISMATCHED_SERIAL_NUMBER` (API Ref, CNCPipe). |
| `CreateReport(string reportPath)` | Creates a CNC12 `Report.zip` in the directory given; the file name is generated. Since v5.42. Failures: `ERROR_REPORT_PATH_EMPTY`, `ERROR_REPORT_PATH_INVALID`, `ERROR_REPORT_PATH_NOT_FOUND` (API Ref, CNCPipe). |

A call that needs a better license than the one loaded returns `ERROR_LICENSE_LOCKED`
(API Ref, CNCPipe).
