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

## Evidence contract and verification

`make verify` runs core tests, legacy adapter tests and the CLI example. The original commands
remain supported. Input now requires expected behavior, allowed file scope, timestamped command
records, exit codes and requirement-linked test counts; missing or contradictory evidence is
rejected. See the [RFC](docs/evidence-contract-rfc.md), [defect and review record](docs/defect-and-review.md)
and [ADRs](docs/adr/0001-reject-unsupported-ratings.md).

The example deliberately pairs convincing prose with a failing implementation. Correctness,
regression risk and explanation quality remain separate. Example parser executions are synthetic
input records, not actual parser runs. The workbench validates supplied evidence and does not
independently authenticate its provenance or execute submitted command strings.
