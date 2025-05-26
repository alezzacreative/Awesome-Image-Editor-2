import pytest
from PyQt6.QtGui import QImage, QColor

# Adjust import path as necessary
from awesome_image_editor.image_processing import apply_brightness_contrast, clamp, apply_grayscale, apply_sepia # Added apply_sepia

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

# --- Apply Grayscale Tests ---
@pytest.fixture
def sample_color_image_gs(): # gs for grayscale
    img = QImage(2, 1, QImage.Format.Format_ARGB32_Premultiplied) # 2 pixels
    img.setPixelColor(0, 0, QColor(100, 150, 200, 255)) # Color pixel
    img.setPixelColor(1, 0, QColor(50, 70, 90, 128))   # Another color pixel with different alpha
    return img

def test_apply_grayscale_conversion(sample_color_image_gs):
    modified_image = apply_grayscale(sample_color_image_gs)
    assert not modified_image.isNull()
    assert modified_image.size() == sample_color_image_gs.size()
    assert modified_image.format() == QImage.Format.Format_ARGB32_Premultiplied

    # Pixel 1: QColor(100, 150, 200, 255)
    # Expected gray: int(0.299*100 + 0.587*150 + 0.114*200)
    # gray1 = int(29.9 + 88.05 + 22.8) = int(140.75) = 141 (standard rounding for int())
    
    px1_color = modified_image.pixelColor(0, 0)
    expected_gray1 = int(0.299 * 100 + 0.587 * 150 + 0.114 * 200) 
    assert px1_color.red() == expected_gray1
    assert px1_color.green() == expected_gray1
    assert px1_color.blue() == expected_gray1
    assert px1_color.alpha() == 255 # Alpha preserved

    # Pixel 2: QColor(50, 70, 90, 128)
    # Expected gray: int(0.299*50 + 0.587*70 + 0.114*90)
    # gray2 = int(14.95 + 41.09 + 10.26) = int(66.3) = 66
    px2_color = modified_image.pixelColor(1, 0)
    expected_gray2 = int(0.299 * 50 + 0.587 * 70 + 0.114 * 90) 
    assert px2_color.red() == expected_gray2
    assert px2_color.green() == expected_gray2
    assert px2_color.blue() == expected_gray2
    assert px2_color.alpha() == 128 # Alpha preserved

def test_apply_grayscale_already_gray(sample_image_bc): # Uses mid-gray image from BC tests
    # sample_image_bc is QColor(128, 128, 128, 200)
    modified_image = apply_grayscale(sample_image_bc)
    assert not modified_image.isNull()
    
    px_color = modified_image.pixelColor(0,0)
    # Expected gray: int(0.299*128 + 0.587*128 + 0.114*128) = int(1.0 * 128) = 128
    # Or more simply, if r=g=b, gray should be r.
    assert px_color.red() == 128
    assert px_color.green() == 128
    assert px_color.blue() == 128
    assert px_color.alpha() == 200

def test_apply_grayscale_null_image():
    null_img = QImage()
    modified_image = apply_grayscale(null_img)
    assert modified_image.isNull()

# --- Apply Sepia Tests ---
# sample_color_image_gs can be reused or a new one defined if different colors are better.
# Let's use the one from grayscale tests: QColor(100, 150, 200, 255) for pixel (0,0)
# and QColor(50, 70, 90, 128) for pixel (1,0)

def test_apply_sepia_conversion(sample_color_image_gs): # Reuses fixture from grayscale tests
    modified_image = apply_sepia(sample_color_image_gs)
    assert not modified_image.isNull()
    assert modified_image.size() == sample_color_image_gs.size()
    assert modified_image.format() == QImage.Format.Format_ARGB32_Premultiplied

    # Pixel 1: QColor(100, 150, 200, 255) (R=100, G=150, B=200)
    # Expected sepia:
    # new_r = (100 * 0.393) + (150 * 0.769) + (200 * 0.189) = 39.3 + 115.35 + 37.8 = 192.45 -> 192
    # new_g = (100 * 0.349) + (150 * 0.686) + (200 * 0.168) = 34.9 + 102.9 + 33.6 = 171.4 -> 171
    # new_b = (100 * 0.272) + (150 * 0.534) + (200 * 0.131) = 27.2 + 80.1 + 26.2 = 133.5 -> 133
    
    px1_color = modified_image.pixelColor(0, 0)
    assert px1_color.red() == 192
    assert px1_color.green() == 171
    assert px1_color.blue() == 133
    assert px1_color.alpha() == 255 # Alpha preserved

    # Pixel 2: QColor(50, 70, 90, 128) (R=50, G=70, B=90)
    # Expected sepia:
    # new_r = (50 * 0.393) + (70 * 0.769) + (90 * 0.189) = 19.65 + 53.83 + 17.01 = 90.49 -> 90
    # new_g = (50 * 0.349) + (70 * 0.686) + (90 * 0.168) = 17.45 + 48.02 + 15.12 = 80.59 -> 81
    # new_b = (50 * 0.272) + (70 * 0.534) + (90 * 0.131) = 13.6 + 37.38 + 11.79 = 62.77 -> 63

    px2_color = modified_image.pixelColor(1, 0)
    assert px2_color.red() == 90
    assert px2_color.green() == 81 # Corrected based on sum then int
    assert px2_color.blue() == 63 # Corrected based on sum then int
    assert px2_color.alpha() == 128 # Alpha preserved

def test_apply_sepia_max_values_clamp():
    # Test with values that would exceed 255 after sepia calculation
    # e.g., R=255, G=255, B=255 (white)
    # new_r = (255 * 0.393) + (255 * 0.769) + (255 * 0.189) = 255 * (0.393+0.769+0.189) = 255 * 1.351 = 344.505 -> 255 (clamped)
    # new_g = (255 * 0.349) + (255 * 0.686) + (255 * 0.168) = 255 * (0.349+0.686+0.168) = 255 * 1.203 = 306.765 -> 255 (clamped)
    # new_b = (255 * 0.272) + (255 * 0.534) + (255 * 0.131) = 255 * (0.272+0.534+0.131) = 255 * 0.937 = 238.935 -> 238 (clamped)
    img = QImage(1, 1, QImage.Format.Format_ARGB32_Premultiplied)
    img.setPixelColor(0, 0, QColor(255, 255, 255, 255)) # White
    
    modified_image = apply_sepia(img)
    px_color = modified_image.pixelColor(0, 0)
    
    assert px_color.red() == 255
    assert px_color.green() == 255
    assert px_color.blue() == 238
    assert px_color.alpha() == 255

def test_apply_sepia_null_image():
    null_img = QImage()
    modified_image = apply_sepia(null_img)
    assert modified_image.isNull()
```
