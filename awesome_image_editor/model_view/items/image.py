from typing import Optional

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

THUMBNAIL_SIZE = QSize(32, 32)


class AIEImageItem(QGraphicsItem):
    def __init__(self, image: QImage, name: str):
        super().__init__()
        self.name = name
        self.image = image
        self.mask = None  # Initialize mask
        self._opacity = 1.0 # Initialize opacity
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def setOpacity(self, opacity: float):
        """Sets the opacity of the layer. Value is clamped between 0.0 and 1.0."""
        self._opacity = max(0.0, min(1.0, opacity))
        self.update() # Schedule a repaint

    def opacity(self) -> float:
        """Returns the current opacity of the layer."""
        return self._opacity

    def set_mask(self, mask_image: QImage):
        """Sets the layer mask for this item."""
        self.mask = mask_image
        self.update()  # Schedule a repaint

    def get_mask(self) -> QImage | None:
        """Returns the layer mask image, or None if no mask is set."""
        return self.mask

    def has_mask(self) -> bool:
        """Returns True if a layer mask is set, False otherwise."""
        return self.mask is not None

    def get_thumbnail(self):
        return self.image.scaled(
            THUMBNAIL_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def get_size_hint(self):
        return THUMBNAIL_SIZE

    def boundingRect(self) -> QRectF:
        return QRectF(self.image.rect())

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = ...,
    ) -> None:
        previous_opacity = painter.opacity()
        painter.setOpacity(self._opacity)
        painter.drawImage(self.boundingRect(), self.image)
        painter.setOpacity(previous_opacity)

    def setImage(self, image: QImage):
        # Check if image dimensions changed to call prepareGeometryChange
        current_rect = self.boundingRect()
        self.image = image # Direct replacement
        new_rect = self.boundingRect()
        
        if current_rect != new_rect:
           self.prepareGeometryChange() # If image size can change by filter
        
        self.update() # Schedule a repaint
