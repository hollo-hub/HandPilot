from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Event, Lock, Thread, current_thread
from typing import Any


@dataclass(frozen=True)
class CameraFrame:
    image: Any
    timestamp: float


class CameraError(RuntimeError):
    """Raised when a camera cannot be opened or read."""


class CameraCapture:
    """Bounded latest-frame camera reader; never queues stale frames."""

    def __init__(
        self,
        index: int = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
    ) -> None:
        if index < 0 or width < 1 or height < 1 or fps < 1:
            raise ValueError("camera settings must be positive")
        self.index = index
        self.width = width
        self.height = height
        self.fps = fps
        self._capture: Any | None = None
        self._latest: CameraFrame | None = None
        self._lock = Lock()
        self._stop = Event()
        self._thread: Thread | None = None
        self.error: str | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        try:
            import cv2
        except ImportError as exc:
            raise CameraError("OpenCV is required for camera capture") from exc
        capture = cv2.VideoCapture(self.index)
        if not capture.isOpened():
            capture.release()
            raise CameraError(f"camera {self.index} could not be opened")
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        capture.set(cv2.CAP_PROP_FPS, self.fps)
        self._capture = capture
        self.error = None
        self._stop.clear()
        self._thread = Thread(target=self._read_loop, name="camera-capture", daemon=True)
        self._thread.start()

    def read_latest(self) -> CameraFrame | None:
        with self._lock:
            return self._latest

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread is not current_thread():
            thread.join(timeout=2)
        self._thread = None
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        with self._lock:
            self._latest = None

    def _read_loop(self) -> None:
        while not self._stop.is_set():
            capture = self._capture
            if capture is None:
                return
            ok, image = capture.read()
            if not ok:
                self.error = "camera stopped returning frames"
                return
            with self._lock:
                self._latest = CameraFrame(image=image, timestamp=time.monotonic())
