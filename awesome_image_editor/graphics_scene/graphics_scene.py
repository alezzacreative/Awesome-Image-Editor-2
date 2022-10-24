from PyQt6.QtCore import QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene


class AIEGraphicsScene(QGraphicsScene):
    itemAboutToBeAppended = pyqtSignal(int)
    itemAppended = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.changed.connect(self._invalidate_foreground)

    def _invalidate_foreground(self):
        self.invalidate(self.sceneRect(), QGraphicsScene.SceneLayer.ForegroundLayer)

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeAppended.emit(len(self.items()))
        super().addItem(item)
        self.itemAppended.emit()

    def _calc_selected_items_bounding_box(self):
        rect = QRectF()
        for item in self.selectedItems():
            rect = rect.united(item.sceneBoundingRect())
        return rect

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        # Draw selection bounding box
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setCompositionMode(
            QPainter.CompositionMode.RasterOp_SourceXorDestination
        )
        painter.setPen(QColor(255, 255, 255))
        painter.drawRect(self._calc_selected_items_bounding_box())
        painter.restore()
