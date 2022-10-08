from PyQt6.QtCore import pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem


class AIEGraphicsScene(QGraphicsScene):
    itemAboutToBeAppended = pyqtSignal(int)
    itemAppended = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.selectionChanged.connect(self.update)
        self.changed.connect(self.update)

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeAppended.emit(len(self.items()))
        super().addItem(item)
        self.itemAppended.emit()

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        # Draw selection bounding box
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setCompositionMode(QPainter.CompositionMode.RasterOp_SourceXorDestination)
        painter.setPen(QColor(255, 255, 255))
        rect = QRectF()
        for item in self.selectedItems():
            rect = rect.united(item.sceneBoundingRect())
        painter.drawRect(rect)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
