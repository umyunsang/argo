#!/usr/bin/env python3
"""Generate one figure through the image API from its committed prompt file.

The credential is read from the environment only to build the request header. It
is never printed, logged, written to a record, or copied into the work tree; the
caller sources the key file inside the single command that runs this script.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = "https://api.openai.com/v1/images/generations"


def generate(figure: str, model: str, size: str, out_dir: Path) -> dict:
    prompt = (ROOT / "paper" / "figures" / "specs" / f"{figure}.prompt.txt").read_text(encoding="utf-8")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return {"figure": figure, "ok": False, "error": "no credential in environment"}
    body = json.dumps({"model": model, "prompt": prompt, "size": size, "n": 1}).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            payload = json.loads(r.read().decode())
            request_id = r.headers.get("x-request-id")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:800]
        return {"figure": figure, "ok": False, "http_status": exc.code, "error_body": detail}
    except Exception as exc:  # noqa: BLE001
        return {"figure": figure, "ok": False, "error": type(exc).__name__}
    item = (payload.get("data") or [{}])[0]
    b64 = item.get("b64_json")
    if not b64:
        return {"figure": figure, "ok": False, "error": "response carried no image payload"}
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{figure}.image.png"
    out.write_bytes(base64.b64decode(b64))
    return {"figure": figure, "ok": True, "path": str(out.relative_to(ROOT)),
            "model": model, "size": size, "request_id": request_id,
            "usage": payload.get("usage")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--figure", required=True)
    ap.add_argument("--model", default="gpt-image-2")
    ap.add_argument("--size", default="1536x1024")
    ap.add_argument("--out", default="paper/figures/rendered")
    a = ap.parse_args()
    res = generate(a.figure, a.model, a.size, ROOT / a.out)
    print(json.dumps(res, ensure_ascii=False))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
