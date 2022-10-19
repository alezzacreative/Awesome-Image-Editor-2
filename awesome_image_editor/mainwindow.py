import traceback
from pathlib import Path

from PyQt6.QtCore import (
    QStandardPaths,
    Qt,
)
from PyQt6.QtGui import QImage, QFont
from PyQt6.QtWidgets import (
    QDockWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QGraphicsBlurEffect,
    QToolBar
)

from .dialogs.gaussian_blur import GaussianBlurDialog
from .file_format import AIEProject
from .psd_read import load_psd_as_project
from .file_dialog import create_open_file_dialog, create_save_file_dialog

__all__ = ("MainWindow",)


class MainWindow(QMainWindow):
    def __init__(self):
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
        self._project = project
        self.setCentralWidget(self._project.get_graphics_view())
        self.layers_dock_widget.setWidget(self._project.get_layers_widget())

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
        self.menuBar().addMenu(menu)
