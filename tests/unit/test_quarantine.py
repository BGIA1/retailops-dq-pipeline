from __future__ import annotations

from retaildq.quality.quarantine import payload_to_json, violation_from_row, violations_to_frame


def test_quarantine_serializes_payload_with_traceability() -> None:
    violation = violation_from_row(
        run_id="unit",
        entity="orders",
        record_id="ORD-00000001",
        row_index=0,
        rule_id="orders_customer_fk",
        rule_name="referential integrity",
        severity="error",
        rejection_reason="customer missing",
        row={"order_id": "ORD-00000001", "customer_id": "CUST-999999"},
    )

    frame = violations_to_frame([violation])

    assert frame.height == 1
    assert frame["record_id"][0] == "ORD-00000001"
    assert "CUST-999999" in payload_to_json(violation.original_payload)
