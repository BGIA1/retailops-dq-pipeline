"""Deterministic synthetic retail data generator without PII."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from math import ceil

import polars as pl

from retaildq.utils.time import utc_today

SEGMENTS = ["consumer", "corporate", "home_office"]
REGIONS = ["north", "central", "south", "online"]
CHANNELS = ["web", "mobile", "marketplace", "store"]
ORDER_STATUSES = ["created", "paid", "shipped", "cancelled", "refunded"]
CATEGORIES = ["electronics", "grocery", "apparel", "home", "sports", "beauty"]
STORE_TYPES = ["flagship", "outlet", "fulfillment", "online"]


@dataclass(frozen=True)
class SyntheticRetailConfig:
    seed: int
    days: int
    orders: int
    invalid_rate: float
    customers: int
    products: int
    stores: int


def _id(prefix: str, value: int, width: int) -> str:
    return f"{prefix}-{value:0{width}d}"


def _weighted_choice(rng: random.Random, values: list[str], weights: list[float]) -> str:
    return rng.choices(values, weights=weights, k=1)[0]


def _make_customers(config: SyntheticRetailConfig, rng: random.Random) -> pl.DataFrame:
    today = utc_today()
    rows = [
        {
            "customer_id": _id("CUST", index, 6),
            "segment": rng.choice(SEGMENTS),
            "region": rng.choice(REGIONS),
            "created_at": today - timedelta(days=rng.randint(30, 900)),
            "is_active": rng.random() > 0.05,
        }
        for index in range(1, config.customers + 1)
    ]
    return pl.DataFrame(rows)


def _make_products(config: SyntheticRetailConfig, rng: random.Random) -> pl.DataFrame:
    rows = [
        {
            "product_id": _id("SKU", index, 6),
            "category": rng.choice(CATEGORIES),
            "base_price": round(rng.uniform(5.0, 750.0), 2),
            "is_active": rng.random() > 0.08,
        }
        for index in range(1, config.products + 1)
    ]
    return pl.DataFrame(rows)


def _make_stores(config: SyntheticRetailConfig, rng: random.Random) -> pl.DataFrame:
    regions = ["north", "central", "south"]
    rows = [
        {
            "store_id": _id("STORE", index, 3),
            "region": rng.choice(regions),
            "store_type": rng.choice(STORE_TYPES[:-1]),
        }
        for index in range(1, config.stores + 1)
    ]
    rows.append({"store_id": "STORE-999", "region": "online", "store_type": "online"})
    return pl.DataFrame(rows)


def _make_channels() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {"channel": "web", "description": "Synthetic web storefront"},
            {"channel": "mobile", "description": "Synthetic mobile app"},
            {"channel": "marketplace", "description": "Synthetic marketplace partner"},
            {"channel": "store", "description": "Synthetic physical store"},
        ]
    )


def _make_orders(
    config: SyntheticRetailConfig, rng: random.Random, stores: pl.DataFrame
) -> pl.DataFrame:
    today = utc_today()
    store_ids = stores["store_id"].to_list()
    rows = []
    for index in range(1, config.orders + 1):
        channel = _weighted_choice(rng, CHANNELS, [0.34, 0.28, 0.18, 0.20])
        store_id = "STORE-999" if channel != "store" else rng.choice(store_ids[:-1])
        order_date = today - timedelta(days=rng.randint(0, config.days - 1))
        rows.append(
            {
                "order_id": _id("ORD", index, 8),
                "customer_id": _id("CUST", rng.randint(1, config.customers), 6),
                "store_id": store_id,
                "channel": channel,
                "order_status": _weighted_choice(
                    rng, ORDER_STATUSES, [0.08, 0.45, 0.32, 0.10, 0.05]
                ),
                "order_date": order_date,
                "created_at": datetime.combine(order_date, time(hour=rng.randint(0, 23))),
            }
        )
    return pl.DataFrame(rows)


def _make_order_items(
    config: SyntheticRetailConfig, rng: random.Random, orders: pl.DataFrame, products: pl.DataFrame
) -> pl.DataFrame:
    product_ids = products["product_id"].to_list()
    price_map = dict(
        zip(products["product_id"].to_list(), products["base_price"].to_list(), strict=True)
    )
    rows = []
    item_index = 1
    for order_id in orders["order_id"].to_list():
        for _ in range(rng.randint(1, 4)):
            product_id = rng.choice(product_ids)
            rows.append(
                {
                    "order_item_id": _id("ITEM", item_index, 10),
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": rng.randint(1, 6),
                    "unit_price": round(float(price_map[product_id]) * rng.uniform(0.85, 1.15), 2),
                }
            )
            item_index += 1
    return pl.DataFrame(rows)


def _pick_indices(rng: random.Random, frame: pl.DataFrame, count: int) -> list[int]:
    if frame.height == 0 or count <= 0:
        return []
    return rng.sample(range(frame.height), min(count, frame.height))


def _mutate_cell(frame: pl.DataFrame, row_index: int, column: str, value: object) -> pl.DataFrame:
    updates = [
        pl.when(pl.arange(0, pl.len()) == row_index)
        .then(pl.lit(value))
        .otherwise(pl.col(column))
        .alias(column)
    ]
    return frame.with_columns(updates)


def inject_invalid_records(
    frames: dict[str, pl.DataFrame], config: SyntheticRetailConfig, rng: random.Random
) -> dict[str, pl.DataFrame]:
    """Inject deterministic bad records that exercise quality rules."""
    invalid_count = max(1, ceil(config.orders * config.invalid_rate))
    per_case = max(1, invalid_count // 12)

    customers = frames["customers"]
    products = frames["products"]
    stores = frames["stores"]
    orders = frames["orders"]
    order_items = frames["order_items"]

    if orders.height:
        duplicate_rows = orders.head(per_case)
        orders = pl.concat([orders, duplicate_rows], how="vertical")
        for idx in _pick_indices(rng, orders, per_case):
            orders = _mutate_cell(orders, idx, "customer_id", "CUST-999999")
        for idx in _pick_indices(rng, orders, per_case):
            orders = _mutate_cell(orders, idx, "order_status", "lost_in_space")
        for idx in _pick_indices(rng, orders, per_case):
            orders = _mutate_cell(orders, idx, "channel", "fax")
        for idx in _pick_indices(rng, orders, per_case):
            orders = _mutate_cell(orders, idx, "order_date", utc_today() + timedelta(days=7))
        for idx in _pick_indices(rng, orders, 1):
            orders = _mutate_cell(orders, idx, "customer_id", None)

    if order_items.height:
        for idx in _pick_indices(rng, order_items, per_case):
            order_items = _mutate_cell(order_items, idx, "product_id", "SKU-999999")
        for idx in _pick_indices(rng, order_items, per_case):
            order_items = _mutate_cell(order_items, idx, "quantity", 0)
        for idx in _pick_indices(rng, order_items, per_case):
            order_items = _mutate_cell(order_items, idx, "unit_price", -3.50)
        for idx in _pick_indices(rng, order_items, per_case):
            order_items = _mutate_cell(order_items, idx, "order_id", "ORD-99999999")
        for idx in _pick_indices(rng, order_items, 1):
            order_items = _mutate_cell(order_items, idx, "product_id", None)

    if products.height:
        for idx in _pick_indices(rng, products, per_case):
            products = _mutate_cell(products, idx, "base_price", -1.0)

    if stores.height:
        for idx in _pick_indices(rng, stores, 1):
            stores = _mutate_cell(stores, idx, "region", "antarctica")

    return {
        "channels": frames["channels"],
        "customers": customers,
        "products": products,
        "stores": stores,
        "orders": orders,
        "order_items": order_items,
    }


def generate_synthetic_retail_data(config: SyntheticRetailConfig) -> dict[str, pl.DataFrame]:
    """Generate all RetailDQ raw entities."""
    rng = random.Random(config.seed)
    customers = _make_customers(config, rng)
    products = _make_products(config, rng)
    stores = _make_stores(config, rng)
    channels = _make_channels()
    orders = _make_orders(config, rng, stores)
    order_items = _make_order_items(config, rng, orders, products)
    frames = {
        "channels": channels,
        "customers": customers,
        "products": products,
        "stores": stores,
        "orders": orders,
        "order_items": order_items,
    }
    if config.invalid_rate > 0:
        frames = inject_invalid_records(frames, config, rng)
    return frames
