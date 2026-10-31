#!/usr/bin/env python
"""Select the notebooks a CI run must execute (used by both workflows).

A notebook is selected when its *code* changed between two commits: a code cell
was added, removed, reordered or edited, or a code cell's tags changed. Edits to
markdown cells or to stored outputs alone do not select it, since executing the
notebook again would test the same code. Every notebook under the given
directories is selected when:

  * ``--all`` is passed (scheduled and manual runs);
  * the base commit is missing, all zeros (a new branch) or not in the clone;
  * a path given with ``--always`` (repeatable) changed, such as ``uv.lock`` or the
    workflow file itself.

``--requires NOTEBOOK=PREREQUISITE`` adds PREREQUISITE whenever NOTEBOOK is
selected, for a notebook that needs state another one creates (repeatable;
names are file names, e.g. ``g_model_serving.ipynb=f_model_registry.ipynb``).

Prints a JSON list of repo-relative paths in execution order (directories in
the order given, notebooks by name) to stdout, and the reason for each
selection to stderr, so the CI log says why a notebook ran.

Usage:
    python tools/select_notebooks.py --base SHA --head SHA [--all] \\
        [--always PATH]... [--requires NB=PREREQ]... DIR [DIR ...]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ZERO_SHA = "0" * 40


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def _is_commit(sha: str) -> bool:
    return (
        bool(sha)
        and sha != ZERO_SHA
        and _git("cat-file", "-e", f"{sha}^{{commit}}").returncode == 0
    )


def _show(sha: str, path: str) -> str | None:
    """The file at ``sha``, or None when it does not exist there."""
    result = _git("show", f"{sha}:{path}")
    return result.stdout if result.returncode == 0 else None


def code_fingerprint(notebook_json: str) -> list[tuple[str, list[str]]]:
    """Each code cell's source and tags, in cell order."""
    nb: dict[str, Any] = json.loads(notebook_json)
    cells: list[tuple[str, list[str]]] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        text = "".join(source) if isinstance(source, list) else str(source)
        tags = [str(t) for t in cell.get("metadata", {}).get("tags", [])]
        cells.append((text, tags))
    return cells


def _notebooks_at(sha: str, dirs: list[str]) -> list[str]:
    selected: list[str] = []
    for directory in dirs:
        listing = _git("ls-tree", "--name-only", f"{sha}:{directory}")
        if listing.returncode != 0:
            continue
        names = sorted(n for n in listing.stdout.splitlines() if n.endswith(".ipynb"))
        selected.extend(f"{directory}/{name}" for name in names)
    return selected


def select(
    base: str,
    head: str,
    dirs: list[str],
    always: list[str],
    requires: dict[str, list[str]],
    run_all: bool = False,
) -> tuple[list[str], dict[str, str]]:
    """The notebooks to execute, in order, and why each was selected."""
    dirs = [d.rstrip("/") for d in dirs]
    candidates = _notebooks_at(head, dirs)

    reason_all = ""
    changed: set[str] = set()
    if run_all:
        reason_all = "every notebook is requested"
    elif not _is_commit(base):
        reason_all = f"base commit {base[:12] or '(none)'} is not available"
    else:
        diff = _git("diff", "--name-only", "--no-renames", base, head)
        if diff.returncode != 0:
            reason_all = f"git diff failed: {diff.stderr.strip()}"
        else:
            changed = set(diff.stdout.splitlines())
            hit = sorted(changed & set(always))
            if hit:
                reason_all = f"{', '.join(hit)} changed"
    if reason_all:
        return candidates, dict.fromkeys(candidates, reason_all)

    reasons: dict[str, str] = {}
    for path in candidates:
        if path not in changed:
            continue
        before = _show(base, path)
        after = _show(head, path)
        if after is None:
            continue
        if before is None:
            reasons[path] = "new notebook"
        elif code_fingerprint(before) != code_fingerprint(after):
            reasons[path] = "code cells changed"

    by_name = {Path(p).name: p for p in candidates}
    pending = list(reasons)
    while pending:
        name = Path(pending.pop()).name
        for prerequisite in requires.get(name, []):
            needed = by_name.get(prerequisite)
            if needed is not None and needed not in reasons:
                reasons[needed] = f"required by {name}"
                pending.append(needed)

    ordered = [p for p in candidates if p in reasons]
    return ordered, {p: reasons[p] for p in ordered}


def _parse_requires(pairs: list[str]) -> dict[str, list[str]]:
    requires: dict[str, list[str]] = {}
    for pair in pairs:
        notebook, sep, prerequisite = pair.partition("=")
        if not sep or not notebook or not prerequisite:
            raise SystemExit(f"--requires expects NOTEBOOK=PREREQUISITE, got {pair!r}")
        requires.setdefault(notebook, []).append(prerequisite)
    return requires


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0] if __doc__ else None
    )
    parser.add_argument("dirs", nargs="+", help="directories holding the notebooks")
    parser.add_argument("--base", default="", help="commit to compare against")
    parser.add_argument("--head", default="HEAD", help="commit being tested")
    parser.add_argument("--all", action="store_true", help="select every notebook")
    parser.add_argument(
        "--always", action="append", default=[], help="a path whose change selects all"
    )
    parser.add_argument(
        "--requires", action="append", default=[], help="NOTEBOOK=PREREQUISITE"
    )
    args = parser.parse_args(argv)

    notebooks, reasons = select(
        args.base,
        args.head,
        args.dirs,
        args.always,
        _parse_requires(args.requires),
        run_all=args.all,
    )
    for path in notebooks:
        print(f"{path}: {reasons[path]}", file=sys.stderr)
    if not notebooks:
        print("no notebook's code changed: nothing to execute", file=sys.stderr)
    print(json.dumps(notebooks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
