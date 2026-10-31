"""Numbers the notebook prose quotes from a stored run must match the stored outputs.

Re-running a notebook changes timings, scores and counts, and nothing else catches prose
that still quotes the old run. Each claim below pairs a quoted fragment of a markdown
cell with patterns that must appear in the same notebook's stored outputs. A second test
finds markdown sentences that quote a result and fails unless a claim covers them. It
detects two shapes: a sentence that names the stored run ("stored run", "run saved",
"example run", ...) and contains a number, and a sentence that gives a metric's value
("`relevance_to_query/mean` is **0.67**"). A quoted result phrased any other way is not
detected, so add a claim for it by hand.

When a re-run changes a quoted number, update the prose and the claim together.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
# Sentences that present a number as coming from the run stored in the notebook. A dot
# followed by a digit is a decimal point, not the end of the sentence, and a single
# newline is the formatter's soft line break inside a sentence.
_SENTENCE_PART = r"(?:[^.\n]|\.(?=\d)|\n(?!\n))*"
QUOTES_A_RUN = re.compile(
    _SENTENCE_PART
    + r"(?:stored run|run stored|saved here|run saved|example run)"
    + _SENTENCE_PART,
    re.IGNORECASE,
)
# Sentences that state a logged metric's value, such as "`concise/mean` is also 0.67".
QUOTES_A_METRIC = re.compile(
    _SENTENCE_PART + r"`[\w./]+/(?:mean|value)`[^.\n]{0,40}?\d\.\d" + _SENTENCE_PART
)


@dataclass(frozen=True)
class Claim:
    notebook: str
    prose: str  # an exact fragment of one markdown cell
    outputs: tuple[str, ...]  # regexes that must each match the stored outputs


CLAIMS = (
    Claim(
        "src/ml/i_system_metrics.ipynb",
        "(8.6 s vs 37.7 s)",
        (r"GPU train: 8\.6s", r"CPU train: 37\.7s"),
    ),
    Claim(
        "src/ml/i_system_metrics.ipynb",
        "99% vs 64%, about 1.7 GB vs 1.2 GB",
        (
            r"gpu_0_utilization_percentage\s+99\.0",
            r"gpu_0_utilization_percentage\s+64\.0",
            r"gpu_0_memory_usage_megabytes\s+1[67]\d\d\.\d",
            r"gpu_0_memory_usage_megabytes\s+1[12]\d\d\.\d",
        ),
    ),
    Claim(
        "src/ml/i_system_metrics.ipynb",
        "(stored run: 92% vs 97%)",
        (
            r"cpu_utilization_percentage\s+91\.\d",
            r"cpu_utilization_percentage\s+96\.\d",
        ),
    ),
    Claim(
        "src/ml/i_system_metrics.ipynb",
        "(37 samples for the CPU run, 10 for the GPU run)",
        (r"\(37 samples\)", r"\(10 samples\)"),
    ),
    Claim(
        "src/ml/i_system_metrics.ipynb",
        "in the stored run its GPU peak reached 64%",
        (r"gpu_0_utilization_percentage\s+64\.0",),
    ),
    Claim(
        "src/gen_ai/e_prompt_registry.ipynb",
        "v1 scored 0.0 on `concise` and v2 scored 0.33",
        (
            r"v1: .*'concise/mean': np\.float64\(0\.0\)",
            r"v2: .*'concise/mean': np\.float64\(0\.33\)",
        ),
    ),
    Claim(
        "src/gen_ai/h_dspy_optimization.ipynb",
        "the optimized program scored the same as the baseline: 75",
        (
            r"baseline: EvaluationResult\(score=75\.0",
            r"optimized: EvaluationResult\(score=75\.0",
        ),
    ),
    Claim(
        "src/gen_ai/i_rag_capstone.ipynb",
        "the judge scored all 8 traces",
        (r"rows the judge couldn't score: 0 of 8",),
    ),
    Claim(
        "src/ml/c_logging_plots.ipynb",
        "in the run saved here it is the deepest of the five (`max_depth=29`)",
        (r"Best params: \{'rf_max_depth': 29,",),
    ),
    Claim(
        "src/gen_ai/c_genai_evaluation.ipynb",
        "`relevance_to_query/mean` is **0.67**",
        (r"'relevance_to_query/mean': np\.float64\(0\.666",),
    ),
    Claim(
        "src/gen_ai/c_genai_evaluation.ipynb",
        "`concise/mean` is also 0.67",
        (r"'concise/mean': np\.float64\(0\.666",),
    ),
)
# Sentences that match QUOTES_A_RUN but quote no stored output, with the reason.
NOT_RESULTS = {
    (
        "src/ml/i_system_metrics.ipynb",
        "laptop with an 8-core CPU and a 6 GB NVIDIA GPU",
    ): ("describes the machine, not a result"),
    (
        "src/setup/a_ollama_setup.ipynb",
        "In one example run on a laptop with a 6 GB GPU",
    ): ("introduces terminal output the reader produces themselves"),
}


def _cells(notebook: str) -> list[dict[str, Any]]:
    nb = json.loads((REPO_ROOT / notebook).read_text(encoding="utf-8"))
    cells: list[dict[str, Any]] = nb["cells"]
    return cells


def _text(value: object) -> str:
    return "".join(value) if isinstance(value, list) else str(value)


def _markdown(notebook: str) -> list[str]:
    return [
        _text(c["source"]) for c in _cells(notebook) if c["cell_type"] == "markdown"
    ]


def _outputs(notebook: str) -> str:
    parts = []
    for cell in _cells(notebook):
        for output in cell.get("outputs", []):
            parts.append(_text(output.get("text", "")))
            parts.append(_text(output.get("data", {}).get("text/plain", "")))
    return "\n".join(parts)


@pytest.mark.parametrize(
    "claim", CLAIMS, ids=[f"{c.notebook}: {c.prose}" for c in CLAIMS]
)
def test_quoted_result_matches_stored_outputs(claim: Claim) -> None:
    assert any(claim.prose in cell for cell in _markdown(claim.notebook)), (
        "prose fragment not found"
    )
    outputs = _outputs(claim.notebook)
    missing = [pattern for pattern in claim.outputs if not re.search(pattern, outputs)]
    assert not missing, f"stored outputs do not show {missing}"


def test_every_quoted_run_result_has_a_claim() -> None:
    notebooks = sorted(
        str(p.relative_to(REPO_ROOT)) for p in (REPO_ROOT / "src").rglob("*.ipynb")
    )
    uncovered = []
    for notebook in notebooks:
        for cell in _markdown(notebook):
            run_sentences = [m.group(0) for m in QUOTES_A_RUN.finditer(cell)]
            for sentence in [
                *(
                    s for s in run_sentences if re.search(r"\d", s)
                ),  # the number may come first
                *(m.group(0) for m in QUOTES_A_METRIC.finditer(cell)),
            ]:
                covered = any(
                    c.notebook == notebook and c.prose in sentence for c in CLAIMS
                ) or any(
                    nb == notebook and fragment in sentence
                    for nb, fragment in NOT_RESULTS
                )
                if not covered:
                    uncovered.append(f"{notebook}: {sentence.strip()[:120]}")
    assert not uncovered, "quoted run results with no claim in CLAIMS:\n" + "\n".join(
        uncovered
    )
