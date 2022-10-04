from typing import Optional

from PyQt6.QtCore import Qt

from .items.base import BaseGraphicsItem


class QGraphicsTreeItem:
    def __init__(self, graphics_item: Optional[BaseGraphicsItem], parent: Optional["QGraphicsTreeItem"]):
        self._parent = parent
        self._graphics_item = graphics_item
        self.childItems = []

    def append_child(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def child_count(self):
        return len(self.childItems)

    def data(self, role: int):
        if role == Qt.ItemDataRole.DisplayRole:
            return getattr(self._graphics_item, "name", "FAILED TO GET LAYER NAME!!")

        elif role == Qt.ItemDataRole.DecorationRole:
            return getattr(self._graphics_item, "get_thumbnail", lambda: None)()

        elif role == Qt.ItemDataRole.SizeHintRole:
            return getattr(self._graphics_item, "get_size_hint", lambda: None)()

    def parent(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent.childItems.index(self)

        return 0
