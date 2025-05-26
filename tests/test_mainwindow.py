# In a file like tests/test_mainwindow.py
import pytest
from unittest.mock import Mock
from PyQt6.QtWidgets import QLabel

# from awesome_image_editor.mainwindow import MainWindow # If testing MainWindow directly

# For now, let's just test the slot logic if we can isolate it.
# If MainWindow is complex to instantiate, we might test a helper or a simplified version.

# Assuming we can get an instance of MainWindow or mock it appropriately
class MockMainWindow: # Simplified mock for the slot
    def __init__(self):
        self.zoom_status_label = Mock(spec=QLabel)
    
    def update_zoom_status(self, scale_factor: float):
        self.zoom_status_label.setText(f"Zoom: {scale_factor * 100:.1f}%")

def test_mainwindow_update_zoom_status():
    mw = MockMainWindow()
    mw.update_zoom_status(1.0)
    mw.zoom_status_label.setText.assert_called_once_with("Zoom: 100.0%")

    mw.update_zoom_status(0.753)
    mw.zoom_status_label.setText.assert_called_with("Zoom: 75.3%")
    
    mw.update_zoom_status(1.2345)
    mw.zoom_status_label.setText.assert_called_with("Zoom: 123.5%") # .1f rounding
```
