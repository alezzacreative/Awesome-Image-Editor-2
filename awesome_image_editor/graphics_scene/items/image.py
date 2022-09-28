from typing import Optional

from PySide6.QtCore import QRectF, QDataStream, QSize
from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget


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
            widget: Optional[QWidget] = ...,
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
