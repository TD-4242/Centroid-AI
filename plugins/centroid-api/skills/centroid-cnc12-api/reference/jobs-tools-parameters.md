# Jobs, tools, parameters and system variables

Source: Centroid API 1.0.0 reference (API Ref), classes `CNCPipe.Job`, `CNCPipe.Tool` and
`CNCPipe.Parameter`. Calls return `CNCPipe.ReturnCode` and are `Since v5.24` unless noted. Reached
through `pipe.job`, `pipe.tool` and `pipe.parameter` (API Ref, CNCPipe).

---

## Job: loading and running

| Call | Does |
| --- | --- |
| `Load(string path)` | Load an existing job into CNC12. Since v5.40. |
| `RunCommand(string command, bool require_cycle_start = true)` | "Run a command now. If we require cycle start, it will post as an actual job." `command` is the G-code command to run. |
| `CancelExecution()` | Cancel execution of a job. In the emulator/offline Intercon this issues the Escape key, since the PLC is not running to accept the cycle cancel command. |
| `ContinueExecution()` | Continue a job waiting at an `M0`/`M200`/`M201`. Machine Parameter 440 must be set to 256 for this call to return `SUCCESS`. |
| `GetJobRepeatState(out bool repeat_state)` / `SetJobRepeatState(bool state)` | Job repeat on or off. |
| `RefreshGraph(bool refresh_rtg)` | Refresh the onscreen graph. |
| `GetPartCount(out int part_count)` / `GetPartNumber(out int part_number)` | Part count and current part number. |
| `GetCurrentlyRunningJob(out string current_job)` | `NO_JOB_RUNNING`, `MDI_RUNNING`, `API_COMMAND_RUNNING`, or the path of the current job. Not guaranteed to be the loaded job during probing macros, API commands, MDI and so on. |

The overloads of `Load` and `RunCommand` that also take `cnc12_working_directory` are deprecated
(API Ref, Deprecated List).

Centroid's example loads a job only after checking that the file exists and the pipe is connected
(PowerFeed example, PipeManager.cs), and starts it with the cycle-start skin event shown in
[plc-and-io.md](plc-and-io.md#pressing-a-button-skin-events). The community Python wrapper's example
runs a line at once with `require_cycle_start=False`
(fca1 wrapper, examples/play_gcode_safe.py):

```python
sk.job.runCommand("G4 P5.0", require_cycle_start=False)
```

A command or job can move the machine. A value that cannot be set because a job is running returns
`ERROR_JOB_IN_PROGRESS`; an action unavailable because the machine is not homed returns
`ERROR_NOT_HOMED`; "the machine is not allowed to move at this time" is `ERROR_CLIENT_LOCKED`
(API Ref, CNCPipe).

`Job` also declares the enum `ProbeBossOrientation` (`X_PLUS`, `Y_PLUS`, `X_MINUS`, `Y_MINUS`) - the
initial direction for probing a boss (API Ref, CNCPipe.Job).

## System variables (`#` variables)

| Call | Range |
| --- | --- |
| `GetSystemVariable(int variable_number, out double value)` | `#1`-`#299`, `#402`-`#31999` |
| `GetSystemVariable(int variable_number, out string value)` | `#300`-`#400` |
| `SetSystemVariable(int variable_number, double value)` | `#1`-`#299`, `#402`-`#31999` |
| `SetSystemVariable(int variable_number, string value)` | `#300`-`#401` |

`GetUserSystemVariable` and `GetUserStringSystemVariable` are deprecated in favor of these
(API Ref, Deprecated List).

## Parameter: machine parameters and user variables

| Call | Does |
| --- | --- |
| `GetMachineParameterValue(int parameter_num, out double parameter_value)` | Value of machine parameter 0-999, or user variable 29000-34999. |
| `SetMachineParameter(int parameter_num, double value)` | Set machine parameter 0-999, or user variable 29000-34999. |

Reading user variables 29000-34999 can occur in any job run state or any menu
(API Ref, CNCPipe.Parameter). The documented example:

```csharp
returnCode = cnc_pipe.parameter.GetMachineParameterValue(32, out double myParamValue);
```

Configuration failures have their own codes: `ERROR_SAVE_CONFIGURATION` ("Could not save the
configuration that was changed"), `ERROR_SEND_SETUPS` and `ERROR_SEND_PID_SETUPS` (CNC12 could not
send setups or PID setups to the MPU) (API Ref, CNCPipe).

## Tool: the tool library

`Tool` is described as the class "to handle Mill Tool Info" (API Ref, CNCPipe.Tool).

### The `Info` struct

One tool library row (API Ref, CNCPipe.Tool.Info):

| Field | Type | Meaning |
| --- | --- | --- |
| `number` | `int` | Tool number. |
| `bin` | `int` | Bin number of the tool. |
| `h_number` | `int` | Default height offset (H) number, 1-200; Intercon uses it for a default H at each tool change. |
| `height_offset` | `double` | Z adjustment applied when G43/G44 uses this H value. |
| `d_number` | `int` | Default diameter (D) number, 1-200. |
| `diameter_offset` | `double` | Adjustment applied when G41/G42 uses this D value. |
| `coolant` | `Coolant` | Default coolant: `FLOOD`, `MIST` or `OFF` (`UNKNOWN` on error); Intercon inserts M7/M8 after a tool change. |
| `spindle_direction` | `SpindleDirection` | Default direction: `CW`, `CCW` or `OFF` (`UNKNOWN` on error); Intercon inserts M3/M4. |
| `spindle_speed` | `int` | Default spindle speed, 0-500000; Intercon inserts an S code. |
| `description` | `string` | Tool description, at most 20 characters. |

### Reading

| Call | Returns |
| --- | --- |
| `GetToolNumber(out int tool_number)` | Current tool number. |
| `Info GetToolInfo()` / `Info GetToolInfo(int t)` | `Info` for the current tool, or tool `t` (returns the struct, not a `ReturnCode`). |
| `GetToolLibrary(out List<Info> ToolLibrary)` | Every tool in the library. |
| `GetToolBin(out int bin)` / `GetToolBin(int T, out int bin)` | Bin of the active tool, or tool `T`. |
| `GetToolHNumber` / `GetToolDNumber` | H or D number, of the active tool or tool `T`. |
| `GetCurrentHeightOffsetNumber(out int height_offset_number)` | Current H number. |
| `GetHeightOffsetAmount(...)` / `GetDiameterOffsetAmount(...)` | Offset amount for the current H/D, or a given `H` or `D` number. |
| `GetToolSpindleSpeed`, `GetToolSpindleDirection`, `GetCoolant`, `GetToolDescription` | Per-tool defaults, for the current tool or tool `T`. |

### Writing

| Call | Does |
| --- | --- |
| `SetToolLibrary(List<Info> toolLibrary)` | Specify the whole tool library. |
| `SetToolInfo(int T, Info Tinfo)` | Specify one tool from an `Info` struct. |
| `SetBinNumber(int T, int value)` | Set tool `T`'s bin. |
| `SetToolHNumber(int T, int height)` / `SetToolDNumber(int T, int dia)` | H or D number. |
| `SetToolHeightOffsetAmount(int T, double value)` / `SetToolDiameterOffsetAmount(int T, double value)` | Offset amounts. Since v5.40; the misspelled `...Amout` forms are deprecated. |
| `SetCoolant(int T, Coolant type)`, `SetSpindleDirection(int T, SpindleDirection dir)`, `SetSpindleSpeed(int T, long speed)`, `SetToolDescription(int T, string description)` | Per-tool defaults. |
| `Save()` | "Save/Write tool related save files." Since v5.40. |

The reference does not say which setters write to disk on their own; `CNCPipe.BurstMode` "sets if
the skinning app is saving after every command or not" (API Ref, CNCPipe).

### Lathe wear adjustment

`SetWearAdjustment(int T, ToolWearAdjustmentType type, double value)` and
`GetWearAdjustment(int T, ToolWearAdjustmentType type, out double value)` set and get a lathe tool's
wear adjustment on `TOOL_WEAR_ADJUSTMENT_X` or `TOOL_WEAR_ADJUSTMENT_Z` (API Ref, CNCPipe.Tool).
