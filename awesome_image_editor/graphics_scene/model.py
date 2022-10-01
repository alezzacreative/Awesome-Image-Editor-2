import typing

from PyQt6.QtCore import QSize, pyqtSignal, QAbstractListModel, QModelIndex, Qt
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene

from .items.image import QGraphicsImageItem

LAYER_THUMBNAIL_SIZE = QSize(32, 32)


class QGraphicsSceneCustom(QGraphicsScene):
    itemAboutToBeInserted = pyqtSignal()
    itemInserted = pyqtSignal()

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeInserted.emit()
        super().addItem(item)
        self.itemInserted.emit()


class QGraphicsSceneModel(QAbstractListModel):
    def __init__(self, scene: QGraphicsSceneCustom) -> None:
        super().__init__()
        self._scene = scene
        self._scene.itemAboutToBeInserted.connect(
            lambda: self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount()))
        self._scene.itemInserted.connect(lambda: self.endInsertRows())

    def scene(self):
        return self._scene

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._scene.items())

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return

        item = self._scene.items()[index.row()]

        if not isinstance(item, QGraphicsImageItem):
            return

        if role == Qt.ItemDataRole.DisplayRole:
            return item.name

        elif role == Qt.ItemDataRole.DecorationRole:
            return item.image.scaled(LAYER_THUMBNAIL_SIZE, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)

        elif role == Qt.ItemDataRole.SizeHintRole:
            return LAYER_THUMBNAIL_SIZE
