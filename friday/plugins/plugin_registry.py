from typing import Dict, List, Optional
from friday.plugins.plugin_manifest import PluginManifest
from friday.plugins.plugin_lifecycle import PluginState

class PluginRegistry:
    """Maintains the loaded catalog of available/installed plugins locally."""
    
    def __init__(self):
        self.plugins: Dict[str, PluginManifest] = {}
        self.states: Dict[str, PluginState] = {}
        self.instances: Dict[str, object] = {}
        
    def register(self, manifest: PluginManifest, state: PluginState = PluginState.UNINSTALLED):
        self.plugins[manifest.name] = manifest
        self.states[manifest.name] = state
        
    def get_manifest(self, name: str) -> Optional[PluginManifest]:
        return self.plugins.get(name)
        
    def get_state(self, name: str) -> Optional[PluginState]:
        return self.states.get(name)
        
    def update_state(self, name: str, state: PluginState):
        self.states[name] = state
        
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())
