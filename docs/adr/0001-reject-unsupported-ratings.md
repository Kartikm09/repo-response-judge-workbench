# ADR 1: reject unsupported ratings

Accepted, 2026-09-18. Missing task requirements, command records or executed requirement coverage
raise `ValueError` in `judge_comparison`; the CLI returns a nonzero argument error. An unknown score
would be easier to display but too easily mistaken for a neutral preference. Regression coverage:
`test_missing_evidence_rejected_instead_of_rated` and `test_missing_regression_evidence_rejected`.
Old boolean-only input must be migrated using `examples/comparison.json`; CLI spelling remains.
