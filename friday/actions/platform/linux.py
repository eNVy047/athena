from __future__ import annotations

import logging
import subprocess
from typing import List
from friday.actions.platform import PlatformAdapter

logger = logging.getLogger("friday-agent")

class LinuxAdapter(PlatformAdapter):
    def __init__(self):
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui.FAILSAFE = False
        except ImportError:
            self.pyautogui = None

    def mouse_move(self, x: int, y: int) -> None:
        if self.pyautogui:
            self.pyautogui.moveTo(x, y)

    def mouse_click(self, x: int, y: int) -> None:
        if self.pyautogui:
            self.pyautogui.click(x, y)

    def mouse_double_click(self, x: int, y: int) -> None:
        if self.pyautogui:
            self.pyautogui.doubleClick(x, y)

    def mouse_right_click(self, x: int, y: int) -> None:
        if self.pyautogui:
            self.pyautogui.rightClick(x, y)

    def keyboard_type(self, text: str) -> None:
        if self.pyautogui:
            self.pyautogui.write(text, interval=0.05)

    def keyboard_press(self, key: str) -> None:
        if self.pyautogui:
            self.pyautogui.press(key)

    def keyboard_hotkey(self, keys: List[str]) -> None:
        if self.pyautogui:
            self.pyautogui.hotkey(*keys)

    def show_notification(self, title: str, message: str) -> None:
        try:
            subprocess.run(["notify-send", title, message], capture_output=True)
        except Exception:
            logger.info(f"[Linux Notification] {title}: {message}")
