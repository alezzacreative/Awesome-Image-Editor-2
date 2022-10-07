from PyQt6.QtCore import QModelIndex, Qt, QAbstractItemModel

from .graphics_scene import AIEGraphicsScene
from .tree_item import TreeItemDataProtocol, TreeItem


class TreeModel(QAbstractItemModel):
    def __init__(self, scene: AIEGraphicsScene, parent=None):
        super().__init__(parent)

        self.root_item = TreeItem(None, None)
        for item in scene.items():
            self.root_item.append_child(TreeItem(item, self.root_item))

        scene.itemAppended.connect(self.append_item)

    def append_item(self, item: TreeItemDataProtocol):
        self.beginInsertRows(QModelIndex(), self.root_item.child_count(), self.root_item.child_count())
        self.root_item.append_child(TreeItem(item, self.root_item))
        self.endInsertRows()

    def columnCount(self, parent: QModelIndex = ...):
        return 1

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return None
        item: TreeItem = index.internalPointer()
        return item.data(role)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def index(self, row: int, column: int, parent: QModelIndex = ...):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = ...):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()
