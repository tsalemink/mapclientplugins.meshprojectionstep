"""
Created: December, 2023

@author: tsalemink
"""
from math import cos, sin, sqrt, acos, pi

from cmlibs.widgets.handlers.keyactivatedhandler import KeyActivatedHandler
from cmlibs.widgets.errors import HandlerError
from cmlibs.maths.vectorops import cross, sub, normalize, axis_angle_to_rotation_matrix

from mapclientplugins.meshprojectionstep.utils import create_plane_manipulation_sphere, get_glyph_position, set_glyph_position, \
    rotate_nodes, calculate_line_plane_intersection, calculate_normal, mesh_nodes_coordinates, point_within_plane_boundaries


class Orientation(KeyActivatedHandler):

    def __init__(self, key_code):
        super().__init__(key_code)

        self._model = None
        self._glyph = None
        self._default_material = None
        self._selected_material = None
        self._start_position = None

    def set_model(self, model):
        attributes = ['get_projection_plane_region', 'get_rotation_point', 'set_rotation_point', 'get_plane_normal', 'set_plane_normal']
        if all(hasattr(model, attr) for attr in attributes):
            self._model = model

            self._glyph = create_plane_manipulation_sphere(model.get_projection_plane_region())
            self._initialise_materials()

        else:
            raise HandlerError('Given model does not have the required API for handling orientation.')

    def _initialise_materials(self):
        context = self._model.get_projection_plane_region().getContext()
        material_module = context.getMaterialmodule()
        self._default_material = material_module.findMaterialByName('blue')
        self._selected_material = material_module.findMaterialByName('red')

    def enter(self):
        self._glyph.setVisibilityFlag(True)
        self._glyph.setMaterial(self._default_material)

        rotation_point = self._model.get_rotation_point()
        set_glyph_position(self._glyph, rotation_point)

    def leave(self):
        self._glyph.setVisibilityFlag(False)

    def mouse_press_event(self, event):
        super().mouse_press_event(event)

        pixel_scale = self._scene_viewer.get_pixel_scale()
        x, y = event.x() * pixel_scale, event.y() * pixel_scale
        self._start_position = [x, y]

        graphic = self._scene_viewer.get_nearest_graphics_point(x, y)
        if graphic and graphic.isValid():
            graphic.setMaterial(self._selected_material)

    def mouse_move_event(self, event):
        if self._start_position:
            scene = self._zinc_sceneviewer.getScene()
            scene.beginChange()

            pixel_scale = self._scene_viewer.get_pixel_scale()
            x = event.x() * pixel_scale
            y = event.y() * pixel_scale

            if self._glyph.getMaterial().getName() == self._selected_material.getName():
                far_plane_point = self._scene_viewer.unproject(x, -y, -1.0)
                near_plane_point = self._scene_viewer.unproject(x, -y, 1.0)
                point_on_plane = calculate_line_plane_intersection(near_plane_point, far_plane_point, self._model.get_rotation_point(),
                                                                   self._model.get_plane_normal())
                if point_on_plane is not None:
                    corners = mesh_nodes_coordinates(self._model.get_projection_plane_region())
                    if point_within_plane_boundaries(point_on_plane, corners):
                        set_glyph_position(self._glyph, point_on_plane)
                        self._model.set_rotation_point(point_on_plane)

            else:
                width = self._scene_viewer.width()
                height = self._scene_viewer.height()
                radius = min([width, height]) / 2.0
                delta_x = float(x - self._start_position[0])
                delta_y = float(y - self._start_position[1])
                tangent_dist = sqrt((delta_x * delta_x + delta_y * delta_y))
                if tangent_dist > 0.0:
                    dx = -delta_y / tangent_dist
                    dy = delta_x / tangent_dist

                    d = dx * (x - 0.5 * (width - 1)) + dy * (y - 0.5 * (height - 1))
                    if d > radius:
                        d = radius
                    if d < -radius:
                        d = -radius

                    phi = acos(d / radius) - 0.5 * pi
                    angle = 1.0 * tangent_dist / radius

                    eye, lookat, up, _ = self._scene_viewer.get_view_parameters()

                    b = up[:]
                    b = normalize(b)
                    a = sub(lookat, eye)
                    a = normalize(a)
                    c = cross(b, a)
                    c = normalize(c)
                    e = [None, None, None]
                    e[0] = dx * c[0] + dy * b[0]
                    e[1] = dx * c[1] + dy * b[1]
                    e[2] = dx * c[2] + dy * b[2]
                    axis = [None, None, None]
                    axis[0] = sin(phi) * a[0] + cos(phi) * e[0]
                    axis[1] = sin(phi) * a[1] + cos(phi) * e[1]
                    axis[2] = sin(phi) * a[2] + cos(phi) * e[2]

                    # Calculate the rotation matrix.
                    rotation_matrix = axis_angle_to_rotation_matrix(axis, angle)
                    rotation_point = self._model.get_rotation_point()

                    rotate_nodes(self._model.get_projection_plane_region(), rotation_matrix, rotation_point)
                    _, normal = calculate_normal(self._model.get_projection_plane_region())

                    self._model.set_plane_normal(normal)
                    self._start_position = [x, y]

            scene.endChange()

    def mouse_release_event(self, event):
        super().mouse_release_event(event)

        self._glyph.setMaterial(self._default_material)
        self._start_position = None
