"""Structural checks on every tracked notebook's stored outputs.

CI executes only src/basics/ and src/ml/; the src/gen_ai/ and src/setup/
notebooks need a local Ollama model and are checked here instead, from what
was stored when the author last ran them. A notebook must have been saved
from one clean top-to-bottom run (or with no outputs at all), and its outputs
must not show the author's machine.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = sorted(
    path
    for path in (REPO_ROOT / "src").rglob("*.ipynb")
    if ".ipynb_checkpoints" not in path.parts
)
# A home directory, as `~/...` or `/home/<user>/...`.
MACHINE_PATH = re.compile(r"(~|/home/[^/\s]+)/")


def _code_cells(path: Path) -> list[dict[str, Any]]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    return [cell for cell in nb["cells"] if cell["cell_type"] == "code"]


def _strings(value: object) -> list[str]:
    """Every string inside a JSON value."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [s for item in value for s in _strings(item)]
    if isinstance(value, dict):
        return [s for item in value.values() for s in _strings(item)]
    return []


notebooks = pytest.mark.parametrize(
    "path", NOTEBOOKS, ids=[str(p.relative_to(REPO_ROOT / "src")) for p in NOTEBOOKS]
)


def test_notebooks_are_found() -> None:
    assert len(NOTEBOOKS) > 1


@notebooks
def test_no_error_outputs(path: Path) -> None:
    errors = [
        (index, output.get("ename"))
        for index, cell in enumerate(_code_cells(path), start=1)
        for output in cell.get("outputs", [])
        if output["output_type"] == "error"
    ]
    assert not errors, f"code cells (1-based) with an error output: {errors}"


@notebooks
def test_execution_counts_are_all_null_or_one_to_n(path: Path) -> None:
    counts = [cell.get("execution_count") for cell in _code_cells(path)]
    if all(count is None for count in counts):
        return
    assert counts == list(range(1, len(counts) + 1)), (
        "save the notebook from one top-to-bottom run of a fresh kernel"
    )


@notebooks
def test_outputs_contain_no_machine_paths(path: Path) -> None:
    hits = [
        (index, match.group(0))
        for index, cell in enumerate(_code_cells(path), start=1)
        for output in cell.get("outputs", [])
        for text in _strings(output)
        for match in MACHINE_PATH.finditer(text)
    ]
    assert not hits, f"code cells (1-based) whose outputs show a home directory: {hits}"
