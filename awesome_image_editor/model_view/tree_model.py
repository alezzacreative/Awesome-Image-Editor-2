from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt

from .graphics_scene import AIEGraphicsScene
from .roles import ItemSelectionRole
from .tree_item import TreeItemProtocol


def child_number(item: TreeItemProtocol):
    parent = item.parentItem()
    if parent is not None:
        return parent.childItems().index(item)

    return 0


class TreeModel(QAbstractItemModel):
    def __init__(self, scene: AIEGraphicsScene, parent=None):
        super().__init__(parent)
        self._scene = scene

        scene.itemAboutToBeAppended.connect(
            lambda i: self.beginInsertRows(QModelIndex(), i, i)
        )
        scene.itemAppended.connect(lambda: self.endInsertRows())

    def scene(self):
        return self._scene

    def columnCount(self, parent: QModelIndex = ...):
        return 1

    def data(self, index: QModelIndex, role: int = ...):
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

    def setData_(self, index: QModelIndex, value, role: int = ...):
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

    def setData(self, index: QModelIndex, value, role: int = ...) -> bool:
        is_data_changed = self.setData_(index, value, role)
        if is_data_changed:
            self.dataChanged.emit(index, index)
        return is_data_changed

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsUserCheckable
        )

    def getItem(self, index: QModelIndex):
        if index.isValid():
            item: TreeItemProtocol = index.internalPointer()
            if item:
                return item

        return None

    def index(self, row: int, column: int, parent: QModelIndex = ...):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        if parentItem is None:
            childItem = self.getIthTopLevelItem(row)
        else:
            childItem = parentItem.childItems()[row]

        return self.createIndex(row, column, childItem)

    def parent(self, index: QModelIndex):
        child_item = self.getItem(index)

        if child_item is None:
            return QModelIndex()

        parent_item = child_item.parentItem()

        if parent_item is None:
            # is root item
            return QModelIndex()

        return self.createIndex(child_number(parent_item), 0, parent_item)

    def getIthTopLevelItem(self, i: int):
        iterator = (
            item
            for item in self._scene.items(order=Qt.SortOrder.DescendingOrder)
            if item.parentItem() is None
        )
        item = None
        for _ in range(i + 1):
            item = next(iterator)
        return item

    def rowCount(self, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        if parentItem is None:
            # root, return number of scene top level items
            return sum(1 for item in self._scene.items() if item.parentItem() is None)
        else:
            return len(parentItem.childItems())
