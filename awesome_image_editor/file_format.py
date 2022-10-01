import struct
from typing import BinaryIO

from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QGraphicsView

from .graphics_scene.items.image import QGraphicsImageItem
from .graphics_scene.model import QGraphicsSceneModel, QGraphicsSceneCustom
from .widgets.layers import LayersWidget

MAGIC_BYTES = b"\x89AIE\r\n\x1a\n"

# Chunk Types
LAYERS_CHUNK_TYPE = b"LAYERS"
IMAGE_CHUNK_TYPE = b"IMAGE"
UNKNOWN_CHUNK_TYPE = b"UNKNOWN"


def write_uint32_le(value: int, file: BinaryIO):
    data = value.to_bytes(4, "little", signed=False)
    file.write(data)


def write_float_le(value: float, file: BinaryIO):
    file.write(struct.pack("<f", value))


def write_pascal_string(string: bytes, file: BinaryIO):
    write_uint32_le(len(string), file)
    file.write(string)


def write_unicode_string(string: str, file: BinaryIO):
    data = string.encode("utf-8")
    write_uint32_le(len(data), file)
    file.write(data)


def read_uint32_le(file: BinaryIO):
    data = file.read(4)
    assert len(data) == 4
    return int.from_bytes(data, "little", signed=False)


def read_pascal_string(file: BinaryIO):
    length = read_uint32_le(file)
    return file.read(length)


def read_unicode_string(file: BinaryIO):
    length = read_uint32_le(file)
    data = file.read(length)
    return data.decode("utf-8")


def read_float_le(file: BinaryIO):
    data = file.read(4)
    assert len(data) == 4  # struct should already error out, assert for consistency
    return struct.unpack("<f", data)[0]


class AIEProject:
    def __init__(self, scene: QGraphicsSceneCustom):
        self.graphics_scene = scene
        self.graphics_scene_model = QGraphicsSceneModel(self.graphics_scene)
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.layers_widget = LayersWidget(self.graphics_scene_model)

    def serialize(self, file: BinaryIO):
        file.write(MAGIC_BYTES)
        write_pascal_string(LAYERS_CHUNK_TYPE, file)
        num_layers = len(self.graphics_scene.items())
        write_uint32_le(num_layers, file)

        # NOTE: save in back-to-front (AscendingOrder) order to preserve same layer order when importing back
        # TODO: order independent file format? (e.g. save Z order in file)
        for item in self.graphics_scene.items(Qt.SortOrder.AscendingOrder):
            if isinstance(item, QGraphicsImageItem):
                write_pascal_string(IMAGE_CHUNK_TYPE, file)
                write_unicode_string(item.name, file)

                write_float_le(item.pos().x(), file)
                write_float_le(item.pos().y(), file)

                byte_array = QByteArray()
                buffer = QBuffer(byte_array)
                buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                item.image.save(buffer, "PNG")

                write_uint32_le(len(byte_array), file)
                file.write(byte_array.data())
            else:
                write_pascal_string(UNKNOWN_CHUNK_TYPE, file)

    @staticmethod
    def deserialize(file: BinaryIO):
        assert file.read(len(MAGIC_BYTES)) == MAGIC_BYTES

        # Expecting layers chunk
        chunk_type = read_pascal_string(file)
        assert chunk_type == LAYERS_CHUNK_TYPE

        scene = QGraphicsSceneCustom()
        num_layers = read_uint32_le(file)

        for i in range(num_layers):
            chunk_type = read_pascal_string(file)

            if chunk_type == IMAGE_CHUNK_TYPE:
                layer_name = read_unicode_string(file)
                x = read_float_le(file)
                y = read_float_le(file)

                image_data_length = read_uint32_le(file)
                image_data = file.read(image_data_length)
                image = QImage.fromData(image_data, "PNG")

                item = QGraphicsImageItem(image, layer_name)
                item.setPos(x, y)
                scene.addItem(item)

        return AIEProject(scene)
