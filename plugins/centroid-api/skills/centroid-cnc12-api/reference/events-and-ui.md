# Inbound messages, the message window and user controls

Source: Centroid API 1.0.0 reference (API Ref): classes `CNCPipe`, `CNCPipe.InboundComm`,
`CNCPipe.MessageWindow`, `MessageReceivedEventArgs`, `PipeDisconnectedEventArgs`, and the CNC12
Main Screen example page.

Polling ([connection-and-setup.md](connection-and-setup.md#polling-and-threads)) pulls data from
CNC12; inbound communications let CNC12 push it - DRO updates, job progress, shutdown notices and
operator prompts.

---

## Listening

On `CNCPipe` (API Ref, CNCPipe):

| Member | Does |
| --- | --- |
| `StartListening()` / `StopListening()` | Begin or stop listening for messages from CNC12. |
| `event EventHandler<MessageReceivedEventArgs> MessageReceived` | Raised for messages from CNC12. |
| `event EventHandler<PipeDisconnectedEventArgs> PipeDisconnected` | Raised when the pipe disconnects. |
| `bool TryPopUnhandledMessage(out InboundComm.CommPacket packet)` | Pop an unhandled message; true if one was available. |
| `ClearUnhandledMessages()` | Clear any unhandled messages. |
| `protected virtual bool OnMessageReceived(InboundComm.CommPacket data)` / `OnPipeDisconnected()` | Overridable in a subclass. |

`MessageReceivedEventArgs` carries `Data` (the `CommPacket`) and a settable `Handled` flag, "Message
data has been handled by user app"; `PipeDisconnectedEventArgs` has the same `Handled` flag
(API Ref, MessageReceivedEventArgs; API Ref, PipeDisconnectedEventArgs).

## The packet

`InboundComm.CommPacket` (API Ref, CNCPipe.InboundComm.CommPacket):

| Field | Type | Use |
| --- | --- | --- |
| `CommunicationType` | `CommunicationTypes` | What kind of message this is. |
| `Flag` | `byte` | General-use flag. |
| `Positions` | `double[]` | General-use positions, indexed 0-7. |
| `LineNumber` | `int` | Line number, for job info. |
| `StackLevel` | `int` | Stack level, for job info. |
| `Message` | `string` | General-use string. |
| `Timer` | `int` | Length of an M2xx timer. |
| `Ticks` | `long` | Timestamp in ticks since 0001-1-1. |
| `InputVar` | `int` (property) | Input variable the M2xx uses; aliased from `LineNumber`. |
| `MCode` | `int` (property) | Currently used M-code; aliased from `StackLevel`. |

`InboundComm.TicksToDateTime(long ticks)` converts `Ticks` to a UTC `DateTime` (since v5.40.03).

## Message types

`CommunicationTypes` and what each carries (API Ref, CNCPipe.InboundComm):

| Type | Carries |
| --- | --- |
| `DRO_UPDATE` | `Positions` - the new DRO location. |
| `CNC12_SHUT_DOWN` | `Flag` - true if CNC12 is shutting down. |
| `PC_SHUT_DOWN` | `Flag` - true if the PC is shutting down. |
| `MESSAGE_WINDOW_MESSAGE` | `Message` - a message added to the message window. |
| `JOB_INFO` | Only while running a job: `LineNumber`, `StackLevel`, and `Message` = the running job. |
| `KEEP_PIPE_ALIVE` | Nothing; keeps the listener pipe alive, no action required. |
| `JOB_CONCLUDED` | `Message` - the job that finished. |
| `M2XX_MESSAGE_ACTIVE` | `Flag` (true if a response is expected), `Message` (the M2xx text), `MCode`, `InputVar` (variable written if responded to), `Timer` (seconds the message is displayed). |
| `M2XX_MESSAGE_CLEARED` | Nothing. For M221 and M223 the cleared state occurs immediately. |

What `DRO_UPDATE` and `JOB_INFO` report is selectable, both since v5.40:

- `InboundComm.ChangeDroType(Dro.DroCoordinates coords)` - local, machine or distance-to-go.
- `InboundComm.ChangeJobInfoType(JobInfoType type)` - `CURRENT_LEVEL` or `TOP_LEVEL`.

## Answering operator prompts

`InboundComm.RespondToM2XX(bool continueCancelFlag, double input)` responds to an `M0`, `M1`,
`M200`, `M201`, `M222`, `M224` or `M225` message. `continueCancelFlag`: **false = cycle cancel,
true = cycle start**. `input` is written to the user input variable and applies only to `M222` and
`M224`; its default is 0 (API Ref, CNCPipe.InboundComm).

Answering `true` continues the job - the machine may move. `Job.ContinueExecution()` is the other
way to continue past `M0`/`M200`/`M201`, and needs Machine Parameter 440 = 256
([jobs-tools-parameters.md](jobs-tools-parameters.md#job-loading-and-running)).

## The message window

(API Ref, CNCPipe.MessageWindow)

| Call | Does |
| --- | --- |
| `GetMessages(out string[] messages)` | Messages currently in CNC12's Message Window. |
| `AddMessage(string message, int backgroundColor = 0x800000, int textColor = 0x00FFFF)` | Display a message in the status window with the given colors. |

**Colors are `0x00bbggrr`** - blue in the high byte, red in the low - not RGB
(API Ref, CNCPipe.MessageWindow).

## Drop-in user controls (WPF)

A separate assembly, `CentroidAPIUserControls`, provides WPF controls that draw CNC12 screen
elements once given a pipe (API Ref, CNC12 Main Screen example):

| Control | Notes |
| --- | --- |
| `DroDisplay` | Set `DroType`: `DRO_LOCAL` or `DRO_DISTANCE_TO_GO`. Styling: `DroTitleColor`, `LoadBarBackgroundColor`, `LoadBarBorderColor`. |
| `StatusWindow` | "Currently being developed. It is NOT INCLUDED in the library." |
| `MessageWindow` | CNC12's message window. |
| `ActiveGCodes` | Active G-codes; `InactiveGCodeColor`. |
| `GCodeDisplay` | The running program; `ActiveLineBorderColor`. |

XAML namespace and use (API Ref, CNC12 Main Screen example):

```xml
xmlns:CentroidAPIUserControls="clr-namespace:CentroidAPIUserControls;assembly=CentroidAPIUserControls"

<CentroidAPIUserControls:DroDisplay x:Name="Dro" DroTitleColor="#FFFFF700" Foreground="White"/>
<CentroidAPIUserControls:GCodeDisplay x:Name="GCodeDisplay" ActiveLineBorderColor="White"/>
```

```csharp
cnc12_pipe = new CNCPipe();
Dro.Pipe = cnc12_pipe;
GCodeDisplay.Pipe = cnc12_pipe;
```

To match CNC12's colors the example sets the window background to RGB(0, 0, 128) and foreground to
RGB(255, 247, 0), and builds with the **Release** configuration; `bin/Release` holds an `.exe` that
runs as a standalone application (API Ref, CNC12 Main Screen example). CNC12 must be running for the
controls to display correctly (same page).
