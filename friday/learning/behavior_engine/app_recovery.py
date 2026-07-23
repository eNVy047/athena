"""
F.R.I.D.A.Y. Application Launch Recovery

Wraps application launches with intelligent failure detection and
natural-language recovery suggestions.

Error types detected:
    NOT_FOUND       — app not installed on this Mac
    ALREADY_RUNNING — app is already open
    PERMISSION_DENIED — macOS permission/sandbox issue
    FROZEN          — app is not responding
    OS_ERROR        — generic OS-level error
    LAUNCH_TIMEOUT  — app took too long to respond

Recovery strategies:
    NOT_FOUND       → "App not found. Would you like me to search the App Store?"
    ALREADY_RUNNING → "Already open. Bring to front or restart?"
    FROZEN          → "App isn't responding. Close and reopen?"
    PERMISSION_DENIED → "Permission denied. Check System Settings > Privacy?"
"""
import asyncio
import logging
import subprocess
from typing import List

from friday.learning.behavior_engine.behavior_models import (
    AppErrorType,
    AppLaunchResult,
)

logger = logging.getLogger(__name__)


# ── Error message fragments → error type ────────────────────────────────────

_ERROR_MAP = [
    (["unable to find application", "not find"], AppErrorType.NOT_FOUND),
    (["already running", "already open"],        AppErrorType.ALREADY_RUNNING),
    (["not permitted", "permission denied", "operation not permitted"], AppErrorType.PERMISSION_DENIED),
    (["not responding", "frozen", "timed out"], AppErrorType.FROZEN),
    (["timeout", "timed out"],                  AppErrorType.LAUNCH_TIMEOUT),
]


def _classify_error(stderr: str) -> AppErrorType:
    lower = stderr.lower()
    for patterns, error_type in _ERROR_MAP:
        if any(p in lower for p in patterns):
            return error_type
    return AppErrorType.OS_ERROR


class AppRecovery:
    """
    Intelligent application launch wrapper.

    Usage:
        recovery = AppRecovery()
        result = await recovery.launch("Google Chrome", 'open -a "Google Chrome"')
        if not result.success:
            print(result.recovery_question)  # "Already open — bring to front?"
    """

    async def launch(
        self,
        app_name: str,
        command: str,
        retry: bool = True,
    ) -> AppLaunchResult:
        """
        Execute a launch command with error classification and recovery.
        Retries once on transient errors before giving up.
        """
        result = await self._try_launch(app_name, command)

        if not result.success and retry and result.error_type not in (
            AppErrorType.NOT_FOUND,
            AppErrorType.PERMISSION_DENIED,
        ):
            logger.info("[AppRecovery] Retrying launch of %s...", app_name)
            await asyncio.sleep(0.5)
            result = await self._try_launch(app_name, command)

        return result

    async def _try_launch(self, app_name: str, command: str) -> AppLaunchResult:
        """Run the launch command and classify any errors."""
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=10.0)
            stderr = stderr_bytes.decode().strip()

            if proc.returncode == 0:
                return AppLaunchResult(success=True, app_name=app_name, message=f"Opening {app_name}.")

            error_type = _classify_error(stderr)
            return self._build_failure(app_name, error_type, stderr)

        except asyncio.TimeoutError:
            return self._build_failure(app_name, AppErrorType.LAUNCH_TIMEOUT, "Launch timed out.")
        except Exception as exc:
            return self._build_failure(app_name, AppErrorType.UNKNOWN, str(exc))

    @staticmethod
    def _build_failure(app_name: str, error_type: AppErrorType, raw_error: str) -> AppLaunchResult:
        """Build a natural-language failure result with recovery options."""
        recovery_q: str
        options: List[str]

        if error_type == AppErrorType.NOT_FOUND:
            recovery_q = (
                f"I couldn't find {app_name} on your Mac. "
                f"Would you like me to search the App Store, or open a similar app?"
            )
            options = ["Search App Store", "Open similar app", "Cancel"]

        elif error_type == AppErrorType.ALREADY_RUNNING:
            recovery_q = (
                f"{app_name} is already running. "
                f"Would you like me to bring it to the front, or restart it?"
            )
            options = ["Bring to front", "Restart", "Cancel"]

        elif error_type == AppErrorType.FROZEN:
            recovery_q = (
                f"{app_name} doesn't seem to be responding. "
                f"Would you like me to force-quit it and reopen?"
            )
            options = ["Force quit and reopen", "Just force quit", "Cancel"]

        elif error_type == AppErrorType.PERMISSION_DENIED:
            recovery_q = (
                f"I don't have permission to open {app_name}. "
                f"You may need to check System Settings → Privacy & Security."
            )
            options = ["Open System Settings", "Cancel"]

        elif error_type == AppErrorType.LAUNCH_TIMEOUT:
            recovery_q = (
                f"{app_name} is taking longer than usual. "
                f"It may be loading — would you like me to try again?"
            )
            options = ["Try again", "Cancel"]

        else:
            recovery_q = (
                f"Something went wrong launching {app_name}. "
                f"Error: {raw_error[:100]}"
            )
            options = ["Try again", "Cancel"]

        return AppLaunchResult(
            success=False,
            app_name=app_name,
            message=recovery_q,
            error_type=error_type,
            recovery_question=recovery_q,
            recovery_options=options,
            raw_error=raw_error,
        )

    @staticmethod
    async def bring_to_front(app_name: str) -> bool:
        """Bring a running application to the foreground via AppleScript."""
        script = f'tell application "{app_name}" to activate'
        proc = await asyncio.create_subprocess_shell(
            f"osascript -e '{script}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, _ = await proc.communicate()
        return proc.returncode == 0

    @staticmethod
    async def force_quit(app_name: str) -> bool:
        """Force-quit an application."""
        proc = await asyncio.create_subprocess_shell(
            f"osascript -e 'tell application \"{app_name}\" to quit'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.communicate(), timeout=5.0)
        # Also try pkill as fallback
        subprocess.run(["pkill", "-x", app_name], capture_output=True)
        return True
