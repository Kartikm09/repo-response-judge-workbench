# ADR 2: correctness precedes prose

Accepted, 2026-09-18. Rank the pass/fail functional assessment before the numeric score.
Scores allocate 60 correctness, 25 regression and 15 explanation-reference points, but a
convincing explanation never hides a failing implementation. This is a transparent rubric,
not an empirically calibrated model or a claim of human reviewer agreement.
Regression: `test_failed_implementation_loses_despite_convincing_explanation`.
