import pytest
from unittest.mock import Mock

from PyQt6.QtWidgets import QApplication # For instantiating dialog
from PyQt6.QtCore import Qt

# Adjust import path
from awesome_image_editor.dialogs.brightness_contrast_dialog import BrightnessContrastDialog

@pytest.fixture
def bc_dialog(qtbot): # qtbot might be needed if dialog shows itself
    # QApplication.instance() is None if not created by pytest-qt
    # For simple dialog logic tests, direct instantiation is fine.
    # If exec() is called, qtbot is useful.
    dialog = BrightnessContrastDialog()
    return dialog

def test_bc_dialog_initial_values(bc_dialog):
    assert bc_dialog.brightness_slider.value() == 0
    assert bc_dialog.brightness_spinbox.value() == 0
    assert bc_dialog.contrast_slider.value() == 0
    assert bc_dialog.contrast_spinbox.value() == 0
    
    values = bc_dialog.get_values()
    assert values["brightness"] == 0
    assert values["contrast"] == 0

def test_bc_dialog_set_get_values(bc_dialog):
    bc_dialog.brightness_slider.setValue(30)
    bc_dialog.contrast_slider.setValue(-20)
    
    assert bc_dialog.brightness_spinbox.value() == 30 # Check sync
    assert bc_dialog.contrast_spinbox.value() == -20  # Check sync
    
    values = bc_dialog.get_values()
    assert values["brightness"] == 30
    assert values["contrast"] == -20

def test_bc_dialog_spinbox_updates_slider(bc_dialog):
    bc_dialog.brightness_spinbox.setValue(45)
    assert bc_dialog.brightness_slider.value() == 45
    
    bc_dialog.contrast_spinbox.setValue(-60)
    assert bc_dialog.contrast_slider.value() == -60

# Test for accept/reject could be added if there's more logic there,
# but typically they just close the dialog with a result code.
```
