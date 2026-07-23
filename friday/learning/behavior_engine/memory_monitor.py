"""
F.R.I.D.A.Y. Memory Monitor

Uses psutil to check system RAM usage and suggest freeable applications.
Never closes anything automatically — only prompts the user.

Threshold:
    NORMAL   < 70%   → do nothing
    ELEVATED 70–85%  → optional note (not intrusive)
    HIGH     > 85%   → proactive prompt before launching heavy apps
"""
import logging
from typing import Any, Dict, List, Optional

from friday.learning.behavior_engine.behavior_models import (
    MemoryPressure,
    MemoryPressureLevel,
)

logger = logging.getLogger(__name__)

# Heavy apps that are known to use significant RAM
_HEAVY_APPS = {
    "Google Chrome":          0.5,   # estimated GB per instance (base)
    "Chromium":               0.5,
    "Brave Browser":          0.4,
    "Firefox":                0.4,
    "Safari":                 0.3,
    "Visual Studio Code":     0.4,
    "Code":                   0.4,
    "Cursor":                 0.4,
    "Xcode":                  1.2,
    "Android Studio":         1.5,
    "IntelliJ IDEA":          1.0,
    "Docker Desktop":         0.8,
    "Docker":                 0.8,
    "Spotify":                0.2,
    "Slack":                  0.4,
    "Discord":                0.3,
    "Zoom":                   0.3,
    "Microsoft Teams":        0.5,
    "WhatsApp":               0.2,
    "Telegram":               0.1,
    "Figma":                  0.5,
    "Notion":                 0.3,
}

# Thresholds
_ELEVATED_THRESHOLD = 0.70
_HIGH_THRESHOLD     = 0.85


class MemoryMonitor:
    """
    Monitors system memory and generates prompts when usage is high.
    Uses psutil which is guaranteed to be in the project dependencies.
    """

    def check(self) -> MemoryPressure:
        """
        Check current memory state.
        Returns MemoryPressure with running heavy apps and suggestions.
        """
        try:
            import psutil
            vm = psutil.virtual_memory()
            used_gb  = vm.used  / (1024 ** 3)
            total_gb = vm.total / (1024 ** 3)
            percent  = vm.percent / 100.0

            level = self._classify(percent)
            closeable = self._find_closeable_apps() if level != MemoryPressureLevel.NORMAL else []

            pressure = MemoryPressure(
                used_gb=round(used_gb, 2),
                total_gb=round(total_gb, 2),
                percent=round(vm.percent, 1),
                level=level,
                closeable_apps=closeable,
            )
            logger.debug(
                "[MemoryMonitor] RAM: %.1f%% (%s) — level=%s, closeable=%d apps",
                vm.percent, f"{used_gb:.1f}/{total_gb:.1f}GB",
                level.value, len(closeable),
            )
            return pressure

        except ImportError:
            logger.warning("[MemoryMonitor] psutil not available — skipping memory check.")
            return MemoryPressure(0, 0, 0, MemoryPressureLevel.NORMAL)
        except Exception as exc:
            logger.warning("[MemoryMonitor] Memory check failed: %s", exc)
            return MemoryPressure(0, 0, 0, MemoryPressureLevel.NORMAL)

    def should_warn_before_launch(self, app_name: str) -> bool:
        """
        Returns True if memory is HIGH and the requested app is known to be heavy.
        """
        pressure = self.check()
        if pressure.level != MemoryPressureLevel.HIGH:
            return False
        app_lower = app_name.lower()
        return any(heavy.lower() in app_lower or app_lower in heavy.lower()
                   for heavy in _HEAVY_APPS)

    def get_prompt(self) -> Optional[str]:
        """Return a natural language prompt if memory is elevated/high, else None."""
        pressure = self.check()
        return pressure.to_suggestion()

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _classify(ratio: float) -> MemoryPressureLevel:
        if ratio >= _HIGH_THRESHOLD:
            return MemoryPressureLevel.HIGH
        if ratio >= _ELEVATED_THRESHOLD:
            return MemoryPressureLevel.ELEVATED
        return MemoryPressureLevel.NORMAL

    @staticmethod
    def _find_closeable_apps() -> List[Dict[str, Any]]:
        """
        Find running applications that are known to be heavy.
        Returns list of {name, pid, memory_gb} sorted by memory desc.
        """
        try:
            import psutil
            closeable = []
            for proc in psutil.process_iter(["pid", "name", "memory_info"]):
                try:
                    pname = proc.info["name"] or ""
                    mem_bytes = proc.info["memory_info"].rss if proc.info["memory_info"] else 0
                    mem_gb = mem_bytes / (1024 ** 3)
                    # Check if it's a known heavy app
                    for app, _ in _HEAVY_APPS.items():
                        if app.lower() in pname.lower() or pname.lower() in app.lower():
                            closeable.append({
                                "name": app,
                                "pid": proc.info["pid"],
                                "memory_gb": round(mem_gb, 2),
                            })
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by memory descending, deduplicate by name
            seen = set()
            unique = []
            for item in sorted(closeable, key=lambda x: x["memory_gb"], reverse=True):
                if item["name"] not in seen:
                    seen.add(item["name"])
                    unique.append(item)
            return unique[:5]  # top 5 heaviest

        except Exception as exc:
            logger.debug("[MemoryMonitor] Process scan failed: %s", exc)
            return []
