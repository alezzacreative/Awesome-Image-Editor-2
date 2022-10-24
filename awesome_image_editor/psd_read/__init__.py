from psd_tools import PSDImage

from ..file_format import AIEProject
from ..graphics_scene.items.group import AIEGroupItem
from .pixel import psd_pixel_layer_to_image_item
from .shape import psd_shape_layer_to_shape_item
from .text import psd_type_layer_to_text_item

__all__ = ["load_psd_as_project"]


def read_psd_layer(scene, layer, psd_width: int, psd_height: int):
    item = None

    if layer.kind == "pixel":
        item = psd_pixel_layer_to_image_item(layer)

    elif layer.kind == "shape":
        item = psd_shape_layer_to_shape_item(layer, psd_width, psd_height)

    elif layer.kind == "type":
        item = psd_type_layer_to_text_item(layer)

    elif layer.kind == "group":
        item = AIEGroupItem(layer.name)

        for child_layer in layer:
            child_item = read_psd_layer(scene, child_layer, psd_width, psd_height)
            if child_item:
                item.addToGroup(child_item)

    if item is not None:
        scene.addItem(item)
        return item


def load_psd_as_project(filepath):
    psd = PSDImage.open(filepath)

    project = AIEProject()
    scene = project.get_graphics_scene()

    for layer in psd:
        read_psd_layer(scene, layer, psd.width, psd.height)

    return project
