from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import (
    QGraphicsTextItem,
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QWidget,
    QStyle,
)
from PyQt6.QtGui import QPainter, QFocusEvent


class AIETextItem(QGraphicsTextItem):
    def __init__(self, text: str, name: str):
        super().__init__(text)
        self.name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.document().setLayoutEnabled(True)

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Enabled
        option.state &= ~QStyle.StateFlag.State_HasFocus
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)

    # Trigger text editor on double click instead of single click
    # https://forum.qt.io/post/482973
    def sceneEvent(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.GraphicsSceneMouseDoubleClick:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            ret = QGraphicsTextItem.sceneEvent(self, event)

            self.setFocus(Qt.FocusReason.MouseFocusReason)
            return ret

        return QGraphicsTextItem.sceneEvent(self, event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        # TODO: focus out text item using ESC and dedicated button instead
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        # Clear cursor when focusing out, otherwise selection will remain.
        # P.S.: We have to get or create a cursor then set it
        # self.getTextCursor won't allow us to modify the selection, it returns a copy
        # https://www.qtcentre.org/threads/4065-QGraphicsTextItem-is-it-a-bug-there
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def get_thumbnail(self):
        ...

    def get_size_hint(self):
        ...
