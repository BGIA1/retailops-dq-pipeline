from __future__ import annotations

from pathlib import Path

from retaildq.contracts.loader import ENTITY_ORDER, load_contracts


def test_contract_loader_reads_all_required_entities() -> None:
    contracts = load_contracts(Path("contracts"))

    assert list(contracts) == ENTITY_ORDER
    assert contracts["orders"].primary_key == "order_id"
    assert contracts["order_items"].foreign_keys[0].reference_entity == "orders"
