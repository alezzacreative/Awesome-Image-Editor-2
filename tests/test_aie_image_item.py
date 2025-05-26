import pytest
from unittest.mock import Mock, call # For checking if self.update() is called

from PyQt6.QtGui import QImage, QPainter, QColor # QColor for filling mask for testing
from PyQt6.QtCore import QSize

# Adjust the import path based on your project structure.
# This assumes 'awesome_image_editor' is a top-level package.
from awesome_image_editor.model_view.items.image import AIEImageItem

@pytest.fixture
def sample_image():
    # Creates a default 10x10 QImage for tests
    return QImage(QSize(10, 10), QImage.Format.Format_ARGB32_Premultiplied)

@pytest.fixture
def image_item(sample_image):
    # Creates an AIEImageItem with a sample image and name
    return AIEImageItem(sample_image, "Test Layer")

def test_aieimageitem_initialization(image_item, sample_image):
    assert image_item.name == "Test Layer"
    assert image_item.image == sample_image
    assert image_item._opacity == 1.0  # Check initial opacity
    assert image_item.mask is None     # Check initial mask state
    assert image_item.flags() & AIEImageItem.GraphicsItemFlag.ItemIsSelectable # Corrected QImageItem to AIEImageItem
    assert image_item.flags() & AIEImageItem.GraphicsItemFlag.ItemIsMovable   # Corrected QImageItem to AIEImageItem

# --- Opacity Tests ---
def test_set_opacity_normal(image_item):
    image_item.update = Mock() # Mock the update method
    image_item.setOpacity(0.5)
    assert image_item.opacity() == 0.5
    image_item.update.assert_called_once()

def test_set_opacity_clamp_low(image_item):
    image_item.update = Mock()
    image_item.setOpacity(-0.5)
    assert image_item.opacity() == 0.0
    image_item.update.assert_called_once()

def test_set_opacity_clamp_high(image_item):
    image_item.update = Mock()
    image_item.setOpacity(1.5)
    assert image_item.opacity() == 1.0
    image_item.update.assert_called_once()

# --- Mask Tests ---
def test_set_mask(image_item, sample_image):
    image_item.update = Mock()
    mask_img = QImage(sample_image.size(), QImage.Format.Format_Grayscale8)
    mask_img.fill(QColor("gray")) # Fill with a distinct color for testing

    image_item.set_mask(mask_img)
    assert image_item.has_mask() is True
    assert image_item.get_mask() == mask_img
    image_item.update.assert_called_once()

def test_get_mask_no_mask(image_item):
    assert image_item.has_mask() is False
    assert image_item.get_mask() is None

# --- Paint Method Tests ---
def test_paint_opacity_application(image_item):
    painter = Mock(spec=QPainter)
    painter.opacity = Mock(return_value=0.75) # Mock initial painter opacity

    image_item.setOpacity(0.5) # Set item opacity

    # Call paint (option and widget are not strictly needed for this test if not used by opacity logic)
    image_item.paint(painter, None, None) 

    # Check that painter's opacity was set for the item and then restored
    expected_calls = [
        call.setOpacity(0.5), # Set to item's opacity
        call.drawImage(image_item.boundingRect(), image_item.image),
        call.setOpacity(0.75)  # Restored to painter's original opacity
    ]
    # We need to check a sub-sequence of calls on the mock object,
    # as other calls might occur (e.g. save/restore state)
    
    # Simple check for calls in order (might need refinement based on exact painter usage)
    assert painter.method_calls.count(expected_calls[0]) == 1
    assert painter.method_calls.count(expected_calls[1]) > 0 # drawImage should be called
    assert painter.method_calls.count(expected_calls[2]) == 1
    
    # Ensure the calls happened in the expected sequence (simplified check)
    # A more robust check would involve inspecting the order of calls in painter.method_calls
    try:
        idx_set_item_opacity = painter.method_calls.index(expected_calls[0])
        idx_draw_image = painter.method_calls.index(expected_calls[1])
        idx_restore_opacity = painter.method_calls.index(expected_calls[2])
        assert idx_set_item_opacity < idx_draw_image < idx_restore_opacity
    except ValueError:
        pytest.fail(f"Expected painter calls not found in the correct order. Calls: {painter.method_calls}")

# (Future: Add test for paint with mask when mask rendering is implemented)
