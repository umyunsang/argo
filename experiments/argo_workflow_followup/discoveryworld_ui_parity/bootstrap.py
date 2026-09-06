#!/usr/bin/env python3
"""Isolated stdlib bootstrap for sealed controller and worker stages."""
from __future__ import annotations
import runpy,sys
from pathlib import Path
def main(argv=None):
 args=list(sys.argv[1:] if argv is None else argv)
 if not args or args[0] not in {"controller","worker","verifier","admission"}:raise RuntimeError("BOOTSTRAP_ROLE")
 role=args.pop(0)
 if role in {"controller","verifier","admission"}:
  root=Path(args.pop(0)).resolve();script=root/{"controller":"run.py","verifier":"verify_result.py","admission":"admit_result.py"}[role];paths=[root]
 else:
  bundle=Path(args.pop(0)).resolve();source=Path(args.pop(0)).resolve();site=Path(args.pop(0)).resolve();script=bundle/"episode.py";paths=[bundle,source,site]
 if not all(path.is_dir() for path in paths) or not script.is_file():raise RuntimeError("BOOTSTRAP_PATH")
 sys.path[:0]=[str(path) for path in paths];sys.argv=[str(script),*args];runpy.run_path(str(script),run_name="__main__");return 0
if __name__=="__main__":raise SystemExit(main())
