# Friday AI OS Test Suite

This directory contains the automated and manual verification suite for the Friday AI Operating System.

## Running Tests

To run the full automated test suite, use the `uv` package manager:

```bash
uv run pytest
```

To run a specific test file:

```bash
uv run pytest tests/test_planner.py
```

## Directory Structure

*   `test_*.py`: Automated unit and integration tests for every subsystem.
*   `TEST.md`: Complete description, expectations, and manual test steps for all subsystems (including Hinglish explanations).
*   `REPORT.md`: Test suite execution report including pass/fail status, coverage summary, and performance metrics.
