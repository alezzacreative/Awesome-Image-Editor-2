from typing import Optional

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPainterPath, QPainter
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget, QGraphicsItem


class AIEShapeItem(QGraphicsItem):
    def __init__(self, path: QPainterPath, name: str):
        super().__init__()
        self.name = name
        self.path = path
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def get_thumbnail(self): ...

    def get_size_hint(self): ...

    def boundingRect(self) -> QRectF:
        return self.path.boundingRect()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.drawPath(self.path)
