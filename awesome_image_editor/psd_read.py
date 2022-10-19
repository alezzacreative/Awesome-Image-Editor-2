from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QPainterPath,
    QTextCharFormat,
    QTextCursor,
    QFont,
    QColor,
    QTextBlockFormat,
)
from psd_tools import PSDImage

from .file_format import AIEProject
from .graphics_scene.items.image import AIEImageItem
from .graphics_scene.items.shape import AIEShapeItem
from .graphics_scene.items.type import AIETextItem

DEFAULT_PSD_TEXT_FILL_COLOR_DATA = {"Type": 1, "Values": [1, 0, 0, 0]}


def add_pixel_layer(scene, layer):
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

    qpath.cubicTo(
        control_point_1_x,
        control_point_1_y,
        control_point_2_x,
        control_point_2_y,
        end_x,
        end_y,
    )


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
        scene.addItem(item)


def add_type_layer(scene, layer):
    item = AIETextItem("", layer.name)
    item.setPos(layer.offset[0], layer.offset[1])
    item.setVisible(layer.visible)
    scene.addItem(item)

    document = item.document()
    document.setUseDesignMetrics(True)
    cursor = QTextCursor(document)

    text = layer.engine_dict["Editor"]["Text"].value
    fontset = layer.resource_dict["FontSet"]
    runlength = layer.engine_dict["StyleRun"]["RunLengthArray"]
    rundata = layer.engine_dict["StyleRun"]["RunArray"]
    assert len(rundata) == len(runlength)

    index = 0
    for length, style in zip(runlength, rundata):
        substring: str = text[index : index + length]

        stylesheet = style["StyleSheet"]["StyleSheetData"]
        font = fontset[stylesheet["Font"]]
        index += length

        fill_color_data = stylesheet.get("FillColor", DEFAULT_PSD_TEXT_FILL_COLOR_DATA)
        fill_color_argb_float = fill_color_data["Values"]
        fill_color_rgba_float = (*fill_color_argb_float[1:], fill_color_argb_float[0])
        fill_color_rgba_uchar = tuple(
            map(lambda x: int(x * 255), fill_color_rgba_float)
        )

        font_family = str(font["Name"])
        font_size = stylesheet["FontSize"]

        qfont = QFont()
        qfont.setPixelSize(font_size)
        qfont.setFamily(font_family)

        char_format = QTextCharFormat()
        char_format.setFont(qfont)
        char_format.setForeground(QColor(*fill_color_rgba_uchar))

        cursor.insertText(substring, char_format)

    paragraph_rundata = layer.engine_dict["ParagraphRun"]["RunArray"]
    # paragraph_runlength = layer.engine_dict['ParagraphRun']['RunLengthArray']

    assert (document.blockCount() - 1) == len(paragraph_rundata)

    document.setTextWidth(document.idealWidth())
    cursor.movePosition(QTextCursor.MoveOperation.Start)
    for i in range(len(paragraph_rundata)):
        block_format = QTextBlockFormat()
        block_format.setAlignment(Qt.AlignmentFlag.AlignRight)
        cursor.setBlockFormat(block_format)

        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)


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
