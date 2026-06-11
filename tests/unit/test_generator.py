from __future__ import annotations

from retaildq.generator.synthetic_retail import (
    SyntheticRetailConfig,
    generate_synthetic_retail_data,
)


def test_generator_is_deterministic() -> None:
    config = SyntheticRetailConfig(
        seed=100,
        days=3,
        orders=15,
        invalid_rate=0.0,
        customers=8,
        products=6,
        stores=2,
    )

    first = generate_synthetic_retail_data(config)
    second = generate_synthetic_retail_data(config)

    assert first["orders"].equals(second["orders"])
    assert first["order_items"].equals(second["order_items"])
    assert "email" not in first["customers"].columns


def test_generator_injects_expected_invalid_cases() -> None:
    config = SyntheticRetailConfig(
        seed=101,
        days=3,
        orders=30,
        invalid_rate=0.2,
        customers=8,
        products=6,
        stores=2,
    )

    frames = generate_synthetic_retail_data(config)

    assert "CUST-999999" in frames["orders"]["customer_id"].to_list()
    assert "SKU-999999" in frames["order_items"]["product_id"].to_list()
    assert frames["order_items"].filter(frames["order_items"]["quantity"] <= 0).height >= 1
