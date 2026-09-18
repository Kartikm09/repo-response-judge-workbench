# Defect and review record

## RRJ-001: unsupported response rated as correct

Baseline: `b447490727636439eeaefdb2ae2e02607579f51e`. Severity: high for an evaluation
artifact because incorrect acceptance undermines the main purpose of the repository.

Reproduce against that commit: pass `final_status=solves_task`, `tests_passed=true`, a filename,
a command string and `rationale_has_evidence=true` to both responses. The scorer emits 100/100
without requirements, timestamps, exit codes or test outcomes. Expected: refuse to rate.

The original isolated suite passed 2 core and 2 adapter tests. Adding the evidence contract
regressions then produced 13-test-suite failures on the original implementation. After the
repair the isolated Python 3.12 Linux arm64 suite passed 13 core and 2 adapter tests; the final macOS Seatbelt run passed 13 core and 5 adapter tests. The CLI
example chooses A and gives the well-written failing B response 15 explanation points, with
functional and regression assessments marked failed. These are synthetic input examples;
the regression suite itself was executed, the fictional parser commands were not.

## Substantive code-review example

This is an internal review example, not an accepted external contribution.

Finding: `if response.get("tests_passed") is True: score += 25` trusts an assertion with no
link to a command. Adding a required timestamp alone would still permit an exit code of 1
paired with all-pass counts. Require command IDs, argv, timezone-aware ordered timestamps,
integer exit codes/counts, coverage of required behavior and rejection of contradictions.

The legacy adapter also rejected neither string booleans nor contradictory successful stages and ranked a failed candidate above an accepted one by raw score. Three additional regression tests reproduced these failures; adapters now validate these records and prioritize acceptance.

The reviewer also checks that Python `bool` does not satisfy integer exit-code validation,
that skipping every test does not count as execution, and that a source path outside the task
scope cannot be laundered through an impressive explanation. These findings correspond to
named tests in `tests/test_evidence_contract.py`. Remaining limitation: internally consistent
fabricated reports remain possible, so provenance must come from a trusted runner.

## Test strategy

Unit tests exercise accepted, failed and refused judgments. The CLI runs the synthetic full
example; adapter tests preserve older report imports. Negative tests mutate one input field at
a time. No external model/API keys or hidden reasoning are needed. `make verify` runs all three
layers. There is no browser UI, production deployment or claim of adversarial sandboxing.

Independent review found a further comparison boundary: raw scores with different maxima cannot be compared fairly. The adapter now refuses mixed scales and rejects malformed stage objects cleanly. These reviewer findings were reproduced before correction; final tests cover 14 core and 7 adapter cases.
