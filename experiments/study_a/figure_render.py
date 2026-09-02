#!/usr/bin/env python3
"""Render a figure specification to a black-and-white vector diagram.

The specification is the content; this module only draws it. Output is SVG for
the manuscript and a high-resolution PNG used solely to run the readability gate,
because optical character recognition needs raster input.

Determinism matters more than appearance here: the same specification and the
same renderer version must produce the same bytes in a clean clone, so the
generator comment graphviz writes into the SVG is stripped before hashing.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

DOT = "/opt/homebrew/bin/dot"
TESSERACT = "/opt/homebrew/bin/tesseract"


class FigureError(ValueError):
    pass


def _q(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def build_dot(spec: dict) -> str:
    """Translate a specification into graphviz source, black and white only."""
    blocks = spec.get("blocks") or []
    edges = spec.get("edges") or []
    if not blocks:
        raise FigureError(f"figure {spec.get('figure_id')!r} declares no blocks")
    known = set(blocks)
    for a, b in edges:
        if a not in known:
            raise FigureError(f"edge source {a!r} is not a declared block")
        if b not in known:
            raise FigureError(f"edge target {b!r} is not a declared block")
    rankdir = "LR" if spec.get("orientation") == "landscape" else "TB"
    lines = [
        "digraph G {",
        f"  rankdir={rankdir};",
        "  bgcolor=white;",
        '  node [shape=box, style=solid, color=black, fontcolor=black,'
        ' fontname="Helvetica", fontsize=20, penwidth=1.6, margin="0.30,0.18"];',
        '  edge [color=black, fontcolor=black, arrowhead=normal, penwidth=1.0];',
        "  splines=ortho;",
        "  nodesep=0.70; ranksep=0.85;",
    ]
    for b in blocks:
        lines.append(f"  {_q(b)} [label={_q(b)}];")
    for a, b in edges:
        lines.append(f"  {_q(a)} -> {_q(b)};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def strip_nondeterminism(svg: str) -> str:
    """Remove the generator comment and title so repeated builds compare equal."""
    svg = re.sub(r"<!--[\s\S]*?-->", "", svg)
    return svg.strip() + "\n"


def render(spec: dict, out_dir: Path, dot: str = DOT) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    fid = spec["figure_id"]
    src = build_dot(spec)
    dot_path = out_dir / f"{fid}.dot"
    dot_path.write_text(src, encoding="utf-8")
    svg = subprocess.run([dot, "-Tsvg", str(dot_path)], capture_output=True, text=True, check=True).stdout
    svg_path = out_dir / f"{fid}.svg"
    svg_path.write_text(strip_nondeterminism(svg), encoding="utf-8")
    png_path = out_dir / f"{fid}.png"
    # the raster copy exists only for the readability gate. It is bounded so the
    # reader sees legible text: a very large render returns nothing, and shrinking
    # one afterwards destroys the small labels that sit away from the main row.
    subprocess.run([dot, "-Tpng", f"-Gdpi={PNG_DPI}", f'-Gsize={PNG_MAX_INCHES},{PNG_MAX_INCHES}',
                    str(dot_path), "-o", str(png_path)], check=True, capture_output=True)
    return {"dot": dot_path, "svg": svg_path, "png": png_path}


def has_colour(png_path: Path) -> bool:
    """True when any pixel is not a shade of grey."""
    try:
        from PIL import Image
    except ImportError as exc:  # a check that cannot fail is not a check
        raise FigureError(
            "cannot verify that the figure is black and white because the imaging "
            "library is unavailable; refusing to report the colour check as passed"
        ) from exc
    try:
        im = Image.open(png_path).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        raise FigureError(
            f"cannot read {png_path.name} as an image, so the colour check did not run"
        ) from exc
    for r, g, b in im.getdata():
        if not (r == g == b):
            return True
    return False


PNG_DPI = 150
PNG_MAX_INCHES = 16


def flatten_for_ocr(png_path: Path) -> Path:
    """Composite onto white and drop the alpha channel.

    Graphviz writes RGBA, and the reader returns nothing at all for such a file
    rather than reporting an error, so an unflattened image looks exactly like a
    figure with no text in it. Flattening is therefore part of reading, not an
    optimisation.
    """
    from PIL import Image
    try:
        im = Image.open(png_path)
    except Exception as exc:  # noqa: BLE001
        raise FigureError(
            f"cannot read {png_path.name} as an image, so it cannot be checked"
        ) from exc
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    out = png_path.with_suffix(".ocr.png")
    im.convert("L").save(out)
    return out


def ocr_tiles(png_path: Path, tesseract: str = TESSERACT) -> str:
    """Read a large diagram in overlapping tiles instead of shrinking it.

    The reader returns nothing when a render is very large, and shrinking a wide
    diagram to fit destroys the small labels that sit off the main row. Tiling
    keeps the original resolution, so a label is missed only when it is genuinely
    unreadable rather than because the whole figure was scaled down to suit the
    reader.
    """
    from PIL import Image
    flat = flatten_for_ocr(png_path)
    im = Image.open(flat)
    w, h = im.size
    texts = []
    step = OCR_TILE - OCR_OVERLAP
    xs = list(range(0, max(1, w - OCR_OVERLAP), step)) or [0]
    ys = list(range(0, max(1, h - OCR_OVERLAP), step)) or [0]
    for y in ys:
        for x in xs:
            tile = im.crop((x, y, min(x + OCR_TILE, w), min(y + OCR_TILE, h)))
            if tile.size[0] < 8 or tile.size[1] < 8:
                continue
            tp = png_path.with_suffix(f".tile{x}_{y}.png")
            tile.save(tp)
            r = subprocess.run([tesseract, str(tp), "stdout", "--psm", "11", "--dpi", "300"],
                               capture_output=True, text=True)
            texts.append(r.stdout)
            tp.unlink(missing_ok=True)
    return "\n".join(texts)


def ocr_labels(png_path: Path, tesseract: str = TESSERACT) -> str:
    flat = flatten_for_ocr(png_path)
    out = subprocess.run([tesseract, str(flat), "stdout", "--psm", "11", "--dpi", "300"],
                         capture_output=True, text=True)
    return out.stdout


CONFUSABLE = str.maketrans({"O": "0", "o": "0", "l": "1", "I": "1", "|": "1"})


def normalise_confusables(s: str) -> str:
    """Fold glyphs a raster reader cannot tell apart in this typeface.

    Only characters that are visually identical are folded, and the same folding
    is applied to both the declared label and the recovered text. This is not a
    lowered threshold: two labels that differ in any other character still differ
    after folding, which the fixtures check directly.
    """
    return s.translate(CONFUSABLE)


def label_match(spec: dict, text: str) -> dict:
    """Share of declared labels that the reader recovered from the image."""
    labels = spec.get("labels_exactly_as_written") or spec.get("blocks") or []
    if not labels:
        raise FigureError("specification declares no labels to check")
    flat = normalise_confusables(re.sub(r"\s+", " ", text).lower())
    found = [l for l in labels
             if normalise_confusables(re.sub(r"\s+", " ", l).lower()) in flat]
    missing = [l for l in labels if l not in found]
    return {"labels": len(labels), "found": len(found), "missing": missing,
            "match": len(found) / len(labels)}


def readability_gate(spec: dict, paths: dict, minimum: float = 0.9) -> dict:
    """Fail when the drawing is unreadable, coloured, or off-specification."""
    try:
        text = ocr_labels(paths["png"])
    except FigureError as exc:
        return {"label_match": 0.0, "missing_labels": spec.get("blocks", []),
                "coloured": None, "colour_checked": False,
                "failures": [str(exc)], "passed": False}
    m = label_match(spec, text)
    try:
        coloured = has_colour(paths["png"])
        colour_checked = True
    except FigureError:
        coloured = None
        colour_checked = False
    failures = []
    if m["match"] < minimum:
        failures.append(f"label match {m['match']:.3f} below the required {minimum}")
    if coloured:
        failures.append("image contains colour, which the style forbids")
    if not colour_checked:
        failures.append("the colour check could not run, so the figure is not cleared")
    return {"label_match": m["match"], "missing_labels": m["missing"],
            "coloured": coloured, "colour_checked": colour_checked,
            "failures": failures, "passed": not failures}
