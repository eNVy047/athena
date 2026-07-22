import os
import shutil
import sys
from friday.domain.pal import CapabilityGraph, PlatformCapabilities

class SystemDetector:
    @staticmethod
    def detect_capabilities() -> CapabilityGraph:
        caps = set()
        
        # Check for browser engines
        if any(shutil.which(browser) for browser in ["chromium", "firefox", "webkit", "google-chrome"]):
            caps.add("browser")
            
        # Check for shell execution
        if shutil.which("bash") or shutil.which("sh") or os.name == "nt":
            caps.add("terminal")
            
        # Check for audio hardware (generic platforms)
        if sys.platform in ["win32", "darwin", "linux"]:
            caps.add("audio")
            
        return CapabilityGraph(
            capabilities=caps,
            metadata={"os": sys.platform, "arch": os.uname().machine if hasattr(os, "uname") else "win32"}
        )
