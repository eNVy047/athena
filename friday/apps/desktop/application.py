import sys
import asyncio
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import qasync  # type: ignore

from friday.kernel.kernel import FridayKernel
from friday.agent.agent import FridayAgent
from friday.apps.desktop.signal_bridge import SignalBridge
from friday.apps.desktop.theme_manager import ThemeManager

class DesktopApplication:
    def __init__(self):
        self.app = QGuiApplication(sys.argv)
        
        # Setup QAsync event loop
        self.loop = qasync.QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)
        
        # Initialize Backend
        self.kernel = FridayKernel()
        self.kernel.bootstrap()
        self.agent = FridayAgent(kernel=self.kernel)
        
        # Initialize Bridges
        self.bridge = SignalBridge(self.agent)
        self.theme = ThemeManager()
        
        # Setup QML Engine
        self.engine = QQmlApplicationEngine()
        context = self.engine.rootContext()
        context.setContextProperty("bridge", self.bridge)
        context.setContextProperty("themeManager", self.theme)
        
    def run(self):
        self.engine.load("friday/apps/desktop/qml/Main.qml")
        if not self.engine.rootObjects():
            sys.exit(-1)
            
        with self.loop:
            self.loop.run_forever()
