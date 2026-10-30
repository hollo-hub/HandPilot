# HandPilot

HandPilot is an existing local-first webcam gesture controller for Windows and
Linux. It processes camera frames locally with OpenCV and MediaPipe; it does
not save webcam video or require an account.

## Why Python?

Python is used for the application layer because the official MediaPipe Tasks
Python API, OpenCV camera integration, PySide6 desktop UI, and cross-platform
PyInstaller packaging are mature and testable together. The release is **not a
Python script pretending to be an app**: GitHub Actions packages the same
source into native platform executables. Python is still required if you run
from source; end users download the packaged executable.

## Gestures in v0.1.1

| Gesture | Action |
| --- | --- |
| Deliberate hand movement up/down | Scroll up/down |
| Open palm | Media play/pause (one trigger per pose) |
| Thumb/index pinch | Volume up (one trigger per pinch) |
| Deliberate swipe left/right | Browser back/forward |

Movement events now pass through the runtime worker. Static actions are
edge-triggered so they do not repeat once per camera frame. Tracking jumps are
rejected, tracking loss stops actions, and the emergency stop is always
available.

## Download

Use the separate [HandPilot-downloads repository](https://github.com/hollo-hub/HandPilot-downloads)
for packaged releases:

- [Windows HandPilot.exe](https://github.com/hollo-hub/HandPilot-downloads/releases/latest)
- [Linux HandPilot tarball](https://github.com/hollo-hub/HandPilot-downloads/releases/latest)

The Linux build targets x86_64 desktop Linux. It requires a graphical desktop
session and a webcam. On X11, `pynput` requires a valid `DISPLAY`; on Wayland,
input injection may be limited by the compositor. See the [pynput Linux
limitations](https://pynput.readthedocs.io/en/latest/limitations.html).

## Run from source

Python 3.11 or 3.12 is supported:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest
python -m gesture_control
```

On Windows, install `.[test,windows,build]`. On Linux, install `.[test,build]`.
The included `models/hand_landmarker.task` is loaded locally; no model download
occurs at runtime. Press **Start tracking** to activate the camera.

## Feedback checklist

When reporting a problem, include:

1. OS version and whether you used the packaged build or source.
2. Webcam model and whether the preview appeared.
3. The exact gesture attempted and the action that occurred.
4. Whether the app showed an error or remained on “looking for a hand”.
5. For Linux, desktop session (`X11` or `Wayland`) and the value of `DISPLAY`.

Do not add arbitrary shell commands as gesture actions. New actions must be
implemented behind the validated action boundary.
