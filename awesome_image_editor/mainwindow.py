import traceback
from pathlib import Path

from PyQt6.QtCore import QStandardPaths, Qt, QModelIndex # Added QModelIndex
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
from .dialogs.brightness_contrast import BrightnessContrastDialog
from PIL import ImageEnhance
from .file_dialog import create_open_file_dialog, create_save_file_dialog
from .file_format import AIEProject
from .model_view.items.image import AIEImageItem # Ensure AIEImageItem is imported
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
        menu.addAction("Invert Colors", self.apply_invert_colors_filter)
        menu.addAction("Brightness/Contrast...", self.apply_brightness_contrast_filter)
        self.menuBar().addMenu(menu)

    def apply_brightness_contrast_filter(self) -> None:
        """Applies a brightness/contrast filter to the selected image layer using a dialog."""
        if not self._project:
            QMessageBox.warning(self, "No Project", "Please open or create a project first.")
            return

        scene = self._project.get_graphics_scene()
        selected_items = scene.selectedItems()

        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a layer.")
            return
        if len(selected_items) > 1:
            QMessageBox.information(self, "Multiple Layers", "Please select only one layer.")
            return

        current_item = selected_items[0]
        if not isinstance(current_item, AIEImageItem):
            QMessageBox.information(self, "Not an Image Layer", "Filter applies only to image layers.")
            return

        original_qimage = current_item.image
        if original_qimage.isNull():
            QMessageBox.warning(self, "Empty Image", "Selected layer has no image data.")
            return

        try:
            pil_original_image = ImageQt.fromqimage(original_qimage)
            self.pil_alpha_channel = None # Initialize attribute

            if pil_original_image.mode == 'RGBA' or pil_original_image.mode == 'LA':
                self.pil_alpha_channel = pil_original_image.getchannel('A') if pil_original_image.mode == 'RGBA' else pil_original_image.getchannel('A') if pil_original_image.mode == 'LA' else None # Ensure alpha channel is correctly extracted for LA
                pil_to_enhance = pil_original_image.convert('RGB')
            elif pil_original_image.mode == 'P':
                 pil_to_enhance = pil_original_image.convert('RGB')
            else: # Includes 'RGB', 'L', etc. If 'L', ImageEnhance will work on it.
                pil_to_enhance = pil_original_image.copy() # Work on a copy

            # self.pil_preview_image = pil_to_enhance.copy() # This was for a copy, let's use pil_to_enhance as base for preview
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not convert image for editing: {e}")
            return

        dialog = BrightnessContrastDialog(self)
        # TODO: Optionally set initial dialog values from stored layer properties if they exist
        # current_brightness, current_contrast = current_item.get_brightness_contrast_values() # Hypothetical
        # dialog.set_values(current_brightness, current_contrast)


        self._active_filter_item = current_item
        # Store the base PIL image (RGB part) that enhancements will be applied to for preview
        self._pil_base_for_preview = pil_to_enhance


        def apply_preview(brightness_val: int, contrast_val: int, is_preview_enabled: bool):
            if not self._active_filter_item or not hasattr(self, '_pil_base_for_preview'):
                return

            if not is_preview_enabled:
                self._active_filter_item.image = original_qimage
                self._active_filter_item.update()
                # Update thumbnail to original
                layers_view = self._project.get_layers_widget().list_view
                tree_model = layers_view.model()
                item_index = layers_view.currentIndex()
                if item_index.isValid() and tree_model.getItem(item_index) == self._active_filter_item:
                    tree_model.dataChanged.emit(item_index, item_index, [Qt.ItemDataRole.DecorationRole])
                return

            temp_pil_image = self._pil_base_for_preview.copy()

            brightness_factor = max(0.1, 1.0 + (brightness_val / 100.0))
            enhancer_brightness = ImageEnhance.Brightness(temp_pil_image)
            img_bright = enhancer_brightness.enhance(brightness_factor)

            contrast_factor = max(0.1, 1.0 + (contrast_val / 100.0))
            enhancer_contrast = ImageEnhance.Contrast(img_bright)
            img_final_pil = enhancer_contrast.enhance(contrast_factor)

            if hasattr(self, 'pil_alpha_channel') and self.pil_alpha_channel:
                # Ensure img_final_pil is RGB before putting alpha
                if img_final_pil.mode != 'RGB':
                    img_final_pil = img_final_pil.convert('RGB')
                img_final_pil.putalpha(self.pil_alpha_channel)

            preview_qimage = ImageQt.toqimage(img_final_pil)
            self._active_filter_item.image = preview_qimage
            self._active_filter_item.update()

            # Update thumbnail in preview
            layers_view = self._project.get_layers_widget().list_view
            tree_model = layers_view.model()
            item_index = layers_view.currentIndex()
            if item_index.isValid() and tree_model.getItem(item_index) == self._active_filter_item:
                tree_model.dataChanged.emit(item_index, item_index, [Qt.ItemDataRole.DecorationRole])

        dialog.valuesChangedForPreview.connect(apply_preview)

        if dialog.is_preview_enabled(): # Apply initial preview
             apply_preview(dialog.get_brightness(), dialog.get_contrast(), True)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            final_brightness = dialog.get_brightness()
            final_contrast = dialog.get_contrast()

            # Apply final transformation to the original RGB part
            final_pil_to_enhance = self._pil_base_for_preview.copy() # Start fresh from original RGB part

            brightness_factor = max(0.1, 1.0 + (final_brightness / 100.0))
            enhancer_b = ImageEnhance.Brightness(final_pil_to_enhance)
            img_b = enhancer_b.enhance(brightness_factor)

            contrast_factor = max(0.1, 1.0 + (final_contrast / 100.0))
            enhancer_c = ImageEnhance.Contrast(img_b)
            final_pil_image = enhancer_c.enhance(contrast_factor)

            if hasattr(self, 'pil_alpha_channel') and self.pil_alpha_channel:
                if final_pil_image.mode != 'RGB': # Ensure it's RGB before putting alpha
                    final_pil_image = final_pil_image.convert('RGB')
                final_pil_image.putalpha(self.pil_alpha_channel)

            final_qimage = ImageQt.toqimage(final_pil_image)
            current_item.image = final_qimage
            current_item.update()

            # Update model thumbnail after final application
            layers_view = self._project.get_layers_widget().list_view
            tree_model = layers_view.model()
            item_index = layers_view.currentIndex()
            if item_index.isValid() and tree_model.getItem(item_index) == current_item:
                 tree_model.dataChanged.emit(item_index, item_index, [Qt.ItemDataRole.DecorationRole])
            else: # Fallback if selection changed or is weird (should not happen with modal dialog)
                for r_idx in range(tree_model.rowCount(QModelIndex())): # Check top-level items
                    idx = tree_model.index(r_idx, 0, QModelIndex())
                    if tree_model.getItem(idx) == current_item:
                        tree_model.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DecorationRole])
                        break
            QMessageBox.information(self, "Filter Applied", "Brightness/Contrast filter applied.")
        else:
            # Dialog was cancelled, ensure original image and thumbnail are restored
            current_item.image = original_qimage
            current_item.update()
            layers_view = self._project.get_layers_widget().list_view
            tree_model = layers_view.model()
            item_index = layers_view.currentIndex()
            if item_index.isValid() and tree_model.getItem(item_index) == current_item:
                 tree_model.dataChanged.emit(item_index, item_index, [Qt.ItemDataRole.DecorationRole])
            # QMessageBox.information(self, "Filter Cancelled", "Brightness/Contrast filter cancelled.")

        if hasattr(self, '_active_filter_item'):
            del self._active_filter_item
        if hasattr(self, '_pil_base_for_preview'):
            del self._pil_base_for_preview
        if hasattr(self, 'pil_alpha_channel'):
            del self.pil_alpha_channel


    def apply_invert_colors_filter(self) -> None:
        """Applies an invert colors filter to the selected image layer."""
        if not self._project:
            QMessageBox.warning(self, "No Project", "Please open or create a project first.")
            return

        scene = self._project.get_graphics_scene()
        selected_items = scene.selectedItems()

        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a layer to apply the filter to.")
            return

        if len(selected_items) > 1:
            QMessageBox.information(self, "Multiple Layers Selected", "Please select only one layer to apply the filter.")
            return

        current_item = selected_items[0]
        if not isinstance(current_item, AIEImageItem):
            QMessageBox.information(self, "Not an Image Layer", "The invert colors filter can only be applied to image layers.")
            return

        # Get the QImage from the AIEImageItem
        image_to_modify = current_item.image

        if image_to_modify.isNull():
            QMessageBox.warning(self, "Empty Image", "The selected layer does not contain valid image data.")
            return

        # Apply the invert filter
        image_to_modify.invertPixels(QImage.InvertMode.InvertRgb)

        # Notify the graphics item that its content has changed, to trigger a repaint
        current_item.update()

        # TODO: Consider if explicit model notification for thumbnail update is needed.
        # For now, item.update() handles the main view.
        # Example:
        # tree_model = self._project.get_layers_widget()._model # Accessing private _model, better to have a getter
        # if tree_model:
        #     # Find index for current_item and emit dataChanged for DecorationRole
        #     pass


        QMessageBox.information(self, "Filter Applied", "Invert colors filter applied successfully.")
