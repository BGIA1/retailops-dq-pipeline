from __future__ import annotations

import pytest

from retaildq.quality.thresholds import QualityThresholdError, raise_if_threshold_failed


def test_quality_threshold_failure_raises() -> None:
    with pytest.raises(QualityThresholdError):
        raise_if_threshold_failed(False, invalid_rate=0.25, max_invalid_rate=0.10)
