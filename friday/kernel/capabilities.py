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
        return SystemCapabilities(
            os_name=sys.platform,
            has_git=bool(shutil.which("git")),
            has_python=bool(shutil.which("python")),
            has_node=bool(shutil.which("node")),
            has_docker=bool(shutil.which("docker")),
            has_chrome=any(shutil.which(b) for b in ["google-chrome", "chrome", "chromium"]),
            has_audio=sys.platform in ["darwin", "win32", "linux"]
        )

    @staticmethod
    def verify_tool_capabilities(tool) -> None:
        """Verifies if the system has the required capabilities to run the tool."""
        sys_caps = CapabilityManager.detect_system_capabilities()
        for cap in tool.required_capabilities:
            if cap == "browser" and not sys_caps.has_chrome:
                # If specifically testing negative scenarios, we can fail
                raise RuntimeError("Capability 'browser' is disabled/missing on this platform.")
            elif cap == "terminal" and not sys_caps.has_python:
                raise RuntimeError("Capability 'terminal' is disabled/missing on this platform.")
