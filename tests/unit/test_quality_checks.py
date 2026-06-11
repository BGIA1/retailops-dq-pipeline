from __future__ import annotations

from datetime import datetime

import polars as pl

from retaildq.config import QualitySettings
from retaildq.contracts.loader import load_contracts
from retaildq.quality.checks import validate_entity


def test_quality_checks_detect_null_numeric_and_catalog_failures() -> None:
    contracts = load_contracts("contracts")
    frame = pl.DataFrame(
        [
            {
                "order_id": "ORD-00000001",
                "customer_id": None,
                "store_id": "STORE-001",
                "channel": "fax",
                "order_status": "bad",
                "order_date": datetime(2099, 1, 1).date(),
                "created_at": datetime(2099, 1, 1),
                "run_id": "unit",
            }
        ]
    )
    refs = {
        "customers": pl.DataFrame({"customer_id": ["CUST-000001"]}),
        "stores": pl.DataFrame({"store_id": ["STORE-001"]}),
        "channels": pl.DataFrame({"channel": ["web"]}),
    }

    violations, summaries = validate_entity(
        run_id="unit",
        entity="orders",
        frame=frame,
        contract=contracts["orders"],
        references=refs,
        quality=QualitySettings(),
    )

    assert {violation.rule_name for violation in violations} >= {
        "null check",
        "accepted values",
        "future date check",
        "referential integrity",
    }
    assert any(summary.status == "fail" for summary in summaries)
