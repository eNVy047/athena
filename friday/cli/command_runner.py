"""
CommandRunner — Single-shot command execution for the F.R.I.D.A.Y. CLI.

Handles: friday "open chrome"

Boots context, runs the query through the full pipeline, prints result, exits.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Optional

from friday.cli import stream_renderer as r

logger = logging.getLogger(__name__)


async def run_single_command(
    query: str,
    dev_mode: bool = False,
    quiet: bool = False,
) -> int:
    """
    Execute a single Friday command through the full pipeline.

    Returns:
        0 on success, 1 on error.
    """
    from friday.cli.cli_context import CLIContext

    if dev_mode:
        os.environ["FRIDAY_DEV_MODE"] = "true"

    if not quiet:
        r.print_user(query)

    # Status callback — feeds into spinner
    def on_status(msg: str) -> None:
        r.show_status(msg)
        r.dev("status", msg)

    ctx = CLIContext(status_callback=on_status)

    try:
        r.start_thinking()
        t_init = time.monotonic()

        await ctx.initialize(verbose=dev_mode)

        t_init_done = time.monotonic()
        r.dev("init_time", f"{(t_init_done - t_init)*1000:.0f}ms")

        r.show_status("Processing…")
        t_proc = time.monotonic()

        response = await ctx.process(query)

        t_proc_done = time.monotonic()
        r.dev("process_time", f"{(t_proc_done - t_proc)*1000:.0f}ms")
        r.dev("total_time",   f"{(t_proc_done - t_init)*1000:.0f}ms")

        r.stop_thinking()

        if not quiet:
            r.print_friday(response)

        return 0

    except KeyboardInterrupt:
        r.stop_thinking()
        r.print_error("Cancelled.")
        return 130

    except Exception as exc:
        r.stop_thinking()
        r.print_error(f"Error: {exc}")
        if dev_mode:
            import traceback
            traceback.print_exc()
        logger.debug("[CommandRunner] Exception", exc_info=True)
        return 1

    finally:
        await ctx.shutdown()
