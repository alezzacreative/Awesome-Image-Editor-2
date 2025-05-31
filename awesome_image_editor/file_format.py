from io import BufferedReader, BufferedWriter

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QGraphicsView

from .model_view.graphics_scene import AIEGraphicsScene
from .model_view.graphics_view import AIEGraphicsView
from .model_view.items.image import AIEImageItem
from .model_view.tree_model import TreeModel
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

MAGIC_BYTES: bytes = b"\x89AIE\r\n\x1a\n"
"""Magic bytes to identify an Awesome Image Editor (.aie) file. Similar to PNG magic bytes."""

# Chunk Types
LAYERS_CHUNK_TYPE: bytes = b"LAYERS"
"""Identifier for a chunk containing layer information."""
IMAGE_CHUNK_TYPE: bytes = b"IMAGE"
"""Identifier for a chunk containing image data for a layer."""


class AIEProject:
    """
    Represents an Awesome Image Editor project.

    This class encapsulates the scene, view, layers, and provides methods
    for adding layers, rendering the project, and serializing/deserializing
    it to/from the .aie file format.
    """

    def __init__(self) -> None:
        """Initializes a new AIEProject with an empty scene and associated view/widgets."""
        self._graphics_scene = AIEGraphicsScene()
        self._graphics_view = AIEGraphicsView(self._graphics_scene)

        self._graphics_scene_model = TreeModel(self._graphics_scene)
        self._layers_widget = LayersWidget(self._graphics_scene_model)

    def add_image_layer(self, image: QImage, layer_name: str) -> None:
        """
        Adds a new image layer to the project.

        Args:
            image: The QImage to add as a layer.
            layer_name: The name for the new layer.
        """
        self._graphics_scene.addItem(AIEImageItem(image, layer_name))

    def get_layers_widget(self) -> LayersWidget:
        """
        Returns the LayersWidget associated with this project.

        Returns:
            The LayersWidget instance.
        """
        return self._layers_widget

    def get_graphics_view(self) -> QGraphicsView:
        """
        Returns the AIEGraphicsView associated with this project.

        Returns:
            The AIEGraphicsView instance.
        """
        return self._graphics_view

    def get_graphics_scene(self) -> AIEGraphicsScene:
        """
        Returns the AIEGraphicsScene associated with this project.

        Returns:
            The AIEGraphicsScene instance.
        """
        return self._graphics_scene

    def render(self) -> QImage:
        """
        Renders the current state of the graphics scene into a QImage.

        The scene is fit to its items, and then rendered onto a transparent
        ARGB32 premultiplied image.

        Returns:
            A QImage containing the rendered scene.
        """
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

    def serialize(self, writer: BufferedWriter) -> None:
        """
        Serializes the project to a binary stream using the .aie file format.

        Writes magic bytes, layer information, and image data for each layer.

        Args:
            writer: A BufferedWriter to write the serialized project data to.
        """
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
    def deserialize(reader: BufferedReader) -> "AIEProject":
        """
        Deserializes an AIEProject from a binary stream.

        Reads the .aie file format, reconstructs layers and their properties.

        Args:
            reader: A BufferedReader to read the serialized project data from.

        Returns:
            A new AIEProject instance populated with data from the reader.

        Raises:
            AssertionError: If the file format is invalid (e.g., wrong magic
                            bytes or unexpected chunk types).
        """
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
