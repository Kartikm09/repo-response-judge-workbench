from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NormalizedEvaluation:
    environment: str
    language: str
    task_id: str
    classification: str
    accepted: bool
    score: int
    maximum_score: int
    changed_files: tuple[dict[str, Any], ...]
    stages: tuple[dict[str, Any], ...]
    benchmark: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "environment": self.environment,
            "language": self.language,
            "task_id": self.task_id,
            "classification": self.classification,
            "accepted": self.accepted,
            "score": self.score,
            "maximum_score": self.maximum_score,
            "changed_files": list(self.changed_files),
            "stages": list(self.stages),
            "benchmark": self.benchmark,
        }


def load_evaluation(report_directory: Path, environment: str, language: str) -> NormalizedEvaluation:
    result = _load_json(report_directory / "result.json")
    timing = _load_json(report_directory / "timing.json")
    score = _load_json(report_directory / "score_breakdown.json")
    if type(result.get("accepted")) is not bool:
        raise ValueError("accepted must be a boolean")
    if type(result.get("score")) is not int or type(score.get("maximum", 100)) is not int:
        raise ValueError("Scores must be integers")
    if not 0 <= result["score"] <= score.get("maximum", 100) or score.get("maximum", 100) <= 0:
        raise ValueError("Score is outside its declared range")
    if score.get("score") != result["score"]:
        raise ValueError("Score artifacts contradict each other")
    if not isinstance(result.get("stages"), list) or not result["stages"]:
        raise ValueError("Missing stage execution evidence")
    stages = []
    for stage in result.get("stages", []):
        if not isinstance(stage, dict):
            raise ValueError("Stage must be an object")
        if type(stage.get("passed")) is not bool:
            raise ValueError("stage passed must be a boolean")
        if stage["passed"] and (type(stage.get("return_code")) is not int or stage["return_code"] != 0):
            raise ValueError("Passing stage contradicts its exit code")
        stages.append(
            {
                "name": stage["name"],
                "passed": bool(stage["passed"]),
                "duration_ms": int(stage["duration_ms"]),
                "return_code": stage.get("return_code"),
                "command": stage.get("command", []),
            }
        )
    if result["accepted"] and (result.get("classification") != "accepted" or any(not s["passed"] for s in stages)):
        raise ValueError("Accepted result contradicts execution evidence")
    benchmark = next((stage for stage in stages if stage["name"] == "benchmark"), None)
    return NormalizedEvaluation(
        environment=environment,
        language=language,
        task_id=str(result["task_id"]),
        classification=str(result["classification"]),
        accepted=bool(result["accepted"]),
        score=int(result["score"]),
        maximum_score=int(score.get("maximum", 100)),
        changed_files=tuple(result.get("changed_files", [])),
        stages=tuple(stages),
        benchmark=benchmark,
    )


def compare(left: NormalizedEvaluation, right: NormalizedEvaluation) -> dict[str, Any]:
    if (left.task_id, left.environment, left.language) != (right.task_id, right.environment, right.language):
        raise ValueError("Evaluations must target the same task ID, environment and language")
    if left.maximum_score != right.maximum_score:
        raise ValueError("Evaluations must use the same score scale")
    score_delta = left.score - right.score
    if (left.accepted, left.score) > (right.accepted, right.score):
        preferred = "left"
    elif (left.accepted, left.score) < (right.accepted, right.score):
        preferred = "right"
    else:
        preferred = "tie"
    return {
        "schema_version": "1.0.0",
        "task_id": left.task_id,
        "preferred": preferred,
        "score_delta": score_delta,
        "left": left.to_dict(),
        "right": right.to_dict(),
        "evidence": {
            "changed_files": {
                "left": [item["path"] for item in left.changed_files],
                "right": [item["path"] for item in right.changed_files],
            },
            "failed_stages": {
                "left": [item["name"] for item in left.stages if not item["passed"]],
                "right": [item["name"] for item in right.stages if not item["passed"]],
            },
            "benchmark": {"left": left.benchmark, "right": right.benchmark},
        },
    }


def comparison_markdown(comparison: dict[str, Any]) -> str:
    left = comparison["left"]
    right = comparison["right"]
    return "\n".join(
        [
            f"# Patch Comparison: {comparison['task_id']}",
            "",
            f"- Preferred: **{comparison['preferred']}**",
            f"- Score delta (left - right): **{comparison['score_delta']}**",
            "",
            "| Candidate | Environment | Classification | Score | Accepted |",
            "| --- | --- | --- | ---: | --- |",
            f"| Left | {left['environment']} | {left['classification']} | {left['score']}/{left['maximum_score']} | {str(left['accepted']).lower()} |",
            f"| Right | {right['environment']} | {right['classification']} | {right['score']}/{right['maximum_score']} | {str(right['accepted']).lower()} |",
            "",
            "## Evidence",
            "",
            f"- Left changed files: {', '.join(comparison['evidence']['changed_files']['left']) or 'none'}",
            f"- Right changed files: {', '.join(comparison['evidence']['changed_files']['right']) or 'none'}",
            f"- Left failed stages: {', '.join(comparison['evidence']['failed_stages']['left']) or 'none'}",
            f"- Right failed stages: {', '.join(comparison['evidence']['failed_stages']['right']) or 'none'}",
            "",
            "This report compares generated evidence only; it does not imply external review.",
            "",
        ]
    )


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing evaluation artifact: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {path.name}")
    return value
