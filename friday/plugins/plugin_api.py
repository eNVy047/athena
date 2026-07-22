from typing import Any, Dict, Optional
from friday.events.event_bus import EventBus
from friday.agent.agent import Agent
from friday.plugins.plugin_permissions import PermissionManager, PluginPermission

class PluginAPI:
    """Facade for plugins to safely interact with Friday."""
    
    def __init__(self, agent: Agent, event_bus: EventBus, permissions: PermissionManager):
        self._agent = agent
        self._event_bus = event_bus
        self._permissions = permissions

    async def submit_request(self, session, request) -> Any:
        # Check permission logic if needed
        return await self._agent.handle_request(session, request)

    async def publish_event(self, topic: str, data: Dict[str, Any]):
        await self._event_bus.publish(topic, data)

    def has_permission(self, perm: PluginPermission) -> bool:
        return self._permissions.has_permission(perm)
