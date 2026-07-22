from typing import Dict, Optional
from friday.domain.tool import AbstractTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, AbstractTool] = {}

    def register(self, tool: AbstractTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[AbstractTool]:
        return self._tools.get(name)

    def get_tool_by_intent(self, intent: str) -> Optional[AbstractTool]:
        mapping = {
            "application.launch": "launcher.open_application",
            "launcher.open_application": "launcher.open_application",
            "browser.open_url": "browser.open_url",
            "browser.search": "browser.search",
            "browser.new_tab": "browser.new_tab",
            "workspace.create_file": "workspace.create_file",
            "memory.store": "memory.store",
            "memory.retrieve": "memory.retrieve",
            "knowledge.search": "knowledge.search",
            "knowledge.summarize": "knowledge.summarize",
            "media.play": "media.play",
            "media.pause": "media.pause",
            "media.next": "media.next",
            "scheduler.create": "scheduler.create",
            "conversation.dialog": "conversation.dialog",
            "conversation.fallback": "conversation.dialog",
            "workflow.execute": "conversation.dialog"
        }
        tool_name = mapping.get(intent, intent)
        return self.get_tool(tool_name)

    def list_tools(self) -> Dict[str, AbstractTool]:
        return self._tools
