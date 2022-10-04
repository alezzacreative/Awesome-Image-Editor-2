from pathlib import PurePath

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QToolBar, QVBoxLayout

from ..graphics_scene.tree_model import QGraphicsTreeModel
from ..graphics_scene.view import TreeView


class LayersWidget(QWidget):
    def __init__(self, model: QGraphicsTreeModel):
        super().__init__()
        self.list_view = TreeView(model)
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
