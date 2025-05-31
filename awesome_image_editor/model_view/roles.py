from PyQt6.QtCore import Qt

ItemSelectionRole = Qt.ItemDataRole.UserRole
"""The data role used to store the selection state of an item in a model."""

OpacityRole = Qt.ItemDataRole.UserRole + 1
"""The data role used to store the opacity of a layer item (float 0.0-1.0)."""
