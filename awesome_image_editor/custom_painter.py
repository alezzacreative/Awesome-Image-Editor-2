from PySide2.QtGui import QPainter, QImage, QTransform
from PySide2.QtCore import QRectF


class CustomQPainter(QPainter):
    def drawImageFitView(self, image: QImage, scale=1.0, rotation=0) -> None:
        # Draw Image centered and fit to view, with a scale and rotation
        # NOTE: there are shorter/easier ways for this
        # but this should? avoid copying QPixmap or a QImage
        w = self.device().width()
        h = self.device().height()

        if not image.isNull():
            iw = image.width()
            ih = image.height()
            if ih > 0 and iw > 0:
                f = min(w / iw, h / ih)

                nw = iw * f
                nh = ih * f
                cx = (w - nw) / 2
                cy = (h - nh) / 2

                rect = QRectF(cx, cy, nw, nh).toRect()
                c = rect.center()
                t = QTransform()
                self.save()
                t.translate(c.x(), c.y())
                t.rotate(rotation)
                t.scale(scale, scale)
                t.translate(-c.x(), -c.y())
                self.setTransform(t)
                self.drawImage(rect, image)
                self.restore()
