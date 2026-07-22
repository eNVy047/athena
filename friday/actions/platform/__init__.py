from __future__ import annotations

import platform
import logging
from abc import ABC, abstractmethod
from typing import List

logger = logging.getLogger("friday-agent")

class PlatformAdapter(ABC):
    @abstractmethod
    def mouse_move(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def mouse_click(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def mouse_double_click(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def mouse_right_click(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def keyboard_type(self, text: str) -> None:
        pass

    @abstractmethod
    def keyboard_press(self, key: str) -> None:
        pass

    @abstractmethod
    def keyboard_hotkey(self, keys: List[str]) -> None:
        pass

    @abstractmethod
    def show_notification(self, title: str, message: str) -> None:
        pass


def get_platform_adapter() -> PlatformAdapter:
    """Returns the adapter matching host system environment."""
    sys_name = platform.system().lower()
    if sys_name == "darwin":
        from friday.actions.platform.macos import MacOsAdapter
        return MacOsAdapter()
    elif sys_name == "windows":
        from friday.actions.platform.windows import WindowsAdapter
        return WindowsAdapter()
    else:
        from friday.actions.platform.linux import LinuxAdapter
        return LinuxAdapter()
