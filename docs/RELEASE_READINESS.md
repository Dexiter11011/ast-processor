# Release Readiness (Iteration 30 → 31)

Checklist for packaging and first public release. Iteration 30 delivers production hardening; Iteration 31 covers packaging.

## Completed (Iteration 30)

- [x] Unified CLI error boundary (`cli/runner.py`, `cli/errors.py`, `cli/diagnostics.py`)
- [x] Exit codes 0 / 1 / 2 preserved
- [x] `--debug` for unexpected internal errors
- [x] Atomic DOCX output with validate-before-replace
- [x] Pre-flight input/output validation
- [x] Transactional plugin loading (all plugins validated before registry mutation)
- [x] Contract tests: exit codes, CLI errors, atomicity, recovery
- [x] `ERROR_HANDLING.md` documentation

## Regression gates (baseline)

| Gate | Target |
|------|--------|
| pytest | 710+ |
| architecture | 75+ |
| golden | 62 |
| validate-docx | PASS |

## Known limitations

| Area | Limitation |
|------|------------|
| Process kill | SIGKILL during write may leave temp files (`.md2docx-*.tmp`) |
| Plugin trust | Plugins execute arbitrary Python; no sandbox |
| Template conditionals | Iteration 29 conditional regions not implemented |
| Windows | Atomic replace tested on current platform; edge cases on locked files possible |
| Logging | No structured logging module in core; CLI owns presentation |

## Iteration 31 (packaging) — out of scope here

- PyPI / wheel distribution
- Entry point verification in clean venv
- Version pinning policy
- CI release workflow

## API stability

Public Tier A/B API unchanged. New internal modules: `cli/runner`, `cli/diagnostics`, `cli/errors`, `output/atomic`. Not exported in the API manifest.
