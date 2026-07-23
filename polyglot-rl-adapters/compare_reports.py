from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from common import compare, comparison_markdown


ADAPTERS = {
    "java": "java_adapter",
    "rust": "rust_adapter",
    "go": "go_adapter",
    "typescript": "typescript_adapter",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two normalized RL evaluation reports.")
    parser.add_argument("--language", choices=sorted(ADAPTERS), required=True)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    adapter = importlib.import_module(ADAPTERS[args.language])
    comparison = compare(adapter.normalize(args.left), adapter.normalize(args.right))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "comparison.json").write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "comparison_report.md").write_text(
        comparison_markdown(comparison), encoding="utf-8"
    )
    print(json.dumps({"preferred": comparison["preferred"], "score_delta": comparison["score_delta"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
