import pytest
import tempfile
import os
from PyQt6.QtGui import QImage, QColor, qRgb
from PyQt6.QtWidgets import QApplication # Required for QImage to function fully

@pytest.fixture(scope="session")
def qt_application():
    """
    Provides a QApplication instance for tests that require it.
    QImage operations, especially for various formats, might implicitly
    depend on a QApplication instance being available.
    """
    app = QApplication.instance()
    if app is None:
        # Pass an empty list for sys.argv
        app = QApplication([])
    return app

def _perform_save_load_test(qt_application, width, height, image_format_suffix, image_format_qimage=None):
    """
    Helper function to test saving and loading a specific image format.
    """
    image = QImage(width, height, QImage.Format.Format_RGB32)
    # Using a simple color like red. For formats like GIF, complex palettes or alpha might behave differently,
    # but for basic save/load, a solid color is sufficient.
    image.fill(QColor(qRgb(255, 0, 0)))

    temp_filename = None
    try:
        # delete=False is used because QImage.save() needs to close the file itself.
        # We will manually delete the file in the finally block.
        with tempfile.NamedTemporaryFile(suffix=image_format_suffix, delete=False) as tmp:
            temp_filename = tmp.name

        if image_format_qimage:
            assert image.save(temp_filename, image_format_qimage) is True, f"Failed to save {image_format_suffix.upper()}"
        else:
            assert image.save(temp_filename) is True, f"Failed to save {image_format_suffix.upper()}"

        loaded_image = QImage(temp_filename)
        assert not loaded_image.isNull(), f"Loaded {image_format_suffix.upper()} image is null"

        # For some formats, the loaded image might have a different format (e.g. GIF might be indexed).
        # However, width and height should generally be preserved.
        assert loaded_image.width() == width, f"{image_format_suffix.upper()} width mismatch: expected {width}, got {loaded_image.width()}"
        assert loaded_image.height() == height, f"{image_format_suffix.upper()} height mismatch: expected {height}, got {loaded_image.height()}"

        # Optional: Check a pixel to ensure content is somewhat preserved, though color profiles/palettes can affect this.
        # For simplicity, this is omitted here but could be added for more robust tests.
        # loaded_color = QColor(loaded_image.pixel(0,0))
        # assert loaded_color.red() == 255, f"Pixel color mismatch for {image_format_suffix.upper()}"


    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)

def test_save_load_bmp(qt_application):
    _perform_save_load_test(qt_application, 32, 32, ".bmp", "BMP")

def test_save_load_gif(qt_application):
    # GIF save might result in an indexed format, but basic save/load should work.
    _perform_save_load_test(qt_application, 32, 32, ".gif", "GIF")

def test_save_load_tiff(qt_application):
    _perform_save_load_test(qt_application, 32, 32, ".tif", "TIFF")

def test_save_load_webp(qt_application):
    # WebP might require system libraries. If this fails in CI, it might indicate missing dependencies.
    _perform_save_load_test(qt_application, 32, 32, ".webp", "WEBP")

# It's good practice to also test common formats like PNG and JPG if not covered elsewhere.
def test_save_load_png(qt_application):
    _perform_save_load_test(qt_application, 32, 32, ".png", "PNG")

def test_save_load_jpg(qt_application):
    # JPG is lossy, so pixel-perfect comparison is not advised without tolerance.
    # Here, we just check if it saves and loads correctly.
    _perform_save_load_test(qt_application, 32, 32, ".jpg", "JPG")
