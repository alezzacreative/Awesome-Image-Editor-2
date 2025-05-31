from pathlib import PurePath
from PyQt6.QtGui import QPainter, QIcon
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QWidget,
)
from PyQt6.QtCore import QRectF


class AIEGroupItem(QGraphicsItem):
    """
    Represents a group of items in the AIEGraphicsScene.

    This item allows for grouping other QGraphicsItems (like images, shapes, text)
    and manipulating them as a single unit (e.g., moving). It does not have
    its own visual representation but defines its bounding rectangle based on
    the items it contains.
    It is selectable and movable.
    """

    # NOTE: We do not use a QGraphicsItemGroup because it forces children to have the same selection state as group
    def __init__(self, name: str) -> None:
        """
        Initializes an AIEGroupItem.

        Args:
            name: The name of the group item, used for display in the layer tree.
        """
        super().__init__()
        self.name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def get_thumbnail(self) -> QIcon:
        """
        Returns an icon representing a group layer.

        This is used for display in the layer tree view.

        Returns:
            A QIcon for a group layer.
        """
        return QIcon(
            (
                PurePath(__file__).parent.parent.parent
                / "icons"
                / "layers"
                / "group_layer.svg"
            ).as_posix()
        )

    def get_size_hint(self):
        """
        Returns the recommended size for this item's thumbnail.

        Currently not implemented.
        """
        ...

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None
    ) -> None:
        """
        Paints the group item.

        This item has no visual representation itself, so this method does nothing.
        The child items are responsible for their own painting.

        Args:
            painter: The QPainter to use for drawing (unused).
            option: Provides style options for the item (unused).
            widget: The widget that is being painted on (unused).
        """
        ...

    def boundingRect(self) -> QRectF:
        """
        Returns the bounding rectangle of this group item.

        The bounding rectangle is determined by the combined bounding rectangles
        of all its child items.

        Returns:
            A QRectF that encompasses all child items.
        """
        return self.childrenBoundingRect()

    def setOpacity(self, opacity: float) -> None:
        """
        Sets the opacity of the group item and its children.
        Note: QGraphicsItem.setOpacity propagates to children.

        Args:
            opacity: The new opacity, from 0.0 (transparent) to 1.0 (opaque).
        """
        super().setOpacity(opacity)

    def opacity(self) -> float:
        """
        Returns the current opacity of the group item.

        Returns:
            The current opacity, from 0.0 (transparent) to 1.0 (opaque).
        """
        return super().opacity()
