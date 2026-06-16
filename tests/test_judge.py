import json
import unittest
from pathlib import Path

from repo_response_judge.judge import judge_comparison


ROOT = Path(__file__).resolve().parents[1]


class RepoJudgeTests(unittest.TestCase):
    def test_example_prefers_a(self):
        payload = json.loads((ROOT / "examples" / "comparison.json").read_text())
        result = judge_comparison(payload)
        self.assertEqual(result.winner, "A")
        self.assertLess(result.preference, 4)

    def test_tie(self):
        payload = json.loads((ROOT / "examples" / "comparison.json").read_text())
        payload["response_b"] = dict(payload["response_a"])
        result = judge_comparison(payload)
        self.assertEqual(result.winner, "tie")


if __name__ == "__main__":
    unittest.main()
