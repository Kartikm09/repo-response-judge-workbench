# ADR 3: ingest command evidence without executing it

Accepted, 2026-09-18. Command argv, timestamps, exit codes and test counts are data. The
review workbench never passes submitted command text to a shell. A separate isolated runner
owns execution; this component validates consistency and linkage, not authenticity. This
keeps review usable for local reports without giving an untrusted report executable authority.
Paths are checked against the task scope and traversal/absolute paths are rejected.
