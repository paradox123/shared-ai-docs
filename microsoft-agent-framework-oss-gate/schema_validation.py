"""Small fail-closed validator for the JSON Schema keywords used by Gate 0."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def validate(instance: object, schema: dict[str, object]) -> list[str]:
    failures: list[str] = []

    def resolve(reference: str) -> dict[str, object]:
        value: object = schema
        for part in reference.removeprefix("#/").split("/"):
            if not isinstance(value, dict) or part not in value:
                raise KeyError(reference)
            value = value[part]
        if not isinstance(value, dict):
            raise TypeError(reference)
        return value

    def type_matches(value: object, expected: str) -> bool:
        return {
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "boolean": isinstance(value, bool),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            "null": value is None,
        }.get(expected, False)

    def walk(value: object, rule: dict[str, object], path: str) -> None:
        reference = rule.get("$ref")
        if isinstance(reference, str):
            try:
                walk(value, resolve(reference), path)
            except (KeyError, TypeError):
                failures.append(f"{path}:unresolved-ref")
            return
        expected_type = rule.get("type")
        expected_types = (
            expected_type if isinstance(expected_type, list) else [expected_type]
        )
        if expected_type is not None and not any(
            isinstance(item, str) and type_matches(value, item)
            for item in expected_types
        ):
            failures.append(f"{path}:type")
            return
        if "const" in rule and value != rule["const"]:
            failures.append(f"{path}:const")
        enum = rule.get("enum")
        if isinstance(enum, list) and value not in enum:
            failures.append(f"{path}:enum")
        if isinstance(value, str):
            if (
                isinstance(rule.get("minLength"), int)
                and len(value) < rule["minLength"]
            ):
                failures.append(f"{path}:minLength")
            pattern = rule.get("pattern")
            if isinstance(pattern, str) and re.search(pattern, value) is None:
                failures.append(f"{path}:pattern")
            if rule.get("format") == "uri" and not urlparse(value).scheme:
                failures.append(f"{path}:format-uri")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if (
                isinstance(rule.get("minimum"), (int, float))
                and value < rule["minimum"]
            ):
                failures.append(f"{path}:minimum")
            if (
                isinstance(rule.get("maximum"), (int, float))
                and value > rule["maximum"]
            ):
                failures.append(f"{path}:maximum")
        if isinstance(value, list):
            if isinstance(rule.get("minItems"), int) and len(value) < rule["minItems"]:
                failures.append(f"{path}:minItems")
            if rule.get("uniqueItems") is True:
                rendered = [repr(item) for item in value]
                if len(rendered) != len(set(rendered)):
                    failures.append(f"{path}:uniqueItems")
            item_rule = rule.get("items")
            if isinstance(item_rule, dict):
                for index, item in enumerate(value):
                    walk(item, item_rule, f"{path}[{index}]")
        if isinstance(value, dict):
            required = rule.get("required")
            if isinstance(required, list):
                for name in required:
                    if isinstance(name, str) and name not in value:
                        failures.append(f"{path}.{name}:required")
            properties = rule.get("properties")
            properties = properties if isinstance(properties, dict) else {}
            if rule.get("additionalProperties") is False:
                for name in value.keys() - properties.keys():
                    failures.append(f"{path}.{name}:additionalProperties")
            for name, child_rule in properties.items():
                if name in value and isinstance(child_rule, dict):
                    walk(value[name], child_rule, f"{path}.{name}")

    walk(instance, schema, "$")
    return failures
