"""
InteractiveShell — REPL mode for the F.R.I.D.A.Y. CLI.

$ friday

Boots the context once, then handles an ongoing conversation.
Slash commands (/status, /providers, /memory, /doctor, /help, /exit) work inline.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from typing import Optional

from friday.cli import stream_renderer as r
from friday.cli.history import SessionHistory, setup_readline, save_readline
from friday.cli.completion import setup_completion


# ── Prompt strings ─────────────────────────────────────────────────────────────

PROMPT_YOU    = f"{r.MUTED_COLOR}  You › {r.RESET}"
PROMPT_FRIDAY = f"{r.FRIDAY_COLOR}{r.BOLD}  Friday › {r.RESET}"


# ── Shell ──────────────────────────────────────────────────────────────────────

class InteractiveShell:
    """
    Full REPL — boots Friday once and handles an ongoing conversation.
    """

    HELP_TEXT = f"""
  {r.FRIDAY_COLOR}F.R.I.D.A.Y. Developer CLI — Slash Commands{r.RESET}

  {r.MUTED_COLOR}/status{r.RESET}            Show system status
  {r.MUTED_COLOR}/providers{r.RESET}         List all providers with health
  {r.MUTED_COLOR}/memory{r.RESET}            Show memory and learned behaviors
  {r.MUTED_COLOR}/doctor{r.RESET}            Run environment validation
  {r.MUTED_COLOR}/benchmark{r.RESET}         Measure pipeline latency
  {r.MUTED_COLOR}/history{r.RESET}           Show session conversation history
  {r.MUTED_COLOR}/voice{r.RESET}             Start voice conversation
  {r.MUTED_COLOR}/logs{r.RESET}              Tail runtime log
  {r.MUTED_COLOR}/reset-memory{r.RESET}      Clear conversation history
  {r.MUTED_COLOR}/reset-learning{r.RESET}    Clear learned behaviors
  {r.MUTED_COLOR}/clear{r.RESET}             Clear terminal
  {r.MUTED_COLOR}/help{r.RESET}              Show this help
  {r.MUTED_COLOR}/exit  /quit  Ctrl+C{r.RESET}   Exit

  {r.MUTED_COLOR}FRIDAY_DEV_MODE=true friday{r.RESET}  — enable verbose developer output
"""

    def __init__(self, dev_mode: bool = False):
        self._dev_mode = dev_mode
        self._history = SessionHistory()
        self._ctx = None

    async def run(self) -> None:
        if self._dev_mode:
            os.environ["FRIDAY_DEV_MODE"] = "true"

        r.print_banner()

        # Boot context
        def on_status(msg: str) -> None:
            r.show_status(msg)
            r.dev("status", msg)

        from friday.cli.cli_context import CLIContext
        self._ctx = CLIContext(status_callback=on_status)

        r.start_thinking()
        r.show_status("Initializing…")
        t0 = time.monotonic()
        try:
            await self._ctx.initialize(verbose=self._dev_mode)
        except Exception as exc:
            r.stop_thinking()
            r.print_error(f"Initialization failed: {exc}")
            if self._dev_mode:
                import traceback
                traceback.print_exc()
            return
        r.stop_thinking()

        elapsed = (time.monotonic() - t0) * 1000
        r.print_success(f"Ready in {elapsed:.0f}ms. Type /help for commands.")
        print()

        # Set up readline
        setup_readline()
        setup_completion()

        # Main REPL loop
        try:
            while True:
                try:
                    if sys.stdout.isatty():
                        user_input = input(PROMPT_YOU).strip()
                    else:
                        line = sys.stdin.readline()
                        if not line:
                            break
                        user_input = line.strip()
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print()
                    r.print_error("Interrupted. Type /exit to quit.")
                    continue

                if not user_input:
                    continue

                # ── Slash commands ─────────────────────────────────────────────
                if user_input.startswith("/"):
                    await self._handle_slash(user_input.lower().strip())
                    continue

                # ── Built-in bare keywords (no slash required) ─────────────────
                cmd_lower = user_input.lower().strip()

                if cmd_lower in ("exit", "quit", "bye", "goodbye"):
                    break

                if cmd_lower == "help":
                    print(self.HELP_TEXT)
                    continue

                if cmd_lower == "clear":
                    await self._handle_slash("/clear")
                    continue

                if cmd_lower == "history":
                    await self._handle_slash("/history")
                    continue

                # ── Normal query → full pipeline (streaming) ───────────────────
                self._history.add_user(user_input)
                r.start_thinking()
                t_start = time.monotonic()
                _streaming_started = False

                def _on_token(token: str) -> None:
                    nonlocal _streaming_started
                    if not _streaming_started:
                        _streaming_started = True
                        r.stop_thinking()
                        r.begin_friday_stream()
                    r.stream_token(token)

                try:
                    response = await self._ctx.process(
                        user_input, stream_callback=_on_token
                    )
                    elapsed_ms = (time.monotonic() - t_start) * 1000

                    if _streaming_started:
                        r.end_friday_stream()
                    else:
                        # Non-streaming result (tool action, clarification, etc.)
                        r.stop_thinking()
                        r.print_friday(response)

                    r.dev("latency", f"{elapsed_ms:.0f}ms")
                    self._history.add_friday(response)

                except asyncio.CancelledError:
                    r.stop_thinking()
                    r.print_error("Cancelled.")

                except Exception as exc:
                    r.stop_thinking()
                    r.print_error(str(exc))
                    if self._dev_mode:
                        import traceback
                        traceback.print_exc()

        finally:
            # Save history
            self._history.save()
            save_readline()
            if self._ctx:
                await self._ctx.shutdown()
            print()
            r.print_success("Goodbye.")
            print()

    # ── Slash command dispatcher ───────────────────────────────────────────────

    async def _handle_slash(self, cmd: str) -> None:
        from friday.cli import developer_tools as dt

        if cmd == "/status":
            await dt.cmd_status(self._ctx)

        elif cmd == "/providers":
            await dt.cmd_providers(self._ctx)

        elif cmd == "/memory":
            await dt.cmd_memory(self._ctx)

        elif cmd == "/doctor":
            await dt.cmd_doctor(self._ctx)

        elif cmd == "/benchmark":
            r.start_thinking()
            await dt.cmd_benchmark(self._ctx)
            r.stop_thinking()

        elif cmd == "/history":
            r.print_header("Session History")
            for turn in self._history.all_turns():
                color = r.FRIDAY_COLOR if turn.role == "friday" else r.USER_COLOR
                label = "Friday" if turn.role == "friday" else "You"
                r.print_row(label, turn.content[:100], color)
            print()

        elif cmd == "/voice":
            await self._run_voice()

        elif cmd == "/logs":
            dt.cmd_logs()

        elif cmd == "/reset-memory":
            dt.cmd_reset_memory()

        elif cmd == "/reset-learning":
            dt.cmd_reset_learning(self._ctx)

        elif cmd == "/clear":
            # Use ANSI escape directly — avoids 'TERM not set' warning in pipes
            if sys.stdout.isatty():
                sys.stdout.write("\033[H\033[2J")
                sys.stdout.flush()
            r.print_banner()

        elif cmd in ("/help", "/?"):
            print(self.HELP_TEXT)

        elif cmd in ("/exit", "/quit"):
            raise SystemExit(0)

        else:
            r.print_error(f"Unknown command: {cmd}. Type /help for help.")

    # ── Voice mode ─────────────────────────────────────────────────────────────

    async def _run_voice(self) -> None:
        vm = self._ctx.voice_manager if self._ctx else None
        if not vm:
            r.print_error("Voice not available. Check STT/TTS provider configuration.")
            return

        r.print_section("Voice Mode — Press Ctrl+C to stop")
        r.print_success("Listening… (push-to-talk: press Enter to record)")

        try:
            await vm.start_listening()
            r.print_success("Voice session started. Speak now.")
            # Keep alive until Ctrl+C
            while True:
                await asyncio.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            try:
                await vm.stop()
            except Exception:
                pass
            r.print_success("Voice mode stopped.")
