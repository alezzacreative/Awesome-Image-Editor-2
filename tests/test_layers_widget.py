import pytest
from unittest.mock import Mock, patch, MagicMock # MagicMock for more complex mocks

# Assuming PyQt6 is used
from PyQt6.QtWidgets import QSlider, QDoubleSpinBox
from PyQt6.QtGui import QImage, QPainter # Added QPainter
from PyQt6.QtCore import QRectF, QPointF # Added QRectF, QPointF

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
    # Mock beginResetModel and endResetModel
    model.beginResetModel = Mock()
    model.endResetModel = Mock()
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
    
    # Mock the _update_opacity_controls_from_selection method as its direct testing is separate
    # and it can interfere with other tests if not managed.
    widget._update_opacity_controls_from_selection = MagicMock()


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
    item.setSelected = Mock()
    item.sceneBoundingRect = MagicMock(return_value=QRectF(0,0,10,10))
    item.pos = MagicMock(return_value=QPointF(0,0))
    return item

# --- Duplicate Layer Tests ---
def test_duplicate_layer_no_selection(layers_widget):
    layers_widget._model.scene().selectedItems.return_value = []
    layers_widget.duplicate_selected_layer()
    # Assert that addItem was not called, or a log/print was made
    layers_widget._model.scene().addItem.assert_not_called()
    layers_widget._update_opacity_controls_from_selection.assert_called_once()


def test_duplicate_layer_single_item(layers_widget, sample_image_item):
    sample_image_item.name = "Original"
    sample_image_item.setOpacity(0.7) # Original item has some opacity
    sample_image_item.setZValue(1.0)
    # sample_image_item.pos = Mock(return_value=Mock(x=10, y=10)) # Mock position
    sample_image_item.pos.return_value = QPointF(10,10)


    layers_widget._model.scene().selectedItems.return_value = [sample_image_item]
    
    # Mock AIEImageItem constructor to capture its arguments or return a new mock
    # Assign the mock for the new item to a variable that can be configured
    created_item_mock = MagicMock(spec=AIEImageItem)
    created_item_mock.image = QImage(10,10, QImage.Format.Format_ARGB32_Premultiplied) # Give it an image
    created_item_mock.setSelected = Mock() # Mock setSelected on the new item


    with patch('awesome_image_editor.widgets.layers.AIEImageItem', return_value=created_item_mock) as mock_aie_constructor:
        layers_widget.duplicate_selected_layer()

        mock_aie_constructor.assert_called_once()
        args, kwargs = mock_aie_constructor.call_args
        assert isinstance(args[0], QImage) # Copied image
        assert args[1] == "Original copy"  # New name

        created_item_mock.setPos.assert_called_with(sample_image_item.pos())
        created_item_mock.setVisible.assert_called_with(sample_image_item.isVisible())
        created_item_mock.setOpacity.assert_called_with(0.7) # Opacity copied
        created_item_mock.setZValue.assert_called_with(1.1) # Z-value incremented

        layers_widget._model.scene().addItem.assert_called_once_with(created_item_mock)
        layers_widget._model.scene().clearSelection.assert_called_once()
        created_item_mock.setSelected.assert_called_once_with(True)
        layers_widget._update_opacity_controls_from_selection.assert_called_once()


# --- Create Layer Mask Tests ---
def test_create_mask_no_selection(layers_widget):
    # layers_widget._model.scene().selectedItems.return_value = [] # This would be caught by _get_selected_image_item
    with patch.object(layers_widget, '_get_selected_image_item', return_value=None):
        layers_widget.create_layer_mask_for_selected_layer()
    # No item.set_mask should be called. We need a way to get the item to check.
    # This test primarily ensures no errors and early exit.
    # Check that AIEImageItem's set_mask was not called on any instance if possible,
    # or that no new image was created for mask. For now, just ensure no crash.

def test_create_mask_for_selected_item(layers_widget, sample_image_item):
    sample_image_item.has_mask.return_value = False # Ensure it doesn't have a mask yet
    # layers_widget._model.scene().selectedItems.return_value = [sample_image_item]

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
    # layers_widget._model.scene().selectedItems.return_value = [sample_image_item]
    
    # Patch _get_selected_image_item to return our sample_image_item
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget.create_layer_mask_for_selected_layer()
    sample_image_item.set_mask.assert_not_called()


# --- Opacity Controls Logic ---
def test_update_opacity_controls_no_selection(layers_widget):
    # layers_widget.list_view.selectedIndexes.return_value = [] # Simulate no selection in TreeView
    # Unmock the specific method for this test if it was globally mocked in fixture
    layers_widget._update_opacity_controls_from_selection = LayersWidget._update_opacity_controls_from_selection.__get__(layers_widget)


    with patch.object(layers_widget, '_get_selected_image_item', return_value=None):
      layers_widget._update_opacity_controls_from_selection()

    layers_widget.opacity_slider.setEnabled.assert_called_with(False)
    layers_widget.opacity_spinbox.setEnabled.assert_called_with(False)
    layers_widget.opacity_slider.setValue.assert_called_with(100)
    layers_widget.opacity_spinbox.setValue.assert_called_with(1.0)


def test_update_opacity_controls_with_selection(layers_widget, sample_image_item):
    layers_widget._update_opacity_controls_from_selection = LayersWidget._update_opacity_controls_from_selection.__get__(layers_widget)
    sample_image_item.opacity.return_value = 0.65 # sample_image_item.opacity is already a mock wrapping the real method
    
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget._update_opacity_controls_from_selection()

    layers_widget.opacity_slider.setEnabled.assert_called_with(True)
    layers_widget.opacity_spinbox.setEnabled.assert_called_with(True)
    
    layers_widget.opacity_slider.setValue.assert_called_with(65) # 0.65 * 100
    layers_widget.opacity_spinbox.setValue.assert_called_with(0.65)


def test_on_opacity_slider_changed(layers_widget, sample_image_item):
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget._on_opacity_slider_changed(75) # Simulate slider moved to 75

    sample_image_item.setOpacity.assert_called_with(0.75)
    layers_widget.opacity_spinbox.setValue.assert_called_with(0.75)


def test_on_opacity_spinbox_changed(layers_widget, sample_image_item):
    with patch.object(layers_widget, '_get_selected_image_item', return_value=sample_image_item):
        layers_widget._on_opacity_spinbox_changed(0.33) # Simulate spinbox changed

    sample_image_item.setOpacity.assert_called_with(0.33)
    layers_widget.opacity_slider.setValue.assert_called_with(33)

# --- Merge Down Tests ---

@pytest.fixture
def top_item(sample_image_item): # Build upon sample_image_item for common mocks
    item = AIEImageItem(QImage(10, 10, QImage.Format.Format_ARGB32_Premultiplied), "TopLayer")
    item.setZValue(2.0)
    item.setOpacity(0.8) # Real opacity
    item.setVisible(True)
    item.setPos(QPointF(0, 0))
    item.sceneBoundingRect = MagicMock(return_value=QRectF(0,0,10,10))
    item.update = Mock()
    item.setSelected = Mock()
    # Ensure 'image' attribute is the actual QImage for painter
    item.image = QImage(10, 10, QImage.Format.Format_ARGB32_Premultiplied) 
    return item

@pytest.fixture
def bottom_item(sample_image_item): # Build upon sample_image_item for common mocks
    item = AIEImageItem(QImage(10, 10, QImage.Format.Format_ARGB32_Premultiplied), "BottomLayer")
    item.setZValue(1.0) # Lower Z-value
    item.setOpacity(0.6) # Real opacity
    item.setVisible(True)
    item.setPos(QPointF(5, 5)) # Slightly offset
    item.sceneBoundingRect = MagicMock(return_value=QRectF(5,5,10,10))
    item.update = Mock()
    item.setSelected = Mock() # Though not strictly needed for bottom item
    # Ensure 'image' attribute is the actual QImage for painter
    item.image = QImage(10, 10, QImage.Format.Format_ARGB32_Premultiplied)
    return item

def test_merge_down_no_selection(layers_widget):
    layers_widget._get_selected_image_item = MagicMock(return_value=None) # Mock helper
    layers_widget.merge_down_selected_layer()
    layers_widget._model.scene().addItem.assert_not_called() # No new item should be added
    layers_widget._model.beginResetModel.assert_not_called() # Model changes not initiated


def test_merge_down_no_layer_below(layers_widget, top_item):
    layers_widget._get_selected_image_item = MagicMock(return_value=top_item)
    # Scene only contains the top_item or items with higher Z value
    layers_widget._model.scene().items.return_value = [top_item] 
    
    layers_widget.merge_down_selected_layer()
    layers_widget._model.scene().addItem.assert_not_called()
    layers_widget._model.beginResetModel.assert_not_called()

def test_merge_down_successful(layers_widget, top_item, bottom_item):
    layers_widget._get_selected_image_item = MagicMock(return_value=top_item)
    layers_widget._model.scene().items.return_value = [top_item, bottom_item]

    created_merged_item_mock = MagicMock(spec=AIEImageItem)
    created_merged_item_mock.image = QImage(15,15, QImage.Format.Format_ARGB32_Premultiplied) 
    created_merged_item_mock.setSelected = Mock() 
    
    with patch('awesome_image_editor.widgets.layers.AIEImageItem', return_value=created_merged_item_mock) as mock_constructor, \
         patch('awesome_image_editor.widgets.layers.QPainter') as mock_qpainter_constructor:
        
        mock_painter_instance = mock_qpainter_constructor.return_value

        layers_widget.merge_down_selected_layer()

        mock_constructor.assert_called_once()
        args, _ = mock_constructor.call_args
        merged_qimage_arg = args[0]
        assert isinstance(merged_qimage_arg, QImage)
        assert merged_qimage_arg.size().width() == 15
        assert merged_qimage_arg.size().height() == 15
        assert args[1] == "BottomLayer (merged)"

        mock_qpainter_constructor.assert_called_once_with(merged_qimage_arg)
        draw_calls = [call_args for name, call_args, _ in mock_painter_instance.mock_calls if name == 'drawImage']

        assert len(draw_calls) == 2
        # First drawImage call (bottom_item.image at its relative pos QPointF(5,5))
        assert draw_calls[0][0] == QPointF(5.0, 5.0)
        assert draw_calls[0][1] == bottom_item.image
        # Second drawImage call (top_item.image at its relative pos QPointF(0,0))
        assert draw_calls[1][0] == QPointF(0.0, 0.0)
        assert draw_calls[1][1] == top_item.image
        
        opacity_calls = [call_args for name, call_args, _ in mock_painter_instance.mock_calls if name == 'setOpacity']
        assert opacity_calls.count((bottom_item.opacity(),)) >= 1
        assert opacity_calls.count((top_item.opacity(),)) >= 1
        assert opacity_calls.count((1.0,)) >= 2

        scene = layers_widget._model.scene()
        scene.removeItem.assert_any_call(top_item)
        scene.removeItem.assert_any_call(bottom_item)
        scene.addItem.assert_called_once_with(created_merged_item_mock)
        
        layers_widget._model.beginResetModel.assert_called_once()
        layers_widget._model.endResetModel.assert_called_once()

        created_merged_item_mock.setPos.assert_called_once_with(QPointF(0,0))
        created_merged_item_mock.setZValue.assert_called_once_with(bottom_item.zValue())
        created_merged_item_mock.setVisible.assert_called_once_with(top_item.isVisible() and bottom_item.isVisible())
        created_merged_item_mock.setOpacity.assert_called_once_with(1.0)

        scene.clearSelection.assert_called_once()
        created_merged_item_mock.setSelected.assert_called_once_with(True)
        layers_widget._update_opacity_controls_from_selection.assert_called_once()


def test_merge_down_z_value_ordering(layers_widget, top_item, bottom_item):
    even_lower_item = AIEImageItem(QImage(5,5, QImage.Format.Format_ARGB32_Premultiplied), "EvenLower")
    even_lower_item.setZValue(0.5) 
    even_lower_item.sceneBoundingRect = MagicMock(return_value=QRectF(0,0,5,5))
    even_lower_item.image = QImage(5,5, QImage.Format.Format_ARGB32_Premultiplied)


    layers_widget._get_selected_image_item = MagicMock(return_value=top_item) 
    layers_widget._model.scene().items.return_value = [top_item, bottom_item, even_lower_item]

    created_merged_item_mock = MagicMock(spec=AIEImageItem) # Mock for the new item
    created_merged_item_mock.image = QImage(15,15, QImage.Format.Format_ARGB32_Premultiplied)
    created_merged_item_mock.setSelected = Mock()

    with patch('awesome_image_editor.widgets.layers.AIEImageItem', return_value=created_merged_item_mock) as mock_constructor, \
         patch('awesome_image_editor.widgets.layers.QPainter'): 
        
        layers_widget.merge_down_selected_layer()
        
        mock_constructor.assert_called_once()
        args, _ = mock_constructor.call_args
        assert args[1] == "BottomLayer (merged)" 
        
        created_merged_item_mock.setZValue.assert_called_with(bottom_item.zValue())
        layers_widget._update_opacity_controls_from_selection.assert_called_once()
```
