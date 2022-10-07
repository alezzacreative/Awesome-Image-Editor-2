from typing import Optional
from typing import Protocol, Union

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QImage

from .roles import ItemSelectionRole


class TreeItemDataProtocol(Protocol):
    name: str

    def get_thumbnail(self) -> Union[QImage]: ...

    def get_size_hint(self) -> QSize: ...

    def isSelected(self) -> bool: ...

    def setSelected(self, value: bool): ...


class TreeItem:
    def __init__(self, data: Optional[TreeItemDataProtocol], parent: Optional["TreeItem"]):
        self._parent = parent
        self._graphics_item = data
        self.child_items = []

    def append_child(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def data(self, role: int):
        if self._graphics_item is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._graphics_item.name

        elif role == Qt.ItemDataRole.DecorationRole:
            return self._graphics_item.get_thumbnail()

        elif role == Qt.ItemDataRole.SizeHintRole:
            return self._graphics_item.get_size_hint()

        elif role == ItemSelectionRole:
            return self._graphics_item.isSelected()

    def setData(self, role: int, value):
        if self._graphics_item is None:
            return

        if role == ItemSelectionRole:
            self._graphics_item.setSelected(value)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent.child_items.index(self)

        return 0
