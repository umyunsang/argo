"""Fixed ORX command: python runner.py. All variation lives in node-spec.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from scientific_bridge import execute_spec


def main() -> int:
    receipt = execute_spec(Path(__file__).resolve().parent)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False), flush=True)
    return 0 if receipt["status"] in {"VALID", "AGENT_INVALID"} else 1


if __name__ == "__main__":
    sys.exit(main())
