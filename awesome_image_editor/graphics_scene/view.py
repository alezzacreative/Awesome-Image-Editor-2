from PyQt6.QtCore import QModelIndex, QItemSelectionModel, QItemSelection
from PyQt6.QtWidgets import QTreeView

from .roles import ItemSelectionRole
from .tree_model import TreeModel


class TreeView(QTreeView):
    def __init__(self, model: TreeModel):
        super().__init__()
        self.setHeaderHidden(True)

        # self.setDragDropMode(QListView.DragDropMode.InternalMove)
        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.setModel(model)

        # Note: selection model is only available after setting model
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self.update_graphics_scene_selection_from_selection_model)

        model.scene().selectionChanged.connect(self.update_selection_model_selection_from_graphics_scene)

    def update_graphics_scene_selection_from_selection_model(self, selected: QItemSelection,
                                                             unselected: QItemSelection):
        # FIXME: index out of range when modifying scene
        for index in selected.indexes():
            # Only select if needed to prevent infinite recursion due to signals connected both ways
            if not self.model().data(index, ItemSelectionRole):
                self.model().setData(index, True, ItemSelectionRole)

        for index in unselected.indexes():
            # Only de-select if needed to prevent infinite recursion due to signals connected both ways
            if self.model().data(index, ItemSelectionRole):
                self.model().setData(index, False, ItemSelectionRole)

    def update_selection_model_selection_from_graphics_scene(self):
        # FIXME: update selection of child layers
        # currently only non-child layers' selection is synchronized
        for i in range(self.model().rowCount()):
            model_index = self.model().index(i, 0, QModelIndex())
            selection_model = self.selectionModel()
            if self.model().data(model_index, ItemSelectionRole):
                command = QItemSelectionModel.SelectionFlag.Select
            else:
                command = QItemSelectionModel.SelectionFlag.Deselect
            selection_model.select(model_index, command)
