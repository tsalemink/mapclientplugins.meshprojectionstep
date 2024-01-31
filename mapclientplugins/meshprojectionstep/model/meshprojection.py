from cmlibs.maths.vectorops import add, sub, matrix_vector_mult
from cmlibs.maths.algorithms import calculate_rotation_matrix
from cmlibs.utils.zinc.field import create_field_coordinates
from cmlibs.utils.zinc.finiteelement import evaluate_field_nodeset_range, create_square_element
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.utils.zinc.node import project_nodes, _transform_node_values, _transform_datapoint_values
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK


class MeshProjectionModel(object):

    def __init__(self):
        self._mesh_coordinates_field = None
        self._mesh_file_location = None
        self._mesh = None

        self._context = Context("MeshProjection")
        self._root_region = self._context.getDefaultRegion()

        self._label_region = self._root_region.createChild("_label")
        self._mesh_region = self._root_region.createChild("mesh")
        self._projected_region = self._root_region.createChild("projected")
        self._projection_plane_region = self._root_region.createChild("projection_plane")

        self._projection_plane_point = None
        self._projection_plane_normal = None

        self.define_standard_materials()
        self.define_standard_glyphs()

        self._selection_filter = self._create_selection_filter()

    def get_root_region(self):
        return self._root_region

    def get_selection_filter(self):
        return self._selection_filter

    def load(self, mesh_file_location):
        fm = self._mesh_region.getFieldmodule()
        with ChangeManager(fm):
            self._mesh_region.readFile(mesh_file_location)
        self._mesh_file_location = mesh_file_location

    def get_context(self):
        return self._context

    def get_mesh_coordinates(self):
        return self._mesh_coordinates_field

    def set_mesh_coordinates(self, coordinates):
        self._mesh_coordinates_field = coordinates

    def get_mesh_region(self):
        return self._mesh_region

    def get_label_region(self):
        return self._label_region

    def get_projected_region(self):
        return self._projected_region

    def get_projection_plane_region(self):
        return self._projection_plane_region

    def remove_label_region(self):
        root_region = self._context.getDefaultRegion()
        root_region.removeChild(self._label_region)

    def get_mesh(self):
        return self._mesh

    def write_projected_mesh(self, location, coordinate_field_name):

        # Rotate to the x-y plane.
        xy_normal = [0, 0, 1]
        rot_mx = calculate_rotation_matrix(xy_normal, self._projection_plane_normal)

        def _transform_value(value):
            return matrix_vector_mult(rot_mx, sub(self._projection_plane_point, value))

        def _transform_parameter(value):
            return matrix_vector_mult(rot_mx, value)

        _transform_node_values(self._projected_region, coordinate_field_name, _transform_value, _transform_parameter)
        _transform_datapoint_values(self._projected_region, "marker_data_coordinates", _transform_value)

        self._projected_region.writeFile(location)

    def _create_selection_filter(self):
        m = self._context.getScenefiltermodule()
        # r1 = m.createScenefilterRegion(self._detection_model.get_region())
        # r2 = m.createScenefilterRegion(self._marker_model.get_region())
        o = m.createScenefilterOperatorOr()
        # o.appendOperand(r1)
        # o.appendOperand(r2)
        return o

    def define_standard_glyphs(self):
        """
        Helper method to define the standard glyphs
        """
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def define_standard_materials(self):
        """
        Helper method to define the standard materials.
        """
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()

    def evaluate_nodes_minima_and_maxima(self):
        fm = self._mesh_region.getFieldmodule()
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        return evaluate_field_nodeset_range(self._mesh_coordinates_field, nodes)

    def create_projection_plane(self, point_on_plane, plane_normal, plane_size):
        self._root_region.removeChild(self._projection_plane_region)
        self._projection_plane_region = self._root_region.createChild("projection_plane")
        fm = self._projection_plane_region.getFieldmodule()

        self._projection_plane_normal = plane_normal
        self._projection_plane_point = point_on_plane

        max_dimension = max(plane_size)
        half_max_dimension = max_dimension / 2
        p_h_m_d = half_max_dimension
        n_h_m_d = -half_max_dimension
        element_points = [[n_h_m_d, n_h_m_d, 0], [p_h_m_d, n_h_m_d, 0], [n_h_m_d, p_h_m_d, 0], [p_h_m_d, p_h_m_d, 0]]
        element_normal = [0, 0, 1.0]

        rot_mx = calculate_rotation_matrix(plane_normal, element_normal)
        rot_element_points = [add(matrix_vector_mult(rot_mx, pt), point_on_plane) for pt in element_points]

        with ChangeManager(fm):
            mesh = fm.findMeshByDimension(2)
            coordinate_field = create_field_coordinates(fm)
            create_square_element(mesh, coordinate_field, rot_element_points)

    def set_plane_normal(self, normal):
        self._projection_plane_normal = normal

    def get_plane_normal(self):
        return self._projection_plane_normal

    def set_rotation_point(self, point):
        self._projection_plane_point = point

    def get_rotation_point(self):
        return self._projection_plane_point

    def mesh_nodes_coordinates(self):
        return get_nodes_coordinates(self._mesh_region, self._mesh_coordinates_field)

    def plane_nodes_coordinates(self):
        field_module = self._projection_plane_region.getFieldmodule()
        coordinate_field_name = self._mesh_coordinates_field.getName()
        coordinate_field = field_module.findFieldByName(coordinate_field_name).castFiniteElement()
        return get_nodes_coordinates(self._projection_plane_region, coordinate_field)

    def project(self, coordinate_field_name):
        self.reset_projection()
        project_nodes(self._projected_region, self._projection_plane_point, self._projection_plane_normal, coordinate_field_name)

    def reset_projection(self):
        projection_field_module = self._projected_region.getFieldmodule()
        projection_nodes = projection_field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        projection_nodes.destroyAllNodes()

        fm = self._projected_region.getFieldmodule()
        with ChangeManager(fm):
            self._projected_region.readFile(self._mesh_file_location)


def get_nodes_coordinates(region, coordinate_field, domain_type=Field.DOMAIN_TYPE_NODES):
    fm = region.getFieldmodule()
    fc = fm.createFieldcache()

    nodes = fm.findNodesetByFieldDomainType(domain_type)
    node_iter = nodes.createNodeiterator()

    node_coordinates = []
    node = node_iter.next()
    while node.isValid():
        fc.setNode(node)
        result, x = coordinate_field.evaluateReal(fc, coordinate_field.getNumberOfComponents())
        if result == RESULT_OK:
            node_coordinates.append(x)
        node = node_iter.next()

    return node_coordinates
