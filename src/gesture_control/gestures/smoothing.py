from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExponentialSmoother:
    """EMA smoother with a bounded coefficient and no hidden time source."""

    alpha: float = 0.35
    _value: float | None = None

    def __post_init__(self) -> None:
        if not 0.0 < self.alpha <= 1.0:
            raise ValueError("alpha must be greater than 0 and at most 1")

    @property
    def value(self) -> float | None:
        return self._value

    def update(self, sample: float) -> float:
        self._value = sample if self._value is None else (
            self.alpha * sample + (1.0 - self.alpha) * self._value
        )
        return self._value

    def reset(self) -> None:
        self._value = None


@dataclass
class Hysteresis:
    enter_threshold: float
    exit_threshold: float

    def __post_init__(self) -> None:
        if self.enter_threshold < self.exit_threshold:
            raise ValueError("enter threshold must be at least exit threshold")
        self.active = False

    def update(self, value: float) -> bool:
        if self.active:
            if value <= self.exit_threshold:
                self.active = False
        elif value >= self.enter_threshold:
            self.active = True
        return self.active

    def reset(self) -> None:
        self.active = False
