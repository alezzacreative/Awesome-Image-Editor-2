from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFocusEvent, QPainter
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QStyle,
    QStyleOptionGraphicsItem,
    QWidget,
)


class AIETextItem(QGraphicsTextItem):
    """
    Represents a text item in the AIEGraphicsScene.

    This item displays editable text and allows it to be selected and moved
    within the scene. Text interaction (editing) is enabled on double-click.
    It handles focus events to switch between interaction modes.
    Thumbnail generation is not currently implemented.
    """

    def __init__(self, text: str, name: str) -> None:
        """
        Initializes an AIETextItem.

        Args:
            text: The initial text content for the item.
            name: The name of the text item, used for display in the layer tree.
        """
        super().__init__(text)
        self.name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.document().setLayoutEnabled(True)

        def update_width_with_layout() -> None:
            """Dynamically updates the text item's width based on its content."""
            # TODO: match text alignment with expected result from a PSD
            # might require a custom text layout: https://doc.qt.io/qt-6/qabstracttextdocumentlayout.html
            # Allow text to expand before setting width to ideal width
            self.document().setTextWidth(-1)
            self.document().setTextWidth(self.document().idealWidth())

        self.document().contentsChanged.connect(update_width_with_layout)

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None
    ) -> None:
        """
        Paints the text item onto the scene.

        It modifies the style options to prevent drawing the default focus or
        selection states, allowing for custom handling.

        Args:
            painter: The QPainter to use for drawing.
            option: Provides style options for the item.
            widget: The widget that is being painted on (unused).
        """
        # Create a new option to avoid modifying the original if it's shared
        custom_option = QStyleOptionGraphicsItem(option)
        custom_option.state &= ~QStyle.StateFlag.State_Enabled
        custom_option.state &= ~QStyle.StateFlag.State_HasFocus
        custom_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, custom_option, widget)

    def sceneEvent(self, event: QEvent) -> bool:
        """
        Handles scene events, specifically to enable text editing on double-click.

        Args:
            event: The QEvent.

        Returns:
            True if the event was handled, False otherwise.
        """
        # Trigger text editor on double click instead of single click
        # https://forum.qt.io/post/482973
        if event.type() == QEvent.Type.GraphicsSceneMouseDoubleClick:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            # Call base class sceneEvent for the double click to be processed for editing
            ret = super().sceneEvent(event)
            # Ensure the item receives focus to start editing
            if self.textInteractionFlags() & Qt.TextInteractionFlag.TextEditorInteraction:
                self.setFocus(Qt.FocusReason.MouseFocusReason)
            return ret

        return super().sceneEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """
        Handles focus out events to disable text editing and clear text selection.

        Args:
            event: The QFocusEvent.
        """
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
        """
        Generates a thumbnail representation of the text item.

        Currently not implemented.
        """
        ...

    def setOpacity(self, opacity: float) -> None:
        """
        Sets the opacity of the text item.

        Args:
            opacity: The new opacity, from 0.0 (transparent) to 1.0 (opaque).
        """
        super().setOpacity(opacity) # Calls QGraphicsItem.setOpacity

    def opacity(self) -> float:
        """
        Returns the current opacity of the text item.

        Returns:
            The current opacity, from 0.0 (transparent) to 1.0 (opaque).
        """
        return super().opacity() # Calls QGraphicsItem.opacity

    def get_size_hint(self):
        """
        Returns the recommended size for this item's thumbnail.

        Currently not implemented.
        """
        ...
