from psd_tools.api.layers import PixelLayer

from ..model_view.items.image import AIEImageItem


def psd_pixel_layer_to_image_item(layer: PixelLayer) -> AIEImageItem | None:
    """
    Converts a PSD pixel layer to an AIEImageItem.

    This function takes a `PixelLayer` object from psd-tools, converts its
    image data to a QImage, and creates an `AIEImageItem` with the appropriate
    name, position, and visibility settings.

    Args:
        layer: The PSD PixelLayer to convert.

    Returns:
        An AIEImageItem representing the pixel layer, or None if the
        layer has no image data (e.g., it's an empty layer).
    """
    assert layer.kind == "pixel"

    pil_image = layer.topil()
    if pil_image is None:
        return

    image = pil_image.toqimage()
    left, top = layer.offset
    image_name = layer.name
    item = AIEImageItem(image, image_name)
    item.setPos(left, top)
    item.setVisible(layer.visible)

    return item
