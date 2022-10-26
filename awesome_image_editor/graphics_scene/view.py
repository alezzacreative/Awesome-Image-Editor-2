from PyQt6.QtCore import QItemSelectionModel, QModelIndex
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

        # NOTE: selection model is only available after setting model
        selection_model = self.selectionModel()

        # Connect selection signals:
        # NOTE: infinite recursion due to signals connected both ways SHOULD NOT HAPPEN
        # since these callbacks should be connected to signals that only fire when the selection is actually changed
        # (e.g. QItemSelectionModel.selectionChanges and QGraphicsScene.selectionChanged)
        selection_model.selectionChanged.connect(
            self.sync_selection_from_selection_model_to_scene
        )
        model.scene().selectionChanged.connect(
            self.sync_selection_from_scene_to_selection_model
        )

        # A lock used for preventing the invoke of selection syncing in the opposite direction (from-scene-to-selection-model as opposed to from-selection-model-to-scene)
        # while selection is being synced, otherwise the selection will resist changes, as the old selection in scene for example, is not yet in sync, so if the sync in opposite direction is invoked,
        # it will try to sync the old selection state
        self._is_selection_locked = False

    def iter_model_indices_recursive(self):
        root_model_index = QModelIndex()
        model_indices_stack = [root_model_index]

        while len(model_indices_stack) > 0:
            model_index = model_indices_stack.pop(0)

            for i in range(self.model().rowCount(model_index)):
                child_model_index = self.model().index(i, 0, model_index)
                model_indices_stack.append(child_model_index)

            if model_index == QModelIndex():
                continue  # skip root node

            yield model_index

    def sync_model_item_selection_to_selection_model(self, model_index: QModelIndex):
        is_selected = self.model().data(model_index, ItemSelectionRole)

        if is_selected:
            command = QItemSelectionModel.SelectionFlag.Select
        else:
            command = QItemSelectionModel.SelectionFlag.Deselect

        self.selectionModel().select(model_index, command)

    def sync_selection_from_selection_model_to_scene(self):
        if self._is_selection_locked:
            return

        self._is_selection_locked = True
        for model_index in self.iter_model_indices_recursive():
            self.model().setData(
                model_index,
                self.selectionModel().isSelected(model_index),
                ItemSelectionRole,
            )

            # Sync selection back from scene, so that non-selectable items are not selected (e.g. non visible items)
            # otherwise the selection will be out of sync
            # TODO: notify model about non-selectable items when selectable flag or visibility changes instead?
            self.sync_model_item_selection_to_selection_model(model_index)
        self._is_selection_locked = False

    def sync_selection_from_scene_to_selection_model(self):
        if self._is_selection_locked:
            return

        self._is_selection_locked = True

        for model_index in self.iter_model_indices_recursive():
            self.sync_model_item_selection_to_selection_model(model_index)

        self._is_selection_locked = False
