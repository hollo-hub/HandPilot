from __future__ import annotations

import logging
from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gesture_control.camera.capture import CameraCapture, CameraError
from gesture_control.camera.hand_tracker import HandTracker
from gesture_control.camera.worker import TrackingWorker
from gesture_control.gestures.types import GestureEvent, TrackingState
from gesture_control.actions.base import ActionDispatcher
from gesture_control.actions.scroll import ScrollAction
from gesture_control.actions.system import register_system_actions
from gesture_control.mappings.profile_manager import default_profile
from gesture_control.mappings.registry import MappingRegistry
from gesture_control.mappings.validator import validate_mappings

from .tracking_bridge import TrackingBridge

LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("HandPilot")
        self.resize(800, 600)
        self._project_root = project_root or _runtime_root()
        self._worker: TrackingWorker | None = None
        self._bridge = TrackingBridge()
        profile = default_profile()
        self._registry = MappingRegistry(validate_mappings(profile["mappings"]))
        self._dispatcher = ActionDispatcher()
        self._dispatcher.register("scroll", ScrollAction())
        register_system_actions(self._dispatcher)

        self.status = QLabel("Tracking is stopped. Start it when you are ready.")
        self.status.setWordWrap(True)
        self.current_gesture = QLabel("Current gesture: none")
        self.preview = QLabel("Camera preview will appear here after tracking starts.")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(640, 360)
        self.preview.setStyleSheet("background: #20242b; color: #c9d1d9;")
        self.start_button = QPushButton("Start tracking")
        self.stop_button = QPushButton("Emergency stop")
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self._start_tracking)
        self.stop_button.clicked.connect(self._stop_tracking)
        self._bridge.status_changed.connect(self._on_status)
        self._bridge.frame_received.connect(self._on_frame)
        self._bridge.gesture_received.connect(self._on_gesture)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.current_gesture)
        layout.addWidget(self.preview)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, event: object) -> None:
        self._stop_worker()
        event.accept()

    def _start_tracking(self) -> None:
        if self._worker is not None and self._worker.is_running:
            return
        model_path = self._project_root / "models" / "hand_landmarker.task"
        capture = CameraCapture()
        tracker = HandTracker(model_path)
        self._worker = TrackingWorker(
            capture,
            tracker,
            on_status=self._bridge.status_callback,
            on_frame=self._bridge.frame_callback,
            on_event=self._bridge.gesture_callback,
        )
        try:
            self._worker.start()
        except (CameraError, RuntimeError, ValueError) as exc:
            self._worker = None
            self.status.setText(f"Unable to start tracking: {exc}")
            QMessageBox.warning(self, "Tracking unavailable", str(exc))
            return
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def _stop_tracking(self) -> None:
        self._stop_worker()
        self.status.setText("Tracking is stopped.")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _stop_worker(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker = None

    def _on_status(self, state: TrackingState, message: str) -> None:
        self.status.setText(f"{state.value.replace('_', ' ').title()}: {message}")
        if state is TrackingState.LOST:
            self.stop_button.setEnabled(True)

    def _on_gesture(self, event: GestureEvent) -> None:
        self.current_gesture.setText(f"Current gesture: {event.value.replace('_', ' ')}")
        command = self._registry.command_for(event)
        if command is None:
            return
        try:
            self._dispatcher.dispatch(command)
        except (RuntimeError, ValueError) as exc:
            LOGGER.warning("Gesture action failed: %s", exc)
            self.status.setText(f"Action unavailable: {exc}")

    def _on_frame(self, frame: object) -> None:
        try:
            import cv2
            import numpy as np
        except ImportError:
            return
        if not isinstance(frame, np.ndarray) or frame.ndim != 3:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb.shape
        image = QImage(rgb.data, width, height, channels * width, QImage.Format.Format_RGB888)
        self.preview.setPixmap(QPixmap.fromImage(image).scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))


def _runtime_root() -> Path:
    bundled_root = getattr(sys, "_MEIPASS", None)
    return Path(bundled_root) if bundled_root else Path(__file__).resolve().parents[3]
