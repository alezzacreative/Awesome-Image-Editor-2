import traceback
from pathlib import Path

from PySide6.QtCore import (
    QStandardPaths,
    Qt
)
from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QGraphicsView,
    QMainWindow,
    QMenu,
    QMessageBox,
    QGraphicsBlurEffect
)

from .dailogs.gaussian_blur import GaussianBlurDialog
from .widgets.graphics_scene import GraphicsSceneModel, QGraphicsImageItem
from .widgets.layers import LayersView

__all__ = ("MainWindow",)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Awesome Image Editor")

        self.graphics_scene_model = GraphicsSceneModel()
        self.graphics_scene = self.graphics_scene_model.graphics_scene
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.graphics_view)

        self.setup_file_menu()
        self.setup_filters_menu()

        layers_widget = LayersView(self.graphics_scene_model)
        dock_widget = QDockWidget()
        dock_widget.setWindowTitle("Layers")
        dock_widget.setWidget(layers_widget)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, dock_widget, Qt.Orientation.Vertical
        )

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
            self.graphics_scene.addItem(QGraphicsImageItem(image, image_name))
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
            image = QImage(
                self.graphics_scene.sceneRect().size().toSize(),
                QImage.Format.Format_ARGB32_Premultiplied,
            )
            assert image is not None

            painter = QPainter(image)
            self.graphics_scene.render(painter)
            # NOTE: End painter explicitly to fix "QPaintDevice: Cannot destroy paint device that is being painted"
            painter.end()
            image.save(filepath)
        except:
            QMessageBox.critical(self, "Error", traceback.format_exc())

    def add_gaussian_blur_to_selected_layer(self):
        if len(self.graphics_scene.selectedItems()) == 0:
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

        selected_item = self.graphics_scene.selectedItems()[0]
        selected_item.setGraphicsEffect(effect)
        dlg.rejected.connect(lambda: selected_item.setGraphicsEffect(None))
        dlg.accepted.connect(lambda: effect.setEnabled(True))

        dlg.show()

    def setup_file_menu(self):
        menu = QMenu("File", self)
        menu.addAction("Open Image", self.open_image)
        menu.addAction("Save Image", self.save_image)
        self.menuBar().addMenu(menu)

    def setup_filters_menu(self):
        menu = QMenu("Filters", self)
        menu.addAction("Gaussian Blur", self.add_gaussian_blur_to_selected_layer)
        self.menuBar().addMenu(menu)
