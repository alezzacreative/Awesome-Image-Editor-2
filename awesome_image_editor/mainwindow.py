import traceback
import typing
from pathlib import Path

from PySide6.QtCore import (
    QStandardPaths,
    Qt,
    QRectF,
    QAbstractListModel,
    QModelIndex,
    Signal,
    QPointF,
    QRect
)
from PySide6.QtGui import QPainter, QImage, QPainterPath
from PySide6.QtWidgets import (
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
    QGraphicsSceneMouseEvent
)

from .filters.gaussian_blur import GaussianBlurDialog

__all__ = ("MainWindow",)


class QGraphicsImageItem(QGraphicsItem):
    def __init__(self, image: QImage, name="Image"):
        super().__init__()
        self.image = image
        self.name = name
        # self.setFlag(QGraphicsImageItem.ItemIsSelectable, True)

    def boundingRect(self) -> QRectF:
        return QRectF(self.image.rect())

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: typing.Optional[QWidget] = ...,
    ) -> None:
        painter.drawImage(self.boundingRect(), self.image)

    # def setSelected(self, selected: bool) -> None:
    #     super().setSelected(selected)
    #     print("setSelected")


class CustomGraphicsScene(QGraphicsScene):
    itemAboutToBeInserted = Signal()
    itemInserted = Signal()

    def __init__(self):
        super().__init__()
        self.drag_start: typing.Optional[QPointF] = None
        self.drag_end: typing.Optional[QPointF] = None

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeInserted.emit()
        super().addItem(item)
        self.itemInserted.emit()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.drag_start = event.scenePos()
        else:
            super(CustomGraphicsScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if (event.buttons() & Qt.LeftButton) and (self.drag_start is not None):
            self.drag_end = event.scenePos()
            self.update()  # force repaint (expensive?)
        else:
            super(CustomGraphicsScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if (event.button() == Qt.LeftButton) and (self.drag_start is not None) and (self.drag_end is not None):
            selection_path = QPainterPath()
            selection_path.addRect(QRectF(self.drag_start, self.drag_end))
            self.setSelectionArea(selection_path)
            self.drag_start = None
            self.drag_end = None
            self.update()  # force repaint (expensive?)
        else:
            super(CustomGraphicsScene, self).mouseReleaseEvent(event)

    def drawForeground(self, painter: QPainter, rect: typing.Union[QRectF, QRect]) -> None:
        if (self.drag_start is not None) and (self.drag_end is not None):
            painter.drawRect(QRectF(self.drag_start, self.drag_end))


class GraphicsSceneModel(QAbstractListModel):
    def __init__(self) -> None:
        super().__init__()
        self.graphics_scene = CustomGraphicsScene()
        self.graphics_scene.itemAboutToBeInserted.connect(
            lambda: self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount()))
        self.graphics_scene.itemInserted.connect(lambda: self.endInsertRows())

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.graphics_scene.items())

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            item: QGraphicsImageItem = self.graphics_scene.items()[index.row()]  # type: ignore
            return item.name


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Awesome Image Editor")

        self.graphics_scene_model = GraphicsSceneModel()
        self.graphics_scene = self.graphics_scene_model.graphics_scene
        self.graphics_view = QGraphicsView(self.graphics_scene)
        # self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.graphics_view)

        self.setup_file_menu()
        self.setup_filters_menu()

        self.layers_list_widget = QListView()
        self.layers_list_widget.setModel(self.graphics_scene_model)
        # self.layers_list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        dock_widget = QDockWidget()
        dock_widget.setWindowTitle("Layers")
        dock_widget.setWidget(self.layers_list_widget)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, dock_widget, Qt.Orientation.Vertical
        )

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
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            ),
            "Image files (*.jpg *.png)",
        )
        if not filepath:
            return
        try:
            image = QImage(filepath)
            image_name = Path(filepath).stem
            self.graphics_scene.addItem(QGraphicsImageItem(image, image_name))
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def save_image(self):
        filepath, chosen_filter = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            ),
            "Image files (*.jpg *.png)",
        )
        if not filepath:
            return

        try:
            # Create new empty image to render the scene into
            image = QImage(
                self.graphics_scene.sceneRect().size().toSize(),
                QImage.Format.Format_ARGB32_Premultiplied,
            )
            assert image is not None

            painter = QPainter(image)
            self.graphics_scene.render(painter)
            # NOTE: End painter explicitly to fix "QPaintDevice: Cannot destroy paint device that is being painted"
            painter.end()
            image.save(filepath)
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def show_gaussian_blur_dialog(self):
        dlg = GaussianBlurDialog()
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        dlg.rejected.connect(lambda: print("Rejected"))
        # TODO: add blur effect to currently selected layer
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
