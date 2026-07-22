import pytest
from typing import List, Type, Dict, Any
from pydantic import BaseModel
from friday.domain.tool import AbstractTool, ToolExecutionContext
from friday.tools.metadata import ToolMetadata
from friday.tools.registry import ToolRegistry
from friday.tools.permissions import PermissionGuard
from friday.tools.executor import ToolExecutor

class SimpleParams(BaseModel):
    value: str

class MockTool(AbstractTool):
    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "A mock tool."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return SimpleParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        return f"Echo: {arguments['value']}"

@pytest.mark.asyncio
async def test_tool_registry_and_execution():
    registry = ToolRegistry()
    tool = MockTool()
    registry.register(tool)
    
    assert registry.get_tool("mock_tool") == tool
    
    guard = PermissionGuard(allowed_permissions=["system"])
    executor = ToolExecutor(permission_guard=guard)
    
    metadata = ToolMetadata(
        name="mock_tool",
        description="Test",
        permissions=["system"],
        parameter_schema=SimpleParams,
        retry_limit=1,
        timeout=5.0
    )
    
    ctx = ToolExecutionContext(session_id="s123", user_id="u456")
    res = await executor.run_tool(tool, metadata, ctx, {"value": "narayan"})
    
    assert res == "Echo: narayan"
