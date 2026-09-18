# RFC: evidence before preference

Status: implemented locally on 18 September 2026. Independent synthetic portfolio work.

The original scorer in `src/repo_response_judge/judge.py` awarded up to 100 points from
`final_status`, `tests_passed`, filenames and rationale booleans. It could rank a response
without any executable result and treated a persuasive explanation as evidence of correctness.
The preserved CLI command now rejects records with absent or contradictory execution evidence.

A task declares requirement IDs, expected behavior, correctness/regression categories and allowed
file patterns. Each response supplies changed paths, timestamped argv/exit records, test counts
linked to a command and requirement IDs, and a separately assessed explanation with references.
Every required behavior needs executed evidence. Duplicate command IDs, unsafe paths, invalid
counts, timezone-free/reversed timestamps and contradictory results are errors.

A failed implementation cannot outrank a passing implementation through better prose. A structured
result exposes correctness, regression risk and explanation quality separately. This deterministic
rule is intentionally conservative: one failed command associated with multiple requirements does
not identify which individual requirement failed. Split commands/results for finer attribution.

These records are supplied artifacts, not cryptographic proof that a command ran or proof of all
possible behavior. The workbench does not execute arbitrary submitted commands. Examples are
explicitly synthetic; trusted runners must capture real records before making public claims.

Validation: `PYTHONPATH=src python3 -m unittest discover -s tests -v` covers absent evidence,
contradictions, failures with polished prose, scope, timestamp and requirement-reference errors.
`python3 -m unittest discover -s polyglot-rl-adapters/tests -v` preserves legacy normalization.
The normalized polyglot format is a separate legacy report adapter; it does not add missing
requirements or timestamps and should not be represented as equivalent to this stricter contract.
