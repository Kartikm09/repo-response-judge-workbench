"""Deterministic review of supplied evidence, not authentication of its provenance."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatchcase
from pathlib import PurePosixPath
from typing import Any


@dataclass(frozen=True)
class ResponseScore:
    label: str
    score: int
    strengths: list[str]
    weaknesses: list[str]
    assessments: dict[str, str]

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
        return {"task_id": self.task_id, "preference": self.preference, "winner": self.winner,
                "response_a": self.response_a.to_dict(), "response_b": self.response_b.to_dict(),
                "rationale": self.rationale}


def _nonempty_list(value: Any, name: str) -> list:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Missing or invalid {name}")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing or invalid {name}")
    return value


def _timestamp(value: Any) -> datetime:
    try:
        parsed = datetime.fromisoformat(_text(value, "timestamp").replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include a timezone")
    return parsed


def judge_comparison(payload: dict[str, Any]) -> Judgment:
    """Reject absent/contradictory records; prose cannot override failing tests."""
    if not isinstance(payload, dict):
        raise ValueError("Comparison must be an object")
    task_id = _text(payload.get("task_id"), "task_id")
    requirements: dict[str, str] = {}
    for requirement in _nonempty_list(payload.get("requirements"), "requirements"):
        if not isinstance(requirement, dict):
            raise ValueError("Requirement must be an object")
        identifier = _text(requirement.get("id"), "requirement ID")
        _text(requirement.get("expected_behavior"), "expected behavior")
        kind = requirement.get("kind")
        if identifier in requirements or kind not in {"correctness", "regression"}:
            raise ValueError("Duplicate requirement ID or invalid requirement kind")
        requirements[identifier] = kind
    if set(requirements.values()) != {"correctness", "regression"}:
        raise ValueError("Correctness and regression requirements are both required")
    allowed = _nonempty_list(payload.get("allowed_paths"), "allowed_paths")
    for pattern in allowed:
        _text(pattern, "allowed path pattern")
    a = _score_response("A", payload.get("response_a"), requirements, allowed)
    b = _score_response("B", payload.get("response_b"), requirements, allowed)
    # A passing implementation always outranks one with a known functional failure.
    a_rank = (a.assessments["correctness"] == "passed", a.score)
    b_rank = (b.assessments["correctness"] == "passed", b.score)
    winner = "A" if a_rank > b_rank else "B" if b_rank > a_rank else "tie"
    preference = 4 if winner == "tie" else (2 if winner == "A" else 6)
    rationale = (f"Evidence verdict: {winner}. A: correctness={a.assessments['correctness']}, "
                 f"regression risk={a.assessments['regression_risk']}; "
                 f"B: correctness={b.assessments['correctness']}, "
                 f"regression risk={b.assessments['regression_risk']}. "
                 "Explanation references are assessed separately; supplied records are not independently authenticated.")
    return Judgment(task_id, preference, winner, a, b, rationale)


def _score_response(label: str, response: Any, requirements: dict[str, str], allowed: list[str]) -> ResponseScore:
    if not isinstance(response, dict):
        raise ValueError(f"Response {label} must be an object")
    changed = _nonempty_list(response.get("files_changed"), "files_changed")
    for name in changed:
        _text(name, "changed path")
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '.git' in path.parts or '\\' in name or not any(fnmatchcase(name, p) for p in allowed):
            raise ValueError(f"Changed file outside task scope: {name}")
    if len(set(changed)) != len(changed):
        raise ValueError("Duplicate changed path")
    commands: dict[str, dict] = {}
    for command in _nonempty_list(response.get("commands"), "commands"):
        if not isinstance(command, dict):
            raise ValueError("Commands require argv, exit_code and timestamps")
        identifier = _text(command.get("id"), "command ID")
        if identifier in commands:
            raise ValueError("Duplicate command ID")
        for argument in _nonempty_list(command.get("argv"), "command argv"):
            _text(argument, "command argument")
        if type(command.get("exit_code")) is not int:
            raise ValueError("Command exit_code must be an integer")
        if _timestamp(command.get("finished_at")) < _timestamp(command.get("started_at")):
            raise ValueError("Command finished before it started")
        commands[identifier] = command
    covered: dict[str, list[bool]] = {identifier: [] for identifier in requirements}
    test_commands: set[str] = set()
    for result in _nonempty_list(response.get("test_results"), "test_results"):
        if not isinstance(result, dict):
            raise ValueError("Test result must be an object")
        identifier = result.get("command_id")
        if identifier not in commands or identifier in test_commands:
            raise ValueError("Unknown or duplicate test command reference")
        test_commands.add(identifier)
        counts = [result.get(key) for key in ("passed", "failed", "skipped")]
        if any(type(count) is not int or count < 0 for count in counts):
            raise ValueError("Test counts must be nonnegative integers")
        passed, failed, skipped = counts
        if passed + failed == 0:
            raise ValueError("Skipped or absent tests are not execution evidence")
        if (commands[identifier]['exit_code'] == 0) != (failed == 0):
            raise ValueError("Exit code contradicts test counts")
        for requirement in _nonempty_list(result.get("requirement_ids"), "requirement references"):
            if requirement not in covered:
                raise ValueError("Unknown requirement reference")
            covered[requirement].append(failed == 0 and skipped == 0)
    if any(not outcomes for outcomes in covered.values()):
        raise ValueError("Missing required behavioral or regression evidence")
    if response.get('tests_passed') is True and any(c['exit_code'] != 0 for c in commands.values()):
        raise ValueError("Self-reported pass contradicts command evidence")
    correctness = all(all(covered[key]) for key, kind in requirements.items() if kind == 'correctness')
    regression = all(all(covered[key]) for key, kind in requirements.items() if kind == 'regression')
    # Failed build/lint commands also prevent a functional success claim.
    correctness = correctness and all(c['exit_code'] == 0 for c in commands.values())
    explanation = response.get('explanation', {})
    refs = explanation.get('source_refs', []) if isinstance(explanation, dict) else []
    referenced = (isinstance(explanation, dict) and isinstance(explanation.get('text'), str)
                  and bool(explanation['text'].strip()) and isinstance(refs, list) and bool(refs)
                  and all(isinstance(ref, str) and ref in set(requirements) | set(changed) for ref in refs))
    assessments = {'correctness': 'passed' if correctness else 'failed',
                   'regression_risk': 'tested' if regression else 'known_failure_or_skip',
                   'explanation_quality': 'referenced' if referenced else 'unsupported'}
    strengths = [f"{key}: {value}" for key, value in assessments.items() if value in {'passed', 'tested', 'referenced'}]
    weaknesses = [f"{key}: {value}" for key, value in assessments.items() if value not in {'passed', 'tested', 'referenced'}]
    return ResponseScore(label, 60 * correctness + 25 * regression + 15 * referenced, strengths, weaknesses, assessments)
