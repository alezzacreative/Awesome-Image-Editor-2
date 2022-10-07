from PyQt6.QtCore import pyqtSignal, QRectF
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem


class QGraphicsSceneCustom(QGraphicsScene):
    itemAboutToBeAppended = pyqtSignal()
    itemAppended = pyqtSignal(QGraphicsItem)

    def __init__(self):
        super().__init__()
        self.selectionChanged.connect(self.update)
        self.changed.connect(self.update)

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeAppended.emit()
        super().addItem(item)
        self.itemAppended.emit(item)

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        # Draw selection bounding box
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        rect = QRectF()
        for item in self.selectedItems():
            rect = rect.united(item.sceneBoundingRect())
        painter.drawRect(rect)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
