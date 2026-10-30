from __future__ import annotations

import logging
import sys


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        logging.error("PySide6 is required to start the desktop UI")
        return 1
    from .ui.main_window import MainWindow

    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()
