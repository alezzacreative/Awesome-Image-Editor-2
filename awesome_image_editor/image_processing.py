from PyQt6.QtGui import QImage, QColor

def clamp(value, min_val=0, max_val=255):
    return max(min_val, min(value, max_val))

def apply_brightness_contrast(original_image: QImage, brightness: int, contrast: int) -> QImage:
    if original_image.isNull():
        return QImage()

    # Create a deep copy to modify
    new_image = original_image.copy()
    # Ensure the image format supports per-pixel alpha, if not convert.
    # Most loaded images (PNG) will. Format_ARGB32 is safe.
    if new_image.format() != QImage.Format.Format_ARGB32 and \
       new_image.format() != QImage.Format.Format_ARGB32_Premultiplied:
        new_image = new_image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)


    # Brightness: value is -100 to 100.
    # Map brightness value (e.g. -100 to 100) to a pixel change (e.g. -128 to 128)
    brightness_offset = int((brightness / 100.0) * 128)


    # Contrast: value is -100 to 100.
    # We'll use an adjusted factor:
    # If contrast is -100, factor = 0. If 0, factor = 1. If 100, factor = 2.
    # This provides a range from no contrast (all gray) to double contrast.
    if contrast >= 0:
        # For C in [0, 100], factor from 1.0 to 2.0
        contrast_factor_adj = 1.0 + (contrast / 100.0) 
    else: # contrast < 0
        # For C in [-100, 0), factor from 0.0 to 1.0 (exclusive of 1.0)
        contrast_factor_adj = (100.0 + contrast) / 100.0
        
    width = new_image.width()
    height = new_image.height()

    for y in range(height):
        for x in range(width):
            pixel_color = new_image.pixelColor(x, y)
            
            r, g, b, a = pixel_color.red(), pixel_color.green(), pixel_color.blue(), pixel_color.alpha()

            # Apply Brightness
            r_bright = clamp(r + brightness_offset)
            g_bright = clamp(g + brightness_offset)
            b_bright = clamp(b + brightness_offset)

            # Apply Contrast (around mid-point 128)
            r_contrast = clamp(int(128 + contrast_factor_adj * (r_bright - 128)))
            g_contrast = clamp(int(128 + contrast_factor_adj * (g_bright - 128)))
            b_contrast = clamp(int(128 + contrast_factor_adj * (b_bright - 128)))
            
            new_image.setPixelColor(x, y, QColor(r_contrast, g_contrast, b_contrast, a))
            
    return new_image
