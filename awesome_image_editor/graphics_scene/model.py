import typing

from PySide6.QtCore import QSize, Signal, QAbstractListModel, QModelIndex, Qt, QDataStream
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene

from .items.image import QGraphicsImageItem

LAYER_THUMBNAIL_SIZE = QSize(32, 32)


class QGraphicsSceneCustom(QGraphicsScene):
    CHUNK_TYPE = "LAYERS"

    itemAboutToBeInserted = Signal()
    itemInserted = Signal()

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeInserted.emit()
        super().addItem(item)
        self.itemInserted.emit()

    def serialize(self, data_stream: QDataStream):
        data_stream << self.CHUNK_TYPE
        data_stream.writeUInt64(len(self.items()))
        for item in self.items():
            item.serialize(data_stream)

    @staticmethod
    def deserialize(data_stream: QDataStream):
        scene = QGraphicsSceneCustom()

        num_items = data_stream.readUInt64()
        for i in range(num_items):
            chunk_type = data_stream.readString()
            assert chunk_type == QGraphicsImageItem.CHUNK_TYPE

            item = QGraphicsImageItem.deserialize(data_stream)
            scene.addItem(item)

        return scene


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

        if role == Qt.DisplayRole:
            return item.name

        elif role == Qt.DecorationRole:
            return item.image.scaled(LAYER_THUMBNAIL_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        elif role == Qt.SizeHintRole:
            return LAYER_THUMBNAIL_SIZE
