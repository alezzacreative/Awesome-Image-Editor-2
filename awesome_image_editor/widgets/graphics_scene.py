import typing

from PySide6.QtCore import QSize, QRectF, Signal, QAbstractListModel, QModelIndex, Qt, QDataStream
from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget, QGraphicsScene

LAYER_THUMBNAIL_SIZE = QSize(32, 32)


class QGraphicsImageItem(QGraphicsItem):
    CHUNK_TYPE = "IMAGE_LAYER"

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

    def serialize(self, data_stream: QDataStream):
        data_stream << self.CHUNK_TYPE
        data_stream << self.name
        data_stream << self.image.size()
        # data_stream << self.image.format()
        data_stream << self.image

    @staticmethod
    def deserialize(data_stream: QDataStream):
        image_size = QSize()
        image_format = QImage.Format()

        image_name = data_stream.readString()
        data_stream >> image_size
        # data_stream >> image_format

        image = QImage(image_size, QImage.Format.Format_ARGB32_Premultiplied)
        data_stream >> image
        assert not image.isNull()

        return QGraphicsImageItem(image, image_name)


class CustomGraphicsScene(QGraphicsScene):
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
        scene = CustomGraphicsScene()

        num_items = data_stream.readUInt64()
        for i in range(num_items):
            chunk_type = data_stream.readString()
            assert chunk_type == QGraphicsImageItem.CHUNK_TYPE

            item = QGraphicsImageItem.deserialize(data_stream)
            scene.addItem(item)

        return scene


class GraphicsSceneModel(QAbstractListModel):
    def __init__(self, scene: CustomGraphicsScene) -> None:
        super().__init__()
        self._scene = scene
        self._scene.itemAboutToBeInserted.connect(
            lambda: self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount()))
        self._scene.itemInserted.connect(lambda: self.endInsertRows())

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._scene.items())

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return

        item: QGraphicsImageItem = self._scene.items()[index.row()]  # type: ignore
        if role == Qt.DisplayRole:
            return item.name
        elif role == Qt.DecorationRole:
            return item.image.scaled(LAYER_THUMBNAIL_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        elif role == Qt.SizeHintRole:
            return LAYER_THUMBNAIL_SIZE
