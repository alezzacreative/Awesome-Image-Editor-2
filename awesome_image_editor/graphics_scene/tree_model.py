from PyQt6.QtCore import QModelIndex, Qt, QAbstractItemModel

from .graphics_scene import AIEGraphicsScene
from .roles import ItemSelectionRole
from .tree_item import TreeItemProtocol


def item_index_relative_to_parent(item: TreeItemProtocol):
    parent = item.parent()
    if parent:
        return parent.childItems().index(item)
    # FIXME: should return index of item in scene items list instead?
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
        item: TreeItemProtocol = index.internalPointer()

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
        if not index.isValid():
            return False

        item: TreeItemProtocol = index.internalPointer()
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

    def index(self, row: int, column: int, parent: QModelIndex = ...):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent.isValid():
            child_item = parent.internalPointer().childItems()[row]
        else:
            child_item = self.scene().items()[row]

        return self.createIndex(row, column, child_item)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parentItem()

        if parent_item is None:
            return QModelIndex()

        row = item_index_relative_to_parent(parent_item)
        return self.createIndex(row, 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return len(parent.internalPointer().childItems())
        else:
            return len(self._scene.items())
