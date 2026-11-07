import argparse
from pathlib import Path
import sys
from common import run_cli

parser = argparse.ArgumentParser(description='Run the project-selected installed Hypit CLI without a shell')
parser.add_argument('--project', type=Path, required=True)
parser.add_argument('command', nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command[1:] if args.command[:1] == ['--'] else args.command
if not command:
    parser.error('A Hypit command is required after --')
raise SystemExit(run_cli(args.project.expanduser().resolve(), command).returncode)
