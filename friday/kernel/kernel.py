import logging
import time
from pathlib import Path
from friday.core.di import container
from friday.kernel.runtime_state import RuntimeState
from friday.kernel.service_registry import ServiceRegistry
from friday.kernel.capabilities import CapabilityManager, SystemCapabilities
from friday.kernel.health import RuntimeHealthMonitor

logger = logging.getLogger(__name__)

class FridayKernel:
    def __init__(self, storage_root: Path):
        self.storage_root = storage_root
        self.state = RuntimeState()
        self.registry = ServiceRegistry()
        self.health = RuntimeHealthMonitor(state=self.state)

        # Core integration components
        self.tool_registry = None
        self.activity_store = None
        self.planner = None
        self.context_builder = None
        self.capabilities = None
        self.provider_manager = None
        self._chat_history: list = []

    def bootstrap(self) -> None:
        """Initializes and builds the unified storage layout folders."""
        logger.info(f"Bootstrapping Friday OS Kernel under {self.storage_root}...")

        # 1. Create the unified storage directory layout
        folders = [
            "memory/episodic", "memory/semantic", "memory/user", "memory/cache",
            "knowledge/documents", "knowledge/chunks", "knowledge/embeddings",
            "knowledge/index", "knowledge/metadata",
            "activities/conversations", "activities/planner", "activities/browser",
            "activities/tools", "activities/workflows", "activities/scheduler", "activities/voice",
            "browser/profiles", "browser/cookies", "browser/downloads",
            "browser/screenshots", "browser/cache", "browser/pdf",
            "workspace/projects", "workspace/sessions", "workspace/artifacts", "workspace/temp",
            "logs/planner", "logs/browser", "logs/voice", "logs/security",
            "logs/workflow", "logs/system",
            "metrics/traces", "metrics/performance", "metrics/health",
        ]

        for folder in folders:
            (self.storage_root / folder).mkdir(parents=True, exist_ok=True)

        # Write VERSION file if not present
        version_file = self.storage_root / "VERSION"
        if not version_file.exists():
            with open(version_file, "w", encoding="utf-8") as f:
                f.write("2.0.0")

        # 2. Compile Capability Graph
        sys_caps = CapabilityManager.detect_system_capabilities()
        from friday.domain.pal import PlatformCapabilities
        caps = PlatformCapabilities(
            has_browser=sys_caps.has_chrome,
            has_terminal=sys_caps.has_python,
            has_audio_input=sys_caps.has_audio,
        )
        self.capabilities = caps
        self.state.health_status = "healthy"

        # 3. Bootstrap pipeline components
        from friday.tools.registry import ToolRegistry
        from friday.tools.production_tools import (
            LauncherOpenApplicationTool, BrowserOpenUrlTool, BrowserSearchTool, BrowserNewTabTool,
            WorkspaceCreateFileTool, MemoryStoreTool, MemoryRetrieveTool, KnowledgeSearchTool,
            KnowledgeSummarizeTool, MediaPlayTool, MediaPauseTool, MediaNextTool,
            SchedulerCreateTool, ConversationDialogTool,
        )
        registry = ToolRegistry()
        registry.register(LauncherOpenApplicationTool())
        registry.register(BrowserOpenUrlTool())
        registry.register(BrowserSearchTool())
        registry.register(BrowserNewTabTool())
        registry.register(WorkspaceCreateFileTool())
        registry.register(MemoryStoreTool())
        registry.register(MemoryRetrieveTool())
        registry.register(KnowledgeSearchTool())
        registry.register(KnowledgeSummarizeTool())
        registry.register(MediaPlayTool())
        registry.register(MediaPauseTool())
        registry.register(MediaNextTool())
        registry.register(SchedulerCreateTool())
        registry.register(ConversationDialogTool())
        self.tool_registry = registry

        from friday.core.activity_store import ActivityStore
        from friday.application.services.context_builder import ContextBuilder
        from friday.providers.base.provider_manager import ProviderManager
        from friday.planner.planner import Planner

        self.activity_store = ActivityStore()
        self.planner = Planner()
        self.context_builder = ContextBuilder(capabilities=caps)
        self.provider_manager = ProviderManager()

        # 4. Register inside the DI container
        container.register(FridayKernel, self)
        container.register(RuntimeState, self.state)
        container.register(ServiceRegistry, self.registry)
        container.register(RuntimeHealthMonitor, self.health)
        container.register(ToolRegistry, self.tool_registry)
        container.register(ActivityStore, self.activity_store)
        container.register(Planner, self.planner)
        container.register(ContextBuilder, self.context_builder)
        container.register(ProviderManager, self.provider_manager)

        logger.info("Friday OS Kernel bootstrapped successfully.")

    async def initialize_providers(self) -> None:
        """
        Asynchronously initializes and connects all registered providers.
        Must be called after bootstrap() and before first execute().
        """
        if self.provider_manager is None:
            raise RuntimeError("Kernel not bootstrapped. Call bootstrap() first.")
        logger.info("Initializing all providers...")
        await self.provider_manager.initialize_all()
        logger.info("All providers initialized.")

    async def execute(self, user_query: str, stream_callback=None) -> str:
        """
        Orchestrates E2E execution:
        ContextBuilder → Planner → ToolRegistry → CapabilityManager
        → Tool Execution → ActivityStore → Response

        Args:
            user_query: The raw user input string.
            stream_callback: Optional callable(token: str) invoked for each LLM
                             token when intent is `conversation.dialog`.
        """
        from friday.domain.context import ExecutionContext, ChatMessage
        from friday.domain.tool import ToolExecutionContext
        from friday.core.activity_store import ActivityRecord
        from friday.providers.llm.base import LLMMessage

        start_time = time.time()

        # 1. Context Builder — build structured context with chat history
        exec_ctx = ExecutionContext(
            session_id="session_current",
            user_id="user_current",
            chat_history=[ChatMessage(role="user", content=user_query)],
        )
        self.context_builder.build_structured_context(
            exec_context=exec_ctx,
            memories=[],
            planner_state={"goal": user_query[:50], "current_step": "Step 1"},
        )

        # 2. Planner Intent Classification — always use the async path (LLM + keyword fallback)
        intent, params = await self.planner.classify_intent_async(user_query)

        # 3. Tool Registry Resolution
        tool = self.tool_registry.get_tool_by_intent(intent)

        response_text = ""
        error_msg = None
        status = "SUCCESS"

        if tool is None:
            status = "FAILED"
            error_msg = f"No tool resolved for intent: {intent}"
            response_text = "I'm not sure how to handle that right now."
            logger.warning(f"[Kernel] No tool for intent '{intent}'. Query: {user_query!r}")
        else:
            try:
                # 4. Capability Verification
                CapabilityManager.verify_tool_capabilities(tool)

                # 5. Tool Execution
                tool_ctx = ToolExecutionContext(session_id="session_current", user_id="user_current")
                tool_args = params

                # Align parameter schema types by intent and inject shared resources
                if intent == "launcher.open_application":
                    tool_args = {"app_name": params.get("app_name", "Finder")}
                elif intent == "browser.open_url":
                    tool_args = {"url": params.get("url", "https://google.com")}
                elif intent == "browser.search":
                    tool_args = {"query": params.get("query", user_query)}
                elif intent == "browser.new_tab":
                    tool_args = {}
                elif intent == "media.play":
                    tool_args = {"song": params.get("song", "")}
                elif intent == "media.pause":
                    tool_args = {}
                elif intent == "media.next":
                    tool_args = {}
                elif intent == "memory.store":
                    tool_args = {"key": params.get("key", ""), "value": params.get("value", "")}
                elif intent == "memory.retrieve":
                    tool_args = {"key": params.get("key", "")}
                elif intent == "scheduler.create":
                    tool_args = {"task": params.get("task", user_query)}
                elif intent == "workspace.create_file":
                    tool_args = {"filename": params.get("filename", "untitled.txt"), "content": params.get("content", "")}
                elif intent in ("knowledge.search", "knowledge.summarize"):
                    tool_args = {"query": params.get("query", user_query)}
                elif intent == "conversation.dialog":
                    # Pass full chat history + provider_manager + optional stream_callback
                    tool_args = {
                        "query": user_query,
                        "chat_history": self._chat_history,
                        "provider_manager": self.provider_manager,
                        "stream_callback": stream_callback,  # None → non-streaming
                    }
                else:
                    # Generic: pass params as-is, inject provider_manager if accepted
                    tool_args = params

                execution_result = await tool.execute(tool_ctx, tool_args)
                response_text = str(execution_result)

            except Exception as exc:
                status = "FAILED"
                error_msg = str(exc)
                response_text = f"Execution failed: {exc}"
                logger.error(f"[Kernel] Tool execution failed: {exc}", exc_info=True)

        # 6. Activity Store Recording
        duration = time.time() - start_time
        record = ActivityRecord(
            conversation_id="conv_current",
            user_request=user_query,
            selected_tools=[tool.name] if tool else [],
            execution_duration=duration,
            error_message=error_msg,
        )
        self.activity_store.record(record)

        # 7. Update chat history for multi-turn context
        self._chat_history.append({"role": "user", "content": user_query})
        self._chat_history.append({"role": "assistant", "content": response_text})
        # Keep history bounded to last 20 turns
        if len(self._chat_history) > 40:
            self._chat_history = self._chat_history[-40:]

        logger.info(
            "[Kernel] Executed | intent=%s | tool=%s | status=%s | %.0fms",
            intent,
            tool.name if tool else "None",
            status,
            duration * 1000,
        )

        return response_text

    def shutdown(self) -> None:
        logger.info("Shutting down Friday OS Kernel...")
        self.registry.clear()
        logger.info("Friday OS Kernel shutdown complete.")
