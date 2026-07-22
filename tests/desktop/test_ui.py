from PySide6.QtCore import QCoreApplication
from friday.apps.desktop.theme_manager import ThemeManager

def test_theme_manager():
    # Requires a QCoreApplication instance to create QObjects
    if not QCoreApplication.instance():
        QCoreApplication([])
        
    theme = ThemeManager()
    assert theme.isDarkMode is True
    assert theme.backgroundColor == "#0f172a"
    
    theme.isDarkMode = False
    assert theme.backgroundColor == "#f8fafc"
