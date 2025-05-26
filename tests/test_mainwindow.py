# In a file like tests/test_mainwindow.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QLabel, QMessageBox # Added QMessageBox for patching
from PyQt6.QtGui import QImage # Added QImage

from awesome_image_editor.model_view.items.image import AIEImageItem # Added AIEImageItem
from awesome_image_editor.mainwindow import MainWindow # Added MainWindow for spec

# For now, let's just test the slot logic if we can isolate it.
# If MainWindow is complex to instantiate, we might test a helper or a simplified version.

# Assuming we can get an instance of MainWindow or mock it appropriately
class MockMainWindowOld: # Simplified mock for the slot
    def __init__(self):
        self.zoom_status_label = Mock(spec=QLabel)
    
    def update_zoom_status(self, scale_factor: float):
        self.zoom_status_label.setText(f"Zoom: {scale_factor * 100:.1f}%")

def test_mainwindow_update_zoom_status():
    mw = MockMainWindowOld()
    mw.update_zoom_status(1.0)
    mw.zoom_status_label.setText.assert_called_once_with("Zoom: 100.0%")

    mw.update_zoom_status(0.753)
    mw.zoom_status_label.setText.assert_called_with("Zoom: 75.3%")
    
    mw.update_zoom_status(1.2345)
    mw.zoom_status_label.setText.assert_called_with("Zoom: 123.5%") # .1f rounding

# --- New Fixtures and Tests for Grayscale ---

@pytest.fixture
def main_window_mock():
    # Create a MagicMock instance that "looks like" a MainWindow
    # This allows methods and attributes to be dynamically created as they are accessed
    # or explicitly set up.
    mw = MagicMock(spec=MainWindow) 
    
    # Mock the _project attribute and its chain of calls
    mw._project = MagicMock()
    mw._project.get_graphics_scene = MagicMock()
    mw._project.get_graphics_scene().selectedItems = MagicMock()
    
    # If MainWindow's __init__ does more complex things that need mocking,
    # those would be added here. For apply_grayscale_filter, this should be enough.
    return mw

@pytest.fixture
def sample_aie_item_mock():
   item = MagicMock(spec=AIEImageItem)
   item.name = "TestItem"
   # Mock the .image attribute to be a QImage, as the tested method accesses it
   item.image = QImage(10, 10, QImage.Format.Format_ARGB32) 
   # Mock the .setImage method, as it's called by the filter
   item.setImage = Mock() 
   return item

# --- Grayscale Filter Slot Test ---
def test_apply_grayscale_filter_success(main_window_mock, sample_aie_item_mock):
    # main_window_mock is the fixture that provides a mocked MainWindow instance
    # sample_aie_item_mock is a fixture for a mocked AIEImageItem
    
    main_window_mock._project.get_graphics_scene().selectedItems.return_value = [sample_aie_item_mock]
    original_qimage = sample_aie_item_mock.image # Use the image from the mock
    
    # Mock the image processing function
    with patch('awesome_image_editor.mainwindow.apply_grayscale') as mock_process_func:
        mock_modified_qimage = QImage(10,10,QImage.Format.Format_ARGB32) # Dummy modified
        mock_process_func.return_value = mock_modified_qimage
        
        main_window_mock.apply_grayscale_filter()
        
        mock_process_func.assert_called_once_with(original_qimage)
        sample_aie_item_mock.setImage.assert_called_once_with(mock_modified_qimage)

def test_apply_grayscale_filter_no_selection(main_window_mock):
    main_window_mock._project.get_graphics_scene().selectedItems.return_value = []
    # Mock QMessageBox to check if it's called
    with patch('awesome_image_editor.mainwindow.QMessageBox.information') as mock_msg_box:
        main_window_mock.apply_grayscale_filter()
        mock_msg_box.assert_called_once()

def test_apply_grayscale_filter_multiple_selection(main_window_mock, sample_aie_item_mock):
    # Simulate multiple items selected
    main_window_mock._project.get_graphics_scene().selectedItems.return_value = [sample_aie_item_mock, MagicMock(spec=AIEImageItem)]
    with patch('awesome_image_editor.mainwindow.QMessageBox.information') as mock_msg_box:
        main_window_mock.apply_grayscale_filter()
        mock_msg_box.assert_called_once()
        # Check that the message box text indicates multiple selection
        args, _ = mock_msg_box.call_args
        assert "select only one" in args[1].lower()


def test_apply_grayscale_filter_not_image_item(main_window_mock):
    # Simulate a non-AIEImageItem selected
    non_image_item = MagicMock() # Not spec'd as AIEImageItem
    main_window_mock._project.get_graphics_scene().selectedItems.return_value = [non_image_item]
    with patch('awesome_image_editor.mainwindow.QMessageBox.information') as mock_msg_box:
        main_window_mock.apply_grayscale_filter()
        mock_msg_box.assert_called_once()
        args, _ = mock_msg_box.call_args
        assert "image layers" in args[1].lower()


def test_apply_grayscale_filter_null_original_image(main_window_mock, sample_aie_item_mock):
    sample_aie_item_mock.image = QImage() # Set item's image to be null
    main_window_mock._project.get_graphics_scene().selectedItems.return_value = [sample_aie_item_mock]
    with patch('awesome_image_editor.mainwindow.QMessageBox.warning') as mock_msg_box:
        main_window_mock.apply_grayscale_filter()
        mock_msg_box.assert_called_once()
        args, _ = mock_msg_box.call_args
        assert "valid image data" in args[1].lower()


def test_apply_grayscale_filter_processing_fails(main_window_mock, sample_aie_item_mock):
    main_window_mock._project.get_graphics_scene().selectedItems.return_value = [sample_aie_item_mock]
    original_qimage = sample_aie_item_mock.image
    
    with patch('awesome_image_editor.mainwindow.apply_grayscale') as mock_process_func, \
         patch('awesome_image_editor.mainwindow.QMessageBox.warning') as mock_msg_box:
        mock_process_func.return_value = QImage() # Simulate processing failure
        
        main_window_mock.apply_grayscale_filter()
        
        mock_process_func.assert_called_once_with(original_qimage)
        sample_aie_item_mock.setImage.assert_not_called()
        mock_msg_box.assert_called_once()
        args, _ = mock_msg_box.call_args
        assert "failed to apply" in args[1].lower()

# --- Sepia Filter Slot Test ---
def test_apply_sepia_filter_success(main_window_mock, sample_aie_item_mock):
    # main_window_mock and sample_aie_item_mock fixtures should be defined
    
    main_window_mock._project.get_graphics_scene().selectedItems.return_value = [sample_aie_item_mock]
    # Reset image on sample_aie_item_mock for this test to ensure it's not null from a previous test
    sample_aie_item_mock.image = QImage(10, 10, QImage.Format.Format_ARGB32)
    original_qimage = sample_aie_item_mock.image 
    
    with patch('awesome_image_editor.mainwindow.apply_sepia') as mock_process_func:
        mock_modified_qimage = QImage(10,10,QImage.Format.Format_ARGB32) # Dummy modified
        mock_process_func.return_value = mock_modified_qimage
        
        main_window_mock.apply_sepia_filter()
        
        mock_process_func.assert_called_once_with(original_qimage)
        sample_aie_item_mock.setImage.assert_called_once_with(mock_modified_qimage)

def test_apply_sepia_filter_no_selection(main_window_mock): # Assuming main_window_mock fixture exists
    main_window_mock._project.get_graphics_scene().selectedItems.return_value = []
    with patch('awesome_image_editor.mainwindow.QMessageBox.information') as mock_msg_box:
        main_window_mock.apply_sepia_filter()
        mock_msg_box.assert_called_once()
        
# (Validation for project, scene, multiple items, wrong item type in apply_sepia_filter
# are identical to apply_grayscale_filter. If those are tested generically for filter slots,
# these specific tests for no_selection might be redundant, but good for clarity here.)
# The other validation tests (multiple_selection, not_image_item, null_original_image, processing_fails)
# can be added for apply_sepia_filter similarly if desired for full coverage,
# but they would be very similar to the grayscale ones.
```
