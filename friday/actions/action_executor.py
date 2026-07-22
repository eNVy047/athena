from __future__ import annotations

import asyncio
import time
import logging
from typing import Any, Dict
from friday.actions.action_models import ActionRequest, ActionType
from friday.actions.action_result import ActionResult
from friday.actions.action_context import ActionContext
from friday.actions.platform import get_platform_adapter

# Import all package handlers
from friday.actions.mouse import MouseActions
from friday.actions.keyboard import KeyboardActions
from friday.actions.screen import ScreenActions
from friday.actions.window import WindowActions
from friday.actions.filesystem import FilesystemActions
from friday.actions.browser import BrowserActions
from friday.actions.terminal import TerminalActions
from friday.actions.application import ApplicationActions
from friday.actions.process import ProcessActions
from friday.actions.clipboard import ClipboardActions
from friday.actions.notification import NotificationActions
from friday.actions.audio import AudioActions
from friday.actions.camera import CameraActions
from friday.actions.power import PowerActions
from friday.actions.network import NetworkActions

logger = logging.getLogger("friday-agent")

class ActionExecutor:
    def __init__(self):
        self.adapter = get_platform_adapter()
        self.mouse = MouseActions(self.adapter)
        self.keyboard = KeyboardActions(self.adapter)
        self.screen = ScreenActions(self.adapter)
        self.window = WindowActions(self.adapter)
        self.filesystem = FilesystemActions(self.adapter)
        self.browser = BrowserActions(self.adapter)
        self.terminal = TerminalActions(self.adapter)
        self.application = ApplicationActions(self.adapter)
        self.process = ProcessActions(self.adapter)
        self.clipboard = ClipboardActions(self.adapter)
        self.notification = NotificationActions(self.adapter)
        self.audio = AudioActions(self.adapter)
        self.camera = CameraActions(self.adapter)
        self.power = PowerActions(self.adapter)
        self.network = NetworkActions(self.adapter)

    async def execute(self, request: ActionRequest, context: ActionContext) -> ActionResult:
        """Executes action request with retries, timeout, and cancellation protection."""
        logs = []
        start_time = time.time()
        
        for attempt in range(request.retries + 1):
            try:
                logs.append(f"Attempt {attempt + 1}: Executing {request.action_type.value}.{request.command}")
                
                # Check for async versus sync execution
                if request.action_type == ActionType.TERMINAL:
                    # Async task wrapper with timeout
                    output = await asyncio.wait_for(
                        self.terminal.execute_async(request.command, request.arguments),
                        timeout=request.timeout
                    )
                else:
                    # Run sync execution
                    output = self._execute_sync(request.action_type, request.command, request.arguments)
                
                execution_time = (time.time() - start_time) * 1000
                logs.append("Execution completed successfully.")
                return ActionResult(
                    success=True,
                    output=output,
                    execution_time_ms=execution_time,
                    logs=logs,
                    telemetry={"attempt_count": attempt + 1}
                )
            except asyncio.TimeoutError:
                err_msg = f"Action timed out after {request.timeout}s."
                logs.append(err_msg)
                logger.error(f"[ActionExecutor] Timeout: {err_msg}")
            except Exception as e:
                err_msg = str(e)
                logs.append(f"Error: {err_msg}")
                logger.error(f"[ActionExecutor] Error: {err_msg}", exc_info=True)
                
            # Wait brief moment before retry
            if attempt < request.retries:
                await asyncio.sleep(0.5)

        # All retries failed
        execution_time = (time.time() - start_time) * 1000
        return ActionResult(
            success=False,
            error=logs[-1] if logs else "Unknown execution failure.",
            execution_time_ms=execution_time,
            logs=logs,
            telemetry={"attempt_count": request.retries + 1}
        )

    def _execute_sync(self, action_type: ActionType, command: str, arguments: Dict[str, Any]) -> Any:
        if action_type == ActionType.MOUSE:
            return self.mouse.execute(command, arguments)
        elif action_type == ActionType.KEYBOARD:
            return self.keyboard.execute(command, arguments)
        elif action_type == ActionType.SCREEN:
            return self.screen.execute(command, arguments)
        elif action_type == ActionType.WINDOW:
            return self.window.execute(command, arguments)
        elif action_type == ActionType.FILESYSTEM:
            return self.filesystem.execute(command, arguments)
        elif action_type == ActionType.BROWSER:
            return self.browser.execute(command, arguments)
        elif action_type == ActionType.APPLICATION:
            return self.application.execute(command, arguments)
        elif action_type == ActionType.PROCESS:
            return self.process.execute(command, arguments)
        elif action_type == ActionType.CLIPBOARD:
            return self.clipboard.execute(command, arguments)
        elif action_type == ActionType.NOTIFICATION:
            return self.notification.execute(command, arguments)
        elif action_type == ActionType.AUDIO:
            return self.audio.execute(command, arguments)
        elif action_type == ActionType.CAMERA:
            return self.camera.execute(command, arguments)
        elif action_type == ActionType.POWER:
            return self.power.execute(command, arguments)
        elif action_type == ActionType.NETWORK:
            return self.network.execute(command, arguments)
        else:
            raise ValueError(f"Unsupported action category: {action_type.value}")
