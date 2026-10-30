# HandPilot

HandPilot is a local-first webcam gesture controller for Windows and Linux.
It processes camera frames locally with OpenCV and MediaPipe and does not save
webcam video or require an account.

## v0.1.3 launch fix

This release fixes a startup failure caused by importing the platform input
backend while the window was being created. HandPilot now starts its UI before
loading `pynput`; input backend failures are reported when an action is used,
not hidden as a silent launch failure. Startup errors are also shown in a
visible dialog and logged.

## Gestures

- Deliberate hand movement up/down: scroll up/down
- Open palm: media play/pause, one trigger per pose
- Thumb/index pinch: volume up, one trigger per pinch
- Deliberate swipe left/right: browser back/forward

## Downloads

Use [HandPilot-downloads](https://github.com/hollo-hub/HandPilot-downloads):

- [Windows HandPilot.exe](https://github.com/hollo-hub/HandPilot-downloads/releases/latest)
- [Linux x86_64 tarball](https://github.com/hollo-hub/HandPilot-downloads/releases/latest)

The Linux build requires an x86_64 graphical desktop and webcam. On X11,
`pynput` requires a valid `DISPLAY`; on Wayland, input injection may be
limited by the compositor. The Linux artifact is a portable PyInstaller
application, not a Debian/RPM package.

## Why Python?

Python is the application layer because MediaPipe Tasks, OpenCV, PySide6, and
PyInstaller provide a mature, testable desktop stack. End users download a
packaged native executable; Python is only needed when running from source.

## Troubleshooting

1. Extract the Linux tarball completely before launching.
2. Start from a terminal so errors remain visible:
   `./HandPilot`
3. Confirm the file is executable: `chmod +x HandPilot`.
4. Check camera permissions and close other camera applications.
5. On Linux/X11, check `echo "$DISPLAY"`; on Wayland, test from an XWayland
   desktop session if input actions do not work.
6. On Windows, allow camera access and launch `HandPilot.exe` directly.

Press **Start tracking** to activate the camera. The app does not start camera
tracking implicitly.

## Source development

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest
python -m gesture_control
```

The existing source project includes the official local
`models/hand_landmarker.task`; no model download occurs at runtime.
