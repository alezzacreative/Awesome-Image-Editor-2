from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt

from .graphics_scene import AIEGraphicsScene
from .roles import ItemSelectionRole
from .tree_item import TreeItemProtocol


class RootItemParent:
    """A marker class used as the parent for the `RootItem`."""

    ...


class RootItem:
    """
    A proxy class that acts as the root item for the `TreeModel`.

    This class interfaces with a `AIEGraphicsScene` to provide its top-level
    items as children of this root item. It implements parts of the
    `TreeItemProtocol` for compatibility with the model.
    """

    def __init__(self, scene: AIEGraphicsScene) -> None:
        """
        Initializes the RootItem.

        Args:
            scene: The AIEGraphicsScene whose items will be managed.
        """
        self.name = ""  # Root item typically has no name
        self._scene = scene

    def parentItem(self) -> RootItemParent:
        """Returns the parent of this root item, which is `RootItemParent`."""
        return RootItemParent

    def get_thumbnail(self):
        """Not implemented for RootItem."""
        ...

    def get_size_hint(self):
        """Not implemented for RootItem."""
        ...

    def isSelected(self) -> bool:
        """RootItem cannot be selected."""
        return False

    def setSelected(self, value: bool) -> None:
        """RootItem cannot be selected."""
        ...

    def childItems(self) -> list[TreeItemProtocol]:
        """
        Returns the top-level items from the associated AIEGraphicsScene.

        Items are returned in descending order as they appear in the scene.
        """
        return [
            item
            for item in self._scene.items(order=Qt.SortOrder.DescendingOrder)
            if item.parentItem() is None
        ]

    def isVisible(self) -> bool:
        """RootItem is always considered visible."""
        return True

    def setVisible(self, value: bool) -> None:
        """Visibility of RootItem cannot be changed."""
        ...


class TreeModel(QAbstractItemModel):
    """
    A QAbstractItemModel that provides a tree-like view of items in an AIEGraphicsScene.

    This model uses a `RootItem` to represent the scene's top-level items
    and allows interaction with items based on the `TreeItemProtocol`.
    It connects to scene signals to automatically update when items are added.
    """

    def __init__(
        self, scene: AIEGraphicsScene, parent: QModelIndex | None = None
    ) -> None:
        """
        Initializes the TreeModel.

        Args:
            scene: The AIEGraphicsScene to model.
            parent: The parent QObject, if any.
        """
        super().__init__(parent)
        self._scene = scene
        self._root_item = RootItem(scene)

        scene.itemAboutToBeAppended.connect(
            lambda i: self.beginInsertRows(QModelIndex(), i, i)
        )
        scene.itemAppended.connect(lambda: self.endInsertRows())

    def scene(self) -> AIEGraphicsScene:
        """
        Returns the AIEGraphicsScene associated with this model.
        """
        return self._scene

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Returns the number of columns for the children of the given parent.

        This model always has 1 column.
        """
        return 1

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """
        Returns the data stored under the given role for the item referred to by the index.

        Args:
            index: The QModelIndex of the item.
            role: The data role to retrieve (e.g., DisplayRole, DecorationRole).

        Returns:
            The data for the given role, or None if the index is invalid or
            the item doesn't have data for that role.
        """
        if not index.isValid():
            return None

        item = self.getItem(index)

        if item is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return item.name
        elif role == Qt.ItemDataRole.DecorationRole:
            return item.get_thumbnail()
        elif role == Qt.ItemDataRole.SizeHintRole:
            return item.get_size_hint()
        elif role == Qt.ItemDataRole.CheckStateRole:
            return (
                Qt.CheckState.Checked if item.isVisible() else Qt.CheckState.Unchecked
            )
        elif role == ItemSelectionRole:
            return item.isSelected()
        return None

    def setData_(
        self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole
    ) -> bool:
        """
        Internal helper to set data for an item.

        Args:
            index: The QModelIndex of the item.
            value: The new value for the data.
            role: The data role to set.

        Returns:
            True if data was set successfully, False otherwise.
        """
        item = self.getItem(index)
        if item is None:
            return False

        if role == ItemSelectionRole:
            item.setSelected(value)
            return True
        elif role == Qt.ItemDataRole.CheckStateRole:
            item.setVisible(Qt.CheckState(value) == Qt.CheckState.Checked)
            return True

        return False

    def setData(
        self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole
    ) -> bool:
        """
        Sets the role data for the item at index to value.

        Emits `dataChanged` signal if successful.

        Args:
            index: The QModelIndex of the item.
            value: The new value for the data.
            role: The data role to set.

        Returns:
            True if data was set successfully, False otherwise.
        """
        is_data_changed = self.setData_(index, value, role)
        if is_data_changed:
            self.dataChanged.emit(index, index)
        return is_data_changed

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """
        Returns the item flags for the given index.

        Args:
            index: The QModelIndex of the item.

        Returns:
            The appropriate Qt.ItemFlags for the item.
        """
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsUserCheckable
        )

    def getItem(self, index: QModelIndex) -> TreeItemProtocol | None:
        """
        Retrieves the TreeItemProtocol object associated with the given QModelIndex.

        Args:
            index: The QModelIndex.

        Returns:
            The TreeItemProtocol object, or None if the index is invalid or
            points to no item.
        """
        if index.isValid():
            item: TreeItemProtocol = index.internalPointer()
            if item:
                return item
        return None

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        """
        Returns the index of the item in the model specified by the given row, column and parent index.

        Args:
            row: The row of the item.
            column: The column of the item.
            parent: The QModelIndex of the parent item.

        Returns:
            A QModelIndex for the child item, or an invalid QModelIndex if
            the parent is invalid or has no such child.
        """
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        if parentItem is None:
            parentItem = self._root_item

        childItems = parentItem.childItems()
        if 0 <= row < len(childItems):
            childItem = childItems[row]
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def row(self, item: TreeItemProtocol) -> int:
        """
        Returns the row of the given item within its parent's list of children.

        Args:
            item: The TreeItemProtocol object.

        Returns:
            The row number, or 0 if it's a top-level item or not found.
        """
        parentItem = item.parentItem()
        if parentItem is None or isinstance(parentItem, RootItemParent):
            # For top-level items, their parent is RootItem or None.
            # We need to find its index in RootItem's children.
            # RootItemParent is a special case for the RootItem itself.
            try:
                return self._root_item.childItems().index(item)
            except ValueError:
                return 0 # Should not happen if item is part of the model

        if hasattr(parentItem, "childItems"):
            try:
                return parentItem.childItems().index(item)
            except ValueError:
                 pass # Should not happen
        return 0


    def parent(self, index: QModelIndex) -> QModelIndex:
        """
        Returns the parent of the model item with the given index.

        If the item has no parent, an invalid QModelIndex is returned.

        Args:
            index: The QModelIndex of the child item.

        Returns:
            A QModelIndex for the parent item, or an invalid QModelIndex.
        """
        if not index.isValid():
            return QModelIndex()

        childItem: TreeItemProtocol | None = index.internalPointer()
        if childItem is None:
            return QModelIndex()

        parentItem: TreeItemProtocol | RootItemParent | None = childItem.parentItem()

        if parentItem is None or parentItem is RootItemParent:
            # Parent is the root item, which is represented by an invalid QModelIndex
            return QModelIndex()

        # Ensure parentItem is TreeItemProtocol, not RootItemParent
        if isinstance(parentItem, RootItemParent): # Should not happen here due to above check
             return QModelIndex()


        return self.createIndex(self.row(parentItem), 0, parentItem)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Returns the number of rows under the given parent.

        When the parent is valid it means that rowCount is returning the number
        of children of parent. When the parent is invalid, it means that the
        number of top-level items is returned.

        Args:
            parent: The QModelIndex of the parent item.

        Returns:
            The number of child items.
        """
        parentItem = self.getItem(parent)

        if parentItem is None:
            # root, return number of scene top level items
            return len(self._root_item.childItems())
        else:
            return len(parentItem.childItems())
