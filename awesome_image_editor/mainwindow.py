import traceback
from pathlib import Path

from PyQt6.QtCore import QStandardPaths, Qt
from PyQt6.QtGui import QFont, QImage
from PIL import Image as PILImage
from PIL import ImageQt
import numpy as np
import qoi
from PyQt6.QtWidgets import (
    QDockWidget,
    QGraphicsBlurEffect,
    QMainWindow,
    QMenu,
    QMessageBox,
    QToolBar,
)

from .dialogs.gaussian_blur import GaussianBlurDialog
from .file_dialog import create_open_file_dialog, create_save_file_dialog
from .file_format import AIEProject
from .psd_read import load_psd_as_project

__all__ = ("MainWindow",)


class MainWindow(QMainWindow):
    """
    The main window of the Awesome Image Editor application.

    This class sets up the UI, including menus, toolbars, and dock widgets.
    It also handles project and image file operations.
    """

    def __init__(self):
        """Initializes the MainWindow."""
        super().__init__()
        self.setWindowTitle("Awesome Image Editor")
        self.setup_file_menu()
        self.setup_filters_menu()

        self.layers_dock_widget = QDockWidget("Layers")
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.layers_dock_widget,
            Qt.Orientation.Vertical,
        )

        self._project = AIEProject()
        self.setCentralWidget(self._project.get_graphics_view())
        self.layers_dock_widget.setWidget(self._project.get_layers_widget())

        # TODO: add tools to toolbar
        toolbar = QToolBar()
        toolbar.setOrientation(Qt.Orientation.Vertical)
        toolbar.setMovable(True)
        toolbar_font = QFont()
        toolbar_font.setPointSize(17)
        toolbar.setFont(toolbar_font)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)

        self.showMaximized()

    def set_project(self, project: AIEProject):
        """
        Sets the current project for the editor.

        Args:
            project: The AIEProject to set as the current project.
        """
        self._project = project
        self.setCentralWidget(self._project.get_graphics_view())
        self.layers_dock_widget.setWidget(self._project.get_layers_widget())

    def get_project(self) -> AIEProject:
        """
        Returns the current project.

        Returns:
            The current AIEProject.
        """
        return self._project

    def open_project(self):
        """Opens an existing project from a .aie file."""
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        )
        dlg = create_open_file_dialog(
            default_dir, "Awesome Image Editor Project (*.aie)"
        )

        if dlg.exec():
            filepath = dlg.selectedFiles()[0]
            with open(filepath, "rb") as file:
                self.set_project(AIEProject.deserialize(file))

    def save_as_project(self):
        """Saves the current project to a .aie file."""
        if self._project is None:
            return

        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        )
        dlg = create_save_file_dialog(
            default_dir, "Awesome Image Editor Project (*.aie)"
        )

        if dlg.exec():
            filepath = dlg.selectedFiles()[0]
            with open(filepath, "wb") as file:
                self._project.serialize(file)

    def open_image(self):
        """Opens an image file (e.g., JPG, PNG) and adds it as a new layer."""
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        )
        dlg = create_open_file_dialog(default_dir, "All Supported Image Files (*.png *.jpg *.jpeg *.avif *.bmp *.gif *.svg *.tif *.tiff *.webp *.qoi);;PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;AVIF Files (*.avif);;QOI Files (*.qoi);;BMP Files (*.bmp);;GIF Files (*.gif);;SVG Files (*.svg);;TIFF Files (*.tif *.tiff);;WebP Files (*.webp)")

        try:
            if dlg.exec():
                filepath = dlg.selectedFiles()[0]
                image: QImage
                lower_filepath = filepath.lower()

                if lower_filepath.endswith(".avif"):
                    pil_img = PILImage.open(filepath)
                    pil_img = pil_img.convert("RGBA") # Ensure consistent format
                    image = ImageQt.toqimage(pil_img)
                elif lower_filepath.endswith(".qoi"):
                    pil_img = PILImage.open(filepath)
                    pil_img = pil_img.convert("RGBA") # Ensure consistent format for QImage
                    image = ImageQt.toqimage(pil_img)
                else:
                    image = QImage(filepath)

                if image.isNull():
                    raise ValueError(f"Failed to load image: {filepath}")

                image_name = Path(filepath).stem
                self._project.add_image_layer(image, image_name)
        except Exception as e:
            QMessageBox.critical(self, "Error Opening Image", f"Could not open image file: {filepath}\n\nError: {e}\n\n{traceback.format_exc()}")

    def save_image(self):
        """Saves the current project as an image file (e.g., JPG, PNG, AVIF)."""
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        )
        dlg = create_save_file_dialog(default_dir, "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;AVIF Files (*.avif);;QOI Files (*.qoi);;BMP Files (*.bmp);;TIFF Files (*.tif *.tiff);;WebP Files (*.webp);;GIF Files (*.gif);;SVG Files (*.svg)")

        try:
            if dlg.exec():
                filepath = dlg.selectedFiles()[0]
                lower_filepath = filepath.lower()

                if lower_filepath.endswith(".avif"):
                    q_image_to_save = self._project.render()
                    pil_image_to_save = ImageQt.fromqimage(q_image_to_save)
                    if pil_image_to_save.mode not in ['RGB', 'RGBA']:
                        pil_image_to_save = pil_image_to_save.convert('RGBA')
                    pil_image_to_save.save(filepath, format='AVIF')
                elif lower_filepath.endswith(".qoi"):
                    q_image_to_save = self._project.render()
                    # Convert QImage to RGBA or RGB format suitable for QOI
                    # QOI typically handles 3 (RGB) or 4 (RGBA) channels.
                    # Ensure format is not indexed or grayscale without conversion.
                    if q_image_to_save.format() not in [QImage.Format.Format_RGB888, QImage.Format.Format_RGBA8888, QImage.Format.Format_RGBA8888_Premultiplied]:
                         q_image_to_save = q_image_to_save.convertToFormat(QImage.Format.Format_RGBA8888)

                    pil_img = ImageQt.fromqimage(q_image_to_save)

                    # Ensure mode is RGB or RGBA for QOI
                    if pil_img.mode not in ('RGB', 'RGBA'):
                        pil_img = pil_img.convert('RGBA' if pil_img.has_alpha() else 'RGB')

                    numpy_array = np.array(pil_img)

                    # The qoi library expects data in HWC (Height, Width, Channels) format.
                    # np.array(pil_img) should already be in this format.
                    # It also expects uint8 data.
                    if numpy_array.dtype != np.uint8:
                        numpy_array = numpy_array.astype(np.uint8)

                    # Determine channels from numpy array shape for qoi.write
                    # The qoi.write function infers channels from the array shape.
                    # It might also take an explicit `channels` argument if needed,
                    # but the `rgb` parameter `const unsigned char[:, :, ::1]` implies it handles it.
                    qoi.write(filepath, numpy_array) # Using qoi.write, assuming qoi.__init__ exposes it from qoi.qoi
                else:
                    image_to_save = self._project.render()
                    if not image_to_save.save(filepath):
                        raise ValueError(f"Failed to save image to: {filepath}. Qt's QImage.save() returned false.")
        except Exception as e:
            QMessageBox.critical(self, "Error Saving Image", f"Could not save image file: {filepath}\n\nError: {e}\n\n{traceback.format_exc()}")

    def add_gaussian_blur_to_selected_layer(self):
        """Applies a Gaussian blur effect to the currently selected layer."""
        scene = self._project.get_graphics_scene()
        if len(scene.selectedItems()) == 0:
            QMessageBox.information(
                self,
                "Warning",
                "No selected layers to apply effect, please select at least one layer",
                QMessageBox.StandardButton.Ok,
            )
            return

        dlg = GaussianBlurDialog()
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)

        effect = QGraphicsBlurEffect()

        dlg.preview_checkbox_toggled.connect(effect.setEnabled)
        dlg.blur_radius_changed.connect(effect.setBlurRadius)

        effect.setEnabled(dlg.is_preview_enabled())
        effect.setBlurRadius(dlg.get_blur_radius())

        selected_item = scene.selectedItems()[0]
        selected_item.setGraphicsEffect(effect)
        dlg.rejected.connect(lambda: selected_item.setGraphicsEffect(None))
        dlg.accepted.connect(lambda: effect.setEnabled(True))

        dlg.show()

    def read_psd_as_project(self):
        """Opens a Photoshop file (.psd) and loads it as a new project."""
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        )
        dlg = create_open_file_dialog(default_dir, "Photoshop Files (*.psd)")
        if dlg.exec():
            filepath = dlg.selectedFiles()[0]
            self.set_project(load_psd_as_project(filepath))

    def setup_file_menu(self):
        """Sets up the 'File' menu with actions for file operations."""
        menu = QMenu("File", self)
        menu.addAction("Open", self.open_project)
        menu.addAction("Open PSD", self.read_psd_as_project)
        menu.addAction("Open Image", self.open_image)
        menu.addSeparator()
        menu.addAction("Save as", self.save_as_project)
        menu.addSeparator()
        menu.addAction("Save Image", self.save_image)
        self.menuBar().addMenu(menu)

    def setup_filters_menu(self):
        """Sets up the 'Filters' menu with actions for applying image filters."""
        menu = QMenu("Filters", self)
        menu.addAction("Gaussian Blur", self.add_gaussian_blur_to_selected_layer)
        self.menuBar().addMenu(menu)
