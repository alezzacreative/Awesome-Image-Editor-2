from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem


class QGraphicsSceneCustom(QGraphicsScene):
    itemAboutToBeAppended = pyqtSignal()
    itemAppended = pyqtSignal(QGraphicsItem)

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeAppended.emit()
        super().addItem(item)
        self.itemAppended.emit(item)
