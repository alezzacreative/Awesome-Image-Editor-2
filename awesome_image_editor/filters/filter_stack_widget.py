from typing import Any

from PySide2.QtCore import QAbstractListModel, QModelIndex, Qt


class FilterStackModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._items = []

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._items)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if index.isValid():
            return self._items(index.row())

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if 0 < row < len(self._items):
            self.beginInsertRows()
            for _ in range(count):
                self._items.insert(row, None)
            self.endInsertRows()
            return True
        return False

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if 0 < row < len(self._items):
            self.beginRemoveRows()
            for _ in range(count):
                if len(self._items) <= row:
                    break
                self._items.pop(row)
            self.endRemoveRows()
            return True
        return False

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if index.isValid():
            self._items[index.row()] = value

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return super().flags(index) | Qt.ItemIsEditable
