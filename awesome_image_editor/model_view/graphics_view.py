from typing import Optional
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QRubberBand
from PyQt6.QtGui import QPainter, QMouseEvent
from PyQt6.QtCore import QRectF, QPoint, QRect, QSize, Qt


class AIEGraphicsView(QGraphicsView):
    """
    A custom QGraphicsView for the Awesome Image Editor.

    This view provides rubber band selection functionality and custom mouse event handling.
    """

    def __init__(self, scene: QGraphicsScene) -> None:
        """
        Initializes the AIEGraphicsView.

        Args:
            scene: The QGraphicsScene to associate with this view.
        """
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        self._rubberband_selection_origin: Optional[QPoint] = None
        self._rubberband: Optional[QRubberBand] = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handles mouse press events in the view.

        Initializes rubber band selection when the left mouse button is pressed
        on an empty area.

        Args:
            event: The QMouseEvent.
        """
        super().mousePressEvent(event)

        if event.button() == Qt.MouseButton.LeftButton and (
            self.itemAt(event.pos()) is None
        ):
            self._rubberband_selection_origin = event.pos()
            if self._rubberband is None:
                self._rubberband = QRubberBand(QRubberBand.Shape.Rectangle, self)

            self._rubberband.setGeometry(
                QRect(self._rubberband_selection_origin, QSize())
            )
            self._rubberband.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handles mouse move events in the view.

        Updates the rubber band geometry and selects items within the
        rubber band area during selection.

        Args:
            event: The QMouseEvent.
        """
        super().mouseMoveEvent(event)

        if (
            self._rubberband is not None
            and self._rubberband_selection_origin is not None
        ):
            rubberband_rect = QRect(
                self._rubberband_selection_origin, event.pos()
            ).normalized()
            self._rubberband.setGeometry(rubberband_rect)

            for item in self.items():
                if len(item.childItems()) > 0:
                    # Skip non-child items to match desired behavior
                    continue

                rubberband_rect_scene = self.mapToScene(rubberband_rect)

                if item.sceneBoundingRect().intersects(
                    rubberband_rect_scene.boundingRect()
                ):
                    item.setSelected(True)
                else:
                    item.setSelected(False)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handles mouse release events in the view.

        Finalizes rubber band selection and hides the rubber band.

        Args:
            event: The QMouseEvent.
        """
        super().mouseReleaseEvent(event)

        if self._rubberband is not None:
            self._rubberband.hide()
            self._rubberband = None
