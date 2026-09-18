from __future__ import annotations

import argparse
import json
from pathlib import Path

from .judge import judge_comparison


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Judge two repo-task AI responses.")
    parser.add_argument("command", choices=["judge"])
    parser.add_argument("path", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)
    try:
        result = judge_comparison(json.loads(args.path.read_text(encoding="utf-8")))
    except (ValueError, TypeError, KeyError) as exc:
        parser.error(f"Evidence rejected: {exc}")
    if args.format == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Repo Response Judge Workbench\nTask: {result.task_id}\nWinner: {result.winner}\nPreference: {result.preference}/7\n{result.rationale}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
