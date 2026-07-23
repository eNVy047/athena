import shutil
import sys
import os
from typing import Dict, Any
from pydantic import BaseModel, Field

class SystemCapabilities(BaseModel):
    os_name: str
    has_git: bool = False
    has_python: bool = False
    has_node: bool = False
    has_docker: bool = False
    has_chrome: bool = False
    has_audio: bool = False

class CapabilityManager:
    @staticmethod
    def detect_system_capabilities() -> SystemCapabilities:
        """Detects OS binaries and platform libraries at startup."""
        # On macOS, browsers are .app bundles not on PATH — use 'open -a' to probe
        def _has_browser_macos() -> bool:
            import subprocess
            browsers = [
                "Google Chrome", "Brave Browser", "Safari",
                "Firefox", "Arc", "Microsoft Edge", "Chromium",
            ]
            for b in browsers:
                result = subprocess.run(
                    ["osascript", "-e", f'id of application "{b}"'],
                    capture_output=True, text=True, timeout=2,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return True
            return False

        def _has_browser() -> bool:
            if sys.platform == "darwin":
                return _has_browser_macos()
            # Linux / Windows: check PATH
            return any(
                shutil.which(b)
                for b in ["google-chrome", "chrome", "chromium", "firefox", "brave"]
            )

        return SystemCapabilities(
            os_name=sys.platform,
            has_git=bool(shutil.which("git")),
            has_python=bool(shutil.which("python3") or shutil.which("python")),
            has_node=bool(shutil.which("node")),
            has_docker=bool(shutil.which("docker")),
            has_chrome=_has_browser(),
            has_audio=sys.platform in ["darwin", "win32", "linux"],
        )

    @staticmethod
    def verify_tool_capabilities(tool) -> None:
        """Verifies if the system has the required capabilities to run the tool."""
        sys_caps = CapabilityManager.detect_system_capabilities()
        for cap in tool.required_capabilities:
            if cap == "browser" and not sys_caps.has_chrome:
                raise RuntimeError(
                    "No browser found. Please install Chrome, Firefox, Brave, or Safari."
                )
            elif cap == "terminal" and not sys_caps.has_python:
                raise RuntimeError("Python is not available on this platform.")
