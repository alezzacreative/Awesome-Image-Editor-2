from typing import Optional

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

THUMBNAIL_SIZE = QSize(32, 32)


class AIEImageItem(QGraphicsItem):
    def __init__(self, image: QImage, name: str):
        super().__init__()
        self.name = name
        self.image = image
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def get_thumbnail(self):
        return self.image.scaled(
            THUMBNAIL_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def get_size_hint(self):
        return THUMBNAIL_SIZE

    def boundingRect(self) -> QRectF:
        return QRectF(self.image.rect())

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = ...,
    ) -> None:
        painter.drawImage(self.boundingRect(), self.image)
