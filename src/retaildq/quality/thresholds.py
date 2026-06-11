"""Quality threshold enforcement."""

from __future__ import annotations


class QualityThresholdError(RuntimeError):
    """Raised when invalid record rate exceeds configured tolerance."""


def raise_if_threshold_failed(passed: bool, invalid_rate: float, max_invalid_rate: float) -> None:
    if not passed:
        raise QualityThresholdError(
            f"Data quality threshold failed: invalid_rate={invalid_rate:.4f}, "
            f"max_invalid_rate={max_invalid_rate:.4f}"
        )
