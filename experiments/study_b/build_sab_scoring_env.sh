#!/bin/bash
# Rebuild SAB scoring env: uv venv mirroring config_conda_env.py semantics (conda unavailable on host)
set +e
VENV=/Users/um-yunsang/argo-paper-orx/.venv-sab
cd /Users/um-yunsang/argo-paper-orx
uv venv "$VENV" --python 3.11 >> /tmp/sab_install.log 2>&1
uv pip install -p "$VENV/bin/python" --python-platform macosx arm64 requests pandas numpy scipy scikit-learn 2>/dev/null >> /tmp/sab_install.log 2>&1 || true
uv pip install -p "$VENV/bin/python" requests pandas numpy scipy scikit-learn >> /tmp/sab_install.log 2>&1
echo "=== rdkit ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" rdkit >> /tmp/sab_install.log 2>&1 && echo "OK rdkit" >> /tmp/sab_install.log || echo "FAIL rdkit" >> /tmp/sab_install.log
echo "=== deepchem ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" deepchem >> /tmp/sab_install.log 2>&1 && echo "OK deepchem" >> /tmp/sab_install.log || echo "FAIL deepchem" >> /tmp/sab_install.log
echo "=== neurokit2 ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" neurokit2 >> /tmp/sab_install.log 2>&1 && echo "OK neurokit2" >> /tmp/sab_install.log || echo "FAIL neurokit2" >> /tmp/sab_install.log
echo "=== biopsykit ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" biopsykit >> /tmp/sab_install.log 2>&1 && echo "OK biopsykit" >> /tmp/sab_install.log || echo "FAIL biopsykit" >> /tmp/sab_install.log
echo "=== DeepPurpose ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" DeepPurpose >> /tmp/sab_install.log 2>&1 && echo "OK DeepPurpose" >> /tmp/sab_install.log || echo "FAIL DeepPurpose" >> /tmp/sab_install.log
echo "=== MASTML ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" MASTML >> /tmp/sab_install.log 2>&1 && echo "OK MASTML" >> /tmp/sab_install.log || echo "FAIL MASTML" >> /tmp/sab_install.log
echo "=== matminer ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" matminer >> /tmp/sab_install.log 2>&1 && echo "OK matminer" >> /tmp/sab_install.log || echo "FAIL matminer" >> /tmp/sab_install.log
echo "=== chemprop ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" chemprop >> /tmp/sab_install.log 2>&1 && echo "OK chemprop" >> /tmp/sab_install.log || echo "FAIL chemprop" >> /tmp/sab_install.log
echo "=== geopandas ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" geopandas >> /tmp/sab_install.log 2>&1 && echo "OK geopandas" >> /tmp/sab_install.log || echo "FAIL geopandas" >> /tmp/sab_install.log
echo "=== papyrus-scripts ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" papyrus-scripts >> /tmp/sab_install.log 2>&1 && echo "OK papyrus-scripts" >> /tmp/sab_install.log || echo "FAIL papyrus-scripts" >> /tmp/sab_install.log
echo "=== MDAnalysis ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" MDAnalysis >> /tmp/sab_install.log 2>&1 && echo "OK MDAnalysis" >> /tmp/sab_install.log || echo "FAIL MDAnalysis" >> /tmp/sab_install.log
echo "=== biopython ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" biopython >> /tmp/sab_install.log 2>&1 && echo "OK biopython" >> /tmp/sab_install.log || echo "FAIL biopython" >> /tmp/sab_install.log
echo "=== cftime ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" cftime >> /tmp/sab_install.log 2>&1 && echo "OK cftime" >> /tmp/sab_install.log || echo "FAIL cftime" >> /tmp/sab_install.log
echo "=== modnet ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" modnet >> /tmp/sab_install.log 2>&1 && echo "OK modnet" >> /tmp/sab_install.log || echo "FAIL modnet" >> /tmp/sab_install.log
echo "=== ccobra ===" >> /tmp/sab_install.log
uv pip install -p "$VENV/bin/python" ccobra >> /tmp/sab_install.log 2>&1 && echo "OK ccobra" >> /tmp/sab_install.log || echo "FAIL ccobra" >> /tmp/sab_install.log
echo "=== done ===" >> /tmp/sab_install.log
