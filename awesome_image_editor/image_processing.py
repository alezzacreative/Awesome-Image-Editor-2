from PyQt6.QtGui import QImage, QColor

def clamp(value, min_val=0, max_val=255):
    return max(min_val, min(value, max_val))

def apply_brightness_contrast(original_image: QImage, brightness: int, contrast: int) -> QImage:
    if original_image.isNull():
        return QImage()

    new_image = original_image.copy()
    if new_image.format() != QImage.Format.Format_ARGB32 and        new_image.format() != QImage.Format.Format_ARGB32_Premultiplied:
        new_image = new_image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)

    brightness_offset = int((brightness / 100.0) * 128)

    if contrast >= 0:
        contrast_factor_adj = 1.0 + (contrast / 100.0) 
    else: 
        contrast_factor_adj = (100.0 + contrast) / 100.0
        
    width = new_image.width()
    height = new_image.height()

    for y in range(height):
        for x in range(width):
            pixel_color = new_image.pixelColor(x, y)
            r, g, b, a = pixel_color.red(), pixel_color.green(), pixel_color.blue(), pixel_color.alpha()
            r_bright = clamp(r + brightness_offset)
            g_bright = clamp(g + brightness_offset)
            b_bright = clamp(b + brightness_offset)
            r_contrast = clamp(int(128 + contrast_factor_adj * (r_bright - 128)))
            g_contrast = clamp(int(128 + contrast_factor_adj * (g_bright - 128)))
            b_contrast = clamp(int(128 + contrast_factor_adj * (b_bright - 128)))
            new_image.setPixelColor(x, y, QColor(r_contrast, g_contrast, b_contrast, a))
            
    return new_image

def apply_grayscale(original_image: QImage) -> QImage:
    if original_image.isNull():
        return QImage()

    processed_image = original_image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
    width = processed_image.width()
    height = processed_image.height()

    for y in range(height):
        for x in range(width):
            pixel_color = processed_image.pixelColor(x, y)
            r = pixel_color.red()
            g = pixel_color.green()
            b = pixel_color.blue()
            a = pixel_color.alpha()
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            gray = clamp(gray)
            processed_image.setPixelColor(x, y, QColor(gray, gray, gray, a))
            
    return processed_image

def apply_sepia(original_image: QImage) -> QImage:
    if original_image.isNull():
        return QImage()

    processed_image = original_image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
    width = processed_image.width()
    height = processed_image.height()

    for y in range(height):
        for x in range(width):
            pixel_color = processed_image.pixelColor(x, y)
            r_orig = pixel_color.red()
            g_orig = pixel_color.green()
            b_orig = pixel_color.blue()
            a = pixel_color.alpha()
            new_r = (r_orig * 0.393) + (g_orig * 0.769) + (b_orig * 0.189)
            new_g = (r_orig * 0.349) + (g_orig * 0.686) + (b_orig * 0.168)
            new_b = (r_orig * 0.272) + (g_orig * 0.534) + (b_orig * 0.131)
            r_sepia = clamp(int(new_r))
            g_sepia = clamp(int(new_g))
            b_sepia = clamp(int(new_b))
            processed_image.setPixelColor(x, y, QColor(r_sepia, g_sepia, b_sepia, a))
            
    return processed_image

def apply_invert_colors(original_image: QImage) -> QImage:
    if original_image.isNull():
        return QImage()

    processed_image = original_image.copy()
    processed_image.invertPixels(QImage.InvertMode.InvertRgb)
            
    return processed_image
```
