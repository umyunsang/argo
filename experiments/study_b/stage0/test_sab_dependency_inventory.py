#!/usr/bin/env python3
"""Tests for deterministic ScienceAgentBench dependency extraction."""
from __future__ import annotations
import tempfile
from pathlib import Path
import audit_sab_dependencies as audit
F=[]
def check(n,ok,d=""):
 print(("PASS " if ok else "FAIL ")+n+(f" :: {d}" if not ok else ""));F.append(n) if not ok else None
def main():
 check("json is stdlib",audit.is_stdlib("json") is True)
 check("nonexistent module is external",audit.is_stdlib("argo_fixture_not_a_real_module") is False)
 check("Bio maps to biopython",audit.dist("Bio")=="biopython")
 check("sklearn maps to scikit-learn",audit.dist("sklearn")=="scikit-learn")
 check("papyrus import maps to distribution",audit.dist("papyrus_scripts")=="papyrus-scripts")
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/"fixture.py";p.write_text("import json\nimport numpy as np\nfrom rdkit import Chem\n")
  check("AST import roots are exact",audit.roots(p)=={"json","numpy","rdkit"},str(audit.roots(p)))
 print(f"\n{len(F)} failing checks" if F else "\nAll checks passed.");return 1 if F else 0
if __name__=="__main__":raise SystemExit(main())
