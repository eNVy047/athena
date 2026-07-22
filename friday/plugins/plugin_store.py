import os
import json
from typing import List, Dict

class PluginStore:
    """Local file-based marketplace/catalog interface to list available plugins."""
    
    def __init__(self, plugins_dir: str):
        self.plugins_dir = plugins_dir
        
    def list_available_plugins(self) -> List[Dict[str, str]]:
        available: List[Dict[str, str]] = []
        if not os.path.exists(self.plugins_dir):
            return available
            
        for d in os.listdir(self.plugins_dir):
            path = os.path.join(self.plugins_dir, d)
            if os.path.isdir(path):
                manifest_path = os.path.join(path, "manifest.json")
                if os.path.isfile(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            data = json.load(f)
                            available.append({
                                "name": data.get("name", d),
                                "version": data.get("version", "1.0"),
                                "description": data.get("description", ""),
                                "dir": path
                            })
                    except Exception:
                        pass
        return available
