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

        # Connect selection signals:
        # NOTE: infinite recursion due to signals connected both ways SHOULD NOT HAPPEN
        # since these callbacks should be connected to signals that only fire when the selection is actually changed
        # (e.g. QItemSelectionModel.selectionChanges and QGraphicsScene.selectionChanged

        selection_model.selectionChanged.connect(self.update_graphics_scene_selection_from_selection_model)

        # Re-sync selection model selection when selection model selection changes
        # This ensures selection is actually in sync with the graphics scene
        # even if some graphics items were not selected (e.g. non-selectable graphics items)
        selection_model.selectionChanged.connect(self.update_selection_model_selection_from_graphics_scene)

        model.scene().selectionChanged.connect(self.update_selection_model_selection_from_graphics_scene)

    def update_graphics_scene_selection_from_selection_model(self, selected: QItemSelection,
                                                             unselected: QItemSelection):
        for index in selected.indexes():
            self.model().setData(index, True, ItemSelectionRole)

        for index in unselected.indexes():
            self.model().setData(index, False, ItemSelectionRole)

    def update_selection_model_selection_from_graphics_scene(self):
        # FIXME: update selection of child layers
        # currently only non-child layers' selection is synchronized
        for i in range(self.model().rowCount()):
            model_index = self.model().index(i, 0, QModelIndex())
            is_selected = self.model().data(model_index, ItemSelectionRole)
            if is_selected:
                command = QItemSelectionModel.SelectionFlag.Select
            else:
                command = QItemSelectionModel.SelectionFlag.Deselect
            self.selectionModel().select(model_index, command)
