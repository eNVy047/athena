import importlib
import sys
from pathlib import Path
from typing import Any

class PluginLoader:
    """Dynamically loads packaged skill plugins at runtime."""
    def __init__(self, plugin_dir: str):
        self.plugin_dir = Path(plugin_dir)

    def load_plugin(self, module_name: str) -> Any:
        sys.path.insert(0, str(self.plugin_dir.absolute()))
        try:
            module = importlib.import_module(module_name)
            return module
        finally:
            if str(self.plugin_dir.absolute()) in sys.path:
                sys.path.remove(str(self.plugin_dir.absolute()))
