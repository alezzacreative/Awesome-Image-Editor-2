from typing import List, Protocol, Union

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QImage


class TreeItemProtocol(Protocol):
    """
    A protocol defining the interface for items in a tree structure.

    This protocol is used by `TreeModel` and `TreeView` to interact with
    items in a generic way.
    """

    name: str
    """The display name of the tree item."""

    def get_thumbnail(self) -> Union[QImage, QIcon]:
        """
        Returns a thumbnail representation of the item.

        This can be a QImage or a QIcon.
        """
        ...

    def get_size_hint(self) -> QSize:
        """
        Returns the recommended size for displaying this item, particularly its thumbnail.
        """
        ...

    def isSelected(self) -> bool:
        """Returns True if the item is currently selected, False otherwise."""
        ...

    def setSelected(self, value: bool) -> None:
        """
        Sets the selection state of the item.

        Args:
            value: True to select the item, False to deselect.
        """
        ...

    def parentItem(self) -> "TreeItemProtocol":
        """
        Returns the parent of this item in the tree.

        Returns None if this is a top-level item.
        """
        ...

    def childItems(self) -> List["TreeItemProtocol"]:
        """Returns a list of child items of this item."""
        ...

    def isVisible(self) -> bool:
        """Returns True if the item is currently visible, False otherwise."""
        ...

    def setVisible(self, value: bool) -> None:
        """
        Sets the visibility state of the item.

        Args:
            value: True to make the item visible, False to hide.
        """
        ...
