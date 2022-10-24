from psd_tools.api.layers import PixelLayer

from ..graphics_scene.graphics_scene import AIEGraphicsScene
from ..graphics_scene.items.image import AIEImageItem


def add_pixel_layer(scene: AIEGraphicsScene, layer: PixelLayer):
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
    scene.addItem(item)
