from psd_tools import PSDImage

from ..file_format import AIEProject
from ..model_view.items.group import AIEGroupItem
from .pixel import psd_pixel_layer_to_image_item
from .shape import psd_shape_layer_to_shape_item
from .text import psd_type_layer_to_text_item

__all__ = ["load_psd_as_project"]


def read_psd_layer(
    scene: "AIEGraphicsScene", layer, psd_width: int, psd_height: int
) -> "QGraphicsItem | None":
    """
    Recursively reads a PSD layer and converts it to an appropriate AIEGraphicsItem.

    This function handles different PSD layer kinds (pixel, shape, type, group)
    and converts them to corresponding items in the Awesome Image Editor scene.
    For group layers, it recursively processes their children.

    Args:
        scene: The AIEGraphicsScene to add the converted items to.
        layer: The PSD layer object from psd-tools.
        psd_width: The width of the PSD document, used for shape conversion.
        psd_height: The height of the PSD document, used for shape conversion.

    Returns:
        The converted QGraphicsItem if successful, or None if the layer type
        is not supported or an error occurs.
    """
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
                child_item.setParentItem(item)

    if item is not None:
        # Items are added to the scene here. If they have a parent,
        # Qt automatically handles removing them from the scene's top-level items.
        scene.addItem(item)
        return item
    return None


def load_psd_as_project(filepath: str) -> AIEProject:
    """
    Loads a PSD file and converts its content into an AIEProject.

    This function opens a PSD file using psd-tools, then iterates through
    its layers, converting each one into the Awesome Image Editor's project structure.

    Args:
        filepath: The path to the PSD file.

    Returns:
        An AIEProject instance populated with the content of the PSD file.
    """
    psd = PSDImage.open(filepath)

    project = AIEProject()
    scene = project.get_graphics_scene()

    for layer in psd:
        read_psd_layer(scene, layer, psd.width, psd.height)

    return project
