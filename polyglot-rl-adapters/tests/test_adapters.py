from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common import compare, comparison_markdown, load_evaluation  # noqa: E402


class AdapterTests(unittest.TestCase):
    def write_report(self, root: Path, score: int, accepted: bool) -> None:
        (root / "result.json").write_text(
            json.dumps(
                {
                    "task_id": "task-001",
                    "classification": "accepted" if accepted else "test_failure",
                    "accepted": accepted,
                    "score": score,
                    "changed_files": [{"path": "src/example.ts"}],
                    "stages": [
                        {
                            "name": "build",
                            "passed": True,
                            "return_code": 0,
                            "duration_ms": 10,
                            "command": ["build"],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (root / "timing.json").write_text('{"total_duration_ms": 10}', encoding="utf-8")
        (root / "score_breakdown.json").write_text(
            json.dumps({"maximum": 100, "score": score}), encoding="utf-8"
        )

    def test_normalizes_and_compares_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            left = root / "left"
            right = root / "right"
            left.mkdir()
            right.mkdir()
            self.write_report(left, 100, True)
            self.write_report(right, 50, False)
            comparison = compare(
                load_evaluation(left, "typescript-service-reliability-rl-lab", "TypeScript"),
                load_evaluation(right, "typescript-service-reliability-rl-lab", "TypeScript"),
            )
            self.assertEqual(comparison["preferred"], "left")
            self.assertEqual(comparison["score_delta"], 50)
            self.assertIn("Patch Comparison", comparison_markdown(comparison))

    def test_rejects_contradictory_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_report(root, 100, True)
            payload = json.loads((root / "result.json").read_text())
            payload["stages"][0]["return_code"] = 1
            (root / "result.json").write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                load_evaluation(root, "typescript", "TypeScript")

    def test_rejects_string_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_report(root, 100, True)
            payload = json.loads((root / "result.json").read_text())
            payload["accepted"] = "false"
            (root / "result.json").write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                load_evaluation(root, "typescript", "TypeScript")

    def test_known_failure_cannot_outrank_accepted_by_score(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); left = root / "left"; right = root / "right"
            left.mkdir(); right.mkdir()
            self.write_report(left, 100, False); self.write_report(right, 80, True)
            comparison = compare(load_evaluation(left, "typescript", "TypeScript"),
                                 load_evaluation(right, "typescript", "TypeScript"))
            self.assertEqual(comparison["preferred"], "right")

    def test_rejects_mismatched_task_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            left = root / "left"
            right = root / "right"
            left.mkdir()
            right.mkdir()
            self.write_report(left, 100, True)
            self.write_report(right, 100, True)
            payload = json.loads((right / "result.json").read_text(encoding="utf-8"))
            payload["task_id"] = "task-002"
            (right / "result.json").write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                compare(
                    load_evaluation(left, "go-concurrency-performance-rl-lab", "Go"),
                    load_evaluation(right, "go-concurrency-performance-rl-lab", "Go"),
                )


if __name__ == "__main__":
    unittest.main()
