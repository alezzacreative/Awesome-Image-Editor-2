import typing

from PySide6.QtCore import QSize, QRectF, Signal, QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget, QGraphicsScene

LAYER_THUMBNAIL_SIZE = QSize(32, 32)


class QGraphicsImageItem(QGraphicsItem):
    def __init__(self, image: QImage, name="Image"):
        super().__init__()
        self.image = image
        self.name = name
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def boundingRect(self) -> QRectF:
        return QRectF(self.image.rect())

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: typing.Optional[QWidget] = ...,
    ) -> None:
        painter.drawImage(self.boundingRect(), self.image)


class CustomGraphicsScene(QGraphicsScene):
    itemAboutToBeInserted = Signal()
    itemInserted = Signal()

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeInserted.emit()
        super().addItem(item)
        self.itemInserted.emit()


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

        item: QGraphicsImageItem = self.graphics_scene.items()[index.row()]  # type: ignore
        if role == Qt.DisplayRole:
            return item.name
        elif role == Qt.DecorationRole:
            return item.image.scaled(LAYER_THUMBNAIL_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        elif role == Qt.SizeHintRole:
            return LAYER_THUMBNAIL_SIZE
