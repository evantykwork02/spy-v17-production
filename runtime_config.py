from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_CAPITAL = 10000.0
DEFAULT_CURRENCY = "SGD"


@dataclass(frozen=True)
class RuntimeConfig:
    capital: float = DEFAULT_CAPITAL
    currency: str = DEFAULT_CURRENCY
    fractional_shares: bool = False
    show_position_sizing: bool = True
    capital_injections: list[dict[str, Any]] = field(default_factory=list)


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _coerce_currency(value: Any) -> str:
    currency = str(value or DEFAULT_CURRENCY).strip().upper()
    return currency or DEFAULT_CURRENCY


def resolve_currency(*values: Any, default: str = DEFAULT_CURRENCY) -> str:
    for value in values:
        currency = str(value or "").strip().upper()
        if currency:
            return currency
    return _coerce_currency(default)


def load_runtime_config(config_path: str | Path | None = None) -> RuntimeConfig:
    root = Path(__file__).resolve().parent
    path = Path(config_path) if config_path is not None else root / "config.json"

    raw: dict[str, Any] = {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        raw = {}

    capital_injections = raw.get("capital_injections", [])
    if not isinstance(capital_injections, list):
        capital_injections = []

    return RuntimeConfig(
        capital=_coerce_float(raw.get("capital"), DEFAULT_CAPITAL),
        currency=_coerce_currency(raw.get("currency")),
        fractional_shares=bool(raw.get("fractional_shares", False)),
        show_position_sizing=bool(raw.get("show_position_sizing", True)),
        capital_injections=capital_injections,
    )
