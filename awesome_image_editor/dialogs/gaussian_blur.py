from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)


class GaussianBlurDialog(QDialog):
    """
    A dialog for configuring Gaussian blur parameters.

    This dialog allows the user to set the blur radius using a spinbox and a slider.
    It provides "OK", "Reset", and "Preview" options. The `blur_radius_changed`
    signal is emitted when the radius value changes, and `preview_checkbox_toggled`
    is emitted when the preview checkbox state changes.
    """

    DEFAULT_RADIUS: float = 7.2
    """The default blur radius value."""
    MIN_RADIUS: float = 0.1
    """The minimum allowable blur radius."""
    MAX_RADIUS: float = 400.0
    """The maximum allowable blur radius."""

    def __init__(self) -> None:
        """Initializes the GaussianBlurDialog."""
        super().__init__()
        self.setWindowTitle("Gaussian Blur")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QHBoxLayout()
        self.setLayout(layout)

        (
            self.spinbox,
            slider,
            slider_spinbox_layout,
        ) = self.create_slider_spinbox_layout()
        layout.addLayout(slider_spinbox_layout)

        self.blur_radius_changed = self.spinbox.valueChanged

        buttons_layout = QVBoxLayout()
        layout.addLayout(buttons_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.accept())
        buttons_layout.addWidget(ok_button)

        reset_button = QPushButton("Reset")
        buttons_layout.addWidget(reset_button)

        def on_reset_clicked():
            self.spinbox.setValue(self.DEFAULT_RADIUS)
            slider.setValue(int(self.DEFAULT_RADIUS * 10))

        self.preview_checkbox = QCheckBox("Preview")
        self.preview_checkbox.setChecked(True)
        self.preview_checkbox_toggled = self.preview_checkbox.toggled
        buttons_layout.addWidget(self.preview_checkbox)

        reset_button.clicked.connect(on_reset_clicked)

    def get_blur_radius(self) -> float:
        """
        Returns the current blur radius value from the spinbox.

        Returns:
            The current blur radius.
        """
        return self.spinbox.value()

    def is_preview_enabled(self) -> bool:
        """
        Checks if the preview checkbox is currently enabled (not just checked).

        Returns:
            True if the preview checkbox is enabled, False otherwise.
        """
        return self.preview_checkbox.isEnabled()

    def create_spinbox_layout(
        self,
    ) -> tuple[QDoubleSpinBox, QHBoxLayout]:
        """
        Creates the layout for the blur radius spinbox.

        This includes a label "Radius:", a stretchable space, and the QDoubleSpinBox.

        Returns:
            A tuple containing the QDoubleSpinBox widget and the QHBoxLayout.
        """
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Radius:"))
        layout.addStretch(1)
        spinbox = QDoubleSpinBox()
        spinbox.setDecimals(1)
        spinbox.setRange(self.MIN_RADIUS, self.MAX_RADIUS)
        spinbox.setValue(self.DEFAULT_RADIUS)
        layout.addWidget(spinbox)
        return spinbox, layout

    def create_slider_widget(self) -> QSlider:
        """
        Creates the slider for adjusting the blur radius.

        The slider's range is synchronized with `MIN_RADIUS` and `MAX_RADIUS`.

        Returns:
            The configured QSlider widget.
        """
        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setRange(int(self.MIN_RADIUS * 10), int(self.MAX_RADIUS * 10))
        slider.setValue(int(self.DEFAULT_RADIUS * 10))
        return slider

    def create_slider_spinbox_layout(
        self,
    ) -> tuple[QDoubleSpinBox, QSlider, QVBoxLayout]:
        """
        Creates the combined layout for the spinbox and slider.

        This method sets up the spinbox, slider, and connects their value changes
        to keep them synchronized.

        Returns:
            A tuple containing the QDoubleSpinBox, QSlider, and the QVBoxLayout
            that holds them.
        """
        layout = QVBoxLayout()
        spinbox, spinbox_layout = self.create_spinbox_layout()
        layout.addLayout(spinbox_layout)

        slider = self.create_slider_widget()
        layout.addWidget(slider)

        def on_spinbox_value_change(value):
            clamped_value = min(max(value, self.MIN_RADIUS), self.MAX_RADIUS)
            new_slider_value = int(clamped_value * 10)
            slider.setValue(new_slider_value)

        def on_slider_move(value):
            spinbox.setValue(min(max(value / 10, self.MIN_RADIUS), self.MAX_RADIUS))

        slider.sliderMoved.connect(on_slider_move)
        spinbox.valueChanged.connect(on_spinbox_value_change)

        return spinbox, slider, layout
