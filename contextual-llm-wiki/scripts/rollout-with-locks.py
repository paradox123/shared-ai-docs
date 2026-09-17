#!/usr/bin/env python3
"""Execute one bounded rollout operation under both existing maintenance writer locks."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import sys
import time
from bounded_process import execute, persist


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--lock-file', required=True)
    parser.add_argument('--artifacts', required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('rollout command required after --')
    artifacts = Path(args.artifacts).resolve()
    artifacts.mkdir(parents=True, exist_ok=False, mode=0o700)
    result = {'ok': False, 'artifacts': str(artifacts)}
    try:
        with Path(args.lock_file).open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if Path(args.lock_file + '.blocked.json').exists():
                raise RuntimeError('Unresolved process custody blocks rollout')
            env = dict(os.environ, WIKI_MAINTENANCE_LOCK_FILE=args.lock_file,
                       WIKI_MAINTENANCE_LOCK_FD=str(lock.fileno()))
            base = Path(__file__).resolve().parent
            with (artifacts/'stdout').open('w') as out, (artifacts/'stderr').open('w') as err:
                code, stopped, forced, owner = execute([str(base.parent/'wiki-node'), str(base/'with-writer.ts'),
                    str(Path(args.config).resolve()), *command], out, err, time.monotonic()+300, 10,
                    artifacts/'progress.json', artifacts/'children', env)
            result.update(ok=code == 0 and stopped is None, exitCode=code, stopped=stopped, forced=forced, writerPid=owner)
    except Exception as error:
        result['error'] = str(error)
    persist(artifacts/'report.json', result)
    print(json.dumps(result), flush=True)
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
