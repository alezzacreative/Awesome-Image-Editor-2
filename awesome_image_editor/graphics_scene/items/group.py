from pathlib import PurePath
from PyQt6.QtGui import QPainter, QIcon
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsItemGroup,
    QStyle,
    QStyleOptionGraphicsItem,
    QWidget,
)


class AIEGroupItem(QGraphicsItemGroup):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def get_thumbnail(self):
        return QIcon(
            (
                PurePath(__file__).parent.parent.parent
                / "icons"
                / "layers"
                / "group_layer.svg"
            ).as_posix()
        )

    def get_size_hint(self):
        ...

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Enabled
        option.state &= ~QStyle.StateFlag.State_HasFocus
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
