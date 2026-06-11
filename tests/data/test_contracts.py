from __future__ import annotations

from retaildq.contracts.loader import load_contracts


def test_contract_foreign_keys_reference_known_entities_and_columns() -> None:
    contracts = load_contracts("contracts")

    for contract in contracts.values():
        for fk in contract.foreign_keys:
            assert fk.reference_entity in contracts
            assert fk.reference_column in contracts[fk.reference_entity].columns
            assert fk.column in contract.columns
