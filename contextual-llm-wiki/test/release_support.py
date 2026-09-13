"""Real runtime and controlled transport fixtures shared by release tests and acceptance."""
import os
from pathlib import Path
import shutil
import sys

BASE = Path(__file__).resolve().parents[1]


def wrapper_input(destination):
    destination.mkdir()
    for name in ('src', 'scripts', 'test', 'patches'):
        shutil.copytree(BASE / name, destination / name, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('compiler-release.json', 'package.json', 'package-lock.json', 'tsconfig.json', 'wiki', 'wiki-node'):
        shutil.copy2(BASE / name, destination / name)
    (destination / '.runtime').mkdir()
    for name in ('compiler', 'node'):
        (destination / '.runtime' / name).symlink_to(BASE / '.runtime' / name)
    (destination / 'node_modules').symlink_to(BASE / 'node_modules')
    return destination



def retrieval_failure_path(root):
    bin_dir = root / 'fault-bin'
    bin_dir.mkdir()
    node = bin_dir / 'node'
    node.write_text('#!' + sys.executable + '\nimport os,sys\n'
                    'if any("/.runtime/releases/" in a and "qmd-bridge" in a for a in sys.argv):\n'
                    ' print("deliberate activation retrieval failure",file=sys.stderr);sys.exit(17)\n'
                    + 'os.execv(' + repr(shutil.which('node')) + ', ["node", *sys.argv[1:]])\n')
    node.chmod(0o755)
    return bin_dir
