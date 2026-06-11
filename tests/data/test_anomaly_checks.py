from __future__ import annotations

from datetime import date, timedelta

import polars as pl

from retaildq.quality.checks import detect_revenue_anomalies


def test_anomaly_check_catches_obvious_revenue_spike() -> None:
    today = date(2026, 1, 10)
    frame = pl.DataFrame(
        {
            "order_date": [today - timedelta(days=index) for index in range(6)],
            "revenue": [100.0, 105.0, 98.0, 102.0, 99.0, 10000.0],
        }
    )

    anomalies = detect_revenue_anomalies(frame, zscore_threshold=1.5)

    assert len(anomalies) == 1
    assert anomalies[0]["revenue"] == 10000.0
