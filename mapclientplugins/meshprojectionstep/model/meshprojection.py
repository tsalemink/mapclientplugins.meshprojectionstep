from cmlibs.maths.vectorops import add, cross, matrix_vector_mult, angle, axis_angle_to_rotation_matrix
from cmlibs.utils.zinc.field import create_field_coordinates
from cmlibs.utils.zinc.finiteelement import evaluate_field_nodeset_range, create_square_element
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.utils.zinc.node import project_nodes, rotate_nodes, translate_nodes, get_field_values
from cmlibs.utils.geometry.plane import ZincPlane
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field


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

        self._plane = None

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

    def get_plane(self):
        """
        API to satisfy the model API requirements for the orientation handler.

        :return: ZincPlane.
        """
        return self._plane

    def get_plane_region(self):
        """
        API to satisfy the model API requirements for the orientation handler.

        :return: The Zinc region the plane is described in.
        """
        return self._projection_plane_region

    def plane_nodes_coordinates(self):
        """
        API to satisfy the model API requirements for the orientation handler.

        :return: Node coordinate values.
        """
        field_module = self._projection_plane_region.getFieldmodule()
        coordinate_field_name = self._mesh_coordinates_field.getName()
        coordinate_field = field_module.findFieldByName(coordinate_field_name).castFiniteElement()
        return get_field_values(self._projection_plane_region, coordinate_field)

    def reset_label_region(self):
        root_region = self._context.getDefaultRegion()
        root_region.removeChild(self._label_region)

    def get_mesh(self):
        return self._mesh

    def write_projected_mesh(self, location, node_coordinate_field_name, datapoint_coordinate_field_name):
        # Rotate to the x-y plane.
        xy_normal = [0, 0, 1]
        plane_normal = self._plane.getNormal()
        theta = angle(xy_normal, plane_normal)
        rot_mx = axis_angle_to_rotation_matrix(cross(plane_normal, xy_normal), theta)

        rotation_point = self._plane.getRotationPoint()
        delta = [-component for component in rotation_point]
        if datapoint_coordinate_field_name:
            rotate_nodes(self._projected_region, rot_mx, rotation_point, node_coordinate_field_name, datapoint_coordinate_field_name)
            translate_nodes(self._projected_region, delta, node_coordinate_field_name, datapoint_coordinate_field_name)
        else:
            rotate_nodes(self._projected_region, rot_mx, rotation_point, node_coordinate_field_name)
            translate_nodes(self._projected_region, delta, node_coordinate_field_name)

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

        field_module = self._mesh_region.getFieldmodule()
        self._plane = ZincPlane(field_module)
        self._plane.setPlaneEquation(plane_normal, point_on_plane)

        max_dimension = plane_size
        half_max_dimension = max_dimension / 2
        p_h_m_d = half_max_dimension
        n_h_m_d = -half_max_dimension
        element_points = [[n_h_m_d, n_h_m_d, 0], [p_h_m_d, n_h_m_d, 0], [n_h_m_d, p_h_m_d, 0], [p_h_m_d, p_h_m_d, 0]]
        element_normal = [0, 0, 1.0]

        theta = angle(plane_normal, element_normal)
        rot_mx = axis_angle_to_rotation_matrix(cross(element_normal, plane_normal), theta)
        rot_element_points = [add(matrix_vector_mult(rot_mx, pt), point_on_plane) for pt in element_points]

        with ChangeManager(fm):
            mesh = fm.findMeshByDimension(2)
            coordinate_field = create_field_coordinates(fm)
            create_square_element(mesh, coordinate_field, rot_element_points)

    def mesh_nodes_coordinates(self):
        return get_field_values(self._mesh_region, self._mesh_coordinates_field)

    def project(self, node_coordinate_field_name, datapoint_coordinate_field_name):
        self.reset_projection()
        point_on_plane = self._plane.getRotationPoint()
        plane_normal = self._plane.getNormal()
        if datapoint_coordinate_field_name:
            project_nodes(self._projected_region, point_on_plane, plane_normal, node_coordinate_field_name, datapoint_coordinate_field_name)
        else:
            project_nodes(self._projected_region, point_on_plane, plane_normal, node_coordinate_field_name)

    def reset_projection(self):
        projection_field_module = self._projected_region.getFieldmodule()
        projection_nodes = projection_field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        projection_nodes.destroyAllNodes()

        fm = self._projected_region.getFieldmodule()
        with ChangeManager(fm):
            self._projected_region.readFile(self._mesh_file_location)

    def reset_projection_region(self):
        self._root_region.removeChild(self._projected_region)
        self._projected_region = self._root_region.createChild("projected")
