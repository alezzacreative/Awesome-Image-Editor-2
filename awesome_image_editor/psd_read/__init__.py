from psd_tools import PSDImage

from ..file_format import AIEProject
from .pixel import add_pixel_layer
from .shape import add_shape_layer
from .text import add_type_layer


def load_psd_as_project(filepath):
    psd = PSDImage.open(filepath)

    project = AIEProject()
    scene = project.get_graphics_scene()
    for layer in psd:
        if layer.kind == "pixel":
            add_pixel_layer(scene, layer)

        elif layer.kind == "shape":
            add_shape_layer(scene, layer, psd.width, psd.height)

        elif layer.kind == "type":
            add_type_layer(scene, layer)

    return project
