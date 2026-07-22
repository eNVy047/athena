from typing import Dict, List, Optional
import logging
from friday.multi_agent.agent_profile import AgentProfile
from friday.multi_agent.agent_state import AgentState

logger = logging.getLogger(__name__)

class AgentRegistry:
    """Central registry of all specialized sub-agents."""
    
    def __init__(self):
        self._profiles: Dict[str, AgentProfile] = {}
        self._states: Dict[str, AgentState] = {}
        
    def register(self, profile: AgentProfile) -> None:
        self._profiles[profile.agent_id] = profile
        self._states[profile.agent_id] = AgentState()
        logger.info(f"Registered Agent: {profile.agent_id}")
        
    def get_profile(self, agent_id: str) -> Optional[AgentProfile]:
        return self._profiles.get(agent_id)
        
    def get_state(self, agent_id: str) -> Optional[AgentState]:
        return self._states.get(agent_id)
        
    def update_state(self, agent_id: str, state: AgentState) -> None:
        if agent_id in self._states:
            self._states[agent_id] = state
            
    def get_all_profiles(self) -> List[AgentProfile]:
        return list(self._profiles.values())
