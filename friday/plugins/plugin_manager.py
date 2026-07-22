import logging
from dataclasses import asdict
from friday.plugins.plugin_registry import PluginRegistry
from friday.plugins.plugin_store import PluginStore
from friday.plugins.plugin_validator import PluginValidator
from friday.plugins.plugin_loader import PluginLoader
from friday.plugins.plugin_lifecycle import PluginState
from friday.plugins.plugin_permissions import PermissionManager
from friday.plugins.plugin_api import PluginAPI
from friday.plugins.plugin_events import PluginStateChangeEvent, PLUGIN_LOADED, PLUGIN_ERROR, PLUGIN_ENABLED, PLUGIN_DISABLED
from friday.events.event_bus import EventBus
from friday.agent.agent import Agent

logger = logging.getLogger(__name__)

class PluginManager:
    """The central Facade coordinating plugin loading, validation, permissions, and lifecycle."""
    
    def __init__(self, agent: Agent, event_bus: EventBus, plugins_dir: str = "friday/plugins"):
        self.agent = agent
        self.event_bus = event_bus
        self.registry = PluginRegistry()
        self.store = PluginStore(plugins_dir)
        self.plugins_dir = plugins_dir
        
    async def discover_and_load_all(self):
        """Scans plugins dir and loads valid plugins."""
        available = self.store.list_available_plugins()
        for p in available:
            await self.install_and_load(p['dir'])
            
    async def install_and_load(self, plugin_dir: str) -> bool:
        valid, err, manifest = PluginValidator.validate_directory(plugin_dir)
        if not valid or not manifest:
            logger.error(f"Plugin validation failed for {plugin_dir}: {err}")
            return False
            
        self.registry.register(manifest, PluginState.DISABLED)
        
        PluginClass = PluginLoader.load_plugin(plugin_dir, manifest)
        if not PluginClass:
            self.registry.update_state(manifest.name, PluginState.ERROR)
            await self._emit_state_change(manifest.name, PluginState.DISABLED, PluginState.ERROR)
            return False
            
        permissions = PermissionManager(manifest.permissions)
        api = PluginAPI(self.agent, self.event_bus, permissions)
        
        try:
            instance = PluginClass(api=api)
            self.registry.instances[manifest.name] = instance
            self.registry.update_state(manifest.name, PluginState.LOADED)
            await self._emit_state_change(manifest.name, PluginState.DISABLED, PluginState.LOADED)
            return True
        except Exception as e:
            logger.error(f"Failed to instantiate plugin {manifest.name}: {e}")
            self.registry.update_state(manifest.name, PluginState.ERROR)
            await self._emit_state_change(manifest.name, PluginState.DISABLED, PluginState.ERROR)
            return False
            
    async def enable_plugin(self, name: str) -> bool:
        state = self.registry.get_state(name)
        if state != PluginState.LOADED:
            return False
            
        instance = self.registry.instances.get(name)
        if hasattr(instance, "on_enable"):
            try:
                await instance.on_enable()
            except Exception as e:
                logger.error(f"Plugin {name} failed on_enable: {e}")
                self.registry.update_state(name, PluginState.ERROR)
                return False
                
        self.registry.update_state(name, PluginState.RUNNING)
        await self._emit_state_change(name, PluginState.LOADED, PluginState.RUNNING)
        return True

    async def _emit_state_change(self, plugin_name: str, old_state: PluginState, new_state: PluginState):
        topic = PLUGIN_LOADED
        if new_state == PluginState.ERROR:
            topic = PLUGIN_ERROR
        elif new_state == PluginState.RUNNING:
            topic = PLUGIN_ENABLED
        elif new_state == PluginState.DISABLED:
            topic = PLUGIN_DISABLED
            
        await self.event_bus.publish(topic, asdict(PluginStateChangeEvent(
            event_type=topic,
            plugin_id=plugin_name,
            plugin_name=plugin_name,
            old_state=old_state.name,
            new_state=new_state.name
        )))
