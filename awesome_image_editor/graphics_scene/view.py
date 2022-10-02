from PyQt6.QtCore import QModelIndex, QItemSelectionModel, QItemSelection
from PyQt6.QtWidgets import QListView

from .model import QGraphicsSceneModel


class QGraphicsListView(QListView):
    def __init__(self, model: QGraphicsSceneModel):
        super().__init__()

        # self.setDragDropMode(QListView.DragDropMode.InternalMove)

        self.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.setModel(model)

        # Note: selection model is only available after setting model
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self.update_graphics_scene_selection_from_selection_model)

        self._scene = model.scene()
        self._scene.selectionChanged.connect(self.update_selection_model_selection_from_graphics_scene)
        self._scene.itemInserted.connect(self.update_selection_model_selection_from_graphics_scene)

    def scene(self):
        return self._scene

    def update_graphics_scene_selection_from_selection_model(self, selected: QItemSelection,
                                                             unselected: QItemSelection):
        # FIXME: index out of range when modifying scene
        for index in selected.indexes():
            item = self._scene.items()[index.row()]
            if not item.isSelected():
                # Only update selection if needed (to stop infinite recursion due to signals connected both ways)
                item.setSelected(True)

        for index in unselected.indexes():
            item = self._scene.items()[index.row()]
            if item.isSelected():
                # Only update selection if needed (to stop infinite recursion due to signals connected both ways)
                item.setSelected(False)

    def update_selection_model_selection_from_graphics_scene(self):
        for i, item in enumerate(self._scene.items()):
            model_index = self.model().index(i, 0, QModelIndex())
            selection_model = self.selectionModel()
            if item.isSelected():
                command = QItemSelectionModel.SelectionFlag.Select
            else:
                command = QItemSelectionModel.SelectionFlag.Deselect
            selection_model.select(model_index, command)
