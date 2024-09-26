from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.zinc.field import Field
from cmlibs.zinc.glyph import Glyph
from cmlibs.zinc.material import Material
from cmlibs.zinc.graphics import Graphics
from cmlibs.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_WINDOW_PIXEL_BOTTOM_LEFT

from cmlibs.utils.zinc.field import create_field_finite_element
from cmlibs.utils.zinc.finiteelement import create_nodes


def _set_graphic_point_size(graphic, size):
    attributes = graphic.getGraphicspointattributes()
    attributes.setBaseSize(size)


def _create_text_graphics(scene, coordinate_field):
    with ChangeManager(scene):
        graphics_points = scene.createGraphicsPoints()
        graphics_points.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphics_points.setCoordinateField(coordinate_field)
        graphics_points.setScenecoordinatesystem(SCENECOORDINATESYSTEM_WINDOW_PIXEL_BOTTOM_LEFT)

    return graphics_points


def _create_surface_graphics(region):
    scene = region.getScene()
    surfaces = scene.createGraphicsSurfaces()
    surfaces.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
    surfaces.setVisibilityFlag(True)

    field_module = region.getFieldmodule()
    # material_module = scene.getMaterialmodule()
    coordinates = field_module.findFieldByName("coordinates")
    surfaces.setCoordinateField(coordinates)
    # cmiss_number = field_module.findFieldByName("cmiss_number")
    # selection_group = field_module.findFieldByName("cmiss_selection")

    # element_numbers = scene.createGraphicsPoints()
    # element_numbers.setFieldDomainType(Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION)
    # element_numbers.setCoordinateField(model_coordinates)
    # element_numbers.setSubgroupField(selection_group)
    # point_attr = element_numbers.getGraphicspointattributes()
    # point_attr.setLabelField(cmiss_number)
    # point_attr.setLabelOffset([0.3, 0.3, 0.3])
    # point_attr.setGlyphShapeType(Glyph.SHAPE_TYPE_NONE)
    # invisible_material = material_module.createMaterial()
    # invisible_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.0)
    # element_numbers.setMaterial(invisible_material)
    # element_numbers.setSelectedMaterial(material_module.findMaterialByName("green"))
    # element_numbers.setName("display_element_numbers")

    return surfaces


class MeshProjectionScene(object):

    def __init__(self, model):
        self._model = model
        self._group_graphics = []
        self._label_graphics = None
        self._surface_graphics = None
        self._surface_material = None
        self._node_graphics = None
        self._mesh_graphics = None
        self._projected_node_graphics = None
        self._projected_mesh_graphics = None
        self._marker_graphics = None
        self._preview_graphics = None
        self._projected_marker_graphics = None
        self._selection_graphics = None
        self._not_field = None
        self._pixel_scale = 1
        self._data_point_base_size = 0.15
        self._setup_label_graphic()

    def setup_visualisation(self):
        if self._node_graphics is None:
            mesh_region = self._model.get_mesh_region()
            scene = mesh_region.getScene()

            with ChangeManager(scene):
                mm = scene.getMaterialmodule()
                silver = mm.findMaterialByName('silver')
                yellow = mm.findMaterialByName('yellow')

                self._surface_material = mm.findMaterialByName('white')
                self._node_graphics = self.create_point_graphics(scene, None, None, None, Field.DOMAIN_TYPE_NODES)
                self._mesh_graphics = scene.createGraphicsLines()
                self._mesh_graphics.setMaterial(yellow)

                self._marker_graphics = self.create_point_graphics(scene, None, None, silver, Field.DOMAIN_TYPE_DATAPOINTS)

    def add_group_graphic(self, graphic):
        self._group_graphics.append(graphic)

    def _setup_label_graphic(self):
        normalised_region = self._model.get_label_region()
        normalised_scene = normalised_region.getScene()
        field_module = normalised_region.getFieldmodule()
        normalised_coordinate_field = create_field_finite_element(field_module, 'normalised', 2)
        create_nodes(normalised_coordinate_field, [[10.0, 10.0]])
        self._label_graphics = _create_text_graphics(normalised_scene, normalised_coordinate_field)

    def create_point_graphics(self, scene, finite_element_field, subgroup_field, material, domain, mode=Graphics.SELECT_MODE_DRAW_UNSELECTED):
        with ChangeManager(scene):
            graphic = scene.createGraphicsPoints()
            graphic.setFieldDomainType(domain)

            if finite_element_field:
                graphic.setCoordinateField(finite_element_field)

            graphic.setSelectMode(mode)

            if subgroup_field:
                graphic.setSubgroupField(subgroup_field)
                graphic.setName(subgroup_field.getName())

            if material:
                graphic.setMaterial(material)

            attributes = graphic.getGraphicspointattributes()
            attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
            _set_graphic_point_size(graphic, self._data_point_base_size * self._pixel_scale)

        return graphic

    def update_mesh_coordinates(self, coordinate_field):
        self._node_graphics.setCoordinateField(coordinate_field)
        self._mesh_graphics.setCoordinateField(coordinate_field)

    def update_datapoint_coordinates(self, coordinate_field):
        self._marker_graphics.setCoordinateField(coordinate_field)

    def delete_point_graphics(self, row):
        scene = self._model.get_points_region().getScene()
        scene.removeGraphics(self._group_graphics[row])
        del self._group_graphics[row]

    def set_pixel_scale(self, scale):
        self._pixel_scale = scale
        attributes = self._label_graphics.getGraphicspointattributes()
        attributes.setGlyphOffset([2.0 * scale, 0.0])
        font = attributes.getFont()
        font.setPointSize(int(font.getPointSize() * scale + 0.5))

        self._update_graphic_point_size()

    def _update_graphic_point_size(self):
        _set_graphic_point_size(self._node_graphics, self._data_point_base_size * self._pixel_scale)
        _set_graphic_point_size(self._marker_graphics, self._data_point_base_size * self._pixel_scale)

        if self._projected_node_graphics:
            _set_graphic_point_size(self._projected_node_graphics, self._data_point_base_size * self._pixel_scale)
        if self._projected_marker_graphics:
            _set_graphic_point_size(self._projected_marker_graphics, self._data_point_base_size * self._pixel_scale)

    def update_graphics_materials(self, materials):
        for (graphic, material) in zip(self._group_graphics, materials):
            graphic.setMaterial(material)

    def change_graphics_order(self, source_row, target_row):
        group_target_row = len(self._group_graphics) - 1 if target_row == -1 else target_row
        self._group_graphics.insert(group_target_row, self._group_graphics.pop(source_row))

        reference = None if target_row == -1 else self._group_graphics[target_row].getName()
        source = self._group_graphics[source_row].getName()
        points_region = self._model.get_points_region()
        scene = points_region.getScene()

        with ChangeManager(scene):
            graphic = scene.findGraphicsByName(source)
            graphic_ref = scene.findGraphicsByName(reference) if reference else scene.createGraphicsPoints()
            scene.moveGraphicsBefore(graphic, graphic_ref)
            if reference is None:
                scene.removeGraphics(graphic_ref)

    def update_label_text(self, handler_label):
        attributes = self._label_graphics.getGraphicspointattributes()
        attributes.setLabelText(1, handler_label)

    def get_node_size(self):
        return self._data_point_base_size

    def set_node_size(self, size):
        self._data_point_base_size = size
        self._update_graphic_point_size()

    def set_plane_alpha(self, value):
        self._surface_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, value)

    def are_surface_graphics_available(self):
        return self._surface_graphics is not None and self._surface_graphics.isValid()

    def set_surfaces_visibility(self, state):
        self._surface_graphics.setVisibilityFlag(state != 0)

    def set_mesh_visibility(self, state):
        self._node_graphics.setVisibilityFlag(state != 0)
        self._mesh_graphics.setVisibilityFlag(state != 0)

    def set_projected_mesh_visibility(self, state):
        if self._projected_node_graphics:
            self._projected_node_graphics.setVisibilityFlag(state != 0)
            self._projected_mesh_graphics.setVisibilityFlag(state != 0)

    def set_markers_visibility(self, state):
        self._marker_graphics.setVisibilityFlag(state != 0)

    def set_projected_markers_visibility(self, state):
        if self._projected_marker_graphics:
            self._projected_marker_graphics.setVisibilityFlag(state != 0)

    def create_projection_plane(self):
        region = self._model.get_projection_plane_region()
        self._surface_graphics = _create_surface_graphics(region)
        self._surface_graphics.setMaterial(self._surface_material)

    @staticmethod
    def visualise_preview(region, mesh_coordinate_field_name, datapoint_coordinate_field_name):
        fm = region.getFieldmodule()
        mesh_coordinates = fm.findFieldByName(mesh_coordinate_field_name)
        scene = region.getScene()
        mm = scene.getMaterialmodule()
        blue = mm.findMaterialByName('blue')

        scene = region.getScene()
        with ChangeManager(scene):
            preview_graphics = scene.createGraphicsLines()
            preview_graphics.setCoordinateField(mesh_coordinates)
            preview_graphics.setMaterial(blue)

        return scene

    def visualise_projected_graphics(self, mesh_coordinate_field_name, marker_coordinate_field_name):
        region = self._model.get_projected_region()
        fm = region.getFieldmodule()
        mesh_coordinates = fm.findFieldByName(mesh_coordinate_field_name)
        scene = region.getScene()
        mm = scene.getMaterialmodule()
        green = mm.findMaterialByName('green')
        blue = mm.findMaterialByName('blue')
        magenta = mm.findMaterialByName('magenta')

        with ChangeManager(scene):
            scene.removeAllGraphics()
            self._projected_node_graphics = self.create_point_graphics(scene, mesh_coordinates, None, green, Field.DOMAIN_TYPE_NODES)
            self._projected_mesh_graphics = scene.createGraphicsLines()
            self._projected_mesh_graphics.setCoordinateField(mesh_coordinates)
            self._projected_mesh_graphics.setMaterial(blue)

            if marker_coordinate_field_name:
                marker_coordinates = fm.findFieldByName(marker_coordinate_field_name)
                self._projected_marker_graphics = self.create_point_graphics(scene, marker_coordinates, None, magenta,
                                                                             Field.DOMAIN_TYPE_DATAPOINTS)
