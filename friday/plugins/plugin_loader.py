import importlib.util
import os
import sys
import logging
from typing import Any, Optional
from friday.plugins.plugin_manifest import PluginManifest

logger = logging.getLogger(__name__)

class PluginLoader:
    """Dynamically loads Python modules from the plugin directories."""
    
    @staticmethod
    def load_plugin(plugin_dir: str, manifest: PluginManifest) -> Optional[Any]:
        plugin_name = manifest.name
        entry_point = os.path.join(plugin_dir, manifest.entry_point)
        
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, entry_point)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)
                
                if hasattr(module, "Plugin"):
                    return module.Plugin
                else:
                    logger.error(f"Plugin {plugin_name} does not export a 'Plugin' class.")
            return None
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return None
