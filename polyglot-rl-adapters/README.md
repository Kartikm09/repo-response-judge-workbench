# Polyglot RL Adapters

Additive adapters for normalizing Java, Rust, Go, and TypeScript coding-agent evaluation
artifacts into one reviewer-facing schema.

## What it compares

- accepted/rejected classification and transparent score
- changed-file hashes and path evidence
- formatter, linter, build, public, held-out, regression, and benchmark stages
- benchmark presence and stage outcome
- score difference between two patches for the same task

## Usage

```bash
cd polyglot-rl-adapters
python3 compare_reports.py \
  --language typescript \
  --left /path/to/left/report \
  --right /path/to/right/report \
  --output reports/typescript-comparison
```

The output contains `comparison.json` and `comparison_report.md`. Adapters read generated
evidence; they do not execute candidate code or independently validate claims.

## Registered environments

See `registry.json`. Every listed project is independent, synthetic public proof of work.
