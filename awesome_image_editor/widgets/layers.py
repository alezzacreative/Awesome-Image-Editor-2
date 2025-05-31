from pathlib import PurePath

from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QToolBar, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSlider, QSpinBox

from ..model_view.tree_model import TreeModel
from ..model_view.tree_view import TreeView
from ..model_view.roles import OpacityRole


class LayersWidget(QWidget):
    def __init__(self, model: TreeModel):
        super().__init__()
        self._model = model
        self.list_view = TreeView(model)
        layout = QVBoxLayout()
        layout.addWidget(self.list_view)
        layout.setContentsMargins(0, 0, 0, 0)

        # Opacity Controls
        opacity_label = QLabel("Opacity:")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100) # 0-100 for 0.0-1.0 opacity
        self.opacity_slider.setValue(100) # Default to fully opaque

        self.opacity_spinbox = QSpinBox()
        self.opacity_spinbox.setRange(0, 100)
        self.opacity_spinbox.setValue(100)
        self.opacity_spinbox.setSuffix("%")

        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_spinbox)

        layout.addLayout(opacity_layout)

        self.opacity_slider.setEnabled(False)
        self.opacity_spinbox.setEnabled(False)

        # Toolbar
        self.toolbar = QToolBar()
        layout.addWidget(self.toolbar)
        self.toolbar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        icon = QIcon(
            (
                PurePath(__file__).parent.parent / "icons" / "layers" / "delete_btn.svg"
            ).as_posix()
        )
        self.toolbar.addAction(icon, "Delete", self.delete_selected_items)
        self.setLayout(layout)

        # Connect signals
        self.list_view.selectionModel().currentChanged.connect(self._on_selection_changed)
        self.opacity_slider.valueChanged.connect(self._on_slider_opacity_changed)
        self.opacity_spinbox.valueChanged.connect(self._on_spinbox_opacity_changed)

    def _on_selection_changed(self, current: QModelIndex, previous: QModelIndex) -> None:
        if not current.isValid() or len(self.list_view.selectionModel().selectedIndexes()) != 1:
            self.opacity_slider.setEnabled(False)
            self.opacity_spinbox.setEnabled(False)
            # self.opacity_slider.setValue(100)
            # self.opacity_spinbox.setValue(100)
            return

        self.opacity_slider.setEnabled(True)
        self.opacity_spinbox.setEnabled(True)

        # Block signals while setting value programmatically
        self.opacity_slider.blockSignals(True)
        self.opacity_spinbox.blockSignals(True)

        opacity_float = self._model.data(current, OpacityRole)
        if opacity_float is not None:
            self.opacity_slider.setValue(int(opacity_float * 100))
            self.opacity_spinbox.setValue(int(opacity_float * 100))
        else: # Should not happen if model provides default
            self.opacity_slider.setValue(100)
            self.opacity_spinbox.setValue(100)

        self.opacity_slider.blockSignals(False)
        self.opacity_spinbox.blockSignals(False)

    def _on_slider_opacity_changed(self, value: int) -> None:
        selected_indexes = self.list_view.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        current_index = selected_indexes[0]

        self.opacity_spinbox.blockSignals(True)
        self.opacity_spinbox.setValue(value)
        self.opacity_spinbox.blockSignals(False)

        new_opacity_float = value / 100.0
        self._model.setData(current_index, new_opacity_float, OpacityRole)

    def _on_spinbox_opacity_changed(self, value: int) -> None:
        selected_indexes = self.list_view.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        current_index = selected_indexes[0]

        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(value)
        self.opacity_slider.blockSignals(False)

        new_opacity_float = value / 100.0
        self._model.setData(current_index, new_opacity_float, OpacityRole)

    def delete_selected_items(self):
        self._model.beginResetModel()
        scene = self._model.scene()
        for item in scene.selectedItems():
            scene.removeItem(item)
        self._model.endResetModel()
