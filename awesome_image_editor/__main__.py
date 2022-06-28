import sys

from .app import Application
from .mainwindow import MainWindow

app = Application(sys.argv)
main_window = MainWindow()
exit_code = app.exec_()
sys.exit(exit_code)
