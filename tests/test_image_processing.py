import pytest
from PyQt6.QtGui import QImage, QColor

# Adjust import path as necessary
from awesome_image_editor.image_processing import apply_brightness_contrast, clamp

# --- Clamp Tests (Optional but good practice) ---
def test_clamp():
    assert clamp(100, 0, 255) == 100
    assert clamp(-10, 0, 255) == 0
    assert clamp(300, 0, 255) == 255
    assert clamp(50, 0, 100) == 50

# --- Apply Brightness/Contrast Tests ---
@pytest.fixture
def sample_image_bc(): # bc for brightness/contrast
    # Create a 1x1 image with a mid-gray color and some alpha
    img = QImage(1, 1, QImage.Format.Format_ARGB32_Premultiplied)
    img.setPixelColor(0, 0, QColor(128, 128, 128, 200)) # Mid-gray, alpha 200
    return img

def test_apply_bc_no_change(sample_image_bc):
    original_pixel = sample_image_bc.pixelColor(0,0)
    modified_image = apply_brightness_contrast(sample_image_bc, 0, 0) # No brightness, no contrast
    
    assert not modified_image.isNull()
    assert modified_image.size() == sample_image_bc.size()
    
    new_pixel = modified_image.pixelColor(0, 0)
    # With brightness_offset = 0 and contrast_factor_adj = 1.0, color should be very close
    # Allow for minor precision differences if any intermediate float calcs occur
    assert new_pixel.red() == pytest.approx(original_pixel.red(), abs=1)
    assert new_pixel.green() == pytest.approx(original_pixel.green(), abs=1)
    assert new_pixel.blue() == pytest.approx(original_pixel.blue(), abs=1)
    assert new_pixel.alpha() == original_pixel.alpha() # Alpha must be preserved

def test_apply_bc_brightness_increase(sample_image_bc):
    brightness_val = 50 # Expected offset for 128 base is (50/100)*128 = 64
                       # So 128 + 64 = 192
    modified_image = apply_brightness_contrast(sample_image_bc, brightness_val, 0)
    new_pixel = modified_image.pixelColor(0, 0)

    expected_val = clamp(128 + int((brightness_val / 100.0) * 128))
    assert new_pixel.red() == expected_val
    assert new_pixel.green() == expected_val
    assert new_pixel.blue() == expected_val
    assert new_pixel.alpha() == 200

def test_apply_bc_brightness_decrease_clamp(sample_image_bc):
    brightness_val = -100 # Expected offset = -128. 128 - 128 = 0
    modified_image = apply_brightness_contrast(sample_image_bc, brightness_val, 0)
    new_pixel = modified_image.pixelColor(0, 0)
    
    assert new_pixel.red() == 0
    assert new_pixel.green() == 0
    assert new_pixel.blue() == 0
    assert new_pixel.alpha() == 200

def test_apply_bc_contrast_increase(sample_image_bc):
    # Original mid-gray (128) should not change with contrast only
    # Let's use a different color: QColor(100, 150, 200, 255)
    img = QImage(1, 1, QImage.Format.Format_ARGB32_Premultiplied)
    img.setPixelColor(0, 0, QColor(100, 150, 200, 255))
    
    contrast_val = 50 # factor_adj = 1.0 + (50/100.0) = 1.5
    # r: 128 + 1.5 * (100-128) = 128 + 1.5 * (-28) = 128 - 42 = 86
    # g: 128 + 1.5 * (150-128) = 128 + 1.5 * (22)  = 128 + 33 = 161
    # b: 128 + 1.5 * (200-128) = 128 + 1.5 * (72)  = 128 + 108 = 236
    
    modified_image = apply_brightness_contrast(img, 0, contrast_val)
    new_pixel = modified_image.pixelColor(0, 0)

    assert new_pixel.red() == 86
    assert new_pixel.green() == 161
    assert new_pixel.blue() == 236
    assert new_pixel.alpha() == 255

def test_apply_bc_contrast_decrease(sample_image_bc):
    img = QImage(1, 1, QImage.Format.Format_ARGB32_Premultiplied)
    img.setPixelColor(0, 0, QColor(100, 150, 200, 255))

    contrast_val = -50 # factor_adj = (100.0 - 50) / 100.0 = 0.5
    # r: 128 + 0.5 * (100-128) = 128 + 0.5 * (-28) = 128 - 14 = 114
    # g: 128 + 0.5 * (150-128) = 128 + 0.5 * (22)  = 128 + 11 = 139
    # b: 128 + 0.5 * (200-128) = 128 + 0.5 * (72)  = 128 + 36 = 164

    modified_image = apply_brightness_contrast(img, 0, contrast_val)
    new_pixel = modified_image.pixelColor(0, 0)

    assert new_pixel.red() == 114
    assert new_pixel.green() == 139
    assert new_pixel.blue() == 164
    assert new_pixel.alpha() == 255

def test_apply_bc_null_image():
    null_img = QImage()
    modified_image = apply_brightness_contrast(null_img, 20, 20)
    assert modified_image.isNull()

def test_apply_bc_image_format_conversion(sample_image_bc):
    # Test with a format that needs conversion, e.g. Format_RGB32
    original_rgb32 = sample_image_bc.convertToFormat(QImage.Format.Format_RGB32)
    # Ensure alpha is opaque for RGB32 for predictable comparison after conversion in func
    original_rgb32.setPixelColor(0,0, QColor(128,128,128,255))


    modified_image = apply_brightness_contrast(original_rgb32, 0, 0)
    assert not modified_image.isNull()
    # The function converts to ARGB32_Premultiplied
    assert modified_image.format() == QImage.Format.Format_ARGB32_Premultiplied
    new_pixel = modified_image.pixelColor(0,0)
    assert new_pixel.red() == 128
    assert new_pixel.alpha() == 255 # Alpha should be preserved from converted image
```
