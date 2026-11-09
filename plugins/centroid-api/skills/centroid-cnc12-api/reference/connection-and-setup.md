# Connection and project setup

Source: Centroid API 1.0.0 reference (API Ref), Centroid's CNC App API page (App API page) and
Centroid's C# PowerFeed example (PowerFeed example). URLs are in the skill's Sources section.

How to start a project, open a `CNCPipe`, keep it connected, and read what a call returned.

---

## Project setup

Only VB.NET and C# are officially supported, in Console, WinForms and WPF projects; Centroid uses
and recommends Visual Studio Community (free) or Pro/Enterprise (App API page).

Centroid's Getting Started steps (API Ref, Getting Started):

1. Create a new **WPF App (.NET Framework)** project in Visual Studio.
2. In Solution Explorer, right-click *References* > *Add reference...* > *Browse*, and select
   `CentroidAPI.dll`. It is in the root directory of the CNC12 installation (`cncm`, `cnct`,
   `MillDemo` or `LatheDemo` folder).
3. Add `using CentroidAPI;` and create the pipe after `InitializeComponent()`.

Centroid's PowerFeed example instead targets .NET 6 (`net6.0-windows`) and references
`..\cncm\CentroidAPI.dll` (PowerFeed example, README and `.csproj`) - both project styles are
Centroid's own.

The reference documentation for the installed version is in the install folder
(App API page):

| Product | Documentation folder |
| --- | --- |
| Mill | `c:\cncm\CentroidAPIDocumentation` |
| Lathe | `c:\cnct\CentroidAPIDocumentation` |
| Router | `c:\cncr\CentroidAPIDocumentation` |
| Plasma | `c:\cncp\CentroidAPIDocumentation` |
| Mill demo | `c:\Centroid_Mill_Intercon_Offline\CentroidAPIDocumentation` |
| Lathe demo | `c:\Centroid_Lathe_Intercon_Offline\CentroidAPIDocumentation` |

## Opening a pipe

`CNCPipe` constructors (API Ref, CNCPipe):

| Constructor | Notes |
| --- | --- |
| `CNCPipe()` | No arguments. |
| `CNCPipe(int timeout = 1)` | Opens a pipe for communicating with CNC12; `timeout` is the number of seconds to wait for a connection. |
| `CNCPipe(bool useVcpPipe = false, int timeout = 1)` | `useVcpPipe = true` uses the named pipe dedicated for VCP. |

`IsConstructed()` returns true if construction succeeded (API Ref, CNCPipe). CNC12 must be running,
finished initializing and error free; otherwise the example's "API is not connected" prompt
appears (API Ref, Axis Data example).

### The sub-objects

A connected pipe exposes one object per area (API Ref, CNCPipe):

| Field | Class | Field | Class |
| --- | --- | --- | --- |
| `axis` | `Axis` | `screen` | `Screen` |
| `csr` | `Csr` | `state` | `State` |
| `dro` | `Dro` | `system` | `Sys` |
| `job` | `Job` | `tool` | `Tool` |
| `parameter` | `Parameter` | `wcs` | `Wcs` |
| `plc` | `Plc` | `message_window` | `MessageWindow` |
| `inbound_communications` | `InboundComm` | | |

Each class also has a public constructor taking the parent pipe, e.g. `Plc(CNCPipe parent)`
(API Ref, CNCPipe.Plc). Centroid's example uses that form:
`var param = new CentroidAPI.CNCPipe.Parameter(m_pipe);` (PowerFeed example, PipeManager.cs).

Other `CNCPipe` members (API Ref, CNCPipe):

- `CNC12BuildRevision` (field) and `APIBuildRevision` (property, get) - build revisions of CNC12 and
  of `CentroidAPI.dll`; both since v5.40.06.
- `BurstMode` (property, get/set) - "Sets if the skinning app is saving after every command or not."
- `StartListening()`, `StopListening()`, `ClearUnhandledMessages()`, `TryPopUnhandledMessage(out
  InboundComm.CommPacket packet)` and the events `MessageReceived` and `PipeDisconnected` - see
  [events-and-ui.md](events-and-ui.md).

## Staying connected

Centroid's example wraps the pipe in a manager that probes the connection with a cheap call and
rebuilds the pipe when CNC12 has gone away (PowerFeed example, PipeManager.cs):

```csharp
if (m_pipe != null && m_pipe.IsConstructed())
{
    var param = new CentroidAPI.CNCPipe.Parameter(m_pipe);
    CNCPipe.ReturnCode returnCode = param.GetMachineParameterValue(1, out paramValue);
    switch (returnCode)
    {
        case CNCPipe.ReturnCode.SUCCESS:             return true;            // connected
        case CNCPipe.ReturnCode.ERROR_PIPE_IS_BROKEN: m_pipe = new CNCPipe(); break;
        case CNCPipe.ReturnCode.ERROR_CLIENT_LOCKED:  return true;            // still connected
        default:                                     return false;
    }
}
else
{
    m_pipe = new CNCPipe();   // not constructed: try again
}
```

`ERROR_CLIENT_LOCKED` is treated as connected: the comment reads "Client locked means we are still
connected but the client is locked, don't treat this as a disconnection" (PowerFeed example,
PipeManager.cs).

The same manager finds the running CNC12's folder - needed only by the deprecated overloads that
take a working directory - by looking for the processes `cncm`, `cnct`, `cncr`, `cncp`, `MillDemo`
and `LatheDemo`, falling back to `C:\cncm` (PowerFeed example, PipeManager.cs).

## Polling and threads

From the App API page:

- Real-time information (DRO, I/O, machine status): poll every **10-50 ms**. Basic status that need
  not update in real time: **50-500 ms**. The best rate depends on the CNC PC's CPU.
- Centroid tested 10 ms polling in Plasma Restart Mode without noticeable delay to CNC12; faster
  than 10 ms has not been extensively tested and is not recommended.
- CNC12 supports up to **5 simultaneous API instances (`CNCPipe`s)**, including the VCP, Wizards, PLC
  Diagnostic Tool and user apps. Each thread using its own `CNCPipe` consumes one; with the VCP
  running, up to 4 remain.
- Calls are blocking, so there is generally little benefit to calling from several threads; a
  single thread is recommended.

`State.IsAPIRestricted(out bool apiRestricted)` reports whether API calls are restricted in any way
- CNC12 running a job, in a menu that does not accept calls, and so on - noting that not every call
is restricted by CNC12's state (API Ref, CNCPipe.State).

## Return codes

Every `ReturnCode` value and its documented meaning (API Ref, CNCPipe):

| Code | Meaning |
| --- | --- |
| `SUCCESS` | No errors occurred. |
| `ERROR_CLIENT_LOCKED` | The machine is not allowed to move at this time. |
| `ERROR_INVALID_ARGUMENT` | The value could not be interpreted as a number by CNC12. |
| `ERROR_INVALID_AXIS` | Axis was not found to be in range 1-8. |
| `ERROR_INVALID_PLC_BIT_NUMBER` | Invalid PLC bit number was selected. |
| `ERROR_INVALID_PLC_BIT_TYPE` | Invalid PLC bit type was selected. |
| `ERROR_INVALID_REQUEST` | Request cannot be granted under current configuration. |
| `ERROR_INVALID_SKINNING_DATA_WORD_INDEX` | The index was out of range. |
| `ERROR_JOB_IN_PROGRESS` | A value could not be set because a job is running. |
| `ERROR_PIPE_IS_BROKEN` | CNC12 closed while you were trying to use the pipe. |
| `ERROR_PLC_SEND_SKINNING_DATA` | Could not send skinning data to the PLC. |
| `ERROR_SAVE_CONFIGURATION` | Could not save the configuration that was changed. |
| `ERROR_SEND_COMMAND` | The command was not sent successfully to CNC12. |
| `ERROR_SEND_PID_SETUPS` | CNC12 could not send PID setups to the MPU. |
| `ERROR_SEND_SETUPS` | CNC12 could not send setups to the MPU. |
| `ERROR_OUT_OF_RANGE` | The value is out of range for the PC. |
| `ERROR_CONVERSION` | Could not convert value to a valid number. |
| `ERROR_UNKNOWN` | An unknown error occurred. |
| `ERROR_VALIDATION` | CNC12 could not set value because it is not valid. |
| `STATUS_UNKNOWN` | Centroid API received unknown response from CNC12. |
| `ERROR_DEPRECATED` | Centroid API received call to deprecated function. |
| `ERROR_LICENSE_GENERAL_FAILURE` | License failed to import due to unknown reason. |
| `ERROR_LICENSE_MISMATCHED_VERSIONS` | License failed to import due to mismatched CNC12 version. |
| `ERROR_LICENSE_MISMATCHED_SERIAL_NUMBER` | License failed to import due to mismatched serial number. |
| `ERROR_LICENSE_LOCKED` | Feature requires a greater license than is currently loaded. |
| `ERROR_INVALID_RETURN` | Requested Return Point is not valid. |
| `ERROR_EXPERIMENTAL_FEATURE` | Feature is experimental; indicates success but makes no guarantee the call will continue to work this way. |
| `ERROR_NOT_HOMED` | Requested action is not available due to the unhomed status of the machine. |
| `ERROR_REPORT_PATH_EMPTY` | Report Path is empty. |
| `ERROR_REPORT_PATH_INVALID` | Report Path is invalid. |
| `ERROR_REPORT_PATH_NOT_FOUND` | Report Path was not found or unattainable. |

A few calls return `bool` instead - `IsConstructed`, the watch-list calls and the convenience
`GetInputState(int)`-style overloads - and some return data directly, e.g. `Tool.GetToolInfo`
(API Ref, CNCPipe.Plc; API Ref, CNCPipe.Tool).

## Versions

Most calls are documented `Since v5.24`. These are newer (API Ref, per class):

| Since | Member |
| --- | --- |
| v5.40 | `Job.Load(string path)`, `State.IsJobRunning`, `State.GetEncoderPosition`, `Tool.Save`, `Tool.SetToolHeightOffsetAmount`, `Tool.SetToolDiameterOffsetAmount`, `Sys.GetHighestLicenseVersion`, `InboundComm.ChangeDroType`, `InboundComm.ChangeJobInfoType` |
| v5.40.03 | `InboundComm.TicksToDateTime` |
| v5.40.05 | `Sys.GetPluginUnlocked` |
| v5.40.06 | `CNCPipe.CNC12BuildRevision`, `CNCPipe.APIBuildRevision` |
| v5.42 | `Sys.CreateReport` |

### Deprecated

Calls listed as deprecated (API Ref, Deprecated List); a deprecated call can return
`ERROR_DEPRECATED` (API Ref, CNCPipe):

| Deprecated | Use instead |
| --- | --- |
| `Job.Load(string path, string cnc12_working_directory)` | `Job.Load(string path)` |
| `Job.RunCommand(string command, string cnc12_working_directory, bool require_cycle_start = true)` | `Job.RunCommand(string command, bool require_cycle_start = true)` |
| `Job.GetUserSystemVariable`, `Job.GetUserStringSystemVariable` | `Job.GetSystemVariable` |
| `Tool.SetToolHeightOffsetAmout`, `Tool.SetToolDiameterOffsetAmout` (misspelled) | `SetToolHeightOffsetAmount`, `SetToolDiameterOffsetAmount` |
| `State.IsPCPoweringOff`, `State.SetPlasmaInterruptPoint` | - |

The "use instead" column pairs each deprecated overload with its documented non-deprecated
sibling in the same class (API Ref, CNCPipe.Job; API Ref, CNCPipe.Tool).

## Other languages (unofficial)

The App API page names two community wrappers, neither officially supported:

- A Python wrapper by GitHub user fca1, described as "an unofficial but robust bridge":
  https://github.com/fca1/cnc_centroid_skinning
- A C++ (CLI bridge) wrapper by Filardo: https://centroidcncforum.com/viewtopic.php?t=12525

The Python wrapper's own README says it targets the API published with CNC12 v5.42, uses
`pythonnet`, needs Python of the same 64-bit architecture as `CentroidAPI.dll`, cannot call
`getPcSystemVariableBit` (its enums are not published in the DLL), and warns that it "is not
**really tested, don't trust it**" (fca1 wrapper, README).
