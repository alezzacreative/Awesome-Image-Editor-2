from typing import Optional
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QRubberBand
from PyQt6.QtGui import QPainter, QMouseEvent, QWheelEvent
from PyQt6.QtCore import QRectF, QPoint, QRect, QSize, Qt, QPointF, pyqtSignal # Added pyqtSignal


class AIEGraphicsView(QGraphicsView):
    zoom_level_changed = pyqtSignal(float)

    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.NoDrag) # Keep NoDrag for default behavior
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self._min_zoom_scale = 0.1
        self._max_zoom_scale = 10.0

        self._rubberband_selection_origin: Optional[QPoint] = None
        self._rubberband: Optional[QRubberBand] = None
        self._last_pan_screen_pos: Optional[QPointF] = None

        # Emit initial scale
        self.zoom_level_changed.emit(self.transform().m11())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._last_pan_screen_pos = event.position() # Store QPointF screen position
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton and self.itemAt(event.pos()) is None:
            # Existing rubber-band logic:
            self._rubberband_selection_origin = event.pos() # QPoint for QRect
            if self._rubberband is None:
                self._rubberband = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._rubberband.setGeometry(QRect(self._rubberband_selection_origin, QSize()))
            self._rubberband.show()
            event.accept() # Accept event if rubber band started
        else:
            # If not middle button or rubber-band left click, call super
            super().mousePressEvent(event)


    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.MiddleButton and self._last_pan_screen_pos is not None:
            delta = event.position() - self._last_pan_screen_pos # QPointF delta in screen coordinates
            
            hs = self.horizontalScrollBar()
            vs = self.verticalScrollBar()
            
            hs.setValue(hs.value() - int(delta.x()))
            vs.setValue(vs.value() - int(delta.y()))
            
            self._last_pan_screen_pos = event.position() # Update for next move
            event.accept()
        elif self._rubberband is not None and self._rubberband_selection_origin is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            # Existing rubber band logic:
            # Note: _rubberband_selection_origin is QPoint, event.pos() is QPoint for QRect
            rubberband_rect = QRect(self._rubberband_selection_origin, event.pos()).normalized()
            self._rubberband.setGeometry(rubberband_rect)

            rubberband_rect_scene = self.mapToScene(rubberband_rect) # This mapToScene is for QRect
            for item in self.items():
                if len(item.childItems()) > 0:
                    continue
                if item.sceneBoundingRect().intersects(
                    rubberband_rect_scene.boundingRect() # Use scene rect for intersection
                ):
                    item.setSelected(True)
                else:
                    item.setSelected(False)
            event.accept() # Accept event if rubber band moved
        else:
            super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton and self._last_pan_screen_pos is not None:
            self._last_pan_screen_pos = None
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor) 
            event.accept()
        elif self._rubberband is not None and event.button() == Qt.MouseButton.LeftButton: 
            # Clear selection origin for rubber band too
            self._rubberband_selection_origin = None # Reset this
            self._rubberband.hide()
            # self._rubberband = None # Decided to keep instance as per original logic.
                                     # If it were set to None, it would be recreated in mousePress.
            event.accept()
        else:
            super().mouseReleaseEvent(event)


    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom
            delta = event.angleDelta().y()
            if delta > 0:
                scale_factor = 1.15
            else:
                scale_factor = 1 / 1.15

            current_scale_x = self.transform().m11()
            # current_scale_y = self.transform().m22() # Assuming uniform scaling

            # Check if the new scale would be within limits
            if self._min_zoom_scale <= current_scale_x * scale_factor <= self._max_zoom_scale:
                self.scale(scale_factor, scale_factor)
                self.zoom_level_changed.emit(self.transform().m11()) # Emit after scaling
            
            event.accept() # Consume the event if Ctrl was pressed
        else:
            # Default behavior (scrolling if applicable)
            super().wheelEvent(event)

    def emit_current_zoom_level(self):
        self.zoom_level_changed.emit(self.transform().m11())
