"""Start a long-running research command in its own session so a closing shell cannot kill it."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True, help="stdout/stderr file (appended)")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        parser.error("command required")
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("ab") as log:
        log.write(f"\n=== detach {time.strftime('%Y-%m-%dT%H:%M:%S%z')} {json.dumps(command)}\n".encode())
        log.flush()
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                 cwd=os.getcwd(), start_new_session=True, close_fds=True)
    print(json.dumps({"pid": child.pid, "log": str(args.log), "command": command}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
