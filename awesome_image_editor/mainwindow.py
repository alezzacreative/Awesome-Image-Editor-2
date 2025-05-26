import traceback
from pathlib import Path

from PyQt6.QtCore import QStandardPaths, Qt
from PyQt6.QtGui import QFont, QImage
from PyQt6.QtWidgets import (
    QDockWidget,
    QGraphicsBlurEffect,
    QMainWindow,
    QMenu,
    QMessageBox,
    QToolBar,
    QLabel, # Ensure QLabel is imported
)

from .dialogs.gaussian_blur import GaussianBlurDialog
from .dialogs import BrightnessContrastDialog # Updated import
from .file_dialog import create_open_file_dialog, create_save_file_dialog
from .file_format import AIEProject
from .psd_read import load_psd_as_project
from .model_view.graphics_view import AIEGraphicsView # Add this import
from .model_view.items.image import AIEImageItem # Import for type checking
from .image_processing import apply_brightness_contrast # Added image processing import

__all__ = ("MainWindow",)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Awesome Image Editor")

        self.zoom_status_label = QLabel("Zoom: 100.0%")
        self.statusBar().addPermanentWidget(self.zoom_status_label)

        self.setup_file_menu()
        self.setup_filters_menu()

        self.layers_dock_widget = QDockWidget("Layers")
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.layers_dock_widget,
            Qt.Orientation.Vertical,
        )

        self._project = AIEProject()
        initial_view = self._project.get_graphics_view()
        if initial_view: # Should always exist
            initial_view.zoom_level_changed.connect(self.update_zoom_status)
            initial_view.emit_current_zoom_level() # Request initial emit
            
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

    def update_zoom_status(self, scale_factor: float):
        self.zoom_status_label.setText(f"Zoom: {scale_factor * 100:.1f}%")

    def set_project(self, project: AIEProject):
        # Disconnect from the old project's view's signal
        # Check if self._project exists and has a view first
        if hasattr(self, '_project') and self._project:
            old_view = self._project.get_graphics_view()
            if old_view and isinstance(old_view, AIEGraphicsView):
                try:
                    old_view.zoom_level_changed.disconnect(self.update_zoom_status)
                except TypeError: # indicates not connected or already disconnected
                    pass
        
        self._project = project # project is a new AIEProject instance
        
        new_view = self._project.get_graphics_view()
        self.setCentralWidget(new_view) # Set the new view as central widget
        self.layers_dock_widget.setWidget(self._project.get_layers_widget())

        # Connect to the new project's view's signal
        if new_view: # Should always be true if project is valid
            new_view.zoom_level_changed.connect(self.update_zoom_status)
            new_view.emit_current_zoom_level() # Request emit for new project's view

    def get_project(self):
        return self._project

    def open_project(self):
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
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        )
        dlg = create_open_file_dialog(default_dir, "Image files (*.jpg *.png)")

        try:
            if dlg.exec():
                filepath = dlg.selectedFiles()[0]
                image = QImage(filepath)
                image_name = Path(filepath).stem
                self._project.add_image_layer(image, image_name)
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def save_image(self):
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        )
        dlg = create_save_file_dialog(default_dir, "Image files (*.jpg *.png)")

        try:
            if dlg.exec():
                filepath = dlg.selectedFiles()[0]
                image = self._project.render()
                image.save(filepath)
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def add_gaussian_blur_to_selected_layer(self):
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
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation
        )
        dlg = create_open_file_dialog(default_dir, "Photoshop Files (*.psd)")
        if dlg.exec():
            filepath = dlg.selectedFiles()[0]
            self.set_project(load_psd_as_project(filepath))

    def setup_file_menu(self):
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
        menu = QMenu("Filters", self)
        menu.addAction("Gaussian Blur", self.add_gaussian_blur_to_selected_layer)
        
        brightness_contrast_action = menu.addAction("Brightness/Contrast...")
        brightness_contrast_action.triggered.connect(self.open_brightness_contrast_dialog)
        
        self.menuBar().addMenu(menu)

    def open_brightness_contrast_dialog(self):
        scene = self._project.get_graphics_scene()
        selected_items = scene.selectedItems()

        if not selected_items:
            QMessageBox.information(self, "Information", "Please select an image layer first.")
            return

        if len(selected_items) > 1:
            QMessageBox.information(self, "Information", "Please select only one image layer.")
            return
            
        current_item = selected_items[0]
        if not isinstance(current_item, AIEImageItem):
            QMessageBox.information(self, "Information", "Brightness/Contrast can only be applied to image layers.")
            return
        
        dialog = BrightnessContrastDialog(self) # Pass parent
        # Optional: Set initial dialog values from item if needed in future, e.g. dialog.set_values(...)
        
        if dialog.exec(): # This shows the dialog modally
            values = dialog.get_values()
            brightness = values["brightness"]
            contrast = values["contrast"]
            
            original_image = current_item.image
            modified_image = apply_brightness_contrast(original_image, brightness, contrast)
            
            if not modified_image.isNull():
                current_item.setImage(modified_image)
                # Note: The TreeView thumbnail update is a potential refinement.
                # For now, the main scene item updates.
                print(f"Applied Brightness: {brightness}, Contrast: {contrast} to layer: {current_item.name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to apply brightness/contrast.")
        else:
            print("Brightness/Contrast dialog cancelled.")
