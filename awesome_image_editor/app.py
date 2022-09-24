import ctypes
import platform
import typing
from pathlib import PurePath

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication

__all__ = ("Application",)


class Application(QApplication):
    def __init__(self, arg__1: typing.Sequence) -> None:
        super().__init__(arg__1)

        # Fixes app icon not displayed in Windows taskbar
        if platform.system() == "Windows":
            appid = "iyadahmed.AwesomeImageEditor"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)  # type: ignore

        QCoreApplication.setApplicationName("Awesome Image Editor")
        QCoreApplication.setOrganizationName("Iyad Ahmed")
        QCoreApplication.setApplicationVersion("0.0.1")

        self.setWindowIcon(
            QIcon((PurePath(__file__).parent / "icons" / "app.png").as_posix())
        )
        # Dark theme
        # https://stackoverflow.com/a/56851493/8094047
        self.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("white"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("white"))
        palette.setColor(QPalette.ColorRole.Text, QColor("white"))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("red"))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("black"))
        self.setPalette(palette)
