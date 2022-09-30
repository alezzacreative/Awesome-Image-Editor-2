import traceback
from pathlib import Path

from PySide6.QtCore import (
    QStandardPaths,
    Qt,
    QFile,
    QIODevice,
    QDataStream
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

from .dialogs.gaussian_blur import GaussianBlurDialog
from .graphics_scene.model import QGraphicsSceneModel, QGraphicsImageItem, QGraphicsSceneCustom
from .psd_read import graphics_scene_from_psd
from .widgets.layers import LayersWidget

__all__ = ("MainWindow",)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Awesome Image Editor")

        self.graphics_scene = QGraphicsSceneCustom()
        self.graphics_scene_model = QGraphicsSceneModel(self.graphics_scene)
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.graphics_view)

        self.setup_file_menu()
        self.setup_filters_menu()

        self.layers_widget = LayersWidget(self.graphics_scene_model)
        self.layers_dock_widget = QDockWidget()
        self.layers_dock_widget.setWindowTitle("Layers")
        self.layers_dock_widget.setWidget(self.layers_widget)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.layers_dock_widget, Qt.Orientation.Vertical
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

        file = QFile(filepath)
        file.open(QIODevice.ReadOnly)
        data_stream = QDataStream(file)
        chunk_type = data_stream.readString()
        assert chunk_type == QGraphicsSceneCustom.CHUNK_TYPE

        # TODO: refactor and allow loading multiple projects at once
        # and switching between them via tabs
        scene = QGraphicsSceneCustom.deserialize(data_stream)

        self.graphics_scene_model = QGraphicsSceneModel(scene)
        self.graphics_scene = scene
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.graphics_view)

        self.layers_widget = LayersWidget(self.graphics_scene_model)
        self.layers_dock_widget.setWidget(self.layers_widget)

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

        file = QFile(filepath)
        file.open(QIODevice.WriteOnly)
        data_stream = QDataStream(file)
        self.graphics_scene.serialize(data_stream)

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
            self.graphics_scene.setSceneRect(self.graphics_scene.itemsBoundingRect())
            image = QImage(
                self.graphics_scene.sceneRect().size().toSize(),
                QImage.Format.Format_ARGB32_Premultiplied,
            )
            assert image is not None  # In case creation of image fails
            image.fill(Qt.GlobalColor.transparent)

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

        scene = graphics_scene_from_psd(filepath)
        self.graphics_scene_model = QGraphicsSceneModel(scene)
        self.graphics_scene = scene
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.graphics_view)

        self.layers_widget = LayersWidget(self.graphics_scene_model)
        self.layers_dock_widget.setWidget(self.layers_widget)

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
