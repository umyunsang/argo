#!/usr/bin/env python3
"""Probe which environment variables the experiment substrate exposes to a run command."""
import json, os, sys
keep = {k: v for k, v in sorted(os.environ.items())
        if any(t in k.upper() for t in ("ORX", "OPENRESEARCH", "RUN", "NODE", "COMMIT", "EXPERIMENT"))}
print(json.dumps(keep, indent=2))
