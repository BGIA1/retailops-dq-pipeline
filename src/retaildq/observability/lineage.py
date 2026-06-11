"""Lineage summaries for generated artifacts."""

from __future__ import annotations

import json
from pathlib import Path

LINEAGE = {
    "customers": ["raw.customers", "silver.customers"],
    "products": ["raw.products", "silver.products"],
    "stores": ["raw.stores", "silver.stores"],
    "channels": ["raw.channels", "silver.channels"],
    "orders": ["raw.orders", "silver.orders"],
    "order_items": ["raw.order_items", "silver.order_items"],
    "revenue_by_day": ["silver.orders", "silver.order_items", "gold.revenue_by_day"],
    "revenue_by_channel": ["silver.orders", "silver.order_items", "gold.revenue_by_channel"],
    "revenue_by_store": [
        "silver.orders",
        "silver.order_items",
        "silver.stores",
        "gold.revenue_by_store",
    ],
    "top_products": [
        "silver.order_items",
        "silver.products",
        "gold.top_products_by_revenue",
        "gold.top_products_by_quantity",
    ],
    "data_quality": ["raw.*", "quarantine.*", "gold.data_quality_pass_fail_summary"],
}


def write_lineage(output_dir: Path, run_id: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {"run_id": run_id, "lineage": LINEAGE}
    (output_dir / "lineage.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [f"# RetailDQ Lineage - {run_id}", ""]
    for artifact, nodes in LINEAGE.items():
        lines.append(f"- `{artifact}`: " + " -> ".join(f"`{node}`" for node in nodes))
    (output_dir / "lineage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
