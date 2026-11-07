"""Local project lookup, atomic JSON and exact installed CLI discovery."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid

SKILL_ROOT = Path(__file__).resolve().parents[1]
PORTS = ('front', 'left45', 'right45', 'left90', 'right90')

def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()

def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)

def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def discover_cli(value: str | None, node: str | None = None) -> list[str]:
    candidate = value or os.environ.get('HYPIT_CLI') or shutil.which('hypit')
    if not candidate:
        raise ValueError('Supply --hypit-cli or HYPIT_CLI, or put an installed hypit executable on PATH')
    path = Path(candidate).expanduser().resolve()
    if path.is_dir():
        path = path / 'bin' / 'hypit.mjs'
    if not path.is_file():
        raise ValueError('Hypit entry does not exist')
    if path.suffix.lower() in {'.mjs', '.js', '.cjs'}:
        runtime = node or shutil.which('node')
        if not runtime:
            raise ValueError('Node.js is required for a JavaScript Hypit entry')
        argv = [str(Path(runtime).resolve()), str(path)]
    elif path.suffix.lower() in {'.cmd', '.bat', '.ps1'}:
        nearby = path.parent / 'node_modules' / '@hypit' / 'hypit' / 'bin' / 'hypit.mjs'
        if not nearby.is_file():
            raise ValueError('Pass the installed bin/hypit.mjs directly instead of a shell wrapper')
        return discover_cli(str(nearby), node)
    else:
        argv = [str(path)]
    checked = subprocess.run(argv + ['--version'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if checked.returncode:
        raise ValueError('Installed Hypit cannot run: ' + checked.stderr[-1000:])
    return argv

def project_cli(project: Path) -> list[str]:
    return read_json(project / '.hypit-tools.json')['argv']

def job_directory(project: Path, job: str) -> Path:
    if len(job) != 24 or any(character not in '0123456789abcdef' for character in job):
        raise ValueError('Job ID must be the actual 24-character local request ID')
    directory = (project / 'exchange' / job).resolve(strict=True)
    if directory.parent != (project / 'exchange').resolve():
        raise ValueError('Job path escapes project exchange')
    request = read_json(directory / 'request.json')
    if request['jobId'] != job:
        raise ValueError('Request ID mismatch')
    return directory

def run_cli(project: Path, args: list[str], **kwargs):
    return subprocess.run(project_cli(project) + args, cwd=project, **kwargs)
