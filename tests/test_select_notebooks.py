"""Tests for tools/select_notebooks.py, against a throwaway git repository."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import select_notebooks as sel  # noqa: E402


def _notebook(code: list[str], markdown: str = "Intro", output: str = "") -> str:
    cells: list[dict[str, object]] = [
        {"cell_type": "markdown", "metadata": {}, "source": [markdown]}
    ]
    for source in code:
        outputs = (
            [{"output_type": "stream", "name": "stdout", "text": [output]}]
            if output
            else []
        )
        cells.append(
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": outputs,
                "source": [source],
            }
        )
    return json.dumps(
        {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
    )


def _git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    result = subprocess.run(
        ["git", *args], cwd=repo, env=env, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _commit(repo: Path, files: dict[str, str]) -> str:
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "change")
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    _git(tmp_path, "init", "-q")
    _commit(
        tmp_path,
        {
            "uv.lock": "v1\n",
            "src/ml/f_model_registry.ipynb": _notebook(["register()"]),
            "src/ml/g_model_serving.ipynb": _notebook(["serve()"]),
            "src/ml/h_dataset_logging.ipynb": _notebook(["log()"]),
        },
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _select(base: str, **kwargs: object) -> list[str]:
    notebooks, _ = sel.select(
        base,
        "HEAD",
        ["src/ml"],
        always=["uv.lock"],
        requires={"g_model_serving.ipynb": ["f_model_registry.ipynb"]},
        **kwargs,  # type: ignore[arg-type]
    )
    return notebooks


def test_markdown_and_output_edits_select_nothing(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    _commit(
        repo,
        {
            "src/ml/h_dataset_logging.ipynb": _notebook(
                ["log()"], "New intro", "printed"
            )
        },
    )
    assert _select(base) == []


def test_a_code_edit_selects_only_that_notebook(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    _commit(repo, {"src/ml/h_dataset_logging.ipynb": _notebook(["log(tags=1)"])})
    assert _select(base) == ["src/ml/h_dataset_logging.ipynb"]


def test_adding_a_code_cell_counts_as_a_code_change(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    _commit(repo, {"src/ml/h_dataset_logging.ipynb": _notebook(["log()", "show()"])})
    assert _select(base) == ["src/ml/h_dataset_logging.ipynb"]


def test_a_prerequisite_runs_first(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    _commit(repo, {"src/ml/g_model_serving.ipynb": _notebook(["serve(port=5002)"])})
    notebooks, reasons = sel.select(
        base,
        "HEAD",
        ["src/ml"],
        always=[],
        requires={"g_model_serving.ipynb": ["f_model_registry.ipynb"]},
    )
    assert notebooks == [
        "src/ml/f_model_registry.ipynb",
        "src/ml/g_model_serving.ipynb",
    ]
    assert (
        reasons["src/ml/f_model_registry.ipynb"] == "required by g_model_serving.ipynb"
    )


def test_a_new_notebook_is_selected(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    _commit(repo, {"src/ml/k_new.ipynb": _notebook(["new()"])})
    assert _select(base) == ["src/ml/k_new.ipynb"]


@pytest.mark.parametrize(
    "base", ["", sel.ZERO_SHA, "1234567890abcdef1234567890abcdef12345678"]
)
def test_an_unusable_base_selects_everything(repo: Path, base: str) -> None:
    assert len(_select(base)) == 3


def test_an_always_path_selects_everything(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    _commit(repo, {"uv.lock": "v2\n"})
    assert len(_select(base)) == 3


def test_run_all_selects_everything_in_order(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    assert _select(base, run_all=True) == [
        "src/ml/f_model_registry.ipynb",
        "src/ml/g_model_serving.ipynb",
        "src/ml/h_dataset_logging.ipynb",
    ]


def test_cli_prints_json(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    _commit(repo, {"src/ml/h_dataset_logging.ipynb": _notebook(["log(tags=1)"])})
    assert sel.main(["--base", base, "--always", "uv.lock", "src/ml"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == ["src/ml/h_dataset_logging.ipynb"]
    assert "code cells changed" in captured.err


def test_requires_needs_both_names() -> None:
    with pytest.raises(SystemExit):
        sel.main(["--requires", "g_model_serving.ipynb", "src/ml"])
