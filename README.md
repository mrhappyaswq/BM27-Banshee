# BANSHEE ESP32 MicroPython starter

This is a new Windows + VS Code project for a **WROOM Dev Board 32S**. The
`device/` contains MicroPython code for the ESP32. `samples/` preserves the
two original GitHub branch snapshots; those scripts run on a laptop or
Raspberry Pi, **not on the ESP32**. `tests/` contains host-side parser tests,
`docs/` contains the porting audit, and `.vscode/` contains editor tasks.
`archive/` holds unrelated Git fragments recovered from the flattened folder;
it is ignored by Git.

The first ESP32 milestone is deliberately read-only: confirm USB upload, then
receive valid MAVLink HEARTBEAT packets from a Pixhawk. It does not arm, fly,
land, send MAVLink messages, or perform ArUco vision. See
[`docs/porting-audit.md`](docs/porting-audit.md).

## 1. Install the Windows tools

Install [VS Code](https://code.visualstudio.com/download),
[Python 3](https://www.python.org/downloads/) and
[Git](https://git-scm.com/download/win). In VS Code, open the **entire project
folder**, then open **Terminal > New Terminal** (PowerShell) and run:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install mpremote esptool
.\.venv\Scripts\python.exe -m mpremote connect list
```

The `py -3` command comes from the Windows Python installation. Select
**Install Recommended Extensions** when VS Code offers it. These add Python
editing, a status-bar upload button, and optional GitHub pull-request tools.
The built-in Git support handles commits and pushes without an extension.

## 2. Install MicroPython firmware once

Connect the ESP32 to the laptop with a **USB data cable**. Download the stable
`.bin` from the official [ESP32 / WROOM firmware page](https://micropython.org/download/ESP32_GENERIC/).
Confirm that your module has **at least 4 MiB flash**, as required by that
generic image. Use the board's COM port from Device Manager or the `mpremote
connect list` output. Replace `COM4` and the `.bin` path below:

```powershell
.\.venv\Scripts\python.exe -m esptool --port COM4 erase-flash
.\.venv\Scripts\python.exe -m esptool --port COM4 --baud 460800 write-flash 0x1000 "C:\path\to\ESP32_GENERIC-firmware.bin"
.\.venv\Scripts\python.exe -m mpremote connect COM4 repl
```

The erase step clears the board's existing firmware and files. Follow the
firmware page's board instructions if your exact module needs a different
image. The REPL should display a `>>>` prompt. Leave it with **Ctrl+]** before
using the upload button. If the firmware tool cannot connect, use the board's
BOOT and RESET buttons as described in the official ESP32 tutorial.

## 3. Upload with one click

Click **Upload ESP32** in the VS Code status bar. It copies both files in
`device/` to the ESP32 filesystem as `mavlink_rx.py` and `main.py`, then hard
resets the board. `main.py` runs again after every reset. The same task runs
with **Ctrl+Shift+B** or **Terminal > Run Build Task**.

Click **ESP32 Monitor** to read its output. With no Pixhawk connected, expect
`BANSHEE ESP32 MicroPython check`, then an `Alive` report every five seconds.
Leave the monitor with **Ctrl+]** before uploading again. `mpremote` holds the
serial port while the monitor is open.

The task uses `connect auto`, so plug in only the target USB serial device for
the initial setup. If your laptop has several USB serial devices, change
`"auto"` in both VS Code tasks to your board's port such as `"COM4"`.

This button uploads Python files. Installing the MicroPython `.bin` above is
a separate, one-time firmware operation. VS Code's generic Python **Run**
triangle executes desktop Python; use **Upload ESP32** for this project.

## 4. Check Pixhawk telemetry

For a first receive-only test with an ArduPilot Pixhawk TELEM port:

| Pixhawk TELEM signal | ESP32 Dev Board 32S |
| --- | --- |
| TX (3.3 V UART signal) | GPIO32 (UART1 RX) |
| GND | GND |

Leave ESP32 GPIO33 (UART1 TX) disconnected for this test. Power the ESP32 via
USB and check the **exact Pixhawk model's TELEM pinout and voltage** before
wiring. Do not connect a 5 V signal directly to an ESP32 GPIO. Configure the
chosen Pixhawk serial port for MAVLink 2 and **57600 baud**, matching
`device/main.py`. On ArduPilot, this is typically `SERIALx_PROTOCOL=2` and
`SERIALx_BAUD=57`; determine `x` from the autopilot's port mapping. When the
link works, the monitor prints `HEARTBEAT` with system, component and mode
fields. If UART bytes increase without valid heartbeats, check baud, serial
protocol, and wiring.

No props should be fitted for bench wiring and software checks.

## 5. Put this new project on GitHub from VS Code

Open the project's
**Source Control** view (Ctrl+Shift+G), stage the files, enter a commit message
such as `Initial ESP32 MicroPython starter`, and select **Commit**. If VS Code
asks, configure your Git author name and email. Then select **Publish to
GitHub**, sign in through the browser prompt, choose the repository name
`banshee-esp32-micropython`, and choose public visibility if your team should
be able to read it without invitations. Open the resulting GitHub page and
verify `README.md`, `device/`, and `samples/` appear. Subsequent work is
**edit → stage → commit → Sync Changes**. Teammates with write access can push
branches and open pull requests.

The branch snapshots contain no license file. Check that you have permission
to republish them before choosing a public repository, and include an
appropriate license once the project owners decide.

## Samples and tests

The unchanged desktop source snapshots in `samples/` are from:

- [`Michael`](https://github.com/khristianjc/BANSHEE-AVIONICS-2025/tree/Michael), commit `3ce4dc32bd1f1e1e25b322b28c3096e6d774eb34`
- [`precision_landing`](https://github.com/khristianjc/BANSHEE-AVIONICS-2025/tree/precision_landing), commit `62e8d8cd391cb2ea30ccffe520f02c15d90c6572`

Run the protocol parser checks on the laptop with:

```powershell
py -3 -m unittest discover -s tests -v
```

The parser tests do not validate the physical Pixhawk connection or flight
behavior. Verify the hardware link on the bench before changing any control
code.
