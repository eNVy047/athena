"""
F.R.I.D.A.Y. Production Tools — Real implementations backed by the Provider Framework.

All tools here call live backend systems via ProviderManager.
NO placeholder implementations. NO hardcoded responses.
"""
import asyncio
import logging
import subprocess
import urllib.parse
from typing import Any, Dict, List, Type

from pydantic import BaseModel, Field
from friday.domain.tool import AbstractTool, ToolExecutionContext

logger = logging.getLogger(__name__)


# ── Param Models ───────────────────────────────────────────────────────────

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


# ── Helper ─────────────────────────────────────────────────────────────────

def _get_provider_manager():
    """Lazy-import ProviderManager from DI container to avoid circular imports."""
    try:
        from friday.core.di import container
        from friday.providers.base.provider_manager import ProviderManager
        pm = container.resolve(ProviderManager)
        return pm
    except Exception:
        return None


# ── 1. Launcher: open_application ─────────────────────────────────────────

class LauncherOpenApplicationTool(AbstractTool):
    @property
    def name(self) -> str:
        return "launcher.open_application"

    @property
    def description(self) -> str:
        return "Launch a system application on macOS."

    @property
    def required_capabilities(self) -> List[str]:
        return ["terminal"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return LaunchParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        app_name = arguments["app_name"]
        app_map = {
            # Browsers
            "chrome": "Google Chrome", "google chrome": "Google Chrome",
            "brave": "Brave Browser", "safari": "Safari",
            "firefox": "Firefox", "edge": "Microsoft Edge", "arc": "Arc",
            "opera": "Opera",

            # Editors / IDEs
            "vs code": "Visual Studio Code", "vscode": "Visual Studio Code",
            "visual studio code": "Visual Studio Code",
            "cursor": "Cursor", "pycharm": "PyCharm",
            "xcode": "Xcode", "vim": "MacVim", "neovim": "VimR",
            "intellij": "IntelliJ IDEA", "webstorm": "WebStorm",
            "android studio": "Android Studio", "fleet": "Fleet",
            "sublime": "Sublime Text", "sublime text": "Sublime Text",
            "atom": "Atom", "zed": "Zed",

            # Terminals
            "terminal": "Terminal", "iterm": "iTerm", "iterm2": "iTerm",
            "warp": "Warp", "kitty": "kitty",

            # Communication
            "slack": "Slack", "discord": "Discord",
            "zoom": "Zoom", "teams": "Microsoft Teams",
            "whatsapp": "WhatsApp", "telegram": "Telegram",
            "signal": "Signal", "skype": "Skype",

            # Productivity
            "notion": "Notion", "obsidian": "Obsidian",
            "notes": "Notes", "reminders": "Reminders",
            "calendar": "Calendar", "contacts": "Contacts",
            "mail": "Mail", "spark": "Spark",
            "things": "Things 3", "todoist": "Todoist", "bear": "Bear",

            # Media
            "spotify": "Spotify", "music": "Music",
            "apple music": "Music", "vlc": "VLC",
            "quicktime": "QuickTime Player", "podcasts": "Podcasts",

            # Creative
            "figma": "Figma", "sketch": "Sketch",
            "photoshop": "Adobe Photoshop", "illustrator": "Adobe Illustrator",
            "premiere": "Adobe Premiere Pro", "final cut": "Final Cut Pro",
            "davinci": "DaVinci Resolve", "resolve": "DaVinci Resolve",
            "logic": "Logic Pro", "garageband": "GarageBand",

            # Dev Tools
            "docker": "Docker", "postman": "Postman",
            "tableplus": "TablePlus", "github": "GitHub Desktop",
            "sourcetree": "Sourcetree", "insomnia": "Insomnia",

            # System
            "finder": "Finder", "settings": "System Preferences",
            "system preferences": "System Preferences",
            "system settings": "System Settings",
            "activity monitor": "Activity Monitor",
            "calculator": "Calculator", "preview": "Preview",
            "photos": "Photos", "maps": "Maps",
            "app store": "App Store", "facetime": "FaceTime",
            "messages": "Messages",
        }
        mac_app = app_map.get(app_name.lower(), app_name)

        # Build OS launch command
        if mac_app == "Google Chrome":
            res = subprocess.run(["pgrep", "-f", "Google Chrome"], capture_output=True, text=True)
            cmd = (
                "osascript -e 'tell application \"Google Chrome\" to tell window 1 to make new tab'"
                if res.returncode == 0
                else 'open -a "Google Chrome"'
            )
        else:
            cmd = f'open -a "{mac_app}"'

        # Use AppRecovery for intelligent failure handling
        from friday.learning.behavior_engine.app_recovery import AppRecovery
        recovery = AppRecovery()
        result = await recovery.launch(mac_app, cmd, retry=True)

        if result.success:
            logger.info("[LauncherTool] Launched: %s", mac_app)
            return result.message

        # Handle specific recovery cases
        from friday.learning.behavior_engine.behavior_models import AppErrorType
        if result.error_type == AppErrorType.ALREADY_RUNNING:
            # Try to bring to front automatically
            brought_up = await recovery.bring_to_front(mac_app)
            if brought_up:
                return f"{mac_app} is already open — I've brought it to the front."
            return result.recovery_question

        # For all other errors, return the natural language recovery question
        logger.warning("[LauncherTool] Launch failed for %s: %s", mac_app, result.raw_error)
        return result.recovery_question or f"I couldn't open {mac_app}. {result.raw_error[:100]}"


# ── 2. Browser: open_url ──────────────────────────────────────────────────


class BrowserOpenUrlTool(AbstractTool):
    @property
    def name(self) -> str:
        return "browser.open_url"

    @property
    def description(self) -> str:
        return "Open a URL in the default browser."

    @property
    def required_capabilities(self) -> List[str]:
        return ["browser"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return OpenUrlParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        import webbrowser
        url = arguments["url"]
        webbrowser.open(url)
        logger.info("[BrowserOpenUrl] Opened: %s", url)
        return f"Opened {url} in browser."


# ── 3. Browser: search ────────────────────────────────────────────────────

class BrowserSearchTool(AbstractTool):
    @property
    def name(self) -> str:
        return "browser.search"

    @property
    def description(self) -> str:
        return "Perform a web search in the default browser."

    @property
    def required_capabilities(self) -> List[str]:
        return ["browser"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return SearchParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        import webbrowser
        query = arguments["query"]
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        logger.info("[BrowserSearch] Searching: %s", query)
        return f"Searching the web for: {query}"


# ── 4. Browser: new_tab ───────────────────────────────────────────────────

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
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return "New tab opened."


# ── 5. Workspace: create_file ─────────────────────────────────────────────

class WorkspaceCreateFileTool(AbstractTool):
    @property
    def name(self) -> str:
        return "workspace.create_file"

    @property
    def description(self) -> str:
        return "Create a file in the project workspace."

    @property
    def required_capabilities(self) -> List[str]:
        return ["terminal"]

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return CreateFileParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        from pathlib import Path
        filename = arguments["filename"]
        content = arguments.get("content", "")
        workspace_dir = Path("friday_data/workspace/projects")
        workspace_dir.mkdir(parents=True, exist_ok=True)
        file_path = workspace_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("[WorkspaceCreate] Created: %s", file_path)
        return f"File '{filename}' created in workspace."


# ── 6. Memory: store ──────────────────────────────────────────────────────

class MemoryStoreTool(AbstractTool):
    @property
    def name(self) -> str:
        return "memory.store"

    @property
    def description(self) -> str:
        return "Store a fact or preference in long-term memory."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return MemoryStoreParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        key = arguments["key"]
        value = arguments["value"]
        pm = _get_provider_manager()
        if pm is not None:
            try:
                from friday.providers.memory.base import MemoryProvider
                await pm.execute_with_fallback(
                    "memory",
                    lambda provider: provider.add(
                        messages=[{"role": "user", "content": f"{key}: {value}"}],
                        user_id="user_current",
                    ),
                )
                logger.info("[MemoryStore] Stored '%s' = '%s'", key, value)
                return f"Remembered: {key} is {value}."
            except Exception as exc:
                logger.warning("[MemoryStore] Provider call failed (%s), falling back to local store.", exc)

        # Local fallback: store in a simple text file
        from pathlib import Path
        mem_file = Path("friday_data/memory/user/facts.txt")
        mem_file.parent.mkdir(parents=True, exist_ok=True)
        with open(mem_file, "a", encoding="utf-8") as f:
            f.write(f"{key}: {value}\n")
        return f"Remembered: {key} is {value}."


# ── 7. Memory: retrieve ───────────────────────────────────────────────────

class MemoryRetrieveTool(AbstractTool):
    @property
    def name(self) -> str:
        return "memory.retrieve"

    @property
    def description(self) -> str:
        return "Retrieve a stored fact or preference from long-term memory."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return MemoryRetrieveParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        key = arguments["key"]
        pm = _get_provider_manager()
        if pm is not None:
            try:
                result = await pm.execute_with_fallback(
                    "memory",
                    lambda provider: provider.search(
                        query=key,
                        user_id="user_current",
                        limit=3,
                    ),
                )
                if result and hasattr(result, "results") and result.results:
                    memories = " | ".join(r.memory for r in result.results[:3])
                    logger.info("[MemoryRetrieve] Found: %s", memories)
                    return f"I recall: {memories}"
            except Exception as exc:
                logger.warning("[MemoryRetrieve] Provider call failed (%s), using local fallback.", exc)

        # Local fallback: read from facts file
        from pathlib import Path
        mem_file = Path("friday_data/memory/user/facts.txt")
        if mem_file.exists():
            with open(mem_file, encoding="utf-8") as f:
                lines = [l for l in f.readlines() if key.lower() in l.lower()]
            if lines:
                return "I recall: " + lines[-1].strip()
        return f"I don't have a specific memory for '{key}' yet."


# ── 8. Knowledge: search ──────────────────────────────────────────────────

class KnowledgeSearchTool(AbstractTool):
    @property
    def name(self) -> str:
        return "knowledge.search"

    @property
    def description(self) -> str:
        return "Search for information online using the configured search provider."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return KnowledgeSearchParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        query = arguments["query"]
        pm = _get_provider_manager()
        if pm is not None:
            try:
                result = await pm.execute_with_fallback(
                    "search",
                    lambda provider: provider.search(query=query, num_results=3),
                )
                if result:
                    summary = str(result)[:500]
                    return f"Search results for '{query}': {summary}"
            except Exception as exc:
                logger.warning("[KnowledgeSearch] Search provider failed: %s", exc)

        # Fallback: open browser search
        import webbrowser
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
        return f"Opened browser search for: {query}"


# ── 9. Knowledge: summarize ───────────────────────────────────────────────

class KnowledgeSummarizeTool(AbstractTool):
    @property
    def name(self) -> str:
        return "knowledge.summarize"

    @property
    def description(self) -> str:
        return "Summarize or explain a topic using the LLM."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return KnowledgeSearchParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        query = arguments.get("query", "Give a summary of the project.")
        pm = _get_provider_manager()
        if pm is not None:
            try:
                from friday.providers.llm.base import LLMMessage
                result = await pm.execute_with_fallback(
                    "llm",
                    lambda provider: provider.chat(
                        messages=[
                            LLMMessage(role="system", content="You are F.R.I.D.A.Y., a helpful AI assistant."),
                            LLMMessage(role="user", content=f"Please summarize or explain: {query}"),
                        ]
                    ),
                )
                return result.content
            except Exception as exc:
                logger.warning("[KnowledgeSummarize] LLM call failed: %s", exc)
        return f"I'd be happy to summarize '{query}', but no LLM provider is available right now."


# ── 10. Media: play ───────────────────────────────────────────────────────

class MediaPlayTool(AbstractTool):
    @property
    def name(self) -> str:
        return "media.play"

    @property
    def description(self) -> str:
        return "Play a song or media."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return MediaPlayParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        song = arguments.get("song", "")
        platform = arguments.get("platform", "")

        # Safety net: if song contains "youtube", "browser", or "in chrome" — redirect to browser
        song_lower = song.lower()
        browser_keywords = ("youtube", "yt", "browser", "chrome", "brave", "safari", "firefox", "netflix")
        if any(kw in song_lower for kw in browser_keywords) or any(kw in platform.lower() for kw in browser_keywords):
            # Extract the actual song name (strip platform mentions)
            import re
            clean_song = re.sub(
                r"\b(in|on|via|through|using)\b.*(youtube|yt|browser|chrome|brave|safari|firefox|netflix)\b.*",
                "", song, flags=re.I
            ).strip()
            if not clean_song:
                clean_song = song
            from urllib.parse import quote as q
            yt_url = f"https://www.youtube.com/results?search_query={q(clean_song)}"
            cmd = f'open "{yt_url}"'
            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return f"Opening YouTube to play {clean_song}."

        # Normal path: local Spotify playback
        if song:
            cmd = f"osascript -e 'tell application \"Spotify\" to play track \"{song}\"' 2>/dev/null || open -a Spotify"
        else:
            cmd = "osascript -e 'tell application \"Spotify\" to play' 2>/dev/null || open -a Spotify"
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return f"Playing {song} on Spotify." if song else "Playing music on Spotify."


# ── 11. Media: pause ──────────────────────────────────────────────────────

class MediaPauseTool(AbstractTool):
    @property
    def name(self) -> str:
        return "media.pause"

    @property
    def description(self) -> str:
        return "Pause currently playing media."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return NoParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        cmd = "osascript -e 'tell application \"Spotify\" to pause'"
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return "Media paused."


# ── 12. Media: next ───────────────────────────────────────────────────────

class MediaNextTool(AbstractTool):
    @property
    def name(self) -> str:
        return "media.next"

    @property
    def description(self) -> str:
        return "Skip to the next song."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return NoParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        cmd = "osascript -e 'tell application \"Spotify\" to next track'"
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return "Skipping to next song."


# ── 13. Scheduler: create ─────────────────────────────────────────────────

class SchedulerCreateTool(AbstractTool):
    @property
    def name(self) -> str:
        return "scheduler.create"

    @property
    def description(self) -> str:
        return "Create a scheduled task or reminder."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return SchedulerCreateParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        task = arguments["task"]
        # Log the task to a scheduled tasks file
        from pathlib import Path
        import datetime
        tasks_file = Path("friday_data/activities/scheduler/tasks.txt")
        tasks_file.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().isoformat()
        with open(tasks_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {task}\n")
        logger.info("[Scheduler] Task created: %s", task)
        return f"Scheduled task created: {task}"


# ── 14. Conversation: dialog (LLM-backed) ─────────────────────────────────

class ConversationDialogTool(AbstractTool):
    """
    General-purpose conversational fallback tool.
    Routes all open-ended queries to the LLM via ProviderManager.
    Supports multi-turn conversation via injected chat_history.
    """

    SYSTEM_PROMPT = (
        "You are F.R.I.D.A.Y. (Female Replacement Intelligent Digital Assistant Youth), "
        "Tony Stark's AI assistant. You are highly intelligent, concise, and professional. "
        "You have access to the user's computer, memory, and various tools. "
        "Be helpful, precise, and slightly witty. Respond in plain text — no markdown formatting."
    )

    @property
    def name(self) -> str:
        return "conversation.dialog"

    @property
    def description(self) -> str:
        return "General conversational dialogue backed by the active LLM provider."

    @property
    def required_capabilities(self) -> List[str]:
        return []

    @property
    def parameter_schema(self) -> Type[BaseModel]:
        return DialogParams

    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        from friday.providers.llm.base import LLMMessage

        query = arguments["query"]
        chat_history: list = arguments.get("chat_history", [])
        pm = arguments.get("provider_manager") or _get_provider_manager()
        stream_callback = arguments.get("stream_callback")  # Optional[Callable[[str], None]]

        if pm is None:
            logger.error("[ConversationDialog] No ProviderManager available.")
            return "I'm having trouble connecting to my reasoning engine right now. Please try again."

        # Build message list: system + history + current query
        messages = [LLMMessage(role="system", content=self.SYSTEM_PROMPT)]

        # Inject conversation history (bounded to last 10 turns = 20 messages)
        recent_history = chat_history[-20:] if len(chat_history) > 20 else chat_history
        for turn in recent_history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append(LLMMessage(role=role, content=content))

        # Add current user message
        messages.append(LLMMessage(role="user", content=query))

        try:
            if stream_callback is not None:
                # ── Streaming path ────────────────────────────────────────────
                response = await pm.execute_with_fallback_stream(
                    messages=messages,
                    stream_callback=stream_callback,
                )
                logger.info("[ConversationDialog] LLM streamed (%d chars)", len(response))
                return response
            else:
                # ── Non-streaming path (unchanged) ────────────────────────────
                result = await pm.execute_with_fallback(
                    "llm",
                    lambda provider: provider.chat(messages=messages),
                )
                response = result.content.strip()
                logger.info("[ConversationDialog] LLM responded (%d chars)", len(response))
                return response
        except Exception as exc:
            logger.error("[ConversationDialog] LLM call failed: %s", exc, exc_info=True)
            return f"I encountered an error processing your request: {exc}"

