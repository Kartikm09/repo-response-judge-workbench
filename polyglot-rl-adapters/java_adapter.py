from __future__ import annotations

from pathlib import Path

from common import NormalizedEvaluation, load_evaluation


def normalize(report_directory: Path) -> NormalizedEvaluation:
    return load_evaluation(report_directory, "java-refactoring-rl-environment", "Java")
