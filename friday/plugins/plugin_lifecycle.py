from enum import Enum, auto

class PluginState(Enum):
    UNINSTALLED = auto()
    DISABLED = auto()
    LOADED = auto()
    RUNNING = auto()
    ERROR = auto()
