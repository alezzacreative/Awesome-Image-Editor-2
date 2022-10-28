from pathlib import PurePath

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QToolBar, QVBoxLayout, QWidget

from ..graphics_scene.tree_model import TreeModel
from ..graphics_scene.tree_view import TreeView


class LayersWidget(QWidget):
    def __init__(self, model: TreeModel):
        super().__init__()
        self._model = model
        self.list_view = TreeView(model)
        layout = QVBoxLayout()
        layout.addWidget(self.list_view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar()
        layout.addWidget(self.toolbar)
        self.toolbar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        icon = QIcon(
            (
                PurePath(__file__).parent.parent / "icons" / "layers" / "delete_btn.svg"
            ).as_posix()
        )
        self.toolbar.addAction(icon, "Delete", self.delete_selected_items)
        self.setLayout(layout)

    def delete_selected_items(self):
        self._model.beginResetModel()
        scene = self._model.scene()
        for item in scene.selectedItems():
            scene.removeItem(item)
        self._model.endResetModel()
