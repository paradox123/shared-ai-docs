#!/usr/bin/env python3
"""Read only the local task metadata index; never certify task identity."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from uuid import UUID


def timestamp(value):
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError('invalid timestamp')
    value = re.sub(r'(\.\d{6})\d+', r'\1', value.replace('Z', '+00:00'))
    result = datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--not-before', required=True)
    args = parser.parse_args()
    try:
        if not args.title.strip() or len(args.title) > 500:
            raise ValueError('invalid title')
        cutoff = timestamp(args.not_before)
        by_id = {}
        for line in args.index.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get('thread_name'), str):
                raise ValueError('invalid row')
            if row.get('thread_name') != args.title:
                continue
            updated = timestamp(row['updated_at'])
            task_id = str(UUID(row['id']))
            if updated >= cutoff:
                previous = by_id.get(task_id)
                if previous is None or updated > timestamp(previous['updated_at']):
                    by_id[task_id] = {'id': task_id, 'thread_name': args.title, 'updated_at': row['updated_at']}
        candidates = sorted(by_id.values(), key=lambda row: (timestamp(row['updated_at']), row['id']), reverse=True)
        status = 'candidate' if len(candidates) == 1 else ('ambiguous' if candidates else 'not-found')
        result = {'schemaVersion': 1, 'status': status, 'count': len(candidates),
                  'candidates': candidates[:10], 'omitted': max(0, len(candidates) - 10),
                  'requiresDirectVerification': True}
        code = 0 if status == 'candidate' else 2
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError):
        result = {'schemaVersion': 1, 'status': 'error', 'candidates': [],
                  'reason': 'Index unreadable/malformed or arguments invalid; no identity inferred.'}
        code = 3
    print(json.dumps(result, ensure_ascii=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
