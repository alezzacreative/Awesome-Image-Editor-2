from typing import Union

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QImage, QIcon
from PyQt6.QtWidgets import QGraphicsItem


class BaseGraphicsItem(QGraphicsItem):
    def __init__(self, name, parent: "BaseGraphicsItem" = None):
        super().__init__(parent)
        self.name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def get_thumbnail(self) -> Union[QIcon, QImage]: ...

    def get_size_hint(self) -> QSize: ...
