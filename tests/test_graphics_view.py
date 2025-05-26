import pytest
from unittest.mock import Mock, patch, call

from PyQt6.QtCore import Qt, QPointF, QPoint, pyqtSignal
from PyQt6.QtGui import QWheelEvent, QMouseEvent, QTransform
from PyQt6.QtWidgets import QGraphicsView, QScrollBar # For type hinting and spec

from awesome_image_editor.model_view.graphics_view import AIEGraphicsView
# Mock QGraphicsScene for the view's constructor
class MockScene:
    pass

@pytest.fixture
def graphics_view(qtbot): # qtbot can be useful for signals
    scene = MockScene() 
    view = AIEGraphicsView(scene) # type: ignore
    # Mock scrollbars directly on the instance for testing pan
    view.horizontalScrollBar = Mock(return_value=Mock(spec=QScrollBar))
    view.verticalScrollBar = Mock(return_value=Mock(spec=QScrollBar))
    view.viewport = Mock(return_value=Mock()) # Mock viewport for setCursor
    return view

# --- Zoom Tests ---
def test_graphics_view_initial_zoom_signal(graphics_view):
    # Test that zoom_level_changed is emitted on init
    # This requires capturing the signal. We can mock the emit method of the signal.
    with patch.object(graphics_view.zoom_level_changed, 'emit') as mock_emit:
        # Re-init or call the specific method if it exists
        # If emit is directly in __init__, this test might need adjustment
        # For now, let's assume a method that can be called or was called.
        # The worker added emit_current_zoom_level(), let's call that.
        # Actually, the signal is emitted directly in __init__, so this fixture already triggered it.
        # We need to capture it during fixture creation or re-emit.
        # Let's re-emit manually for clarity in this test.
        graphics_view.emit_current_zoom_level() 
        # The first call was in __init__, the second is from emit_current_zoom_level()
        # We are testing the explicit call here.
        mock_emit.assert_called_with(1.0) # Initial scale is 1.0

def test_wheel_event_zoom_in_ctrl_pressed(graphics_view):
    initial_scale = graphics_view.transform().m11()
    # Mock the event
    pos = QPoint(50, 50)
    global_pos = QPoint(100,100) # Dummy global pos
    pixel_delta = QPoint(0,0) # Dummy pixel_delta
    angle_delta = QPoint(0, 120) # Positive Y for zoom in
    buttons = Qt.MouseButton.NoButton
    modifiers = Qt.KeyboardModifier.ControlModifier
    phase = Qt.ScrollPhase.ScrollBegin # Dummy phase
    inverted = False # Dummy inverted

    # For PyQt6.6+, source might be needed
    # event = QWheelEvent(pos, global_pos, pixel_delta, angle_delta, buttons, modifiers, phase, inverted, Qt.MouseEventSource.MouseEventSynthesizedBySystem)
    # For older PyQt6 versions, source might not be there:
    event = QWheelEvent(pos, global_pos, pixel_delta, angle_delta, buttons, modifiers, phase, inverted)


    # We need to let self.scale run to test the emitted value.
    # So, don't patch 'scale'. Instead, connect to the signal.
    mock_slot = Mock()
    graphics_view.zoom_level_changed.connect(mock_slot)
    
    graphics_view.wheelEvent(event) # Call actual method
    
    expected_new_scale = initial_scale * 1.15
    assert graphics_view.transform().m11() == pytest.approx(expected_new_scale)
    mock_slot.assert_called_with(pytest.approx(expected_new_scale))
    
    graphics_view.zoom_level_changed.disconnect(mock_slot)


def test_wheel_event_zoom_out_ctrl_pressed(graphics_view):
    # Set an initial scale > min so we can zoom out
    graphics_view.scale(2.0, 2.0) # Start at 200% zoom
    initial_scale = graphics_view.transform().m11()
    
    pos = QPoint(50,50); global_pos=QPoint(100,100); pixel_delta=QPoint(0,0)
    angle_delta = QPoint(0, -120) # Negative Y for zoom out
    buttons = Qt.MouseButton.NoButton; modifiers = Qt.KeyboardModifier.ControlModifier
    phase = Qt.ScrollPhase.ScrollBegin; inverted = False
    event = QWheelEvent(pos, global_pos, pixel_delta, angle_delta, buttons, modifiers, phase, inverted)

    mock_slot = Mock()
    graphics_view.zoom_level_changed.connect(mock_slot)

    graphics_view.wheelEvent(event)

    expected_new_scale = initial_scale * (1 / 1.15)
    assert graphics_view.transform().m11() == pytest.approx(expected_new_scale)
    mock_slot.assert_called_with(pytest.approx(expected_new_scale))

    graphics_view.zoom_level_changed.disconnect(mock_slot)


def test_wheel_event_zoom_respects_max_limit(graphics_view):
    # Set scale exactly to max_zoom_scale
    # To do this without triggering signals or being blocked by limits, we directly set transform
    max_scale_transform = QTransform().scale(graphics_view._max_zoom_scale, graphics_view._max_zoom_scale)
    graphics_view.setTransform(max_scale_transform)
    assert graphics_view.transform().m11() == pytest.approx(graphics_view._max_zoom_scale)

    pos = QPoint(50,50); global_pos=QPoint(100,100); pixel_delta=QPoint(0,0)
    angle_delta = QPoint(0, 120) # Zoom in
    buttons = Qt.MouseButton.NoButton; modifiers = Qt.KeyboardModifier.ControlModifier
    phase = Qt.ScrollPhase.ScrollBegin; inverted = False
    event = QWheelEvent(pos, global_pos, pixel_delta, angle_delta, buttons, modifiers, phase, inverted)
    
    mock_slot = Mock()
    graphics_view.zoom_level_changed.connect(mock_slot)

    # Store current transform before event
    transform_before_event = graphics_view.transform()
    
    graphics_view.wheelEvent(event) # Try to zoom in more
    
    # Assert that the transform hasn't changed
    assert graphics_view.transform() == transform_before_event
    # Assert that the signal was not emitted because no scaling happened
    mock_slot.assert_not_called()
    
    graphics_view.zoom_level_changed.disconnect(mock_slot)


def test_wheel_event_respects_min_limit(graphics_view):
    # Set scale exactly to min_zoom_scale
    min_scale_transform = QTransform().scale(graphics_view._min_zoom_scale, graphics_view._min_zoom_scale)
    graphics_view.setTransform(min_scale_transform)
    assert graphics_view.transform().m11() == pytest.approx(graphics_view._min_zoom_scale)

    pos = QPoint(50,50); global_pos=QPoint(100,100); pixel_delta=QPoint(0,0)
    angle_delta = QPoint(0, -120) # Zoom out
    buttons = Qt.MouseButton.NoButton; modifiers = Qt.KeyboardModifier.ControlModifier
    phase = Qt.ScrollPhase.ScrollBegin; inverted = False
    event = QWheelEvent(pos, global_pos, pixel_delta, angle_delta, buttons, modifiers, phase, inverted)

    mock_slot = Mock()
    graphics_view.zoom_level_changed.connect(mock_slot)
    
    transform_before_event = graphics_view.transform()
    graphics_view.wheelEvent(event) # Try to zoom out more
    
    assert graphics_view.transform() == transform_before_event
    mock_slot.assert_not_called()
    
    graphics_view.zoom_level_changed.disconnect(mock_slot)


def test_wheel_event_no_ctrl_passes_to_super(graphics_view):
    pos = QPoint(50,50); global_pos=QPoint(100,100); pixel_delta=QPoint(0,0)
    angle_delta = QPoint(0, 120)
    buttons = Qt.MouseButton.NoButton; modifiers = Qt.KeyboardModifier.NoModifier # No Ctrl
    phase = Qt.ScrollPhase.ScrollBegin; inverted = False
    event = QWheelEvent(pos, global_pos, pixel_delta, angle_delta, buttons, modifiers, phase, inverted)

    # For QGraphicsView, wheelEvent is a virtual protected method.
    # We need to patch it on the QGraphicsView class itself, or on super() if that's how it's called.
    # The implementation calls super().wheelEvent(event).
    # Patching QGraphicsView.wheelEvent directly is more robust for testing the call to super.
    with patch.object(QGraphicsView, 'wheelEvent') as mock_super_wheel_event:
        graphics_view.wheelEvent(event) # graphics_view is an instance of AIEGraphicsView
        mock_super_wheel_event.assert_called_once_with(event)

# --- Pan Tests ---
def test_middle_mouse_press_pan_init(graphics_view):
    pos = QPointF(30, 40)
    # Note: QMouseEvent.Type.MouseButtonPress is an enum value, not a position
    event = QMouseEvent(QMouseEvent.Type.MouseButtonPress, pos, Qt.MouseButton.MiddleButton, Qt.MouseButton.MiddleButton, Qt.KeyboardModifier.NoModifier)
    
    graphics_view.mousePressEvent(event)
    
    assert graphics_view._last_pan_screen_pos == pos
    graphics_view.viewport().setCursor.assert_called_once_with(Qt.CursorShape.ClosedHandCursor)

def test_middle_mouse_move_pan(graphics_view):
    # Initial press
    press_pos = QPointF(30, 40)
    graphics_view._last_pan_screen_pos = press_pos # Simulate press already happened

    # Move event
    move_pos = QPointF(50, 60)
    event = QMouseEvent(QMouseEvent.Type.MouseMove, move_pos, Qt.MouseButton.NoButton, Qt.MouseButton.MiddleButton, Qt.KeyboardModifier.NoModifier) # Middle button is in `buttons()`

    # Mock scrollbar behavior
    h_scrollbar_mock = graphics_view.horizontalScrollBar()
    v_scrollbar_mock = graphics_view.verticalScrollBar()
    h_scrollbar_mock.value.return_value = 100 # Current value before change
    v_scrollbar_mock.value.return_value = 100 # Current value before change

    graphics_view.mouseMoveEvent(event)

    # Delta is move_pos - press_pos = (20, 20)
    # Scrollbar value decreases by delta: 100 - 20 = 80
    h_scrollbar_mock.setValue.assert_called_once_with(100 - 20)
    v_scrollbar_mock.setValue.assert_called_once_with(100 - 20)
    assert graphics_view._last_pan_screen_pos == move_pos # Position updated

def test_middle_mouse_release_pan_end(graphics_view):
    graphics_view._last_pan_screen_pos = QPointF(30,40) # Simulate panning was active
    
    pos = QPointF(50,60) # Release position
    event = QMouseEvent(QMouseEvent.Type.MouseButtonRelease, pos, Qt.MouseButton.MiddleButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)

    graphics_view.mouseReleaseEvent(event)
    
    assert graphics_view._last_pan_screen_pos is None
    graphics_view.viewport().setCursor.assert_called_with(Qt.CursorShape.ArrowCursor)

# --- Rubber Band interaction (ensure it's not broken by pan changes) ---
def test_left_mouse_press_rubber_band_starts_if_no_item(graphics_view):
    graphics_view.itemAt = Mock(return_value=None) # No item under cursor
    graphics_view._rubberband = None # Ensure it's created

    pos = QPointF(10,10) # QMouseEvent expects QPointF for pos()
    event = QMouseEvent(QMouseEvent.Type.MouseButtonPress, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    
    with patch('awesome_image_editor.model_view.graphics_view.QRubberBand') as mock_rubber_band_constructor:
        rb_instance_mock = mock_rubber_band_constructor.return_value
        graphics_view.mousePressEvent(event)
        
        mock_rubber_band_constructor.assert_called_once_with(QRubberBand.Shape.Rectangle, graphics_view)
        rb_instance_mock.setGeometry.assert_called_once()
        rb_instance_mock.show.assert_called_once()
        assert graphics_view._rubberband_selection_origin == pos.toPoint() # Stored as QPoint
```
