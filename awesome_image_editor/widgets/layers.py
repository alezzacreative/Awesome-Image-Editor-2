from pathlib import PurePath

from PyQt6.QtCore import Qt, QRectF, QPointF # For Qt.GlobalColor, QRectF, QPointF
from PyQt6.QtGui import QAction, QIcon, QImage, QPainter
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QSlider, QDoubleSpinBox, 
                             QToolBar, QVBoxLayout, QWidget)

from ..model_view.items.image import AIEImageItem # Should be there
from ..model_view.tree_model import TreeModel
from ..model_view.tree_view import TreeView


class LayersWidget(QWidget):
    def __init__(self, model: TreeModel):
        super().__init__()
        self._model = model
        self.list_view = TreeView(model)
        layout = QVBoxLayout()
        layout.addWidget(self.list_view)
        layout.setContentsMargins(0, 0, 0, 0)

        # Opacity controls (defined before toolbar, but added to layout later)
        opacity_container = QWidget()
        opacity_layout = QHBoxLayout(opacity_container)
        opacity_layout.setContentsMargins(5, 2, 5, 2) # Adjust margins as needed
        opacity_layout.setSpacing(5) # Add spacing between widgets

        opacity_label = QLabel("Opacity:")
        opacity_layout.addWidget(opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setEnabled(False)
        self.opacity_slider.setToolTip("Adjust layer opacity (0-100%)")
        opacity_layout.addWidget(self.opacity_slider)

        self.opacity_spinbox = QDoubleSpinBox()
        self.opacity_spinbox.setRange(0.0, 1.0)
        self.opacity_spinbox.setSingleStep(0.01)
        self.opacity_spinbox.setDecimals(2)
        self.opacity_spinbox.setValue(1.0)
        self.opacity_spinbox.setEnabled(False)
        self.opacity_spinbox.setToolTip("Adjust layer opacity (0.00-1.00)")
        opacity_layout.addWidget(self.opacity_spinbox)

        # Toolbar (defined now, added to layout after opacity controls)
        self.toolbar = QToolBar()
        # self.toolbar.setLayoutDirection(Qt.LayoutDirection.RightToLeft) # Removed for horizontal toolbar

        icon = QIcon(
            (
                PurePath(__file__).parent.parent / "icons" / "layers" / "delete_btn.svg"
            ).as_posix()
        )
        self.toolbar.addAction(icon, "Delete", self.delete_selected_items)

        # Add Duplicate Layer action
        duplicate_icon_path = (
            PurePath(__file__).parent.parent / "icons" / "layers" / "duplicate_layer_btn.svg"
        ).as_posix()
        duplicate_action = QAction(QIcon(duplicate_icon_path), "Duplicate Selected Layer", self)
        duplicate_action.triggered.connect(self.duplicate_selected_layer)
        self.toolbar.addAction(duplicate_action)

        # Add Create Layer Mask action
        mask_icon_path = (
            PurePath(__file__).parent.parent / "icons" / "layers" / "create_mask_btn.svg"
        ).as_posix()
        mask_action = QAction(QIcon(mask_icon_path), "Create Layer Mask", self)
        mask_action.triggered.connect(self.create_layer_mask_for_selected_layer)
        self.toolbar.addAction(mask_action)

        # Add Merge Down action
        merge_down_action = QAction("Merge Down", self) # No icon specified, text only
        merge_down_action.setToolTip("Merge selected layer with the one below it")
        merge_down_action.triggered.connect(self.merge_down_selected_layer)
        self.toolbar.addAction(merge_down_action)
        
        # Add widgets to main layout in the new order
        layout.addWidget(opacity_container) 
        layout.addWidget(self.toolbar) # Toolbar is now at the bottom

        self.setLayout(layout)

        # Connect signals
        # Listen to selection changes in the QGraphicsScene directly, as it's more reliable
        # for getting the QGraphicsItem. TreeView selection might need more complex mapping.
        self._model.scene().selectionChanged.connect(self._update_opacity_controls_from_selection)
        self.opacity_slider.valueChanged.connect(self._on_opacity_slider_changed)
        self.opacity_spinbox.valueChanged.connect(self._on_opacity_spinbox_changed)


    def _get_selected_image_item(self) -> AIEImageItem | None:
        """
        Retrieves the currently selected AIEImageItem from the QGraphicsScene.
        Returns the item if exactly one AIEImageItem is selected, otherwise None.
        """
        selected_scene_items = self._model.scene().selectedItems()
        if len(selected_scene_items) == 1:
            item = selected_scene_items[0]
            if isinstance(item, AIEImageItem):
                return item
        return None

    def _update_opacity_controls_from_selection(self):
        """
        Updates the opacity controls (slider and spinbox) based on the
        currently selected AIEImageItem in the scene.
        """
        selected_item = self._get_selected_image_item()
        if selected_item:
            self.opacity_slider.setEnabled(True)
            self.opacity_spinbox.setEnabled(True)

            current_opacity = selected_item.opacity()

            # Block signals to prevent feedback loops
            self.opacity_slider.blockSignals(True)
            self.opacity_spinbox.blockSignals(True)

            self.opacity_slider.setValue(int(current_opacity * 100))
            self.opacity_spinbox.setValue(current_opacity)

            # Unblock signals
            self.opacity_slider.blockSignals(False)
            self.opacity_spinbox.blockSignals(False)
        else:
            self.opacity_slider.setEnabled(False)
            self.opacity_spinbox.setEnabled(False)
            
            # Optionally reset to defaults when no valid item is selected
            self.opacity_slider.blockSignals(True)
            self.opacity_spinbox.blockSignals(True)
            
            self.opacity_slider.setValue(100) # Default slider value
            self.opacity_spinbox.setValue(1.0) # Default spinbox value

            self.opacity_slider.blockSignals(False)
            self.opacity_spinbox.blockSignals(False)

    def _on_opacity_slider_changed(self, value: int):
        """
        Handles value changes from the opacity slider.
        Updates the selected AIEImageItem's opacity and the spinbox value.
        """
        selected_item = self._get_selected_image_item()
        if selected_item:
            opacity = value / 100.0
            selected_item.setOpacity(opacity) # This should call item.update()

            # Update spinbox, blocking its signals
            self.opacity_spinbox.blockSignals(True)
            self.opacity_spinbox.setValue(opacity)
            self.opacity_spinbox.blockSignals(False)
            
            # item.update() called by setOpacity should be sufficient.
            # If not, self._model.scene().update() can be used.

    def _on_opacity_spinbox_changed(self, value: float):
        """
        Handles value changes from the opacity spinbox.
        Updates the selected AIEImageItem's opacity and the slider value.
        """
        selected_item = self._get_selected_image_item()
        if selected_item:
            opacity = value
            selected_item.setOpacity(opacity) # This should call item.update()

            # Update slider, blocking its signals
            self.opacity_slider.blockSignals(True)
            self.opacity_slider.setValue(int(opacity * 100))
            self.opacity_slider.blockSignals(False)

            # item.update() called by setOpacity should be sufficient.

    def delete_selected_items(self):
        self._model.beginResetModel()
        scene = self._model.scene()
        for item in scene.selectedItems():
            scene.removeItem(item)
        self._model.endResetModel()
        scene.setSceneRect(scene.itemsBoundingRect())

    def duplicate_selected_layer(self):
        selected_graphics_items = self._model.scene().selectedItems()

        if not selected_graphics_items:
            print("No layer selected to duplicate.")
            return

        selected_graphics_items.reverse()  # Process from bottom-most to top-most

        newly_added_items = []
        for current_item in selected_graphics_items:
            if isinstance(current_item, AIEImageItem):
                copied_image = current_item.image.copy()
                new_name = f"{current_item.name} copy"
                # Basic uniqueness check might be needed here if names must be unique in the model/scene

                duplicated_item = AIEImageItem(copied_image, new_name)
                duplicated_item.setPos(current_item.pos()) 
                duplicated_item.setVisible(current_item.isVisible())
                duplicated_item.setZValue(current_item.zValue() + 0.1) 
                duplicated_item.setOpacity(current_item.opacity()) # Copy opacity

                self._model.scene().addItem(duplicated_item)
                newly_added_items.append(duplicated_item)
                print(f"Duplicated layer: '{current_item.name}' as '{new_name}'")
            else:
                item_name = "Unknown Item"
                try: item_name = current_item.name
                except AttributeError: pass
                print(f"Skipping non-image layer: {item_name}")
        
        scene = self._model.scene() # Get scene reference
        if newly_added_items:
            scene.clearSelection()
            if newly_added_items: 
                newly_added_items[-1].setSelected(True) 
        
        scene.setSceneRect(scene.itemsBoundingRect())
        # Selection has changed, so update controls
        self._update_opacity_controls_from_selection()


    def create_layer_mask_for_selected_layer(self):
        # Use the helper to get the selected item
        current_item = self._get_selected_image_item()

        if not current_item: # _get_selected_image_item ensures it's an AIEImageItem if not None
            print("Please select a single image layer to add a mask.")
            return
        
        # No need to check isinstance(current_item, AIEImageItem) again due to _get_selected_image_item
        
        if current_item.has_mask():
            print(f"Layer '{current_item.name}' already has a mask. (Future: option to replace/delete).")
            return

        layer_image = current_item.image
        mask_image = QImage(layer_image.size(), QImage.Format.Format_Grayscale8)
        mask_image.fill(Qt.GlobalColor.white)  # Mask is initially fully revealing
        current_item.set_mask(mask_image)
        print(f"Created and assigned a new mask to layer '{current_item.name}'.")
        # Note: No direct visual change to opacity controls unless mask affects selection/opacity state.
        # self._update_opacity_controls_from_selection() # Call if mask creation affects item's properties displayed

    def merge_down_selected_layer(self):
        top_layer = self._get_selected_image_item()

        if top_layer is None:
            # _get_selected_image_item already implies single selection of AIEImageItem
            # No need for a separate message here if _get_selected_image_item is silent.
            # However, if _get_selected_image_item can return None for other reasons than no selection
            # (e.g. multiple selected, or non-AIEImageItem selected), then a message is good.
            # Assuming _get_selected_image_item is robust for "single AIEImageItem or None".
            print("Merge Down: No valid single image layer selected.")
            return

        print(f"Top layer for merge: {top_layer.name} (Z-value: {top_layer.zValue()})")

        bottom_layer = None
        max_z_below_top = -float('inf')
        
        # Ensure we are getting items from the correct scene instance
        scene = self._model.scene() 
        if not scene:
            print("Merge Down: Scene not available.")
            return
            
        all_scene_items = scene.items()

        for item in all_scene_items:
            if item is top_layer:
                continue
            if not isinstance(item, AIEImageItem):
                continue
            if item.parentItem() is not None: # Skip items part of a group
                continue

            item_z_value = item.zValue()
            if item_z_value < top_layer.zValue() and item_z_value > max_z_below_top:
                max_z_below_top = item_z_value
                bottom_layer = item
        
        if bottom_layer is None:
            print(f"Merge Down: No layer found directly below '{top_layer.name}'.")
            return

        print(f"Bottom layer for merge: {bottom_layer.name} (Z-value: {bottom_layer.zValue()})")
        
        # --- Start of Merge Rendering Logic ---

        # Calculate Combined Bounding Rectangle
        top_rect = top_layer.sceneBoundingRect()
        bottom_rect = bottom_layer.sceneBoundingRect()
        combined_rect = top_rect.united(bottom_rect)

        if combined_rect.isEmpty():
            print("Merge Down: Combined bounding rectangle is empty. Cannot merge.")
            return

        # Create New QImage for Merged Result
        # Ensure size is at least 1x1, QImage errors on zero dimension
        img_width = max(1, int(combined_rect.width()))
        img_height = max(1, int(combined_rect.height()))
        merged_image = QImage(img_width, img_height, QImage.Format.Format_ARGB32_Premultiplied)
        merged_image.fill(Qt.GlobalColor.transparent)

        # Setup QPainter
        painter = QPainter(merged_image)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

            # Draw Bottom Layer
            bottom_layer_relative_pos = bottom_layer.scenePos() - combined_rect.topLeft()
            painter.setOpacity(bottom_layer.opacity())
            # Future: painter.setCompositionMode(bottom_layer.blend_mode())
            painter.drawImage(bottom_layer_relative_pos, bottom_layer.image)
            painter.setOpacity(1.0) # Reset opacity

            # Draw Top Layer
            top_layer_relative_pos = top_layer.scenePos() - combined_rect.topLeft()
            painter.setOpacity(top_layer.opacity())
            # Future: painter.setCompositionMode(top_layer.blend_mode())
            painter.drawImage(top_layer_relative_pos, top_layer.image)
            painter.setOpacity(1.0) # Reset opacity
        finally:
            painter.end() # Ensure painter is always ended

        # Store merged_image and combined_rect.topLeft() for the next step (scene update)
        # For now, we'll just print success.
        # In the next subtask, these variables (merged_image, combined_rect.topLeft())
        # --- End of Merge Rendering Logic, Start of Scene Update ---

        # Determine Name for Merged Layer
        merged_layer_name = f"{bottom_layer.name} (merged)"
        # Consider a loop for unique name if necessary, similar to duplicate layer

        # Create New AIEImageItem for Merged Layer
        new_merged_item = AIEImageItem(merged_image, merged_layer_name)

        # Set Properties for New Merged Item
        new_merged_item.setPos(combined_rect.topLeft())
        new_merged_item.setZValue(bottom_layer.zValue()) # Merged layer takes Z of bottom layer
        new_merged_item.setVisible(top_layer.isVisible() and bottom_layer.isVisible())
        new_merged_item.setOpacity(1.0) # Visual opacity is baked in, item opacity is reset

        # Scene Manipulation
        # scene = self._model.scene() # Already have 'scene' from earlier
        
        self._model.beginResetModel() # Notify views that a major change is about to happen
                                      # This might be too coarse; specific item removal/addition signals
                                      # are often preferred if the model can handle them gracefully.
                                      # However, for complex changes like merge, it can be safer.

        scene.removeItem(top_layer)
        scene.removeItem(bottom_layer)
        scene.addItem(new_merged_item)
        
        self._model.endResetModel() # Notify views that changes are complete

        # Post-Merge Actions
        scene.clearSelection()
        new_merged_item.setSelected(True)
        scene.setSceneRect(scene.itemsBoundingRect()) # Update sceneRect after merge
        self._update_opacity_controls_from_selection() # Update UI based on new selection

        print(f"Successfully merged '{top_layer.name}' and '{bottom_layer.name}' into '{new_merged_item.name}'.")
