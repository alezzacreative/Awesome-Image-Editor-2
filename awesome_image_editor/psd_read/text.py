from psd_tools.api.layers import TypeLayer
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor

from ..model_view.items.text import AIETextItem

DEFAULT_PSD_TEXT_FILL_COLOR_DATA: dict = {"Type": 1, "Values": [1, 0, 0, 0]}
"""
Default fill color data for PSD text layers if not specified.
Represents black color in ARGB format (A=1, R=0, G=0, B=0).
Used when a style sheet in the PSD does not explicitly define a `FillColor`.
"""

PSD_PARAGRAPH_JUSTIFICATION_QT_ALIGNMENT_MAP: dict[int, Qt.AlignmentFlag] = {
    0: Qt.AlignmentFlag.AlignLeft,  # PSD Justification: Left
    # 1: Qt.AlignmentFlag.AlignRight, # PSD Justification: Right (TODO: Verify if this mapping is correct if needed)
    2: Qt.AlignmentFlag.AlignCenter,  # PSD Justification: Center
    # 3: Qt.AlignmentFlag.AlignJustify, # PSD Justification: Justify (TODO: Verify if this mapping is correct if needed)
}
"""
Maps PSD paragraph justification values to Qt.AlignmentFlag values.
PSD justification values are integers (0 for left, 2 for center, etc.).
This map is used to set the text alignment in QTextBlockFormat.
"""


def psd_type_layer_to_text_item(layer: TypeLayer) -> AIETextItem:
    """
    Converts a PSD type layer (text layer) to an AIETextItem.

    This function processes a `TypeLayer` object from psd-tools, extracting
    text content, font styles, colors, and paragraph formatting. It then
    constructs an `AIETextItem` with this information.

    The process involves:
    1. Initializing an empty `AIETextItem` and setting its basic properties
       (name, position, visibility) from the PSD layer.
    2. Iterating through style runs (`RunArray`) in the PSD layer's engine data
       to apply character-level formatting (font, size, color) to corresponding
       substrings of the text.
    3. Iterating through paragraph runs to apply block-level formatting
       (text alignment) to paragraphs within the text item.

    Args:
        layer: The PSD TypeLayer to convert.

    Returns:
        An AIETextItem representing the text layer, with content and formatting
        derived from the PSD data.
    """
    item = AIETextItem("", layer.name)
    item.setPos(layer.offset[0], layer.offset[1])
    item.setVisible(layer.visible)

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

    cursor.movePosition(QTextCursor.MoveOperation.Start)
    for paragraph_style in paragraph_rundata:
        block_format = QTextBlockFormat()

        alignment = PSD_PARAGRAPH_JUSTIFICATION_QT_ALIGNMENT_MAP[
            paragraph_style["ParagraphSheet"]["Properties"]["Justification"]
        ]

        block_format.setAlignment(alignment)
        cursor.setBlockFormat(block_format)

        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)

    return item
