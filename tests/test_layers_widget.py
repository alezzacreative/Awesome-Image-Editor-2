import pytest
from unittest.mock import Mock, patch, MagicMock # MagicMock for more complex mocks

# Assuming PyQt6 is used
from PyQt6.QtWidgets import QSlider, QDoubleSpinBox
from PyQt6.QtGui import QImage

# Adjust imports based on your project structure
from awesome_image_editor.widgets.layers import LayersWidget
from awesome_image_editor.model_view.items.image import AIEImageItem
# from awesome_image_editor.model_view.tree_model import TreeModel # If needed for type hinting
# from awesome_image_editor.model_view.graphics_scene import AIEGraphicsScene # If needed

# It's often useful to have a fixture for the widget itself,
# though it might need a mock model passed to its constructor.

@pytest.fixture
def mock_model():
    model = MagicMock() # Using MagicMock for more flexibility
    model.scene = MagicMock(return_value=MagicMock()) # Mock the scene object too
    return model

@pytest.fixture
def layers_widget(mock_model, qtbot): # qtbot might be needed if UI elements are interacted with
    # Temporarily patch out UI elements not directly related to the logic being tested, if necessary
    # For example, if TreeView instantiation is complex:
    with patch('awesome_image_editor.widgets.layers.TreeView', Mock()):
        widget = LayersWidget(model=mock_model)
    # qtbot.addWidget(widget) # If you need to interact with it as a live widget
    
    # Mock UI elements directly on the instance for testing logic
    widget.opacity_slider = MagicMock(spec=QSlider)
    widget.opacity_spinbox = MagicMock(spec=QDoubleSpinBox)
    widget.list_view = MagicMock() # Mock the list_view for selectedIndexes

    return widget

@pytest.fixture
def sample_image_item():
    img = QImage(10, 10, QImage.Format.Format_ARGB32_Premultiplied)
    item = AIEImageItem(img, "SampleLayer")
    item.update = Mock() # Mock update to prevent actual GUI updates
    item.setOpacity = Mock(wraps=item.setOpacity) # Wrap to still call original but allow spying
    item.opacity = Mock(wraps=item.opacity)
    item.set_mask = Mock(wraps=item.set_mask)
    item.has_mask = Mock(wraps=item.has_mask)
    return item

# --- Duplicate Layer Tests ---
def test_duplicate_layer_no_selection(layers_widget):
    layers_widget._model.scene().selectedItems.return_value = []
    layers_widget.duplicate_selected_layer()
    # Assert that addItem was not called, or a log/print was made
    layers_widget._model.scene().addItem.assert_not_called()

def test_duplicate_layer_single_item(layers_widget, sample_image_item):
    sample_image_item.name = "Original"
    sample_image_item.setOpacity(0.7) # Original item has some opacity
    sample_image_item.setZValue(1.0)
    sample_image_item.pos = Mock(return_value=Mock(x=10, y=10)) # Mock position

    layers_widget._model.scene().selectedItems.return_value = [sample_image_item]
    
    # Mock AIEImageItem constructor to capture its arguments or return a new mock
    with patch('awesome_image_editor.widgets.layers.AIEImageItem', return_value=MagicMock(spec=AIEImageItem)) as mock_aie_constructor:
        new_item_mock = mock_aie_constructor.return_value
        new_item_mock.image = QImage(10,10, QImage.Format.Format_ARGB32_Premultiplied) # Give it an image

        layers_widget.duplicate_selected_layer()

        mock_aie_constructor.assert_called_once()
        args, kwargs = mock_aie_constructor.call_args
        assert isinstance(args[0], QImage) # Copied image
        assert args[1] == "Original copy"  # New name

        new_item_mock.setPos.assert_called_with(sample_image_item.pos())
        new_item_mock.setVisible.assert_called_with(sample_image_item.isVisible())
        new_item_mock.setOpacity.assert_called_with(0.7) # Opacity copied
        new_item_mock.setZValue.assert_called_with(1.1) # Z-value incremented

        layers_widget._model.scene().addItem.assert_called_once_with(new_item_mock)

# --- Create Layer Mask Tests ---
def test_create_mask_no_selection(layers_widget):
    layers_widget._model.scene().selectedItems.return_value = []
    layers_widget.create_layer_mask_for_selected_layer()
    # No item.set_mask should be called. We need a way to get the item to check.
    # This test primarily ensures no errors and early exit.

def test_create_mask_for_selected_item(layers_widget, sample_image_item):
    sample_image_item.has_mask.return_value = False # Ensure it doesn't have a mask yet
    layers_widget._model.scene().selectedItems.return_value = [sample_image_item]

    # Patch _get_selected_image_item to return our sample_image_item
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget.create_layer_mask_for_selected_layer()

    sample_image_item.set_mask.assert_called_once()
    args, _ = sample_image_item.set_mask.call_args
    mask_arg = args[0]
    assert isinstance(mask_arg, QImage)
    assert mask_arg.size() == sample_image_item.image.size()
    # assert mask_arg.format() == QImage.Format.Format_Grayscale8 # This is checked by worker

def test_create_mask_already_exists(layers_widget, sample_image_item):
    sample_image_item.has_mask.return_value = True # Item already has a mask
    layers_widget._model.scene().selectedItems.return_value = [sample_image_item]
    
    # Patch _get_selected_image_item to return our sample_image_item
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget.create_layer_mask_for_selected_layer()
    sample_image_item.set_mask.assert_not_called()


# --- Opacity Controls Logic ---
def test_update_opacity_controls_no_selection(layers_widget):
    layers_widget.list_view.selectedIndexes.return_value = [] # Simulate no selection in TreeView
    # Or use the helper:
    with patch.object(layers_widget, '_get_selected_image_item', return_value=None):
      layers_widget._update_opacity_controls_from_selection()

    layers_widget.opacity_slider.setEnabled.assert_called_with(False)
    layers_widget.opacity_spinbox.setEnabled.assert_called_with(False)
    layers_widget.opacity_slider.setValue.assert_called_with(100)
    layers_widget.opacity_spinbox.setValue.assert_called_with(1.0)


def test_update_opacity_controls_with_selection(layers_widget, sample_image_item):
    sample_image_item.opacity.return_value = 0.65
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget._update_opacity_controls_from_selection()

    layers_widget.opacity_slider.setEnabled.assert_called_with(True)
    layers_widget.opacity_spinbox.setEnabled.assert_called_with(True)
    
    # Check that setValue was called correctly, considering signal blocking
    # The actual call to setValue is what matters.
    layers_widget.opacity_slider.setValue.assert_called_with(65) # 0.65 * 100
    layers_widget.opacity_spinbox.setValue.assert_called_with(0.65)


def test_on_opacity_slider_changed(layers_widget, sample_image_item):
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget._on_opacity_slider_changed(75) # Simulate slider moved to 75

    sample_image_item.setOpacity.assert_called_with(0.75)
    layers_widget.opacity_spinbox.setValue.assert_called_with(0.75)
    # layers_widget._model.scene().update.assert_called_once() # or item.update()


def test_on_opacity_spinbox_changed(layers_widget, sample_image_item):
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget._on_opacity_spinbox_changed(0.33) # Simulate spinbox changed

    sample_image_item.setOpacity.assert_called_with(0.33)
    layers_widget.opacity_slider.setValue.assert_called_with(33)
    # layers_widget._model.scene().update.assert_called_once()

# TODO: Test signal blocking logic in opacity updates if critical, though it's hard
# to directly test if signals were blocked without more intricate qtbot usage.
# Focus on the outcome (correct values set, methods called).
