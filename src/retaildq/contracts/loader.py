"""YAML data contract loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ENTITY_ORDER = ["channels", "customers", "products", "stores", "orders", "order_items"]


@dataclass(frozen=True)
class ColumnContract:
    name: str
    type: str
    nullable: bool
    accepted_values: list[str] = field(default_factory=list)
    minimum: float | int | None = None
    maximum: float | int | None = None
    pattern: str | None = None


@dataclass(frozen=True)
class ForeignKeyContract:
    column: str
    reference_entity: str
    reference_column: str


@dataclass(frozen=True)
class QualityRuleContract:
    rule_id: str
    rule_type: str
    column: str
    severity: str = "error"
    minimum: float | int | None = None
    maximum: float | int | None = None


@dataclass(frozen=True)
class EntityContract:
    entity: str
    description: str
    primary_key: str
    columns: dict[str, ColumnContract]
    foreign_keys: list[ForeignKeyContract] = field(default_factory=list)
    quality_rules: list[QualityRuleContract] = field(default_factory=list)


def _column_from_yaml(name: str, payload: dict[str, Any]) -> ColumnContract:
    return ColumnContract(
        name=name,
        type=str(payload["type"]),
        nullable=bool(payload.get("nullable", True)),
        accepted_values=list(payload.get("accepted_values", [])),
        minimum=payload.get("min"),
        maximum=payload.get("max"),
        pattern=payload.get("pattern"),
    )


def load_contract(path: Path) -> EntityContract:
    with path.open("r", encoding="utf-8") as handle:
        payload: dict[str, Any] = yaml.safe_load(handle) or {}

    columns = {
        name: _column_from_yaml(name, column_payload)
        for name, column_payload in payload.get("columns", {}).items()
    }
    foreign_keys = [
        ForeignKeyContract(
            column=item["column"],
            reference_entity=item["references"]["entity"],
            reference_column=item["references"]["column"],
        )
        for item in payload.get("foreign_keys", [])
    ]
    quality_rules = [
        QualityRuleContract(
            rule_id=item["rule_id"],
            rule_type=item["type"],
            column=item["column"],
            severity=item.get("severity", "error"),
            minimum=item.get("min"),
            maximum=item.get("max"),
        )
        for item in payload.get("quality", [])
    ]
    return EntityContract(
        entity=payload["entity"],
        description=payload.get("description", ""),
        primary_key=payload["primary_key"],
        columns=columns,
        foreign_keys=foreign_keys,
        quality_rules=quality_rules,
    )


def load_contracts(contract_dir: str | Path = "contracts") -> dict[str, EntityContract]:
    directory = Path(contract_dir)
    contracts = {path.stem: load_contract(path) for path in sorted(directory.glob("*.yaml"))}
    missing = [entity for entity in ENTITY_ORDER if entity not in contracts]
    if missing:
        raise FileNotFoundError(f"Missing contracts: {', '.join(missing)}")
    return {entity: contracts[entity] for entity in ENTITY_ORDER}
