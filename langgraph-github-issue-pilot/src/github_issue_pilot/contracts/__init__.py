from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def load_contract(name: str) -> dict[str, Any]:
    resource = files(__package__).joinpath(name)
    return json.loads(resource.read_text(encoding="utf-8"))
