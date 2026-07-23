# Repo Response Judge Workbench

Evidence-first workbench for comparing two AI coding-agent responses on the same repository task.

The evaluator prioritizes:

- Final correctness
- Test evidence
- Specific file and command evidence
- Regression risk
- Weakness symmetry
- Rationale consistency

## Quick Start

```bash
PYTHONPATH=src python3 -m repo_response_judge.cli judge examples/comparison.json
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Portfolio Signal

This project demonstrates repo-based model evaluation, coding-agent response comparison, evidence-backed rationale writing, and labeling QA.

## Polyglot RL Environments

The additive [polyglot adapter module](polyglot-rl-adapters/README.md) normalizes file-change,
build, test, benchmark, and score evidence from four independent synthetic engineering labs:

- [Java Refactoring RL Environment](https://github.com/Kartikm09/java-refactoring-rl-environment)
- [Rust Systems Reliability RL Lab](https://github.com/Kartikm09/rust-systems-reliability-rl-lab)
- [Go Concurrency Performance RL Lab](https://github.com/Kartikm09/go-concurrency-performance-rl-lab)
- [TypeScript Service Reliability RL Lab](https://github.com/Kartikm09/typescript-service-reliability-rl-lab)

Use `polyglot-rl-adapters/compare_reports.py` to compare two candidate patches for the same
task and generate reviewer-ready JSON and Markdown evidence.
