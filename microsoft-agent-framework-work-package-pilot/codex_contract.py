"""Canonical validation and the separately probed Codex output contract."""
import json
from pathlib import Path

CANONICAL_PATH = Path(__file__).parent / 'contracts/worker-result-v3.json'


def canonical_schema():
    return json.loads(CANONICAL_PATH.read_text())


def endpoint_schema():
    # This is a transport projection, not a substitute for canonical validation.
    # Keep object property names separate from schema keyword processing.
    def project(rule):
        result = {}
        for key, value in rule.items():
            if key in {'$schema', '$id', 'allOf', 'if', 'then', 'minLength',
                       'minItems', 'minimum', 'pattern'}:
                continue
            if key in {'properties', '$defs'}:
                result[key] = {name: project(child) for name, child in value.items()}
            elif key == 'items':
                result[key] = project(value)
            elif key == 'oneOf':
                result['anyOf'] = [project(child) for child in value]
            elif key == 'const':
                result['enum'] = [value]
            else:
                result[key] = value
        return result
    return project(canonical_schema())


def validate_result(result):
    from jsonschema import Draft202012Validator
    schema = canonical_schema()
    Draft202012Validator.check_schema(schema)
    return sorted('.'.join(map(str, error.absolute_path)) + ':' + error.validator
                  for error in Draft202012Validator(schema).iter_errors(result))
if __name__ == '__main__':
    import sys
    try:
        valid = not validate_result(json.load(sys.stdin))
    except (ValueError, TypeError):
        valid = False
    print('valid' if valid else 'invalid')
    raise SystemExit(0 if valid else 2)
