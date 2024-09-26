"""
Created: April, 2023

@author: tsalemink
"""
import math
import os
import json

import numpy as np
from PySide6 import QtWidgets, QtCore

from cmlibs.maths.vectorops import magnitude
from cmlibs.utils.zinc.finiteelement import is_field_defined_for_nodeset
from cmlibs.widgets.handlers.fixed import Fixed

from cmlibs.widgets.handlers.scenemanipulation import SceneManipulation
from cmlibs.widgets.handlers.sceneselection import SceneSelection
from cmlibs.widgets.handlers.orientation import Orientation
from cmlibs.widgets.handlers.fixedaxistranslation import FixedAxisTranslation
from cmlibs.widgets.handlers.zoomonly import ZoomOnly
from cmlibs.zinc.field import Field

from mapclientplugins.meshprojectionstep.view.ui_meshprojectionwidget import Ui_MeshProjectionWidget
from mapclientplugins.meshprojectionstep.scene.meshprojection import MeshProjectionScene


class ZincFieldListModel(QtCore.QAbstractListModel):

    def __init__(self):
        super().__init__()
        self._fields = []

    def rowCount(self, parent=...):
        return len(self._fields)

    def data(self, index, role=...):
        if index.isValid():
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return self._fields[index.row()].getName()
            elif role == QtCore.Qt.ItemDataRole.UserRole:
                return self._fields[index.row()]

    def populate(self, fields):
        self._fields = fields


def _get_coordinate_fields(region):
    fm = region.getFieldmodule()
    fi = fm.createFielditerator()
    field = fi.next()
    field_list = []
    while field.isValid():
        if field.isTypeCoordinate() and (field.getNumberOfComponents() == 3) and (field.castFiniteElement().isValid()):
            field_list.append(field)

        field = fi.next()

    return field_list


class MeshProjectionWidget(QtWidgets.QWidget):

    def __init__(self, model, parent=None):
        super(MeshProjectionWidget, self).__init__(parent)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

        self._ui = Ui_MeshProjectionWidget()
        self._ui.setupUi(self)

        self._model = model
        self._location = None
        self._callback = None
        self._plane_handlers_registered = False
        self._coordinate_field_list = []

        self._scene = MeshProjectionScene(model)

        self._make_connections()

        self._ui.widgetZinc.set_grab_focus(True)
        self._ui.widgetZinc.set_context(model.get_context())
        self._ui.widgetZinc.register_handler(SceneManipulation())
        self._ui.widgetZinc.register_handler(SceneSelection(QtCore.Qt.Key.Key_S))

        self._ui.widgetZincPreview.set_context(model.get_output_context())
        self._ui.widgetZincPreview.register_handler(Fixed())

        self._projected_graphics_available = False

        self._update_ui()

    def set_identifier(self, identifier):
        self._ui.labelMeshProjectionIdentifier.setText(identifier)

    def load(self, mesh_file_location):
        self._scene.setup_visualisation()
        self._load_settings()

        # self._input_hash = _generate_hash(points_file_location)
        # if self._input_hash == previous_hash:
        #     points_file_location = self.get_output_file()
        self._model.load(mesh_file_location)
        #
        # self._get_regions_fields(self._model.get_points_region(), self._points_field_list, True)
        # self._get_regions_fields(self._model.get_surfaces_region(), self._surfaces_field_list, False)
        # self._update_node_graphics_subgroup()
        self._coordinate_field_list = _get_coordinate_fields(self._model.get_mesh_region())
        self._setup_field_combo_boxes()

    def clear(self):
        pass

    def set_location(self, location):
        self._location = location

    def get_output_file(self):
        return os.path.join(self._location, "projected-mesh.exf")

    def register_done_execution(self, done_execution):
        self._callback = done_execution

    def _make_connections(self):
        self._ui.pushButtonContinue.clicked.connect(self._continue_execution)
        self._ui.pushButtonViewAll.clicked.connect(self._view_all_button_clicked)
        self._ui.widgetZinc.graphics_initialized.connect(self._zinc_widget_ready)
        self._ui.widgetZinc.pixel_scale_changed.connect(self._pixel_scale_changed)
        self._ui.widgetZinc.handler_activated.connect(self._update_label_text)
        self._ui.checkBoxSurfacesVisibility.stateChanged.connect(self._scene.set_surfaces_visibility)
        self._ui.checkBoxMeshVisibility.stateChanged.connect(self._scene.set_mesh_visibility)
        self._ui.checkBoxProjectedMeshVisibility.stateChanged.connect(self._scene.set_projected_mesh_visibility)
        self._ui.checkBoxMarkersVisibility.stateChanged.connect(self._scene.set_markers_visibility)
        self._ui.checkBoxProjectedMarkersVisibility.stateChanged.connect(self._scene.set_projected_markers_visibility)
        self._ui.spinBoxNodeSize.valueChanged.connect(self._scene.set_node_size)
        self._ui.spinBoxPlaneAlpha.valueChanged.connect(self._scene.set_plane_alpha)
        self._ui.sliderFinalOrientation.valueChanged.connect(self._final_orientation_value_changed)
        self._ui.pushButtonAutoAlignPlane.clicked.connect(self._auto_align_clicked)
        self._ui.pushButtonProject.clicked.connect(self._project_clicked)

    def _update_ui(self):
        surface_graphics_available = self._scene.are_surface_graphics_available()
        self._ui.checkBoxSurfacesVisibility.setEnabled(surface_graphics_available)
        self._ui.pushButtonProject.setEnabled(surface_graphics_available)

        self._ui.checkBoxProjectedMeshVisibility.setEnabled(self._projected_graphics_available)
        self._ui.checkBoxProjectedMarkersVisibility.setEnabled(self._projected_graphics_available)
        self._ui.sliderFinalOrientation.setEnabled(self._projected_graphics_available)

    def _register_plane_handlers(self):
        if not self._plane_handlers_registered:
            self._plane_handlers_registered = True
            orientation_handler = Orientation(QtCore.Qt.Key.Key_O)
            orientation_handler.set_model(self._model)
            self._ui.widgetZinc.register_handler(orientation_handler)

            normal_handler = FixedAxisTranslation(QtCore.Qt.Key.Key_T)
            normal_handler.set_model(self._model)
            self._ui.widgetZinc.register_handler(normal_handler)

    def _setup_field_combo_boxes(self):
        node_fields = []
        datapoint_fields = []
        for field in self._coordinate_field_list:
            if is_field_defined_for_nodeset(field, nodeset_domain=Field.DOMAIN_TYPE_NODES):
                node_fields.append(field)
            if is_field_defined_for_nodeset(field, nodeset_domain=Field.DOMAIN_TYPE_DATAPOINTS):
                datapoint_fields.append(field)

        node_model = ZincFieldListModel()
        node_model.populate(node_fields)

        datapoint_model = ZincFieldListModel()
        datapoint_model.populate(datapoint_fields)

        self._ui.comboBoxNodeCoordinateField.setModel(node_model)
        self._ui.comboBoxDatapointCoordinateField.setModel(datapoint_model)
        self._ui.comboBoxNodeCoordinateField.currentTextChanged.connect(self._update_node_coordinates_field)
        self._ui.comboBoxDatapointCoordinateField.currentTextChanged.connect(self._update_datapoint_coordinates_field)
        self._update_node_coordinates_field()
        self._update_datapoint_coordinates_field()

    def _update_node_coordinates_field(self):
        self._model.set_mesh_coordinates(self._ui.comboBoxNodeCoordinateField.currentData())
        self._scene.update_mesh_coordinates(self._ui.comboBoxNodeCoordinateField.currentData())

    def _update_datapoint_coordinates_field(self):
        datapoint_coordinates_field = self._ui.comboBoxDatapointCoordinateField.currentData()
        if datapoint_coordinates_field:
            self._scene.update_datapoint_coordinates(datapoint_coordinates_field)

    def _settings_file(self):
        return os.path.join(self._location, 'settings.json')

    def _write(self):
        if not os.path.exists(self._location):
            os.makedirs(self._location)

        node_coordinate_field_name, datapoint_coordinate_field_name = self._current_coordinate_field_names()
        theta = self._ui.sliderFinalOrientation.value() * math.pi / 180
        self._model.write_projected_mesh(self.get_output_file(), node_coordinate_field_name, datapoint_coordinate_field_name, theta)
        self._reset_projection()

    def _reset_projection(self):
        self._projected_graphics_available = False
        self._model.reset_projection_region()

    def _update_label_text(self):
        handler_label_map = {"SceneManipulation": "View", "SceneSelection": "Selection", "FixedAxisTranslation": "Translation"}
        handler_label = self._ui.widgetZinc.active_handler().get_mode()
        if handler_label in handler_label_map:
            handler_label = handler_label_map[handler_label]
        self._scene.update_label_text("Mode: " + handler_label)

    def _zinc_widget_ready(self):
        self._ui.widgetZinc.set_selection_filter(self._model.get_selection_filter())

    def _pixel_scale_changed(self, scale):
        self._scene.set_pixel_scale(scale)

    def _calculate_plane_size(self):
        minima, maxima = self._model.evaluate_nodes_minima_and_maxima()
        return magnitude([maxima[0] - minima[0], maxima[1] - minima[1], maxima[2] - minima[2]])

    def _auto_align_clicked(self):
        data_points = self._model.mesh_nodes_coordinates()
        point_on_plane, plane_normal = _calculate_best_fit_plane(data_points)
        plane_size = self._calculate_plane_size()
        self._create_projection_plane(point_on_plane, plane_normal, plane_size)

    def _create_projection_plane(self, point_on_plane, plane_normal, plane_size):
        self._model.create_projection_plane(point_on_plane, plane_normal, plane_size)
        self._scene.create_projection_plane()
        self._register_plane_handlers()
        self._update_ui()

    def _current_coordinate_field_names(self):
        node_coordinate_field_name = self._ui.comboBoxNodeCoordinateField.currentData().getName()
        datapoint_coordinate_field = self._ui.comboBoxDatapointCoordinateField.currentData()
        # If no datapoint coordinate field is defined set the default that is going to be used anyway.
        datapoint_coordinate_field_name = datapoint_coordinate_field.getName() if datapoint_coordinate_field else "coordinates"
        return node_coordinate_field_name, datapoint_coordinate_field_name

    def _update_preview(self):
        node_coordinate_field_name, datapoint_coordinate_field_name = self._current_coordinate_field_names()
        theta = self._ui.sliderFinalOrientation.value() * math.pi / 180
        preview_region = self._model.preview_projected_mesh(node_coordinate_field_name, datapoint_coordinate_field_name, theta)
        preview_scene = self._scene.visualise_preview(preview_region, node_coordinate_field_name, datapoint_coordinate_field_name)
        self._ui.widgetZincPreview.set_scene(preview_scene)
        self._ui.widgetZincPreview.view_all()

    def _project_clicked(self):
        self._projected_graphics_available = True
        node_coordinate_field_name, datapoint_coordinate_field_name = self._current_coordinate_field_names()
        self._model.project(node_coordinate_field_name, datapoint_coordinate_field_name)
        self._scene.visualise_projected_graphics(node_coordinate_field_name, datapoint_coordinate_field_name)

        self._update_preview()

        # Use check-box states for visibility.
        self._scene.set_projected_mesh_visibility(self._ui.checkBoxProjectedMeshVisibility.isChecked())
        self._scene.set_projected_markers_visibility(self._ui.checkBoxProjectedMarkersVisibility.isChecked())

        self._update_ui()

    def _final_orientation_value_changed(self, value):
        self._ui.sliderFinalOrientation.setToolTip(f"{value} (degrees)")
        self._update_preview()

    def _view_all_button_clicked(self):
        self._ui.widgetZinc.view_all()

    def _continue_execution(self):
        self._save_settings()
        self._remove_ui_region()
        self._write()
        self._callback()

    def _remove_ui_region(self):
        self._model.reset_label_region()

    def _load_settings(self):
        if os.path.isfile(self._settings_file()):
            with open(self._settings_file()) as f:
                settings = json.load(f)

            if "node_size" in settings:
                self._ui.spinBoxNodeSize.setValue(settings["node_size"])
                self._scene.set_node_size(settings["node_size"])
            if "alpha" in settings:
                self._ui.spinBoxPlaneAlpha.setValue(settings["alpha"])
                self._scene.set_plane_alpha(settings["alpha"])

            if "plane_size" in settings:
                plane_size = settings["plane_size"]
                plane_rotation_point = settings["plane_rotation_point"]
                plane_normal = settings["plane_normal"]
                self._create_projection_plane(plane_rotation_point, plane_normal, plane_size)

            self._ui.sliderFinalOrientation.blockSignals(True)
            value = settings.get("final_orientation", 0.0)
            self._ui.sliderFinalOrientation.setValue(value)
            self._ui.sliderFinalOrientation.setToolTip(f"{value} (degrees)")
            self._ui.sliderFinalOrientation.blockSignals(False)

    def _save_settings(self):
        if not os.path.exists(self._location):
            os.makedirs(self._location)

        plane = self._model.get_plane()

        settings = {
            "node_size": self._ui.spinBoxNodeSize.value(),
            "alpha": self._ui.spinBoxPlaneAlpha.value(),
            "plane_size": self._calculate_plane_size(),
            "plane_rotation_point": plane.getRotationPoint(),
            "plane_normal": plane.getNormal(),
            "final_orientation": self._ui.sliderFinalOrientation.value(),
        }

        with open(self._settings_file(), "w") as f:
            json.dump(settings, f)


def _calculate_best_fit_plane(points):
    actual_points = np.array(points).transpose()
    centroid = np.mean(actual_points, axis=1, keepdims=True)
    # subtract out the centroid and take the SVD
    U, S, Vh = np.linalg.svd(actual_points - centroid)

    return centroid.reshape(-1).tolist(), U[:, -1].tolist()
