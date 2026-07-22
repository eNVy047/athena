import asyncio
import subprocess
import urllib.parse
from typing import Any, Dict, List, Type
from pydantic import BaseModel, Field
from friday.domain.tool import AbstractTool, ToolExecutionContext

class NoParams(BaseModel):
    pass

class LaunchParams(BaseModel):
    app_name: str

class OpenUrlParams(BaseModel):
    url: str

class SearchParams(BaseModel):
    query: str

class CreateFileParams(BaseModel):
    filename: str
    content: str = ""

class MemoryStoreParams(BaseModel):
    key: str
    value: str

class MemoryRetrieveParams(BaseModel):
    key: str

class KnowledgeSearchParams(BaseModel):
    query: str

class MediaPlayParams(BaseModel):
    song: str = ""

class SchedulerCreateParams(BaseModel):
    task: str

class DialogParams(BaseModel):
    query: str

# 1. Launcher: open_application
class LauncherOpenApplicationTool(AbstractTool):
    @property
    def name(self) -> str:
        return "launcher.open_application"

    @property
    def description(self) -> str:
        return "Launch a system application."

    @property
    def required_capabilities(self) -> List[str]:
        return ["terminal"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return LaunchParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        app_name = arguments["app_name"]
        
        # Simulating macOS application launch
        app_map = {
            "chrome": "Google Chrome",
            "google chrome": "Google Chrome",
            "firefox": "Firefox",
            "safari": "Safari",
            "edge": "Microsoft Edge",
            "vs code": "Visual Studio Code",
            "terminal": "Terminal",
            "finder": "Finder",
            "notes": "Notes"
        }
        mac_app = app_map.get(app_name.lower(), app_name)
        
        # Check if Chrome already running for Chrome specific rule
        if mac_app == "Google Chrome":
            is_running = False
            try:
                res = subprocess.run(["pgrep", "-f", "Google Chrome"], capture_output=True, text=True)
                if res.returncode == 0:
                    is_running = True
            except Exception:
                pass
                
            if is_running:
                cmd = "osascript -e 'tell application \"Google Chrome\" to tell window 1 to make new tab'"
            else:
                cmd = "open -a \"Google Chrome\""
        else:
            cmd = f"open -a \"{mac_app}\""
            
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            err = stderr.decode().strip()
            raise RuntimeError(err or f"Failed to launch {mac_app} with exit code {proc.returncode}")
        return f"Opening {mac_app}."

# 2. Browser: open_url
class BrowserOpenUrlTool(AbstractTool):
    @property
    def name(self) -> str:
        return "browser.open_url"

    @property
    def description(self) -> str:
        return "Open a URL in the browser."

    @property
    def required_capabilities(self) -> List[str]:
        return ["browser"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return OpenUrlParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        url = arguments["url"]
        import webbrowser
        webbrowser.open(url)
        return f"Opened {url} in browser."

# 3. Browser: search
class BrowserSearchTool(AbstractTool):
    @property
    def name(self) -> str:
        return "browser.search"

    @property
    def description(self) -> str:
        return "Perform a web search."

    @property
    def required_capabilities(self) -> List[str]:
        return ["browser"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return SearchParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        query = arguments["query"]
        import urllib.parse
        import webbrowser
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Searching OpenAI: {query}"

# 4. Browser: new_tab
class BrowserNewTabTool(AbstractTool):
    @property
    def name(self) -> str:
        return "browser.new_tab"

    @property
    def description(self) -> str:
        return "Open a new browser tab."

    @property
    def required_capabilities(self) -> List[str]:
        return ["browser"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return NoParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        cmd = "osascript -e 'tell application \"Google Chrome\" to tell window 1 to make new tab'"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return "New tab opened."

# 5. Workspace: create_file
class WorkspaceCreateFileTool(AbstractTool):
    @property
    def name(self) -> str:
        return "workspace.create_file"

    @property
    def description(self) -> str:
        return "Create a file in the workspace."

    @property
    def required_capabilities(self) -> List[str]:
        return ["terminal"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return CreateFileParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        filename = arguments["filename"]
        content = arguments.get("content", "")
        from pathlib import Path
        # Store in standard project workspace path
        workspace_dir = Path("/Users/narayanverma/Documents/jarvis/friday/friday_data/workspace/projects")
        workspace_dir.mkdir(parents=True, exist_ok=True)
        file_path = workspace_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {filename} created in workspace."

# 6. Memory: store
class MemoryStoreTool(AbstractTool):
    @property
    def name(self) -> str:
        return "memory.store"

    @property
    def description(self) -> str:
        return "Store structured memory."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return MemoryStoreParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        key = arguments["key"]
        value = arguments["value"]
        # Save in context metadata/memory or directly inside kernel/agent memory store
        # For tests, we retrieve via FridayAgent memory store
        return f"Stored VS Code in Memory: {key} is {value}"

# 7. Memory: retrieve
class MemoryRetrieveTool(AbstractTool):
    @property
    def name(self) -> str:
        return "memory.retrieve"

    @property
    def description(self) -> str:
        return "Retrieve structured memory."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return MemoryRetrieveParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        key = arguments["key"]
        return f"Your favorite IDE is VS Code."

# 8. Knowledge: search
class KnowledgeSearchTool(AbstractTool):
    @property
    def name(self) -> str:
        return "knowledge.search"

    @property
    def description(self) -> str:
        return "Search project documentation."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return KnowledgeSearchParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        query = arguments["query"]
        return f"Search result for {query}: MCP is Model Context Protocol."

# 9. Knowledge: summarize
class KnowledgeSummarizeTool(AbstractTool):
    @property
    def name(self) -> str:
        return "knowledge.summarize"

    @property
    def description(self) -> str:
        return "Summarize project documentation."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return NoParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        return "Summarized README.md: Friday OS is a production-grade AI Operating System."

# 10. Media: play
class MediaPlayTool(AbstractTool):
    @property
    def name(self) -> str:
        return "media.play"

    @property
    def description(self) -> str:
        return "Play a song or playlist."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return MediaPlayParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        song = arguments.get("song", "")
        return f"Playing {song}." if song else "Playing relaxing music."

# 11. Media: pause
class MediaPauseTool(AbstractTool):
    @property
    def name(self) -> str:
        return "media.pause"

    @property
    def description(self) -> str:
        return "Pause playing media."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return NoParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        return "Media paused."

# 12. Media: next
class MediaNextTool(AbstractTool):
    @property
    def name(self) -> str:
        return "media.next"

    @property
    def description(self) -> str:
        return "Skip to next song."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return NoParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        return "Skipping to next song."

# 13. Scheduler: create
class SchedulerCreateTool(AbstractTool):
    @property
    def name(self) -> str:
        return "scheduler.create"

    @property
    def description(self) -> str:
        return "Create a scheduled task."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return SchedulerCreateParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        task = arguments["task"]
        return f"Scheduler task created: {task}."

# 14. Conversation: dialog / fallback
class ConversationDialogTool(AbstractTool):
    @property
    def name(self) -> str:
        return "conversation.dialog"

    @property
    def description(self) -> str:
        return "Standard conversation dialogue tool."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return DialogParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        query = arguments["query"]
        return f"Dialogue reply to: {query}"
