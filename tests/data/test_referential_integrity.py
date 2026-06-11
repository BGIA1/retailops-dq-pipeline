from __future__ import annotations

import polars as pl

from retaildq.config import QualitySettings
from retaildq.contracts.loader import load_contracts
from retaildq.quality.checks import validate_entity


def test_referential_integrity_catches_missing_product() -> None:
    contracts = load_contracts("contracts")
    frame = pl.DataFrame(
        [
            {
                "order_item_id": "ITEM-0000000001",
                "order_id": "ORD-00000001",
                "product_id": "SKU-999999",
                "quantity": 1,
                "unit_price": 10.0,
                "run_id": "data-test",
            }
        ]
    )

    violations, _ = validate_entity(
        run_id="data-test",
        entity="order_items",
        frame=frame,
        contract=contracts["order_items"],
        references={
            "orders": pl.DataFrame({"order_id": ["ORD-00000001"]}),
            "products": pl.DataFrame({"product_id": ["SKU-000001"]}),
        },
        quality=QualitySettings(),
    )

    assert any(violation.rule_id == "order_items_product_id_fk" for violation in violations)
