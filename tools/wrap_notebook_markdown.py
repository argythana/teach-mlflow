#!/usr/bin/env python
"""Wrap + justify Jupyter *markdown* cells (a pre-commit formatter).

Wraps prose in the *source* at clause boundaries — the first ``. ? ; : —`` mark
*after* a line passes the target width — so the diff stays readable. The breaks
are soft (a single newline), so the rendered text re-flows. With ``--justify``
each markdown cell is wrapped in a ``<div style="text-align: justify">`` so the
render fills both margins; headings, being single lines, stay left-aligned (the
CSS default for the last line of a justified block).

Scope and safety:
  * Only ``.ipynb`` *markdown* cells are touched. Code cells, outputs, and all
    notebook metadata are left byte-identical.
  * Breaks only at ``. ? ; :`` followed by whitespace (NOT commas).
  * Never breaks inside inline code spans (`` `...` ``) or links ``[..](..)``,
    and skips a small set of abbreviations (``e.g.``, ``i.e.``, …). Decimals
    like ``3.14`` and ``gemma3:4b`` are safe because the punctuation there is
    not followed by whitespace.
  * Leaves headings, tables, block quotes, fenced code, and horizontal rules
    untouched; wraps list-item bodies with a hanging indent.

Usage (formatter contract, like ruff/mdformat):
    python tools/wrap_notebook_markdown.py [--width N] FILE.ipynb [FILE...]
Exits non-zero if any file was changed (so pre-commit reports it).
"""

from __future__ import annotations

import argparse
import json
import re
import sys

BOUNDARY_CHARS = ".?;:—"  # sentence + strong-clause enders (no commas)
_BOUNDARY = re.compile(rf"[{re.escape(BOUNDARY_CHARS)}](?=\s)")
_CODE_SPAN = re.compile(r"`+[^`]*`+")
_LINK = re.compile(r"!?\[[^\]]*\]\([^)]*\)")
_LIST = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
_FENCE = re.compile(r"^\s*(```|~~~)")
_HR = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_LEAVE_PREFIX = ("#", ">", "|", "<")
ABBREV = {
    "e.g.", "i.e.", "etc.", "vs.", "cf.", "al.", "approx.",
    "dr.", "mr.", "mrs.", "ms.", "no.", "fig.", "eq.", "st.",
}


_JUSTIFY_OPEN = '<div style="text-align: justify; max-width: 90ch">'


def _strip_wrapper(src: str) -> str:
    """Remove an existing <div> alignment wrapper (center or justify) so a cell
    re-wraps idempotently."""
    s = src.strip()
    if s.startswith("<div") and s.endswith("</div>"):
        return s[s.find(">") + 1 : s.rfind("</div>")].strip()
    return src


def _unbreak(s: str) -> str:
    """Drop an existing hard-break marker (trailing `\\` or two spaces) so a
    paragraph re-flows from clean text."""
    return s.rstrip().removesuffix("\\").rstrip()


def _protected(text: str) -> list[tuple[int, int]]:
    spans = [(m.start(), m.end()) for m in _CODE_SPAN.finditer(text)]
    spans += [(m.start(), m.end()) for m in _LINK.finditer(text)]
    return spans


def semantic_wrap(text: str, width: int) -> str:
    """Reflow one logical paragraph into hard-broken lines."""
    text = " ".join(text.split())
    if not text:
        return text
    prot = _protected(text)

    breaks: list[int] = []
    for m in _BOUNDARY.finditer(text):
        i = m.start()
        if any(a <= i < b for a, b in prot):
            continue
        if text[i] == ".":
            j = i
            while j > 0 and not text[j - 1].isspace():
                j -= 1
            if text[j : i + 1].lower() in ABBREV:
                continue
        breaks.append(i + 1)  # break position is right after the punctuation

    clauses, prev = [], 0
    for b in breaks:
        clauses.append(text[prev:b].strip())
        prev = b
    tail = text[prev:].strip()
    if tail:
        clauses.append(tail)
    clauses = [c for c in clauses if c]

    # Comma fallback: commas are NOT a normal break point, but a single clause
    # longer than the width would otherwise become one very long line — so split
    # such a clause at its commas (only) to cap the line length.
    segs: list[str] = []
    for c in clauses:
        if len(c) <= width:
            segs.append(c)
            continue
        cprot = _protected(c)
        cuts = [m.start() + 1 for m in re.finditer(r",(?=\s)", c)
                if not any(a <= m.start() < b for a, b in cprot)]
        prev = 0
        for cut in [*cuts, len(c)]:
            piece = c[prev:cut].strip()
            if piece:
                # A clause with no mark and no comma stays on one line, even if it runs
                # past the width — we never break mid-clause at an arbitrary word.
                segs.append(piece)
            prev = cut

    # Assemble segments into lines: keep adding clauses and break only once the
    # line has *passed* `width` — i.e. at the first mark after the limit, not at
    # every mark. Lines therefore run a little past `width` to the next boundary.
    lines: list[str] = []
    cur = ""
    for c in segs:
        cur = f"{cur} {c}".strip() if cur else c
        if len(cur) >= width:
            lines.append(cur)
            cur = ""
    if cur:
        lines.append(cur)
    return "\n".join(lines)  # soft breaks: source wraps, the render re-flows + justifies


def process_source(src: str, width: int) -> str:
    lines = src.split("\n")
    out: list[str] = []
    i, in_fence = 0, False
    while i < len(lines):
        line = lines[i]
        if _FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue
        s = line.strip()
        if s == "" or s.startswith(_LEAVE_PREFIX) or _HR.match(line):
            out.append(line)
            i += 1
            continue

        m = _LIST.match(line)
        if m:
            indent, marker, body = m.group(1), m.group(2), _unbreak(m.group(3))
            hang = len(indent) + len(marker) + 1
            cont, j = [], i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "" or _FENCE.match(nxt) or _LIST.match(nxt):
                    break
                if (len(nxt) - len(nxt.lstrip())) < len(indent) + 1:
                    break
                cont.append(_unbreak(nxt.strip()))
                j += 1
            wrapped = semantic_wrap(" ".join([body, *cont]), max(20, width - hang))
            wl = wrapped.split("\n")
            out.append(f"{indent}{marker} {wl[0]}")
            out.extend(f"{' ' * hang}{w}" for w in wl[1:])
            i = j
            continue

        para, j = [_unbreak(s)], i + 1
        while j < len(lines):
            ln = lines[j]
            ns = ln.strip()
            if ns == "" or ns.startswith(_LEAVE_PREFIX) or _FENCE.match(ln) or _LIST.match(ln):
                break
            para.append(_unbreak(ns))
            j += 1
        out.extend(semantic_wrap(" ".join(para), width).split("\n"))
        i = j
    return "\n".join(out)


def process_notebook(path: str, width: int, justify: bool = False) -> bool:
    with open(path, encoding="utf-8") as fh:
        nb = json.load(fh)
    changed = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        src = "".join(cell["source"])
        new = process_source(_strip_wrapper(src) if justify else src, width)
        if justify:
            new = f"{_JUSTIFY_OPEN}\n\n{new}\n\n</div>"
        if new != src:
            cell["source"] = [l + "\n" for l in new.split("\n")]
            if cell["source"]:
                cell["source"][-1] = cell["source"][-1].rstrip("\n")
            changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(nb, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=90)
    ap.add_argument("--justify", action="store_true",
                    help="wrap each markdown cell in a <div style='text-align: justify'>")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()
    any_changed = False
    for f in args.files:
        if f.endswith(".ipynb") and process_notebook(f, args.width, args.justify):
            print(f"reformatted {f}")
            any_changed = True
    return 1 if any_changed else 0


if __name__ == "__main__":
    sys.exit(main())
