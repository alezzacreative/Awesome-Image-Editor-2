from PySide6.QtCore import QItemSelection, QModelIndex, QItemSelectionModel
from PySide6.QtWidgets import QListView

from .graphics_scene import GraphicsSceneModel


class LayersView(QListView):
    def __init__(self, model: GraphicsSceneModel):
        super().__init__()

        # self.setDragDropMode(QListView.DragDropMode.InternalMove)

        self.setSelectionMode(QListView.ExtendedSelection)
        self.setModel(model)

        # Note: selection model is only available after setting model
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self.update_graphics_scene_selection_from_selection_model)

        self.graphics_scene = model.graphics_scene
        self.graphics_scene.selectionChanged.connect(self.update_selection_model_selection_from_graphics_scene)
        self.graphics_scene.itemInserted.connect(self.update_selection_model_selection_from_graphics_scene)

    def update_graphics_scene_selection_from_selection_model(self, selected: QItemSelection,
                                                             unselected: QItemSelection):
        for index in selected.indexes():
            item = self.graphics_scene.items()[index.row()]
            if not item.isSelected():
                # Only update selection if needed (to stop infinite recursion due to signals connected both ways)
                item.setSelected(True)

        for index in unselected.indexes():
            item = self.graphics_scene.items()[index.row()]
            if item.isSelected():
                # Only update selection if needed (to stop infinite recursion due to signals connected both ways)
                item.setSelected(False)

    def update_selection_model_selection_from_graphics_scene(self):
        for i, item in enumerate(self.graphics_scene.items()):
            model_index = self.model().index(i, 0, QModelIndex())
            selection_model = self.selectionModel()
            command = QItemSelectionModel.Select if item.isSelected() else QItemSelectionModel.Deselect
            selection_model.select(model_index, command)
