from typing import Iterator
from PyQt6.QtCore import QItemSelectionModel, QModelIndex
from PyQt6.QtWidgets import QTreeView

from .roles import ItemSelectionRole
from .tree_model import TreeModel


class TreeView(QTreeView):
    """
    A custom QTreeView for displaying and interacting with a `TreeModel`.

    This view synchronizes its selection state with the underlying
    `AIEGraphicsScene` associated with the model. It also provides
    utility methods for iterating over model indices.
    """

    def __init__(self, model: TreeModel) -> None:
        """
        Initializes the TreeView.

        Args:
            model: The TreeModel to display.
        """
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
        # (e.g. QItemSelectionModel.selectionChanged and QGraphicsScene.selectionChanged)
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

    def iter_model_indices_recursive(self) -> Iterator[QModelIndex]:
        """
        Iterates recursively over all valid QModelIndex items in the model.

        This method performs a breadth-first traversal.

        Yields:
            QModelIndex: The next model index in the traversal.
        """
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

    def sync_model_item_selection_to_selection_model(
        self, model_index: QModelIndex
    ) -> bool:
        """
        Synchronizes the selection state of a single model item to the view's selection model.

        Reads the selection state from the model's `ItemSelectionRole` and
        updates the `QItemSelectionModel` of the view accordingly.

        Args:
            model_index: The QModelIndex of the item to synchronize.

        Returns:
            bool: The selection state of the item after synchronization (True if selected).
        """
        is_selected = self.model().data(model_index, ItemSelectionRole)

        if is_selected:
            command = QItemSelectionModel.SelectionFlag.Select
        else:
            command = QItemSelectionModel.SelectionFlag.Deselect

        self.selectionModel().select(model_index, command)

        return bool(is_selected)

    def sync_selection_from_selection_model_to_scene(self) -> None:
        """
        Synchronizes the selection state from the view's selection model to the scene.

        Iterates over all items in the model, gets their selection state from
        the `QItemSelectionModel`, and sets it in the `TreeModel` (which in
        turn updates the `AIEGraphicsScene` items). This also handles ensuring
        that non-selectable items in the scene are not marked as selected in the view.
        Uses a lock to prevent recursive sync calls.
        """
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

    def sync_selection_from_scene_to_selection_model(self) -> None:
        """
        Synchronizes the selection state from the scene (via the TreeModel) to this view's selection model.

        Iterates over all items in the model, gets their selection state from
        the `TreeModel` (which reflects the `AIEGraphicsScene` item's state),
        and updates the `QItemSelectionModel` of the view. If an item is
        selected, it also ensures it's scrolled to be visible.
        Uses a lock to prevent recursive sync calls.
        """
        if self._is_selection_locked:
            return

        self._is_selection_locked = True

        for model_index in self.iter_model_indices_recursive():
            is_selected = self.sync_model_item_selection_to_selection_model(model_index)

            # Ensure selected item is visible in tree view
            if is_selected:
                self.scrollTo(model_index)

        self._is_selection_locked = False
