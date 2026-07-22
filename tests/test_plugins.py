import pytest
import json
from unittest.mock import MagicMock

from friday.plugins.plugin_permissions import PluginPermission
from friday.plugins.plugin_validator import PluginValidator
from friday.plugins.plugin_sandbox import PluginSandbox, SecurityException
from friday.plugins.plugin_api import PluginAPI

def test_manifest_validation(tmp_path):
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()
    
    manifest_data = {
        "name": "TestPlugin",
        "version": "1.0",
        "author": "Jarvis",
        "description": "Test plugin",
        "permissions": ["network", "filesystem"],
        "entry_point": "main.py"
    }
    
    with open(plugin_dir / "manifest.json", "w") as f:
        json.dump(manifest_data, f)
        
    with open(plugin_dir / "main.py", "w") as f:
        f.write("class Plugin:\n    pass")
        
    valid, err, manifest = PluginValidator.validate_directory(str(plugin_dir))
    
    assert valid is True
    assert err is None
    assert manifest.name == "TestPlugin"
    assert PluginPermission.NETWORK in manifest.permissions

@pytest.mark.asyncio
async def test_plugin_sandbox():
    api = MagicMock(spec=PluginAPI)
    api.has_permission.return_value = False
    
    class MockPlugin:
        def __init__(self, api):
            self.api = api
            
        @PluginSandbox.require_permission(PluginPermission.FILESYSTEM)
        async def dangerous_action(self):
            return "Read shadow file"
            
    plugin = MockPlugin(api)
    
    with pytest.raises(SecurityException):
        await plugin.dangerous_action()
        
    api.has_permission.return_value = True
    result = await plugin.dangerous_action()
    assert result == "Read shadow file"
