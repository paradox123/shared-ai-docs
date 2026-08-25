from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def load_contract(name: str) -> dict[str, Any]:
    resource = files(__package__).joinpath(name)
    return json.loads(resource.read_text(encoding="utf-8"))


def load_codex_output_contract(name: str) -> dict[str, Any]:
    """Return the canonical contract projected onto Codex's supported schema subset."""

    return _codex_output_schema(load_contract(name))


def _codex_output_schema(value: Any) -> Any:
    if isinstance(value, list):
        return [_codex_output_schema(item) for item in value]
    if not isinstance(value, dict):
        return value

    projected: dict[str, Any] = {}
    for key, item in value.items():
        if key in {"allOf", "if", "then", "else"}:
            continue
        projected["anyOf" if key == "oneOf" else key] = _codex_output_schema(item)
    return projected
