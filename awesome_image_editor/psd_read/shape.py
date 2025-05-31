from psd_tools.api.layers import ShapeLayer
from psd_tools.api.shape import Subpath
from psd_tools.psd.vector import Knot
from PyQt6.QtGui import QPainterPath

from ..model_view.items.shape import AIEShapeItem


def _connect_knots_cubic(
    qpath: QPainterPath, k1: Knot, k2: Knot, psd_width: int, psd_height: int
) -> None:
    """
    Connects two knots (points) in a QPainterPath using a cubic Bezier curve.

    This helper function takes two `Knot` objects from a PSD subpath and
    calculates the control points and end point for a cubic Bezier curve.
    The coordinates are scaled from the PSD's relative coordinate system (0-1)
    to absolute pixel coordinates based on `psd_width` and `psd_height`.

    Args:
        qpath: The QPainterPath to add the cubic Bezier curve to.
        k1: The starting Knot of the segment. Its `anchor` is the start point,
            and `leaving` is the first control point.
        k2: The ending Knot of the segment. Its `anchor` is the end point,
            and `preceding` is the second control point.
        psd_width: The width of the PSD document in pixels.
        psd_height: The height of the PSD document in pixels.
    """
    # Note: PSD knots store coordinates as (y, x) tuples.
    # QPainterPath uses (x, y).
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

    qpath.cubicTo(
        control_point_1_x,
        control_point_1_y,
        control_point_2_x,
        control_point_2_y,
        end_x,
        end_y,
    )


def psd_shape_layer_to_shape_item(
    layer: ShapeLayer, psd_width: int, psd_height: int
) -> AIEShapeItem | None:
    """
    Converts a PSD shape layer to an AIEShapeItem.

    This function processes the vector mask of a `ShapeLayer` from psd-tools.
    It iterates through the subpaths and knots defined in the vector mask,
    converting them into a QPainterPath. This path is then used to create
    an `AIEShapeItem`. The item's visibility is also set based on the PSD layer.

    The conversion involves scaling coordinates from the PSD's relative system
    to absolute pixel values. Each segment between knots is drawn as a
    cubic Bezier curve using the `_connect_knots_cubic` helper.

    Args:
        layer: The PSD ShapeLayer to convert.
        psd_width: The width of the PSD document.
        psd_height: The height of the PSD document.

    Returns:
        An AIEShapeItem representing the shape layer, or None if the layer
        has no vector mask or no paths in its mask. Currently, it only processes
        the first valid subpath encountered into a single AIEShapeItem.
    """
    # What mainly helped:
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths#b%C3%A9zier_curves
    # https://doc.qt.io/qt-5/qpainterpath.html
    # https://psd-tools.readthedocs.io/en/latest/reference/psd_tools.api.shape.html#psd_tools.api.shape.VectorMask.paths

    if layer.vector_mask is None:
        return

    left, top = layer.offset
    layer_name = layer.name

    subpath: Subpath
    for subpath in layer.vector_mask.paths:
        num_knots = len(subpath)
        if num_knots == 0:
            continue

        qpath = QPainterPath()
        qpath.moveTo(
            subpath[0].anchor[1] * psd_width, subpath[0].anchor[0] * psd_height
        )

        for i in range(num_knots - 1):
            current_knot = subpath[i]
            next_knot = subpath[i + 1]
            _connect_knots_cubic(qpath, current_knot, next_knot, psd_width, psd_height)

        if subpath.is_closed():
            _connect_knots_cubic(qpath, subpath[-1], subpath[0], psd_width, psd_height)

        item = AIEShapeItem(qpath, layer_name)
        item.setVisible(layer.visible)
        # TODO: Handle multiple subpaths within a single shape layer.
        # Currently, only the first subpath is converted and returned.
        return item
    return None
