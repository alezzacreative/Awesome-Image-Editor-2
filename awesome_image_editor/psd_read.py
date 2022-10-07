from PyQt6.QtGui import QPainterPath
from psd_tools import PSDImage

from .file_format import AIEProject
from .graphics_scene.items.image import AIEImageItem
from .graphics_scene.items.shape import AIEShapeItem


def add_pixel_layer(scene, layer):
    assert layer.kind == "pixel"
    image = layer.topil().toqimage()
    left, top = layer.offset
    image_name = layer.name
    item = AIEImageItem(image, image_name)
    item.setPos(left, top)
    scene.addItem(item)


def _connect_knots_cubic(qpath: QPainterPath, k1, k2, psd_width, psd_height):
    start_y, start_x = k1.anchor
    start_x *= psd_width
    start_y *= psd_height

    end_y, end_x = k2.anchor
    end_x *= psd_width
    end_y *= psd_height

    control_point_1_y, control_point_1_x = k1.leaving
    control_point_1_x *= psd_width
    control_point_1_y *= psd_height

    control_point_2_y, control_point_2_x = k2.preceding
    control_point_2_x *= psd_width
    control_point_2_y *= psd_height

    qpath.cubicTo(control_point_1_x, control_point_1_y, control_point_2_x, control_point_2_y, end_x, end_y)


def add_shape_layer(scene, layer, psd_width, psd_height):
    # What mainly helped:
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths#b%C3%A9zier_curves
    # https://doc.qt.io/qt-5/qpainterpath.html
    # https://psd-tools.readthedocs.io/en/latest/reference/psd_tools.api.shape.html#psd_tools.api.shape.VectorMask.paths
    left, top = layer.offset
    layer_name = layer.name
    for subpath in layer.vector_mask.paths:
        num_knots = len(subpath)
        if num_knots == 0:
            continue
        qpath = QPainterPath()
        qpath.moveTo(subpath[0].anchor[1] * psd_width, subpath[0].anchor[0] * psd_height)
        for i in range(num_knots - 1):
            current_knot = subpath[i]
            next_knot = subpath[i + 1]
            _connect_knots_cubic(qpath, current_knot, next_knot, psd_width, psd_height)
        if subpath.is_closed():
            _connect_knots_cubic(qpath, subpath[-1], subpath[0], psd_width, psd_height)

        item = AIEShapeItem(qpath, layer_name)
        scene.addItem(item)


def load_psd_as_project(filepath):
    psd = PSDImage.open(filepath)

    project = AIEProject()
    scene = project.get_graphics_scene()
    for layer in psd:
        if layer.kind == "pixel":
            add_pixel_layer(scene, layer)

        elif layer.kind == "shape":
            add_shape_layer(scene, layer, psd.width, psd.height)

    return project
