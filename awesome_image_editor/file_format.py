from io import BufferedReader, BufferedWriter

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QGraphicsView

from .graphics_scene.graphics_scene import AIEGraphicsScene
from .graphics_scene.items.image import AIEImageItem
from .graphics_scene.tree_model import TreeModel
from .widgets.layers import LayersWidget
from .binary_io.write import (
    write_pascal_string,
    write_uint32_le,
    write_unicode_string,
    write_float_le,
)
from .binary_io.read import (
    read_float_le,
    read_uint32_le,
    read_pascal_string,
    read_unicode_string,
)

MAGIC_BYTES = b"\x89AIE\r\n\x1a\n"  # Similar to PNG magic bytes

# Chunk Types
LAYERS_CHUNK_TYPE = b"LAYERS"
IMAGE_CHUNK_TYPE = b"IMAGE"


class AIEProject:
    def __init__(self):
        self._graphics_scene = AIEGraphicsScene()
        self._graphics_scene_model = TreeModel(self._graphics_scene)
        self._graphics_view = QGraphicsView(self._graphics_scene)
        self._graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self._graphics_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self._layers_widget = LayersWidget(self._graphics_scene_model)

    def add_image_layer(self, image: QImage, layer_name: str):
        self._graphics_scene.addItem(AIEImageItem(image, layer_name))

    def get_layers_widget(self):
        return self._layers_widget

    def get_graphics_view(self):
        return self._graphics_view

    def get_graphics_scene(self):
        return self._graphics_scene

    def render(self):
        scene = self._graphics_scene
        # Fit scene to items
        scene.setSceneRect(scene.itemsBoundingRect())

        # Create new empty image to render the scene into
        image = QImage(
            scene.sceneRect().size().toSize(),
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        assert image is not None  # In case creation of image fails
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        scene.render(painter)
        # NOTE: End painter explicitly to fix "QPaintDevice: Cannot destroy paint device that is being painted"
        painter.end()

        return image

    def serialize(self, writer: BufferedWriter):
        writer.write(MAGIC_BYTES)
        write_pascal_string(LAYERS_CHUNK_TYPE, writer)
        num_layers = len(self._graphics_scene.items())
        write_uint32_le(num_layers, writer)

        # NOTE: save in back-to-front (AscendingOrder) order to preserve same layer order when importing back
        # TODO: order independent file format? (e.g. save layer index in file?)
        for item in self._graphics_scene.items(Qt.SortOrder.AscendingOrder):
            if isinstance(item, AIEImageItem):
                write_pascal_string(IMAGE_CHUNK_TYPE, writer)
                write_unicode_string(item.name, writer)

                write_float_le(item.pos().x(), writer)
                write_float_le(item.pos().y(), writer)

                byte_array = QByteArray()
                buffer = QBuffer(byte_array)
                buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                item.image.save(buffer, "PNG")

                write_uint32_le(len(byte_array), writer)
                writer.write(byte_array.data())

    @staticmethod
    def deserialize(reader: BufferedReader):
        assert reader.read(len(MAGIC_BYTES)) == MAGIC_BYTES

        # Expecting layers chunk
        chunk_type = read_pascal_string(reader)
        assert chunk_type == LAYERS_CHUNK_TYPE

        project = AIEProject()
        scene = project.get_graphics_scene()
        num_layers = read_uint32_le(reader)

        for i in range(num_layers):
            chunk_type = read_pascal_string(reader)

            if chunk_type == IMAGE_CHUNK_TYPE:
                layer_name = read_unicode_string(reader)
                x = read_float_le(reader)
                y = read_float_le(reader)

                image_data_length = read_uint32_le(reader)
                image_data = reader.read(image_data_length)
                image = QImage.fromData(image_data, "PNG")

                item = AIEImageItem(image, layer_name)
                item.setPos(x, y)
                scene.addItem(item)

        return project
