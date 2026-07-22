import asyncio
import logging
from typing import Any, Dict
from friday.domain.tool import AbstractTool, ToolExecutionContext
from friday.tools.metadata import ToolMetadata
from friday.tools.validators import ToolValidator
from friday.tools.permissions import PermissionGuard

logger = logging.getLogger(__name__)

class ToolExecutor:
    def __init__(self, permission_guard: PermissionGuard):
        self.permission_guard = permission_guard

    async def run_tool(
        self,
        tool: AbstractTool,
        metadata: ToolMetadata,
        context: ToolExecutionContext,
        arguments: Dict[str, Any]
    ) -> Any:
        # 1. Permission checks
        if not self.permission_guard.is_authorized(metadata.permissions):
            raise PermissionError(f"Unauthorized to run tool: {tool.name}")

        # 2. Argument validation
        validated_args = ToolValidator.validate_inputs(metadata.parameter_schema, arguments)

        # 3. Execution loop with retries and timeout
        last_error = None
        for attempt in range(metadata.retry_limit + 1):
            try:
                # Wrap execution in timeout
                return await asyncio.wait_for(
                    tool.execute(context, validated_args),
                    timeout=metadata.timeout
                )
            except asyncio.TimeoutError:
                last_error = TimeoutError(f"Tool {tool.name} timed out after {metadata.timeout}s.")
                logger.warning(f"Timeout on tool {tool.name} (attempt {attempt+1})")
            except Exception as e:
                last_error = e
                logger.warning(f"Error executing tool {tool.name} (attempt {attempt+1}): {e}")
                
            await asyncio.sleep(0.5 * attempt)

        if last_error is not None:
            raise last_error
        raise RuntimeError("Tool execution failed with no recorded exceptions.")
