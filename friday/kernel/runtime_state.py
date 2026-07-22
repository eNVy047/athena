from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class RuntimeState(BaseModel):
    """Single source of truth for Friday OS active sessions and running states."""
    active_conversation_id: Optional[str] = None
    active_planner_goal: Optional[str] = None
    running_workflows: List[str] = Field(default_factory=list)
    active_browser_tabs: List[str] = Field(default_factory=list)
    active_downloads: List[str] = Field(default_factory=list)
    current_workspace_project: Optional[str] = None
    voice_session_active: bool = False
    background_task_count: int = 0
    active_mcp_connections: List[str] = Field(default_factory=list)
    current_user_profile: str = "default"
    health_status: str = "healthy"
