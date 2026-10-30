from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pynput.mouse import Controller


class ScrollAction:
    def __init__(self, controller: Any | None = None, max_step: int = 8) -> None:
        if max_step < 1:
            raise ValueError("max_step must be positive")
        self.controller = controller
        self.max_step = max_step

    def __call__(self, parameters: dict[str, object]) -> None:
        raw_steps = parameters.get("steps", 0)
        if not isinstance(raw_steps, int):
            raise ValueError("scroll steps must be an integer")
        steps = max(-self.max_step, min(self.max_step, raw_steps))
        if not steps:
            return
        controller = self.controller
        if controller is None:
            try:
                from pynput.mouse import Controller
            except ImportError as exc:
                raise RuntimeError("pynput is required for scroll actions") from exc
            controller = Controller()
        controller.scroll(0, steps)
