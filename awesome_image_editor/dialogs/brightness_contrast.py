from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox,
    QPushButton, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class BrightnessContrastDialog(QDialog):
    """
    A dialog for adjusting brightness and contrast of an image.
    Emits valueChanged signal for live preview and uses accepted/rejected signals for final action.
    """
    # Signal to indicate values have changed, potentially for preview
    # Emits: brightness (int), contrast (int), is_preview_enabled (bool)
    valuesChangedForPreview = pyqtSignal(int, int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Brightness / Contrast")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)


        # --- Layouts ---
        main_layout = QVBoxLayout(self)
        controls_layout = QVBoxLayout()
        # buttons_layout = QHBoxLayout() # This was defined but not used, QDialogButtonBox handles button layout

        # --- Brightness Controls ---
        brightness_label = QLabel("Brightness:")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_spinbox = QSpinBox()
        self.brightness_spinbox.setRange(-100, 100)
        self.brightness_spinbox.setValue(0)

        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_spinbox)
        controls_layout.addLayout(brightness_layout)

        # --- Contrast Controls ---
        contrast_label = QLabel("Contrast:")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100) # Contrast typically 0-100 or -100 to 100 for adjustment
        self.contrast_slider.setValue(0)      # 0 means no change
        self.contrast_spinbox = QSpinBox()
        self.contrast_spinbox.setRange(-100, 100)
        self.contrast_spinbox.setValue(0)

        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_spinbox)
        controls_layout.addLayout(contrast_layout)

        main_layout.addLayout(controls_layout)

        # --- Preview Checkbox ---
        self.preview_checkbox = QCheckBox("Enable Preview")
        self.preview_checkbox.setChecked(True)
        main_layout.addWidget(self.preview_checkbox)

        # --- Dialog Buttons (OK/Cancel) ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        # Add Reset button
        reset_button = self.button_box.addButton("Reset", QDialogButtonBox.ButtonRole.ResetRole)
        reset_button.clicked.connect(self.reset_values)
        main_layout.addWidget(self.button_box)

        # --- Signal Connections for Sliders and Spinboxes ---
        self.brightness_slider.valueChanged.connect(self.brightness_spinbox.setValue)
        self.brightness_spinbox.valueChanged.connect(self.brightness_slider.setValue)
        self.contrast_slider.valueChanged.connect(self.contrast_spinbox.setValue)
        self.contrast_spinbox.valueChanged.connect(self.contrast_slider.setValue)

        # Connect to custom signal for preview
        self.brightness_slider.valueChanged.connect(self._emit_values_changed_for_preview)
        self.contrast_slider.valueChanged.connect(self._emit_values_changed_for_preview)
        self.preview_checkbox.toggled.connect(self._emit_values_changed_for_preview)

    def _emit_values_changed_for_preview(self):
        """Emits the current values for preview purposes."""
        self.valuesChangedForPreview.emit(
            self.brightness_slider.value(),
            self.contrast_slider.value(),
            self.preview_checkbox.isChecked()
        )

    def reset_values(self):
        """Resets brightness and contrast controls to their default values."""
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        # self.preview_checkbox.setChecked(True) # Optionally reset preview checkbox
        # Emission for preview update will happen due to slider valueChanged signals

    def get_brightness(self) -> int:
        """Returns the current brightness value."""
        return self.brightness_slider.value()

    def get_contrast(self) -> int:
        """Returns the current contrast value."""
        return self.contrast_slider.value()

    def is_preview_enabled(self) -> bool:
        """Returns whether the preview checkbox is checked."""
        return self.preview_checkbox.isChecked()

    def set_values(self, brightness: int, contrast: int, preview_enabled: bool = True) -> None:
        """Sets initial values for the dialog controls."""
        self.brightness_slider.setValue(brightness)
        self.contrast_slider.setValue(contrast)
        self.preview_checkbox.setChecked(preview_enabled)
        # Emit values after setting them, so preview can update if dialog is already visible
        self._emit_values_changed_for_preview()


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    dialog_instance = BrightnessContrastDialog()
    dialog_instance.set_values(brightness=10, contrast=-5) # Example of setting initial values

    def on_preview(b, c, p_enabled):
        print(f"Preview: Brightness={b}, Contrast={c}, Preview Active={p_enabled}")

    dialog_instance.valuesChangedForPreview.connect(on_preview)

    # To trigger initial preview if needed when dialog is shown:
    # dialog_instance.show()
    # if dialog_instance.is_preview_enabled():
    #     dialog_instance._emit_values_changed_for_preview()
    # result = dialog_instance.exec()

    # Or more simply, the main application can call _emit_values_changed_for_preview()
    # or set_values() which calls it, after instantiating and before/after showing.
    # For this standalone test, set_values already calls it.

    if dialog_instance.exec() == QDialog.DialogCode.Accepted:
        final_brightness = dialog_instance.get_brightness()
        final_contrast = dialog_instance.get_contrast()
        print(f"Dialog OK: Brightness={final_brightness}, Contrast={final_contrast}")
    else:
        print("Dialog Cancelled")

    sys.exit()
