from typing import Optional

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget


class AIEShapeItem(QGraphicsItem):
    """
    Represents a shape item in the AIEGraphicsScene.

    This item displays a shape defined by a QPainterPath and allows it
    to be selected and moved within the scene. It has a configurable stroke color.
    Thumbnail generation is not currently implemented.
    """

    def __init__(self, path: QPainterPath, name: str) -> None:
        """
        Initializes an AIEShapeItem.

        Args:
            path: The QPainterPath defining the geometry of the shape.
            name: The name of the shape item, used for display in the layer tree.
        """
        super().__init__()
        self.name = name
        self.path = path
        self.stroke_color = QColor(0, 0, 0)  # Default stroke color is black
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def get_thumbnail(self):
        """
        Generates a thumbnail representation of the shape.

        Currently not implemented.
        """
        ...

    def get_size_hint(self):
        """
        Returns the recommended size for this item's thumbnail.

        Currently not implemented.
        """
        ...

    def boundingRect(self) -> QRectF:
        """
        Returns the bounding rectangle of this shape item.

        The bounding rectangle is determined by the QPainterPath.

        Returns:
            A QRectF representing the shape's boundaries.
        """
        return self.path.boundingRect()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """
        Paints the shape item onto the scene.

        The shape is drawn using its QPainterPath and stroke_color.

        Args:
            painter: The QPainter to use for drawing.
            option: Provides style options for the item (unused).
            widget: The widget that is being painted on (unused).
        """
        painter.setPen(self.stroke_color)
        painter.drawPath(self.path)

    def setOpacity(self, opacity: float) -> None:
        """
        Sets the opacity of the shape item.

        Args:
            opacity: The new opacity, from 0.0 (transparent) to 1.0 (opaque).
        """
        super().setOpacity(opacity)

    def opacity(self) -> float:
        """
        Returns the current opacity of the shape item.

        Returns:
            The current opacity, from 0.0 (transparent) to 1.0 (opaque).
        """
        return super().opacity()
