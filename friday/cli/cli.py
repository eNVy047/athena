"""
F.R.I.D.A.Y. Developer CLI — Main entry point.

Usage:
    friday "open chrome"           Single command
    friday                         Interactive REPL
    friday status                  System status
    friday providers               Provider dashboard
    friday memory                  Memory + behaviors
    friday doctor                  Environment check
    friday benchmark               Latency benchmark
    friday logs                    Tail log file
    friday voice                   Voice conversation
    friday reset-memory            Clear history
    friday reset-learning          Clear learned behaviors
    friday --dev "open chrome"     Dev mode (verbose)
    friday --quiet "open chrome"   No output (for scripting)
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys


# ── Logging setup ─────────────────────────────────────────────────────────────

def _configure_logging(dev_mode: bool) -> None:
    level = logging.DEBUG if dev_mode else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # Suppress noisy 3rd-party loggers unless in dev mode
    if not dev_mode:
        for noisy in ["httpx", "httpcore", "urllib3", "asyncio", "hpack"]:
            logging.getLogger(noisy).setLevel(logging.ERROR)


# ── Standalone dev commands (no boot required) ─────────────────────────────────

_STANDALONE_CMDS = {"logs", "reset-memory"}


async def _run_with_context(cmd: str, ctx, dev_mode: bool) -> None:
    """Dispatch a dev-tool command that requires an initialized CLIContext."""
    from friday.cli import developer_tools as dt

    if cmd == "status":
        await dt.cmd_status(ctx)
    elif cmd == "providers":
        await dt.cmd_providers(ctx)
    elif cmd == "memory":
        await dt.cmd_memory(ctx)
    elif cmd == "doctor":
        await dt.cmd_doctor(ctx)
    elif cmd == "benchmark":
        from friday.cli import stream_renderer as r
        r.start_thinking()
        await dt.cmd_benchmark(ctx)
        r.stop_thinking()
    elif cmd == "voice":
        shell = __import__("friday.cli.interactive_shell", fromlist=["InteractiveShell"]).InteractiveShell(dev_mode=dev_mode)
        shell._ctx = ctx
        await shell._run_voice()
    elif cmd == "reset-learning":
        dt.cmd_reset_learning(ctx)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point — registered as `friday` console script."""
    parser = argparse.ArgumentParser(
        prog="friday",
        description="F.R.I.D.A.Y. Developer CLI — Full pipeline testing tool",
        add_help=True,
    )
    parser.add_argument(
        "command_or_query",
        nargs="?",
        help=(
            "Command to run (status|providers|memory|doctor|benchmark|"
            "voice|logs|reset-memory|reset-learning) "
            "or a natural language query in quotes."
        ),
    )
    parser.add_argument(
        "--dev", "-d",
        action="store_true",
        default=os.getenv("FRIDAY_DEV_MODE", "").lower() in ("1", "true", "yes"),
        help="Enable developer mode (verbose planner, tool, latency output).",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress banner and formatting (for scripting).",
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Print version and exit.",
    )

    args = parser.parse_args()

    if args.version:
        print("friday-cli 1.0.0")
        sys.exit(0)

    dev_mode = args.dev
    if dev_mode:
        os.environ["FRIDAY_DEV_MODE"] = "true"

    _configure_logging(dev_mode)

    cmd = (args.command_or_query or "").strip()

    # ── Standalone commands (no boot) ─────────────────────────────────────────
    if cmd == "logs":
        from friday.cli import developer_tools as dt
        dt.cmd_logs()
        sys.exit(0)

    if cmd == "reset-memory":
        from friday.cli import developer_tools as dt
        dt.cmd_reset_memory()
        sys.exit(0)

    # ── Interactive REPL ───────────────────────────────────────────────────────
    if not cmd:
        from friday.cli.interactive_shell import InteractiveShell
        shell = InteractiveShell(dev_mode=dev_mode)
        try:
            asyncio.run(shell.run())
        except KeyboardInterrupt:
            pass
        sys.exit(0)

    # ── All other commands require a booted context ────────────────────────────
    async def _boot_and_run():
        from friday.cli import stream_renderer as r
        from friday.cli.cli_context import CLIContext

        def on_status(msg: str) -> None:
            r.show_status(msg)
            r.dev("status", msg)

        ctx = CLIContext(status_callback=on_status)

        # Dev-tool commands (status/providers/memory/doctor/benchmark/voice)
        DEV_CMDS = {"status", "providers", "memory", "doctor", "benchmark", "voice", "reset-learning"}
        is_dev_cmd = cmd in DEV_CMDS

        # Boot (show spinner for dev cmds too, since they need providers)
        if not args.quiet:
            r.start_thinking()
            r.show_status("Initializing…")

        try:
            await ctx.initialize(verbose=dev_mode)
        except Exception as exc:
            if not args.quiet:
                r.stop_thinking()
                r.print_error(f"Initialization failed: {exc}")
            if dev_mode:
                import traceback
                traceback.print_exc()
            return 1

        if not args.quiet:
            r.stop_thinking()

        try:
            if is_dev_cmd:
                await _run_with_context(cmd, ctx, dev_mode)
                return 0

            # Natural language query
            import time

            if not args.quiet:
                r.print_user(cmd)
                r.start_thinking()

            t0 = time.monotonic()

            if args.quiet:
                # Quiet / pipe mode: non-streaming, accumulate then print
                response = await ctx.process(cmd)
                elapsed = (time.monotonic() - t0) * 1000
                print(response)
            else:
                # Interactive / TTY mode: stream tokens live
                _streaming_started = False

                def _on_token(token: str) -> None:
                    nonlocal _streaming_started
                    if not _streaming_started:
                        _streaming_started = True
                        r.stop_thinking()
                        r.begin_friday_stream()
                    r.stream_token(token)

                response = await ctx.process(cmd, stream_callback=_on_token)
                elapsed = (time.monotonic() - t0) * 1000

                if _streaming_started:
                    r.end_friday_stream()
                else:
                    # No tokens streamed (tool action / short answer)
                    r.stop_thinking()
                    r.print_friday(response)

                r.dev("latency", f"{elapsed:.0f}ms")

            return 0

        except KeyboardInterrupt:
            if not args.quiet:
                r.stop_thinking()
                r.print_error("Cancelled.")
            return 130

        except Exception as exc:
            if not args.quiet:
                r.stop_thinking()
                r.print_error(str(exc))
            else:
                print(f"Error: {exc}", file=sys.stderr)
            if dev_mode:
                import traceback
                traceback.print_exc()
            return 1

        finally:
            await ctx.shutdown()

    exit_code = asyncio.run(_boot_and_run())
    sys.exit(exit_code or 0)


if __name__ == "__main__":
    main()
