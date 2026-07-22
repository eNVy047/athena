from typing import List, Dict, Any, Optional
from datetime import datetime
from friday.domain.context import ExecutionContext
from friday.domain.pal import PlatformCapabilities

class ContextBuilder:
    def __init__(self, capabilities: PlatformCapabilities):
        self.capabilities = capabilities

    def build_structured_context(
        self,
        exec_context: ExecutionContext,
        memories: List[str],
        planner_state: Optional[Dict[str, Any]] = None,
        workspace_details: Optional[str] = None
    ) -> str:
        """Merges multiple sources into a single structured prompt context block."""
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        sections = [
            f"### SYSTEM CLOCK\n* Current Time: {now_str}\n",
            f"### PLATFORM CAPABILITIES\n* Browser Available: {self.capabilities.has_browser}\n* Terminal/Shell: {self.capabilities.has_terminal}\n* Audio Channels: {self.capabilities.has_audio_input}\n"
        ]
        
        # Inject Memories
        if memories:
            sections.append("### RELEVANT LONG-TERM MEMORY")
            for mem in memories:
                sections.append(f"* {mem}")
            sections.append("")

        # Inject Workspace Details
        if workspace_details:
            sections.append(f"### CURRENT WORKSPACE STATE\n{workspace_details}\n")

        # Inject Planner State
        if planner_state:
            sections.append("### ACTIVE EXECUTION PLAN")
            sections.append(f"* Current Goal: {planner_state.get('goal', 'N/A')}")
            sections.append(f"* Current Step: {planner_state.get('current_step', 'N/A')}")
            sections.append("")

        # Inject Chat Context Summary
        if exec_context.chat_history:
            sections.append("### SESSION CONTEXT")
            for msg in exec_context.chat_history[-5:]:  # Last 5 messages
                sections.append(f"  [{msg.role.upper()}]: {msg.content}")
            sections.append("")

        return "\n".join(sections)
