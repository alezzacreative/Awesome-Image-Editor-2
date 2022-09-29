from pathlib import PurePath

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QToolBar, QVBoxLayout

from ..graphics_scene.model import QGraphicsSceneModel
from ..graphics_scene.view import QGraphicsListView


class LayersWidget(QWidget):
    def __init__(self, model: QGraphicsSceneModel):
        super().__init__()
        self.list_view = QGraphicsListView(model)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.list_view)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar()
        self.layout.addWidget(self.toolbar)
        self.toolbar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        icon = QIcon((PurePath(__file__).parent.parent / "icons" / "recycle_bin.svg").as_posix())

        def delete_selected_items():
            self.list_view.model().beginResetModel()
            scene = self.list_view.scene()
            for item in scene.selectedItems():
                scene.removeItem(item)
            self.list_view.model().endResetModel()

        self.toolbar.addAction(icon, "Delete", delete_selected_items)

        self.setLayout(self.layout)
