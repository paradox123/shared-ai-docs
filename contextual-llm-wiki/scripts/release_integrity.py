"""Content binding for qualified, self-contained release runtimes."""
import hashlib
import json
import os
from pathlib import Path
import stat

REQUIRED = ('release', 'runtime', 'checkout', 'patches', 'dependencies', 'build',
            'typecheck', 'upstream-tests', 'integration-tests', 'integrity')


def runtime_manifest(root):
    root = root.resolve()
    entries = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in ('.git', '__pycache__'))
        for name in sorted(dirs + files):
            file = Path(directory) / name
            relative = str(file.relative_to(root))
            info = file.lstat()
            if stat.S_ISLNK(info.st_mode):
                if not file.resolve(strict=True).is_relative_to(root):
                    raise RuntimeError('Runtime symlink escapes snapshot: ' + relative)
                entries[relative] = ['link', os.readlink(file)]
            elif stat.S_ISREG(info.st_mode):
                with file.open('rb') as stream:
                    sha = hashlib.sha256()
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        sha.update(block)
                entries[relative] = ['file', info.st_mode & 0o111, sha.hexdigest()]
            elif not stat.S_ISDIR(info.st_mode):
                raise RuntimeError('Unsupported runtime artifact: ' + relative)
    if not entries:
        raise RuntimeError('Empty runtime snapshot')
    return entries


def runtime_digest(root):
    return hashlib.sha256(json.dumps(runtime_manifest(root), sort_keys=True).encode()).hexdigest()


def qualified_report(candidate):
    report = json.loads((candidate / 'report.json').read_text())
    if (report.get('ok') is not True or report.get('eligible') is not True
            or any(report.get('checks', {}).get(name, {}).get('status') != 'passed' for name in REQUIRED)):
        raise RuntimeError('Candidate is not qualified; install and check it again')
    if report.get('schemaVersion') != 2 or not report.get('runtimeTreeSha256'):
        raise RuntimeError('Candidate needs renewed qualification with full runtime binding')
    wrapper = candidate / 'wrapper'
    if runtime_digest(wrapper) != report['runtimeTreeSha256']:
        raise RuntimeError('Candidate changed since qualification; install and check it again')
    definition = json.loads((wrapper / 'compiler-release.json').read_text())
    if (definition['commit'] != report['commit'] or definition['release'] != report['release']['tag_name']
            or definition['repository'] != report['repository']):
        raise RuntimeError('Candidate identity does not match qualification')
    return report
