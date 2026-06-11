"""Time helpers kept in one place for deterministic tests."""

from __future__ import annotations

from datetime import UTC, date, datetime


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(tz=UTC)


def utc_today() -> date:
    """Return the current UTC date."""
    return utc_now().date()


def make_run_id(prefix: str = "run") -> str:
    """Create a compact sortable run id."""
    return f"{prefix}-{utc_now().strftime('%Y%m%d%H%M%S')}"
