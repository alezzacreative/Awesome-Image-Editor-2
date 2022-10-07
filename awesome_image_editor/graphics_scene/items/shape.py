from PyQt6.QtGui import QPainterPath
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem


class AIEShapeItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath, name: str):
        super().__init__(path, None)
        self.name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def get_thumbnail(self): ...

    def get_size_hint(self): ...
