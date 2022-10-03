import traceback
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import (
    QStandardPaths,
    Qt,
)
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QGraphicsBlurEffect
)

from .dialogs.gaussian_blur import GaussianBlurDialog
from .file_format import AIEProject
from .graphics_scene.items.image import QGraphicsImageItem
from .graphics_scene.model import QGraphicsSceneCustom
from .psd_read import load_project_from_psd

__all__ = ("MainWindow",)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Awesome Image Editor")
        self.setup_file_menu()
        self.setup_filters_menu()

        self._project: Optional[AIEProject] = None

        self.layers_dock_widget = QDockWidget("Layers")
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.layers_dock_widget, Qt.Orientation.Vertical
        )

        scene = QGraphicsSceneCustom()
        self.set_project(AIEProject(scene))

        # TODO: toolbar with tools
        # toolbar = QToolBar()
        # toolbar.setOrientation(Qt.Vertical)
        # toolbar.setMovable(False)
        # toolbar_font = QFont()
        # toolbar_font.setPointSize(17)
        # toolbar.setFont(toolbar_font)

        # # Blur
        # toolbar.addAction("Blur", lambda: ...)
        # blur_widget = LinkedSliderSpinBox(100, 0, 1000)
        # toolbar.addWidget(blur_widget)

        # self.addToolBar(Qt.LeftToolBarArea, toolbar)

        self.showMaximized()

    def set_project(self, project: AIEProject):
        self._project = project
        self.setCentralWidget(self._project.graphics_view)
        self.layers_dock_widget.setWidget(self._project.layers_widget)

    def get_project(self):
        return self._project

    def open_project(self):
        filepath, chosen_filter = QFileDialog.getOpenFileName(
            self,
            "Open",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            ),
            "Awesome Image Editor Project (*.aie)",
        )
        if not filepath:
            return

        with open(filepath, "rb") as file:
            self.set_project(AIEProject.deserialize(file))

    def save_as_project(self):
        filepath, chosen_filter = QFileDialog.getSaveFileName(
            self,
            "Save as",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            ),
            "Awesome Image Editor Project (*.aie)",
        )
        if not filepath:
            return

        if self._project is None:
            return

        with open(filepath, "wb") as file:
            self._project.serialize(file)

    def open_image(self):
        filepath, chosen_filter = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            ),
            "Image files (*.jpg *.png)",
        )
        if not filepath:
            return
        try:
            image = QImage(filepath)
            image_name = Path(filepath).stem
            self._project.graphics_scene.addItem(QGraphicsImageItem(image, image_name))
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def save_image(self):
        filepath, chosen_filter = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            ),
            "Image files (*.jpg *.png)",
        )
        if not filepath:
            return

        try:
            # Create new empty image to render the scene into
            scene = self._project.graphics_scene
            scene.setSceneRect(scene.itemsBoundingRect())
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
            image.save(filepath)
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def add_gaussian_blur_to_selected_layer(self):
        scene = self._project.graphics_scene
        if len(scene.selectedItems()) == 0:
            QMessageBox.information(self,
                                    "Warning",
                                    "No selected layers to apply effect, please select at least one layer",
                                    QMessageBox.StandardButton.Ok)
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
        filepath, chosen_filter = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            ),
            "Photoshop Files (*.psd)",
        )
        if not filepath:
            return

        self.set_project(load_project_from_psd(filepath))

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
