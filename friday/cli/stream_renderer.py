"""
StreamRenderer — Rich terminal output for the F.R.I.D.A.Y. CLI.

Handles:
- Animated status spinner (Thinking... Planning... Executing...)
- Streaming token output
- Colored Friday/User message display
- Dev mode verbose panels
- Table rendering for providers/memory/doctor
"""
from __future__ import annotations

import os
import sys
import time
import threading
from typing import Optional

# ── Color constants (ANSI) ─────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

# Palette
FRIDAY_COLOR  = "\033[38;5;75m"   # cornflower blue
USER_COLOR    = "\033[38;5;252m"  # near-white
STATUS_COLOR  = "\033[38;5;220m"  # amber
SUCCESS_COLOR = "\033[38;5;83m"   # green
ERROR_COLOR   = "\033[38;5;203m"  # red-orange
MUTED_COLOR   = "\033[38;5;245m"  # grey
DEV_COLOR     = "\033[38;5;141m"  # lavender
HEADER_COLOR  = "\033[38;5;75m"   # same as friday

# ── Dev mode flag ──────────────────────────────────────────────────────────────

DEV_MODE = os.getenv("FRIDAY_DEV_MODE", "").lower() in ("1", "true", "yes")

# ── Internal helpers ───────────────────────────────────────────────────────────

def _c(color: str, text: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{RESET}"


def _print(text: str, end: str = "\n") -> None:
    print(text, end=end, flush=True)


# ── Spinner ────────────────────────────────────────────────────────────────────

class Spinner:
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._message = ""
        self._lock = threading.Lock()

    def start(self, message: str = "Thinking…") -> None:
        if not sys.stdout.isatty():
            _print(_c(STATUS_COLOR, f"  {message}"))
            return
        with self._lock:
            self._message = message
            self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def update(self, message: str) -> None:
        with self._lock:
            self._message = message

    def stop(self, final: str = "") -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        # Clear spinner line
        if sys.stdout.isatty():
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()
        if final:
            _print(_c(SUCCESS_COLOR, f"  ✓ {final}"))

    def _spin(self) -> None:
        idx = 0
        while self._running:
            with self._lock:
                msg = self._message
            frame = self.FRAMES[idx % len(self.FRAMES)]
            sys.stdout.write(f"\r  {_c(STATUS_COLOR, frame)} {_c(STATUS_COLOR, msg)}  ")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.08)


# ── Global spinner instance ─────────────────────────────────────────────────────

_spinner = Spinner()


# ── Public API ─────────────────────────────────────────────────────────────────

def show_status(message: str) -> None:
    """Called by status_callback — updates spinner text."""
    _spinner.update(message)
    if not sys.stdout.isatty():
        _print(_c(STATUS_COLOR, f"  ▸ {message}"))


def start_thinking() -> None:
    _spinner.start("Thinking…")


def stop_thinking(final: str = "") -> None:
    _spinner.stop(final)


def print_friday(message: str) -> None:
    """Print a Friday response message (non-streaming, complete string)."""
    _print("")
    prefix = _c(FRIDAY_COLOR, _c(BOLD, "  Friday  "))
    _print(f"{prefix}")
    for line in message.strip().split("\n"):
        _print(f"  {_c(FRIDAY_COLOR, line)}")
    _print("")


def begin_friday_stream() -> None:
    """Print the Friday speaker label before streaming tokens begin."""
    _print("")
    prefix = _c(FRIDAY_COLOR, _c(BOLD, "  Friday  "))
    _print(f"{prefix}")
    # Print the leading indent for the first token line
    sys.stdout.write(f"  {FRIDAY_COLOR}")
    sys.stdout.flush()


def stream_token(token: str) -> None:
    """Write a single streamed token to stdout immediately (no newline)."""
    sys.stdout.write(token)
    sys.stdout.flush()


def end_friday_stream() -> None:
    """Finalise a streamed Friday response: reset colour and add trailing newlines."""
    sys.stdout.write(RESET + "\n\n")
    sys.stdout.flush()


def print_user(message: str) -> None:
    """Echo the user's input line (for non-interactive mode)."""
    prefix = _c(USER_COLOR, _c(BOLD, "  You  "))
    _print(f"\n{prefix}")
    _print(f"  {_c(USER_COLOR, message)}\n")


def print_error(message: str) -> None:
    _print(f"\n  {_c(ERROR_COLOR, '✗')} {_c(ERROR_COLOR, message)}\n")


def print_success(message: str) -> None:
    _print(f"  {_c(SUCCESS_COLOR, '✓')} {message}")


def print_header(title: str) -> None:
    width = 60
    _print("")
    _print(_c(HEADER_COLOR, "  " + "─" * width))
    _print(_c(HEADER_COLOR, _c(BOLD, f"  {title}")))
    _print(_c(HEADER_COLOR, "  " + "─" * width))


def print_section(title: str) -> None:
    _print(f"\n  {_c(MUTED_COLOR, title)}")
    _print(f"  {_c(MUTED_COLOR, '─' * 40)}")


def print_row(label: str, value: str, color: str = "") -> None:
    label_s = _c(MUTED_COLOR, f"{label:<22}")
    value_s = _c(color or USER_COLOR, value) if value else _c(MUTED_COLOR, "—")
    _print(f"  {label_s}  {value_s}")


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    sep = "  " + "  ".join("─" * w for w in col_widths)
    header_row = "  " + "  ".join(
        _c(HEADER_COLOR, _c(BOLD, h.ljust(col_widths[i])))
        for i, h in enumerate(headers)
    )
    _print("")
    _print(header_row)
    _print(_c(MUTED_COLOR, sep))
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            cell_s = str(cell).ljust(col_widths[i])
            # Color status cells
            if cell_s.strip() in ("✓ Connected", "OK", "PASS"):
                cells.append(_c(SUCCESS_COLOR, cell_s))
            elif cell_s.strip() in ("✗ Error", "FAIL", "Missing"):
                cells.append(_c(ERROR_COLOR, cell_s))
            elif cell_s.strip() == "Deferred":
                cells.append(_c(STATUS_COLOR, cell_s))
            else:
                cells.append(_c(USER_COLOR, cell_s))
        _print("  " + "  ".join(cells))
    _print("")


def dev(label: str, value: str) -> None:
    """Print a dev-mode diagnostic line."""
    if DEV_MODE:
        _print(f"  {_c(DEV_COLOR, f'[DEV] {label}:')} {_c(DIM, value)}")


def print_banner() -> None:
    """Print F.R.I.D.A.Y. ASCII banner."""
    lines = [
        "",
        "  ███████╗██████╗ ██╗██████╗  █████╗ ██╗   ██╗",
        "  ██╔════╝██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝",
        "  █████╗  ██████╔╝██║██║  ██║███████║ ╚████╔╝ ",
        "  ██╔══╝  ██╔══██╗██║██║  ██║██╔══██║  ╚██╔╝  ",
        "  ██║     ██║  ██║██║██████╔╝██║  ██║   ██║   ",
        "  ╚═╝     ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   ",
        "",
        "  Female Replacement Intelligent Digital Assistant Youth",
        "  Developer CLI — v1.0",
        "",
    ]
    for line in lines:
        _print(_c(FRIDAY_COLOR, line))
