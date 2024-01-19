"""
Created: January, 2024

@author: tsalemink
"""
from cmlibs.widgets.handlers.keyactivatedhandler import KeyActivatedHandler
from cmlibs.widgets.errors import HandlerError
from cmlibs.maths.vectorops import sub, mult, dot

from mapclientplugins.meshprojectionstep.utils import create_plane_normal_indicator, get_glyph_position, set_glyph_position, \
    calculate_centroid, translate_nodes


class Normal(KeyActivatedHandler):

    def __init__(self, key_code):
        super().__init__(key_code)

        self._model = None
        self._glyph = None
        self._default_material = None
        self._selected_material = None
        self._start_position = None

    def set_model(self, model):
        attributes = ['get_projection_plane_region', 'set_rotation_point', 'set_plane_normal', 'get_plane_normal', 'get_plane_normal_field']
        if all(hasattr(model, attr) for attr in attributes):
            self._model = model

            region = model.get_projection_plane_region()
            normal_field = model.get_plane_normal_field()
            self._glyph = create_plane_normal_indicator(region, normal_field)
            self._initialise_materials()

        else:
            raise HandlerError('Given model does not have the required API for handling translation.')

    def _initialise_materials(self):
        context = self._model.get_projection_plane_region().getContext()
        material_module = context.getMaterialmodule()
        self._default_material = material_module.findMaterialByName('orange')
        self._selected_material = material_module.findMaterialByName('red')

    def enter(self):
        self._glyph.setVisibilityFlag(True)
        self._glyph.setMaterial(self._default_material)

        centroid = calculate_centroid(self._model.get_projection_plane_region()).tolist()
        set_glyph_position(self._glyph, centroid)

    def leave(self):
        self._glyph.setVisibilityFlag(False)

    def mouse_press_event(self, event):
        super().mouse_press_event(event)

        pixel_scale = self._scene_viewer.get_pixel_scale()
        x, y = event.x() * pixel_scale, event.y() * pixel_scale
        self._start_position = [x, y]

        graphic = self._scene_viewer.get_nearest_graphics_point(x, y)
        if graphic and graphic.isValid() and graphic == self._glyph:
            graphic.setMaterial(self._selected_material)

    def mouse_move_event(self, event):
        if self._glyph.getMaterial().getName() == self._selected_material.getName():
            pixel_scale = self._scene_viewer.get_pixel_scale()
            x = event.x() * pixel_scale
            y = event.y() * pixel_scale
            pos = get_glyph_position(self._glyph)
            screen_pos = self._scene_viewer.project(pos[0], pos[1], pos[2])
            global_cur_pos = self._scene_viewer.unproject(x, -y, screen_pos[2])
            global_old_pos = self._scene_viewer.unproject(self._start_position[0], -self._start_position[1], screen_pos[2])
            global_pos_diff = sub(global_cur_pos, global_old_pos)

            n = self._model.get_plane_normal()
            proj_n = mult(n, dot(global_pos_diff, n))

            scene = self._glyph.getScene()
            scene.beginChange()

            translate_nodes(self._model.get_projection_plane_region(), proj_n)
            centroid = calculate_centroid(self._model.get_projection_plane_region()).tolist()
            if centroid is not None:
                self._model.set_rotation_point(centroid)
                set_glyph_position(self._glyph, centroid)

            scene.endChange()
            self._start_position = [x, y]
        else:
            super(Normal, self).mouse_move_event(event)

    def mouse_release_event(self, event):
        super().mouse_release_event(event)

        self._glyph.setMaterial(self._default_material)
        self._start_position = None
