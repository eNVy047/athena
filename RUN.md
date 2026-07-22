# F.R.I.D.A.Y. — Official Execution & Operational Guide

This document is the official execution reference for building, running, testing, and maintaining F.R.I.D.A.Y.

---

## 1. Requirements & System Prerequisites

### Supported Operating Systems
* **macOS**: macOS 12+ (Apple Silicon & Intel)
* **Linux**: Ubuntu 20.04+, Debian 11+, Arch Linux
* **Windows**: Windows 10/11 (Native & WSL2)

### Runtimes & Dependencies
* **Python**: `>= 3.11`
* **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`
* **Media Dependencies** (Desktop & Audio):
  * **macOS**: System Audio permissions & Qt dependencies
  * **Linux**: `libportaudio2`, `libxcb`, `libgl1-mesa-glx`, `ffmpeg`

---

## 2. Quick Setup & Environment Initialization

### 1. Install `uv` (Package Manager)
```bash
pip install uv
# or on macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Project Dependencies & Virtual Environment
```bash
# Sync all dependencies and auto-create .venv
uv sync
```

### 3. Install Playwright Browsers (for browser automation tools)
```bash
uv run playwright install --with-deps
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```
*Edit `.env` to supply required API keys (e.g. `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `DEEPGRAM_API_KEY`).*

---

## 3. Development Commands

### Initialize / Refresh Environment
```bash
# Re-sync virtual environment with dependencies in pyproject.toml
uv sync
```

### 1. Run MCP Backend Server
Launches the FastMCP SSE tool server on `http://127.0.0.1:8000/sse`.
```bash
uv run friday
# Alternative invocation:
uv run python server.py
```

### 2. Run Desktop GUI Application
Launches the PySide6 / QML desktop user interface.
```bash
uv run friday-desktop
# Alternative invocation:
uv run python -m friday.apps.desktop.app
```

### 3. Run Test Suite
```bash
# Run all unit and integration tests
uv run pytest

# Run tests with output verbosity
uv run pytest -v

# Run specific test suite (e.g. perception tests)
uv run pytest tests/test_perception.py
```

### 4. Code Quality & Linting
```bash
# Run ruff check (if installed)
uv run ruff check .

# Run mypy type checker (if installed)
uv run mypy friday
```

---

## 4. Production Deployment

### Local Production Process Launch
In production mode, start the FastMCP tool server and Desktop Application:

```bash
# 1. Start MCP Tool Server (Production Mode)
uv run python server.py

# 2. Start Desktop Application
uv run python -m friday.apps.desktop.app
```

### Docker Deployment
*(Optional containerized deployment)*

```bash
# Build Docker image
docker build -t friday:latest .

# Run Docker container with environment file
docker run --env-file .env -p 8000:8000 friday:latest
```

---

## 5. Maintenance & Cleaning

### Clear Python & Test Caches
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
rm -rf .ruff_cache
```

### Reset Development Environment
```bash
# Remove virtual environment and reinstall
rm -rf .venv
uv sync
```

### Update Playwright Web Drivers
```bash
uv run playwright install --with-deps
```

---

## 6. Troubleshooting Guide

### 1. Missing Environment Variables
* **Symptom**: `KeyError` or provider error on initialization.
* **Fix**: Run `cp .env.example .env` and ensure all required keys for your selected `LLM_PROVIDER` / `STT_PROVIDER` are defined.

### 2. Playwright / Browser Tool Errors
* **Symptom**: `ExecutableNotFoundError` when executing web browser tools.
* **Fix**: Re-run browser driver installation: `uv run playwright install --with-deps`.

### 3. PySide6 / Qt GUI Display Issues
* **Symptom**: `qt.qpa.plugin: Could not load the Qt platform plugin` on Linux.
* **Fix**: Ensure system dependencies for X11 / Wayland are installed (`sudo apt install libxcb-cursor0 libgl1`).

### 4. Audio Input / Output Device Issues
* **Symptom**: No audio captured or output muted.
* **Fix**: Ensure default microphone and speaker devices are selected in system settings, and check `MIC_DEVICE=default` in `.env`.

### 5. Provider Authentication Errors
* **Symptom**: `401 Unauthorized` or `Invalid API Key`.
* **Fix**: Verify API keys in `.env` without leading/trailing whitespaces or quote wrap issues.
