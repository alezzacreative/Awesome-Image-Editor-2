import ctypes
import platform
import typing
from pathlib import PurePath

from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QColor, QIcon, QPalette, Qt
from PySide2.QtWidgets import QApplication


__all__ = ("Application",)


class Application(QApplication):
    def __init__(self, arg__1: typing.Sequence) -> None:
        super().__init__(arg__1)

        # Fix app icon not displayed in Windows taskbar
        if platform.system() == "Windows":
            appid = "iyadahmed.awesomeimageeditor.1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

        QCoreApplication.setApplicationName("Awesome Image Editor")
        QCoreApplication.setOrganizationName("Iyad Ahmed")
        QCoreApplication.setApplicationVersion("0.0.1")

        self.setWindowIcon(QIcon((PurePath(__file__).parent / "icons" / "app.png").as_posix()))
        # Dark theme
        self.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)
