from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResponseScore:
    label: str
    score: int
    strengths: list[str]
    weaknesses: list[str]

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__


@dataclass(frozen=True)
class Judgment:
    task_id: str
    preference: int
    winner: str
    response_a: ResponseScore
    response_b: ResponseScore
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "preference": self.preference,
            "winner": self.winner,
            "response_a": self.response_a.to_dict(),
            "response_b": self.response_b.to_dict(),
            "rationale": self.rationale,
        }


def judge_comparison(payload: dict[str, Any]) -> Judgment:
    a = _score_response("A", payload["response_a"])
    b = _score_response("B", payload["response_b"])
    if a.score > b.score:
        winner = "A"
        preference = 2 if a.score - b.score >= 20 else 3
    elif b.score > a.score:
        winner = "B"
        preference = 5 if b.score - a.score < 20 else 6
    else:
        winner = "tie"
        preference = 4
    rationale = _rationale(a, b, winner)
    return Judgment(str(payload.get("task_id", "unknown-task")), preference, winner, a, b, rationale)


def _score_response(label: str, response: dict[str, Any]) -> ResponseScore:
    strengths: list[str] = []
    weaknesses: list[str] = []
    score = 0
    if response.get("final_status") == "solves_task":
        score += 35
        strengths.append("final code solves the requested task")
    else:
        weaknesses.append("final output does not fully solve the task")
    if response.get("tests_passed") is True:
        score += 25
        strengths.append("tests passed or were convincingly validated")
    else:
        weaknesses.append("missing or failing test evidence")
    if response.get("files_changed"):
        score += 15
        strengths.append("specific changed files are documented")
    else:
        weaknesses.append("changed files are not documented")
    if response.get("commands"):
        score += 10
        strengths.append("commands or validation steps are listed")
    if response.get("introduced_regression") is True:
        score -= 30
        weaknesses.append("introduced a regression")
    if response.get("rationale_has_evidence") is True:
        score += 15
        strengths.append("rationale references concrete evidence")
    else:
        weaknesses.append("rationale lacks concrete evidence")
    return ResponseScore(label, max(0, min(100, score)), strengths, weaknesses)


def _rationale(a: ResponseScore, b: ResponseScore, winner: str) -> str:
    if winner == "tie":
        return "Both responses are similarly strong because their final correctness and validation evidence are close."
    better = a if winner == "A" else b
    worse = b if winner == "A" else a
    return (
        f"Response {better.label} is stronger because it scored {better.score}/100 versus "
        f"{worse.score}/100, with stronger evidence around {', '.join(better.strengths[:2])}. "
        f"Response {worse.label} is weaker due to {', '.join(worse.weaknesses[:2])}."
    )
