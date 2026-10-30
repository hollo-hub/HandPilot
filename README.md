# Gesture Control — HandPilot

HandPilot is a local-first Windows desktop controller that uses a webcam to
recognize deliberate hand gestures. Webcam frames are processed locally and
are not saved by default.

## Included gestures

The safe Reading profile includes:

| Gesture | Default action |
| --- | --- |
| Move hand up/down | Scroll up/down |
| Open palm | Media play/pause |
| Pinch | Volume up |
| Swipe left/right | Browser back/forward |

Every action is bounded and validated. No arbitrary scripts or shell commands
can be placed in a profile. Tracking must be started manually and emergency
stop is always available.

## Current production milestone

The project currently contains the tested foundation for:

- explicit tracking state transitions with activation hold, release grace,
  cooldown, tracking loss, and emergency stop;
- EMA smoothing and hysteresis primitives;
- validated gesture-to-action mappings;
- atomic JSON profile persistence with schema validation;
- an action dispatcher boundary and bounded scroll adapter;
- a PySide6 dashboard with live preview, tracking state, current gesture, and
  explicit Start/Emergency Stop controls;
- a bounded latest-frame camera reader, lazy MediaPipe Tasks adapter, and
  lifecycle-safe tracking worker.

- a motion detector, mapping registry, and action dispatcher for scroll, media,
  volume, and validated keyboard shortcuts.

## Development setup

On Windows 10/11 with Python 3.11:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,windows,build]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m gesture_control
```

Before starting tracking, place the official MediaPipe Hand Landmarker model
at `models/hand_landmarker.task`. The app intentionally reports a clear model
error instead of downloading or executing anything silently.

## Windows executable

The official model is included in the repository at
`models/hand_landmarker.task`. On Windows, run:

```powershell
.\build_windows.ps1
```

The executable is created at
`dist\GestureControl.exe`. A webcam is required, and Windows
camera permissions must allow the application to use it. Tracking is opt-in:
the camera does not start until **Start tracking** is pressed.

## Feedback to send after testing

Please include:

1. Windows version and webcam model.
2. Whether the app opens and the preview appears.
3. Which gestures worked, failed, or triggered accidentally.
4. Whether scrolling speed feels too slow or too fast.
5. Any error text from the dashboard.

Do not add arbitrary shell commands as gesture actions. New actions must be
implemented behind the action boundary and validated before they are exposed
to profiles.
