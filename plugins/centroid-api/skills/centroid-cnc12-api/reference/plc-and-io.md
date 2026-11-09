# PLC and I/O: bits, watch lists, words, skinning data, skin events

Source: Centroid API 1.0.0 reference (API Ref), class `CNCPipe.Plc` unless noted. Calls are
`Since v5.24`. Reached through `pipe.plc` (API Ref, CNCPipe).

Reading and forcing PLC bits, reading PLC words, and the two channels an app uses to *send* things
to the PLC program: skinning data words and skin events. What the PLC program does with them is PLC code:
if the centroid-plc plugin is installed, see `centroid-plc-programming`; otherwise (PLC Manual, PDF p.106, p.110-112).

---

## Bit types and states

| Enum | Values |
| --- | --- |
| `BitType` | `Input`, `Output`, `Memory`, `UsbInput` (a USB-BOB input bit) |
| `IOState` | `IO_LOGICAL_0` (open or off), `IO_LOGICAL_1` (closed or on), `IO_INDEX_OUT_OF_RANGE` (invalid bit index), `IO_STATE_UNKNOWN` (could not be determined) |
| `ForceState` | `NotForced` (controlled by the PLC program logic), `ForcedOn`, `ForcedOff` |
| `InversionState` | `NotInverted`, `Inverted` |

## Reading one bit

| Call | Range |
| --- | --- |
| `GetInputState(int bitNumber, out IOState input_state)` | inputs 1-1312 |
| `GetOutputState(int bitNumber, out IOState io_state)` | outputs 1-1312 |
| `GetMemoryState(int bitNumber, out IOState io_state)` | memory 1-1024 |

Each also has a `bool` overload - `GetInputState(int)`, `GetOutputState(int)`,
`GetMemoryState(int)` - that "may be more convenient to use with the drawback that if it returns
false, it could be caused by a bad bitNumber or other failure". Use the `ReturnCode` form when false
must mean *off*.

Centroid's example maps the state to a bool and treats anything other than `IO_LOGICAL_1` as off
(PowerFeed example, PipeManager.cs):

```csharp
var cncPlc = new CentroidAPI.CNCPipe.Plc(m_pipe);
CentroidAPI.CNCPipe.Plc.IOState inputState;
if (cncPlc.GetInputState(iInput, out inputState) == ReturnCode.SUCCESS)
{
    switch (inputState)
    {
        case IOState.IO_LOGICAL_0: return false;
        case IOState.IO_LOGICAL_1: return true;
    }
}
return false;
```

## Watch lists

`SetWatchList` then `GetWatchList` is the recommended way to read multiple I/O and memory bits
(App API page).

| Call | Does |
| --- | --- |
| `bool SetWatchList(ref List<IOMBit> bitList)` | Sets the PLC watch list **and** returns with the current states filled in. Limited to 255 inputs, outputs and memory bits. |
| `bool GetWatchList(ref List<IOMBit> bitList)` | Gets the states of the watched bits. For repeated reads of the same list, call `SetWatchList` once, then `GetWatchList`. |
| `bool SetUsbWatchList(ref List<IOMBit> bitList)` / `bool GetUsbWatchList(ref List<IOMBit> bitList)` | The same for USB-BOB bits. |

All four return true on success. Each `IOMBit` carries `type` (`BitType`), `number` (bit number),
`state` (`IOState`, filled in when the list returns) and `vcpButton` (the VCP button object)
(API Ref, CNCPipe.Plc.IOMBit).

## PLC system-variable bits and VCP LEDs

| Call | Does |
| --- | --- |
| `GetPcSystemVariableBit(PcToMpuSysVarBit bit, out IOState state)` | A "PC" system variable bit: in most cases set by the CNC software on the PC to tell the MPU's PLC system its status. |
| `GetPlcSystemVariableBit(MpuToPcSysVarBit bit, out IOState state)` | A "PLC" system variable bit: in most cases set by the PLC program to tell the CNC software its status. |
| `ulong GetVcpLedStates()` | All VCP output LEDs at once, bit-mapped; the low bit is the upper-left LED. |

Centroid's example decides "is a program running" from `PcToMpuSysVarBit.SV_PROGRAM_RUNNING` and
treats `IO_STATE_UNKNOWN` as running "for safety" (PowerFeed example, PipeManager.cs). That bit is 1
in **MDI mode or** while a job is in progress (PLC Manual, PDF p.104); `State.IsJobRunning`
(v5.40) reports whether a job is running (API Ref, CNCPipe.State).

## Reading PLC words

The PLC's numeric registers are readable, and only the first block of each is available to CNC
software:

| Call | Register | Index |
| --- | --- | --- |
| `GetWordValue(int index, out Int32 value)` | `W`, 32-bit integer | 1-88 |
| `GetDoubleWordValue(int index, out Int64 value)` | `DW`, 64-bit integer | 1-22 |
| `GetFloatWordValue(int index, out float value)` | `FW`, 32-bit float | 1-44 |
| `GetDoubleFloatWordValue(int index, out double value)` | `DFW`, 64-bit float | 1-22 |

There is no setter for these; to send a value to the PLC, use a skinning data word.

## Sending values to the PLC: skinning data words

A skinning data word is a general-purpose value an app writes and the PLC program reads through a
system variable:

| Set / get | Type | Index | PLC reads it as |
| --- | --- | --- | --- |
| `SetSkinningDataWord(int index, Int32 value, bool sendImmediately = true)` / `GetSkinningDataWord(int index, out Int32 ...)` | 32-bit integer | 1-12 | `SV_SKINNING_DATA_W_1`-`_12` |
| `SetSkinningDataFloatWord(int index, float value, bool sendImmediately = true)` / `GetSkinningDataFloatWord(int index, out float ...)` | 32-bit float | 1-11 | `SV_SKINNING_DATA_FW_1`-`_11` |
| `SetSkinningDataDoubleFloatWord(int index, double value, bool sendImmediately = true)` / `GetSkinningDataDoubleFloatWord(int index, out double ...)` | 64-bit float | 1-11 | `SV_SKINNING_DATA_DFW_1`-`_11` |

The index is one-based. `sendImmediately = true` sends every previously updated skinning data value
to the MPU now; with `false`, the new value is not visible to the PLC until another skinning-data
set call is made with `sendImmediately = true` - so a group of values can be written and then
released together. A bad index returns `ERROR_INVALID_SKINNING_DATA_WORD_INDEX`, and a failed send
`ERROR_PLC_SEND_SKINNING_DATA` (API Ref, CNCPipe).

## Pressing a button: skin events

| Call | Does |
| --- | --- |
| `SetSkinEventState(int eventNumber, int state)` | Set a skin event number to a given state. |
| `GetSkinEventState(int skin_event, out int state)` | Get the state of a skin event. |

The PLC program sees them as `SV_SKIN_EVENT_1`-`255`; by convention events 1-50 are the fifty keys of
a hardware jog panel, left to right and top to bottom, with 1 = Spindle+ and **50 = CYCLE_START**
(PLC Manual, PDF p.106). The VCP binds a button to the same numbers through `<skin_event_num>`:
if the centroid-vcp plugin is installed, see `centroid-vcp`; otherwise (VCP Manual p.36).

Skin event calls are not possible on the Offline CNC12 install (App API page).

Centroid's example emulates a cycle-start press - and labels it "Use with Caution. Operators should
have to press cycle start to begin machine motion." It starts the job if CNC12 is on a screen that
allows cycle start (PowerFeed example, PipeManager.cs):

```csharp
var cncPLC = new CentroidAPI.CNCPipe.Plc(m_pipe);
if (cncPLC.SetSkinEventState(50, 1) == CNCPipe.ReturnCode.SUCCESS)
{
    System.Threading.Thread.Sleep(50);   // let the PLC see the press
    return cncPLC.SetSkinEventState(50, 0);
}
```

## Forcing and inverting bits

| Call | Range | Notes |
| --- | --- | --- |
| `SetIoForceState(int ioBit, BitType bitType, ForceState state)` | 1-80 | `BitType.Output` or `BitType.Memory`. Memory bits are forced only at the beginning of a PLC pass, so PLC code can still change them. |
| `SetInputForceState(int inputBit, ForceState state)` | 1-80 | For inputs `ForcedOn` and `ForcedOff` behave the same: force the input, then set the forced level with `SetInputInversionState`. |
| `SetInputInversionState(int inputBit, InversionState state)` | 1-80 | Whether an input is inverted. |

`NotForced` hands the bit back to the PLC program logic (API Ref, CNCPipe.Plc `ForceState`).

## USB-BOB inputs

These live on `State` (API Ref, CNCPipe.State):

| Call | Does |
| --- | --- |
| `GetUsbInputInversions(out string inversionBits)` / `SetUsbInputInversions(char[] inputInversions)` | USB-BOB input inversion bits. |
| `ToggleUsbInputInversionBit(int inpNum)` | Toggle one inversion bit. |
| `GetUsbOnlineBits(out bool[] onlineBits)` | Online bits of the connected USB-BOBs. |

Watching USB-BOB inputs uses `SetUsbWatchList` / `GetUsbWatchList` ([Watch lists](#watch-lists)).
