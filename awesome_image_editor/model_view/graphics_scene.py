from PyQt6.QtCore import QRectF, pyqtSignal, Qt # Added Qt
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

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect) # Call super if it might do something useful

        # Define checkerboard properties
        square_size = 16 # Size of each square in pixels
        color1 = QColor(220, 220, 220) # Light gray
        color2 = QColor(255, 255, 255) # White
        # Alternate suggestion for slightly more contrast:
        # color2 = QColor(200, 200, 200) # Slightly darker gray

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen) # No outlines for the squares

        # Fill the entire background with the first color
        # This ensures areas outside the checkerboard loop (if any) or rect itself are covered
        painter.fillRect(rect, color1)

        # Determine the start of the drawing aligned to the grid
        # rect coordinates are in scene coordinates
        start_x = int(rect.left() / square_size) * square_size
        start_y = int(rect.top() / square_size) * square_size
        
        # Adjust for negative coordinates to ensure pattern is consistent
        if rect.left() < 0:
            start_x -= square_size
        if rect.top() < 0:
            start_y -= square_size

        # Iterate to draw the second color squares
        y = start_y
        row_index = int(start_y / square_size) # Initial row index for color alternation

        while y < rect.bottom():
            x = start_x
            col_index = int(start_x / square_size) # Initial col index for color alternation
            while x < rect.right():
                if (row_index + col_index) % 2 == 1: # Or 0, depending on which color starts
                    painter.fillRect(QRectF(x, y, square_size, square_size), color2)
                x += square_size
                col_index += 1
            y += square_size
            row_index += 1
        
        painter.restore()
