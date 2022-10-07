from typing import List, Protocol, Union

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QImage


class TreeItemProtocol(Protocol):
    name: str

    def get_thumbnail(self) -> Union[QImage]: ...

    def get_size_hint(self) -> QSize: ...

    def isSelected(self) -> bool: ...

    def setSelected(self, value: bool): ...

    def parent(self) -> "TreeItemProtocol": ...

    def childItems(self) -> List["TreeItemProtocol"]: ...
