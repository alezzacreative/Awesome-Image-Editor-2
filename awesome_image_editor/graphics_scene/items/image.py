from typing import Optional

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from .base import BaseGraphicsItem

THUMBNAIL_SIZE = QSize(32, 32)


class QGraphicsImageItem(BaseGraphicsItem):
    def __init__(self, image: QImage, name, parent: BaseGraphicsItem = None):
        super().__init__(name, parent)
        self.image = image

    def get_thumbnail(self):
        return self.image.scaled(THUMBNAIL_SIZE, Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)

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
