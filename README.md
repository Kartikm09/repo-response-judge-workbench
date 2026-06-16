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
