from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox, 
    QDialogButtonBox, QPushButton
)
from PyQt6.QtCore import Qt

class BrightnessContrastDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Brightness/Contrast")

        layout = QVBoxLayout(self)

        # Brightness controls
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("Brightness:")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_spinbox = QSpinBox()
        self.brightness_spinbox.setRange(-100, 100)
        self.brightness_spinbox.setValue(0)
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_spinbox)
        layout.addLayout(brightness_layout)

        # Connect slider and spinbox for Brightness
        self.brightness_slider.valueChanged.connect(self.brightness_spinbox.setValue)
        self.brightness_spinbox.valueChanged.connect(self.brightness_slider.setValue)

        # Contrast controls
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("Contrast:")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_spinbox = QSpinBox()
        self.contrast_spinbox.setRange(-100, 100)
        self.contrast_spinbox.setValue(0)
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_spinbox)
        layout.addLayout(contrast_layout)

        # Connect slider and spinbox for Contrast
        self.contrast_slider.valueChanged.connect(self.contrast_spinbox.setValue)
        self.contrast_spinbox.valueChanged.connect(self.contrast_slider.setValue)
        
        # Placeholder for Preview checkbox (optional future addition)
        # self.preview_checkbox = QCheckBox("Preview")
        # layout.addWidget(self.preview_checkbox)

        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_values(self):
        return {
            "brightness": self.brightness_slider.value(),
            "contrast": self.contrast_slider.value()
        }

if __name__ == '__main__':
    # For testing the dialog independently
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dialog = BrightnessContrastDialog()
    if dialog.exec():
        print(dialog.get_values())
    sys.exit(app.exec())
