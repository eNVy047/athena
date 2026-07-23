from PySide6.QtCore import QObject, Property, Signal

class ThemeManager(QObject):
    themeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_dark_mode = True
        
    @Property(bool, notify=themeChanged)
    def isDarkMode(self):
        return self._is_dark_mode
        
    @isDarkMode.setter
    def isDarkMode(self, value):
        if self._is_dark_mode != value:
            self._is_dark_mode = value
            self.themeChanged.emit()

    @Property(str, notify=themeChanged)
    def backgroundColor(self):
        return "#0f172a" if self._is_dark_mode else "#f8fafc"
        
    @Property(str, notify=themeChanged)
    def textColor(self):
        return "#f1f5f9" if self._is_dark_mode else "#0f172a"
        
    @Property(str, notify=themeChanged)
    def primaryColor(self):
        return "#0ea5e9" # Cyan/Blue neon glow
