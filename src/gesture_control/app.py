from __future__ import annotations

import logging
import sys

LOGGER = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
    except ImportError:
        LOGGER.error("PySide6 is required to start the desktop UI")
        return 1
    try:
        from .ui.main_window import MainWindow
        application = QApplication(sys.argv)
        window = MainWindow()
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        LOGGER.exception("HandPilot could not start")
        QMessageBox.critical(None, "HandPilot could not start", str(exc))
        return 1
    window.show()
    return application.exec()
