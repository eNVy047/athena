import os
import json
from typing import Tuple, Optional
from friday.plugins.plugin_manifest import PluginManifest
from friday.plugins.plugin_permissions import PluginPermission

class PluginValidator:
    """Validates the structure and manifest of a plugin directory before load."""
    
    @staticmethod
    def validate_directory(plugin_dir: str) -> Tuple[bool, Optional[str], Optional[PluginManifest]]:
        if not os.path.isdir(plugin_dir):
            return False, f"Directory does not exist: {plugin_dir}", None
            
        manifest_path = os.path.join(plugin_dir, "manifest.json")
        if not os.path.isfile(manifest_path):
            return False, f"Missing manifest.json in {plugin_dir}", None
            
        try:
            with open(manifest_path, 'r') as f:
                data = json.load(f)
                
            # Convert permissions strings to Enums
            if 'permissions' in data:
                data['permissions'] = [PluginPermission(p) for p in data['permissions']]
                
            manifest = PluginManifest(**data)
            
            entry_point = os.path.join(plugin_dir, manifest.entry_point)
            if not os.path.isfile(entry_point):
                return False, f"Entry point {manifest.entry_point} not found.", None
                
            return True, None, manifest
        except Exception as e:
            return False, f"Invalid manifest format: {e}", None
