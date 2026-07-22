from dataclasses import dataclass, field
from typing import List
from friday.plugins.plugin_permissions import PluginPermission

@dataclass
class PluginManifest:
    name: str
    version: str
    author: str
    description: str
    permissions: List[PluginPermission] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    required_providers: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    platform_support: List[str] = field(default_factory=lambda: ["linux", "macos", "windows"])
    entry_point: str = "main.py"
