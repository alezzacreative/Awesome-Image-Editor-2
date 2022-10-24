from psd_tools import PSDImage

from ..file_format import AIEProject
from .pixel import psd_pixel_layer_to_image_item
from .shape import psd_shape_layer_to_shape_item
from .text import psd_type_layer_to_text_item


def load_psd_as_project(filepath):
    psd = PSDImage.open(filepath)

    project = AIEProject()
    for layer in psd:
        item = None

        if layer.kind == "pixel":
            item = psd_pixel_layer_to_image_item(layer)

        elif layer.kind == "shape":
            item = psd_shape_layer_to_shape_item(layer, psd.width, psd.height)

        elif layer.kind == "type":
            item = psd_type_layer_to_text_item(layer)

        if item is not None:
            project.get_graphics_scene().addItem(item)

    return project
