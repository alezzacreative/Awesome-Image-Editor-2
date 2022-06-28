import traceback

from PIL import Image
from PySide2.QtCore import QStandardPaths, Qt
from PySide2.QtWidgets import (
    QAction,
    QFileDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem,
    QListView,
    QDockWidget,
    QGraphicsScene,
    QGraphicsView
)

from .filters.base import evaluate_image
from .filters.gaussian_blur import GaussianBlurDialog, GaussianBlurFilter
from .widgets import ImageViewer
from .filters.filter_stack_widget import FilterStackModel

__all__ = ("MainWindow",)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Awesome Image Editor")

        self.scene = QGraphicsScene()
        self.canvas = QGraphicsView(self.scene)
        self.setCentralWidget(self.canvas)

        self.setup_file_menu()
        self.setup_filters_menu()

        # TODO: visualize filter stack using list view
        self.filter_stack = []
        self.image = None
        self.filter_stack_widget = QListView()
        self.filter_stack_widget.setDragDropMode(QAbstractItemView.InternalMove)

        self.filter_stack_model = FilterStackModel()
        self.filter_stack_widget.setModel(self.filter_stack_model)

        dock_widget = QDockWidget()
        dock_widget.setWidget(self.filter_stack_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget, Qt.Vertical)

        # TODO: toolbar with tools
        # toolbar = QToolBar()
        # toolbar.setOrientation(Qt.Vertical)
        # toolbar.setMovable(False)
        # toolbar_font = QFont()
        # toolbar_font.setPointSize(17)
        # toolbar.setFont(toolbar_font)

        # # Blur
        # toolbar.addAction("Blur", lambda: ...)
        # blur_widget = LinkedSliderSpinBox(100, 0, 1000)
        # toolbar.addWidget(blur_widget)

        # self.addToolBar(Qt.LeftToolBarArea, toolbar)

        self.showMaximized()

    def open_image(self):
        filepath, chosen_filter = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation),
            "Image files (*.jpg *.png)",
        )
        if not filepath:
            return
        try:
            self.image = Image.open(filepath)
            self.canvas.set_image(self.image.toqimage())
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def save_image(self):
        filepath, chosen_filter = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation),
            "Image files (*.jpg *.png)",
        )
        if not filepath:
            return
        if self.image is None:
            QMessageBox.critical(self, "Error", "No image is currently opened")

        try:
            new_image = evaluate_image(self.image, self.filter_stack)
            new_image.save(filepath)
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def show_gaussian_blur_dialog(self):
        dlg = GaussianBlurDialog()
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.rejected.connect(lambda: print("Rejected"))
        dlg.accepted.connect(lambda: self.filter_stack.append(GaussianBlurFilter(False, dlg.get_blur_radius())))
        dlg.show()

    def setup_file_menu(self):
        menu = QMenu("File", self)
        menu.addAction("Open Image", self.open_image)
        menu.addAction("Save Image", self.save_image)
        self.menuBar().addMenu(menu)

    def setup_filters_menu(self):
        menu = QMenu("Filters", self)
        menu.addAction("Gaussian Blur", self.show_gaussian_blur_dialog)
        self.menuBar().addMenu(menu)
