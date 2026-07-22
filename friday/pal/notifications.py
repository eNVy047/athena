import sys
import subprocess
from friday.domain.pal import PlatformManager

class NotificationManager:
    def __init__(self, platform: PlatformManager):
        self.platform = platform

    async def send_notification(self, title: str, message: str) -> None:
        os_name = self.platform.get_os_name()
        
        if os_name == "windows":
            try:
                from winotify import Notification
                toast = Notification(app_id="Friday AI OS", title=title, msg=message)
                toast.show()
            except ImportError:
                pass
        elif os_name == "macos":
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], capture_output=True)
        elif os_name == "linux":
            subprocess.run(["notify-send", title, message], capture_output=True)
