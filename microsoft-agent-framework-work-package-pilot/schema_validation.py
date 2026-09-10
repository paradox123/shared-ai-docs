"""Fail-closed validator for the JSON Schema keywords used by this gate."""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urlparse


def validate(instance: object, schema: dict[str, object]) -> list[str]:
    failures: list[str] = []

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
        all_of = rule.get("allOf")
        if isinstance(all_of, list):
            for child_rule in all_of:
                if isinstance(child_rule, dict):
                    walk(value, child_rule, path)
        condition = rule.get("if")
        then_rule = rule.get("then")
        if isinstance(condition, dict) and isinstance(then_rule, dict):
            failure_count = len(failures)
            walk(value, condition, path)
            condition_matches = len(failures) == failure_count
            del failures[failure_count:]
            if condition_matches:
                walk(value, then_rule, path)
        expected_type = rule.get("type")
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if expected_type is not None and not any(
            isinstance(item, str) and type_matches(value, item) for item in expected_types
        ):
            failures.append(f"{path}:type")
            return
        if "const" in rule and value != rule["const"]:
            failures.append(f"{path}:const")
        enum = rule.get("enum")
        if isinstance(enum, list) and value not in enum:
            failures.append(f"{path}:enum")
        if isinstance(value, str):
            if isinstance(rule.get("minLength"), int) and len(value) < rule["minLength"]:
                failures.append(f"{path}:minLength")
            pattern = rule.get("pattern")
            if isinstance(pattern, str) and re.search(pattern, value) is None:
                failures.append(f"{path}:pattern")
            if rule.get("format") == "uri" and not urlparse(value).scheme:
                failures.append(f"{path}:format-uri")
            if rule.get("format") == "uuid" and re.fullmatch(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                value,
            ) is None:
                failures.append(f"{path}:format-uuid")
            if rule.get("format") == "date":
                try:
                    parsed_date = date.fromisoformat(value)
                except ValueError:
                    failures.append(f"{path}:format-date")
                else:
                    if parsed_date.isoformat() != value:
                        failures.append(f"{path}:format-date")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            minimum = rule.get("minimum")
            if isinstance(minimum, (int, float)) and value < minimum:
                failures.append(f"{path}:minimum")
        if isinstance(value, list):
            minimum_items = rule.get("minItems")
            maximum_items = rule.get("maxItems")
            if isinstance(minimum_items, int) and len(value) < minimum_items:
                failures.append(f"{path}:minItems")
            if isinstance(maximum_items, int) and len(value) > maximum_items:
                failures.append(f"{path}:maxItems")
            if rule.get("uniqueItems") is True:
                rendered = [repr(item) for item in value]
                if len(rendered) != len(set(rendered)):
                    failures.append(f"{path}:uniqueItems")
            item_rule = rule.get("items")
            if isinstance(item_rule, dict):
                for index, item in enumerate(value):
                    walk(item, item_rule, f"{path}[{index}]")
        if isinstance(value, dict):
            minimum_properties = rule.get("minProperties")
            if isinstance(minimum_properties, int) and len(value) < minimum_properties:
                failures.append(f"{path}:minProperties")
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
