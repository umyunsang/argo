#!/usr/bin/env python3
"""Build the Word submission artifact from the validated manuscript.

The LaTeX source stays ASCII so the deterministic PDF build keeps working with
the pinned toolchain, which has no CJK font. The Korean summary and keywords
required by the official form live in paper/korean-summary.txt and are injected
here, so that file remains the single source for them (RD-2026-09-02-18A).

    /usr/bin/python3 paper/word/build_submission.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANDOC = "/usr/local/bin/quarto"
PAPER = ROOT / "paper.tex"
SUMMARY = ROOT / "paper" / "korean-summary.txt"
OUT = ROOT / "paper" / "word" / "graduation-thesis.docx"
REF = ROOT / "paper" / "word" / "reference.docx"


def run(args: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, check=False, **kw)


def front_matter() -> str:
    raw = SUMMARY.read_text(encoding="utf-8").strip().splitlines()
    body = [l for l in raw if l.strip() and not l.strip().startswith("#")]
    summary_lines, keyword_line = [], ""
    for line in body:
        if re.match(r"^\s*(키워드|keywords)\s*[:：]", line, re.I):
            keyword_line = line.split(":", 1)[-1].split("：")[-1].strip()
        else:
            summary_lines.append(line.strip())
    summary = " ".join(summary_lines)
    keywords = [k.strip() for k in re.split(r"[,，]", keyword_line) if k.strip()]
    if len(summary) > 500:
        raise SystemExit(f"Korean summary is {len(summary)} characters, over the 500 limit")
    if len(keywords) > 5:
        raise SystemExit(f"{len(keywords)} keywords, over the limit of 5")
    return "", summary, keywords


XML_NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"')


def _para(style: str, text: str) -> str:
    esc = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
            f'<w:r><w:t xml:space="preserve">{esc}</w:t></w:r></w:p>')


def inject_front_matter(docx_path: Path, summary: str, keywords: list[str]) -> None:
    """Insert the Korean summary after the title, editing the document part directly.

    The direct LaTeX conversion preserves the title and citation markers, which a
    markdown round-trip drops, so the conversion is kept and the required section
    is added to its output instead.
    """
    import shutil, zipfile
    src = zipfile.ZipFile(docx_path)
    parts = {n: src.read(n) for n in src.namelist()}
    src.close()
    doc = parts["word/document.xml"].decode("utf-8")
    block = _para("Heading1", "국문 요약") + _para("BodyText", summary)
    if keywords:
        block += _para("BodyText", "키워드: " + ", ".join(keywords))
    m = re.search(r"</w:p>", doc)
    if not m:
        raise SystemExit("no paragraph found in the converted document")
    doc = doc[:m.end()] + block + doc[m.end():]
    parts["word/document.xml"] = doc.encode("utf-8")
    tmp = docx_path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in parts.items():
            out.writestr(name, data)
    shutil.move(str(tmp), str(docx_path))


def numbered_source(paper_text: str) -> tuple[str, int]:
    """Replace citation commands with bracketed numbers in first-citation order.

    The converter drops natbib citations and leaves dangling punctuation, while
    the official form requires a bracketed citation number, so the numbering the
    validator already enforces is materialised for the Word build only.
    """
    body = paper_text.split("\\begin{thebibliography}", 1)[0]
    order: list[str] = []
    for m in re.finditer(r"\\citep?\{([^}]+)\}", body):
        for key in m.group(1).split(","):
            key = key.strip()
            if key and key not in order:
                order.append(key)
    number = {k: i + 1 for i, k in enumerate(order)}

    def repl(m: re.Match) -> str:
        keys = [k.strip() for k in m.group(1).split(",") if k.strip()]
        return "[" + ", ".join(str(number[k]) for k in keys if k in number) + "]"

    return re.sub(r"\\citep?\{([^}]+)\}", repl, paper_text), len(order)


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
FOOTER_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
    '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    '<w:r><w:t>1</w:t></w:r>'
    '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    '</w:p></w:ftr>'
)


def apply_official_format(docx_path: Path, front_matter_heading: str) -> dict:
    """Apply the three official properties the converter does not supply.

    Chapters carry Roman numerals, body text is double spaced, and pages are
    numbered. Front matter before the first chapter is not numbered.
    """
    import shutil, zipfile
    src = zipfile.ZipFile(docx_path)
    parts = {n: src.read(n) for n in src.namelist()}
    src.close()

    doc = parts["word/document.xml"].decode("utf-8")
    applied = {"numbered_chapters": [], "double_spacing": False, "page_numbers": False}

    def number_headings(text: str) -> str:
        index = {"n": 0}

        def repl(m: re.Match) -> str:
            block = m.group(0)
            if 'w:val="Heading1"' not in block:
                return block
            label = re.sub(r"<[^>]+>", "", "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", block, re.S)))
            if label.strip() == front_matter_heading:
                return block
            if index["n"] >= len(ROMAN):
                return block
            numeral = ROMAN[index["n"]]
            index["n"] += 1
            applied["numbered_chapters"].append(f"{numeral}. {label}")
            return re.sub(r"(<w:t[^>]*>)", r"\g<1>" + f"{numeral}. ", block, count=1)

        return re.sub(r"<w:p[ >].*?</w:p>", repl, text, flags=re.S)

    doc = number_headings(doc)

    styles = parts["word/styles.xml"].decode("utf-8")
    double = '<w:spacing w:line="480" w:lineRule="auto" w:after="0"/>'
    if "<w:docDefaults>" in styles:
        styles = re.sub(r"(<w:pPrDefault><w:pPr>)", r"\g<1>" + double, styles, count=1)
        if double not in styles:
            styles = styles.replace("<w:docDefaults>",
                                    "<w:docDefaults><w:pPrDefault><w:pPr>" + double + "</w:pPr></w:pPrDefault>", 1)
        applied["double_spacing"] = double in styles
    parts["word/styles.xml"] = styles.encode("utf-8")

    parts["word/footer1.xml"] = FOOTER_XML.encode("utf-8")
    rels = parts["word/_rels/document.xml.rels"].decode("utf-8")
    if "footer1.xml" not in rels:
        rels = rels.replace("</Relationships>",
            '<Relationship Id="rIdFtr1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"'
            ' Target="footer1.xml"/></Relationships>')
    parts["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    ct = parts["[Content_Types].xml"].decode("utf-8")
    if "footer+xml" not in ct:
        ct = ct.replace("</Types>",
            '<Override PartName="/word/footer1.xml"'
            ' ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
    parts["[Content_Types].xml"] = ct.encode("utf-8")
    if "<w:footerReference" not in doc:
        doc = re.sub(r"(<w:sectPr[^>]*>)", r"\g<1>" + '<w:footerReference w:type="default" r:id="rIdFtr1"/>',
                     doc, count=1)
    applied["page_numbers"] = "<w:footerReference" in doc
    parts["word/document.xml"] = doc.encode("utf-8")

    tmp = docx_path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in parts.items():
            out.writestr(name, data)
    shutil.move(str(tmp), str(docx_path))
    return applied


def main() -> int:
    _, summary, keywords = front_matter()
    numbered, n_refs = numbered_source(PAPER.read_text(encoding="utf-8"))
    staged = ROOT / "paper" / "word" / "_numbered.tex"
    staged.write_text(numbered, encoding="utf-8")
    args = [PANDOC, "pandoc", str(staged), "-f", "latex", "-t", "docx", "-o", str(OUT)]
    if REF.is_file():
        args += ["--reference-doc", str(REF)]
    conv = run(args)
    if conv.returncode != 0:
        print(conv.stderr[-800:]); return 1
    staged.unlink(missing_ok=True)
    inject_front_matter(OUT, summary, keywords)
    applied = apply_official_format(OUT, "국문 요약")
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(json.dumps({"artifact": str(OUT.relative_to(ROOT)), "bytes": OUT.stat().st_size,
                      "sha256": digest, "korean_summary_chars": len(summary),
                      "keywords": keywords, "numbered_references": n_refs,
                      "official_format": applied}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
