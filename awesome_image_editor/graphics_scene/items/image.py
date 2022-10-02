from typing import Optional

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget


class QGraphicsImageItem(QGraphicsItem):
    def __init__(self, image: QImage, name="Image"):
        super().__init__()
        self.image = image
        self.name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def boundingRect(self) -> QRectF:
        return QRectF(self.image.rect())

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = ...,
    ) -> None:
        painter.drawImage(self.boundingRect(), self.image)
