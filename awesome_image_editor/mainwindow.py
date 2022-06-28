import traceback
import typing

from PIL import Image
from PySide2.QtCore import QStandardPaths, Qt, QRectF
from PySide2.QtGui import QPainter, QImage
from PySide2.QtWidgets import (
    QAbstractItemView,
    QDockWidget,
    QFileDialog,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QListView,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStyleOptionGraphicsItem,
    QWidget,
)

from .filters.base import evaluate_image
from .filters.filter_stack_widget import FilterStackModel
from .filters.gaussian_blur import GaussianBlurDialog, GaussianBlurFilter

__all__ = ("MainWindow",)


class QGraphicsImageItem(QGraphicsItem):
    def __init__(self, image: QImage):
        super().__init__()
        self.image = image

    def boundingRect(self) -> QRectF:
        return QRectF(self.image.rect())

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: typing.Optional[QWidget] = ...,
    ) -> None:
        painter.drawImage(self.boundingRect(), self.image)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Awesome Image Editor")

        self.graphics_scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.setCentralWidget(self.graphics_view)

        self.setup_file_menu()
        self.setup_filters_menu()

        # TODO: visualize filter stack using list view
        self.filter_stack = []
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
            image = Image.open(filepath).toqimage()
            self.graphics_scene.addItem(QGraphicsImageItem(image))
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

        try:
            image = QImage(self.graphics_scene.sceneRect().size().toSize(), QImage.Format.Format_ARGB32_Premultiplied)
            assert image is not None

            painter = QPainter(image)
            self.graphics_scene.render(painter)
            # NOTE: End painter explictly to fix "QPaintDevice: Cannot destroy paint device that is being painted"
            painter.end()
            image.save(filepath)
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
