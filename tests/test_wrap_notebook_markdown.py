"""Tests for tools/wrap_notebook_markdown.py, the pre-commit markdown formatter.

Each test runs the tool as the pre-commit hook does (a subprocess on a notebook
file) and checks a promise from its docstring. The fixture notebook is built
here rather than committed as an .ipynb file, because the repo's pre-commit
hooks would reformat a committed fixture and leave nothing to test.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Parsed notebook JSON: a whole notebook, or one cell or output inside it.
type JSONObject = dict[str, Any]

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL = REPO_ROOT / "tools" / "wrap_notebook_markdown.py"

# The arguments the wrap-notebook-markdown hook passes in .pre-commit-config.yaml.
WIDTH = 120
HOOK_ARGS = ["--width", str(WIDTH), "--justify"]
JUSTIFY_OPEN = '<div style="text-align: justify; max-width: 90ch">'

LONG_PROSE = (
    "MLflow records parameters, metrics and artifacts for every run. "
    "The tracking server stores them in a backend store and an artifact store; "
    "the UI reads both. A run belongs to an experiment: experiments group runs "
    "that answer one question. Compare runs side by side to pick a model."
)
LIST_ITEM = (
    "- Start the server first. Then point the client at it with "
    "`mlflow.set_tracking_uri`; every later call logs there. Runs that fail "
    "still appear in the UI: their status says FAILED."
)

# A paragraph whose lead-in passes WIDTH with no clause mark and no comma, so
# the formatter must break at the first mark after the lead-in. Each `middle`
# below contains a mark that is *not* a valid break point; the break must land
# after it, at "ends here.".
LEAD_IN = " ".join(
    ["this lead-in runs past the target width without any clause mark"] * 2
)
CLAUSE_END = "and the clause ends here."
NEXT_SENTENCE = "A new sentence starts."
NO_BREAK_INSIDE = {
    # Protected spans: their marks are followed by whitespace.
    "code-span": "`mlflow.set_experiment('demo'). Then: log; done`",
    "link": "[the tracking guide. It covers: runs; metrics](https://mlflow.org/docs/latest/ml/tracking/)",
    # An abbreviation from the tool's skip list.
    "abbreviation": "for example e.g. with",
    # Marks that are not followed by whitespace.
    "model-tag": "pull gemma3:4b first",
    "decimal": "Python 3.14 is required",
}

UNTOUCHED_LINES = [
    "## A heading that is long enough to wrap. It has clause marks: here; there. And more text after them",
    "> A block quote that is long enough to wrap. It has clause marks: here; there. And more text after them",
    "| column one. with a mark: | column two; with another. And more text so the row runs past the width |",
    "```python",
    "print('a fenced line long enough to wrap. It has clause marks: here; there. And more after them')",
    "```",
    "---",
]


def _lines(text: str) -> list[str]:
    """Split text into notebook source lines, as Jupyter stores them."""
    return text.splitlines(keepends=True)


def _markdown_cell(cell_id: str, source: str) -> JSONObject:
    return {
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": _lines(source),
    }


def _code_cell(count: int, source: str, outputs: list[JSONObject]) -> JSONObject:
    return {
        "cell_type": "code",
        "execution_count": count,
        "id": f"code-{count}",
        "metadata": {"tags": ["keep-me"]},
        "outputs": outputs,
        "source": _lines(source),
    }


def _fixture_notebook() -> JSONObject:
    # Code sources and outputs carry long prose with clause marks, so a
    # formatter that touched them would visibly rewrap them.
    stream = {
        "name": "stdout",
        "output_type": "stream",
        "text": _lines(f"{LONG_PROSE}\n{LONG_PROSE} — done.\n"),
    }
    display = {
        "data": {
            "text/markdown": _lines(LONG_PROSE),
            "text/plain": ["<IPython.core.display.Markdown object>"],
        },
        "metadata": {},
        "output_type": "display_data",
    }
    result = {
        "data": {"text/plain": [repr(LONG_PROSE)]},
        "execution_count": 2,
        "metadata": {},
        "output_type": "execute_result",
    }
    return {
        "cells": [
            _markdown_cell("prose", LONG_PROSE),
            _code_cell(
                1,
                "# A long comment with clause marks. It must stay as it is: the formatter skips code; always.\n"
                f"print({LONG_PROSE!r})\n"
                "display(Markdown(LONG_PROSE))",
                [stream, display],
            ),
            _markdown_cell("list", LIST_ITEM),
            *(
                _markdown_cell(name, f"{LEAD_IN} {middle} {CLAUSE_END} {NEXT_SENTENCE}")
                for name, middle in NO_BREAK_INSIDE.items()
            ),
            _code_cell(2, repr(LONG_PROSE), [result]),
            _markdown_cell(
                "blocks",
                "\n\n".join(UNTOUCHED_LINES[:3])
                + "\n\n"
                + "\n".join(UNTOUCHED_LINES[3:6])
                + "\n\n---",
            ),
            {
                "cell_type": "raw",
                "id": "raw",
                "metadata": {},
                "source": _lines(LONG_PROSE),
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.14.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def _dump(nb: JSONObject) -> str:
    """Serialize a notebook the way Jupyter and the formatter both write it."""
    return json.dumps(nb, ensure_ascii=False, indent=1) + "\n"


def _run_formatter(
    *paths: Path, args: list[str] = HOOK_ARGS
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args, *map(str, paths)],
        capture_output=True,
        text=True,
        check=False,
    )


def _markdown_sources(nb: JSONObject) -> dict[str, str]:
    return {
        c["id"]: "".join(c["source"])
        for c in nb["cells"]
        if c["cell_type"] == "markdown"
    }


def _body_lines(source: str) -> list[str]:
    """The lines of a justified cell's source, without its <div> wrapper."""
    assert source.startswith(JUSTIFY_OPEN + "\n\n")
    assert source.endswith("\n\n</div>")
    return source[len(JUSTIFY_OPEN) : -len("</div>")].strip("\n").split("\n")


@pytest.fixture
def notebook(tmp_path: Path) -> Path:
    path = tmp_path / "fixture.ipynb"
    path.write_text(_dump(_fixture_notebook()), encoding="utf-8")
    return path


@pytest.fixture
def formatted(notebook: Path) -> tuple[JSONObject, JSONObject]:
    """The fixture notebook before and after one run of the hook."""
    before = json.loads(notebook.read_text(encoding="utf-8"))
    proc = _run_formatter(notebook)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    after = json.loads(notebook.read_text(encoding="utf-8"))
    return before, after


@pytest.mark.parametrize(
    "args", [HOOK_ARGS, ["--width", str(WIDTH)]], ids=["hook", "no-justify"]
)
def test_second_run_changes_nothing(notebook: Path, args: list[str]) -> None:
    first = _run_formatter(notebook, args=args)
    assert first.returncode == 1, "the fixture should need formatting on the first run"
    once = notebook.read_bytes()

    second = _run_formatter(notebook, args=args)

    assert second.returncode == 0, second.stdout + second.stderr
    assert second.stdout == ""
    assert notebook.read_bytes() == once


def test_exit_status_reports_whether_a_file_changed(notebook: Path) -> None:
    first = _run_formatter(notebook)
    assert first.returncode == 1
    assert first.stdout.strip() == f"reformatted {notebook}"

    second = _run_formatter(notebook)
    assert second.returncode == 0
    assert second.stdout == ""


def test_code_cells_and_outputs_are_byte_identical(
    formatted: tuple[JSONObject, JSONObject],
) -> None:
    before, after = formatted
    code_before = [c for c in before["cells"] if c["cell_type"] == "code"]
    code_after = [c for c in after["cells"] if c["cell_type"] == "code"]

    assert len(code_before) == 2
    assert [_dump(c).encode() for c in code_after] == [
        _dump(c).encode() for c in code_before
    ]
    assert _markdown_sources(after) != _markdown_sources(before), (
        "the markdown should have been reformatted"
    )


def test_only_markdown_sources_change(notebook: Path) -> None:
    original = notebook.read_bytes()
    before = json.loads(original)
    _run_formatter(notebook)
    after = json.loads(notebook.read_bytes())

    # Put the original markdown sources back: every other byte, including the
    # raw cell, cell ids and notebook metadata, must match the original file.
    for old, new in zip(before["cells"], after["cells"], strict=True):
        if new["cell_type"] == "markdown":
            new["source"] = old["source"]

    assert _dump(after).encode() == original


@pytest.mark.parametrize("cell_id", NO_BREAK_INSIDE)
def test_breaks_only_at_the_first_valid_mark_after_the_width(
    formatted: tuple[JSONObject, JSONObject], cell_id: str
) -> None:
    """Never inside code spans or links, after skipped abbreviations, or at a mark
    with no whitespace after it (decimals, model tags)."""
    middle = NO_BREAK_INSIDE[cell_id]
    # The test is only meaningful if the lead-in alone passes the width.
    assert len(LEAD_IN) > WIDTH
    if cell_id in {"code-span", "link"}:
        assert re.search(r"[.?;:—]\s", middle), (
            "a protected span needs a mark the formatter could break at"
        )

    _, after = formatted
    lines = _body_lines(_markdown_sources(after)[cell_id])

    assert lines == [f"{LEAD_IN} {middle} {CLAUSE_END}", NEXT_SENTENCE]


def test_leaves_headings_quotes_tables_fences_and_rules_untouched(
    formatted: tuple[JSONObject, JSONObject],
) -> None:
    _, after = formatted
    lines = _body_lines(_markdown_sources(after)["blocks"])

    assert [line for line in lines if line] == UNTOUCHED_LINES


def test_list_items_wrap_with_a_hanging_indent(
    formatted: tuple[JSONObject, JSONObject],
) -> None:
    _, after = formatted
    lines = _body_lines(_markdown_sources(after)["list"])

    assert len(lines) > 1, "the list item should have been wrapped"
    assert lines[0].startswith("- ")
    assert all(re.match(r"  \S", line) for line in lines[1:])
    assert " ".join(line.strip() for line in lines) == LIST_ITEM


def test_justify_wraps_each_markdown_cell_exactly_once(notebook: Path) -> None:
    _run_formatter(notebook)
    _run_formatter(notebook)
    for cell_id, source in _markdown_sources(json.loads(notebook.read_bytes())).items():
        assert source.count("<div") == 1, cell_id
        assert source.startswith(JUSTIFY_OPEN), cell_id
        assert source.endswith("</div>"), cell_id


def test_tracked_notebooks_are_stable_under_the_hook(tmp_path: Path) -> None:
    """A second run of the hook changes nothing on copies of the real notebooks."""
    src = REPO_ROOT / "src"
    copies = []
    for nb in sorted(src.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in nb.parts:
            continue
        dest = tmp_path / "__".join(nb.relative_to(src).parts)
        shutil.copyfile(nb, dest)
        copies.append(dest)
    assert copies

    _run_formatter(*copies)
    once = {p.name: p.read_bytes() for p in copies}
    second = _run_formatter(*copies)

    assert second.returncode == 0, second.stdout
    assert {p.name: p.read_bytes() for p in copies} == once
