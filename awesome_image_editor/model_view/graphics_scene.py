from PyQt6.QtCore import QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene


class AIEGraphicsScene(QGraphicsScene):
    """
    A custom QGraphicsScene for the Awesome Image Editor.

    This scene handles drawing of items and provides signals for item additions.
    It also draws a custom foreground to indicate selected item bounding boxes.
    """

    itemAboutToBeAppended = pyqtSignal(
        int, name="itemAboutToBeAppended"
    )  # int: current number of items
    """Signal emitted just before an item is added to the scene. Passes the current item count."""

    itemAppended = pyqtSignal(name="itemAppended")
    """Signal emitted after an item has been added to the scene."""

    def __init__(self) -> None:
        """Initializes the AIEGraphicsScene."""
        super().__init__()
        self.changed.connect(self._invalidate_foreground)

    def _invalidate_foreground(self) -> None:
        """Invalidates the foreground layer of the scene to trigger a redraw."""
        self.invalidate(self.sceneRect(), QGraphicsScene.SceneLayer.ForegroundLayer)

    def addItem(self, item: QGraphicsItem) -> None:
        """
        Adds an item to the scene.

        Emits `itemAboutToBeAppended` before adding and `itemAppended` after.

        Args:
            item: The QGraphicsItem to add.
        """
        self.itemAboutToBeAppended.emit(len(self.items()))
        super().addItem(item)
        self.itemAppended.emit()

    def _calc_selected_items_bounding_box(self) -> QRectF:
        """
        Calculates the combined bounding box of all currently selected items.

        Returns:
            A QRectF representing the total bounding box of selected items.
            Returns an empty QRectF if no items are selected.
        """
        rect = QRectF()
        for item in self.selectedItems():
            rect = rect.united(item.sceneBoundingRect())
        return rect

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        """
        Draws the foreground content of the scene.

        This method is responsible for drawing the selection bounding box
        around selected items.

        Args:
            painter: The QPainter to use for drawing.
            rect: The QRectF area that needs to be redrawn.
        """
        # Draw selection bounding box
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setCompositionMode(
            QPainter.CompositionMode.RasterOp_SourceXorDestination
        )
        painter.setPen(QColor(255, 255, 255))
        painter.drawRect(self._calc_selected_items_bounding_box())
        painter.restore()
