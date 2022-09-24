from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSlider,
    QSpinBox,
    QWidget,
)

__all__ = ("LinkedSliderSpinBox",)


class LinkedSliderSpinBox(QWidget):
    """A slider and a spin box linked to the same value"""

    def __init__(self, default_value, min_value, max_value):
        super().__init__()
        self.value = default_value

        layout = QHBoxLayout()
        self.setLayout(layout)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(
            min_value, max_value
        )  # Range must be set before setting value
        self.slider.setValue(default_value)
        self.slider.valueChanged.connect(self._on_slider_set_value)
        layout.addWidget(self.slider)

        self.spinbox = QSpinBox()
        self.spinbox.setRange(
            min_value, max_value
        )  # Range must be set before setting value
        self.spinbox.setValue(default_value)
        self.spinbox.valueChanged.connect(self._on_spinbox_set_value)
        layout.addWidget(self.spinbox)

    def _on_slider_set_value(self, value: int):
        self.value = value
        self.spinbox.setValue(value)

    def _on_spinbox_set_value(self, value: int):
        self.value = value
        self.slider.setValue(value)
