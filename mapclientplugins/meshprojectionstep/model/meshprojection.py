import math

import numpy as np
from cmlibs.maths.vectorops import dot, magnitude, cross, add, sub, mult, axis_angle_to_rotation_matrix, matrix_vector_mult
from cmlibs.utils.zinc.field import create_field_coordinates
from cmlibs.utils.zinc.finiteelement import evaluate_field_nodeset_range, create_square_element
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.node import Node
from cmlibs.zinc.result import RESULT_OK


class MeshProjectionModel(object):

    def __init__(self):
        self._mesh_coordinates_field = None
        self._mesh = None

        self._context = Context("MeshProjection")
        self._root_region = self._context.getDefaultRegion()

        self._label_region = self._root_region.createChild("_label")
        self._mesh_region = self._root_region.createChild("mesh")
        self._projected_region = self._root_region.createChild("projected")
        self._projection_plane_region = self._root_region.createChild("projection_plane")

        self._projection_plane_normal = None
        self._projection_plane_point = None

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
        fm = self._projected_region.getFieldmodule()
        with ChangeManager(fm):
            self._projected_region.readFile(mesh_file_location)

    def get_context(self):
        return self._context

    def get_mesh_coordinates(self):
        return self._mesh_coordinates_field

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

    def write_projected_mesh(self, location):

        # Rotate to the x-y plane.
        xy_normal = [0, 0, 1]
        rot_mx = _define_rotation_matrix(xy_normal, self._projection_plane_normal)
        # add(matrix_vector_mult(rot_mx, pt), point_on_plane)

        def _transform_value(value):
            return matrix_vector_mult(rot_mx, sub(self._projection_plane_point, value))

        def _transform_parameter(value):
            return matrix_vector_mult(rot_mx, value)

        _transform_node_values(self._projected_region, "coordinates", _transform_value, _transform_parameter)

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

    def mesh_nodes_coordinates(self, coordinates):
        fm = self._mesh_region.getFieldmodule()
        fc = fm.createFieldcache()

        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        node_iter = nodes.createNodeiterator()

        node_coordinates = []
        node = node_iter.next()
        while node.isValid():
            fc.setNode(node)
            result, x = coordinates.evaluateReal(fc, coordinates.getNumberOfComponents())
            if result == RESULT_OK:
                node_coordinates.append(x)
            node = node_iter.next()

        return node_coordinates

    def evaluate_nodes_minima_and_maxima(self, field):
        fm = self._mesh_region.getFieldmodule()
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        return evaluate_field_nodeset_range(field, nodes)

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

        rot_mx = _define_rotation_matrix(plane_normal, element_normal)
        rot_element_points = [add(matrix_vector_mult(rot_mx, pt), point_on_plane) for pt in element_points]

        with ChangeManager(fm):
            mesh = fm.findMeshByDimension(2)
            coordinate_field = create_field_coordinates(fm)
            create_square_element(mesh, coordinate_field, rot_element_points)

    def project(self, coordinate_field_name):

        def _project_point(pt):
            v = sub(pt, self._projection_plane_point)
            dist = dot(v, self._projection_plane_normal)
            return sub(pt, mult(self._projection_plane_normal, dist))

        def _project_vector(vec):
            dist = dot(vec, self._projection_plane_normal)
            return sub(vec, mult(self._projection_plane_normal, dist))

        _transform_node_values(self._projected_region, coordinate_field_name, _project_point, _project_vector)


def _transform_node_values(region, coordinate_field_name, _node_values_fcn, _node_parameters_fcn):
    fm = region.getFieldmodule()
    fc = fm.createFieldcache()
    node_derivatives = [Node.VALUE_LABEL_D_DS1, Node.VALUE_LABEL_D_DS2, Node.VALUE_LABEL_D_DS3,
                        Node.VALUE_LABEL_D2_DS1DS2, Node.VALUE_LABEL_D2_DS1DS3, Node.VALUE_LABEL_D2_DS2DS3, Node.VALUE_LABEL_D3_DS1DS2DS3]
    derivatives_count = len(node_derivatives)

    nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    node_iter = nodes.createNodeiterator()

    coordinates = fm.findFieldByName(coordinate_field_name).castFiniteElement()
    components_count = coordinates.getNumberOfComponents()

    with ChangeManager(fm):

        node = node_iter.next()
        while node.isValid():
            fc.setNode(node)
            result, x = coordinates.evaluateReal(fc, coordinates.getNumberOfComponents())
            if result == RESULT_OK:
                proj_x = _node_values_fcn(x)
                coordinates.assignReal(fc, proj_x)
                for d in range(derivatives_count):
                    result, values = coordinates.getNodeParameters(fc, -1, node_derivatives[d], 1, components_count)
                    if result == RESULT_OK:
                        proj_param = _node_parameters_fcn(values)
                        coordinates.setNodeParameters(fc, -1, node_derivatives[d], 1, proj_param)

            node = node_iter.next()


def _define_rotation_matrix(normal1, normal2):
    normal_dot_product = dot(normal1, normal2)
    normal1_length = magnitude(normal1)
    normal2_length = magnitude(normal2)
    theta = math.acos(normal_dot_product / (normal1_length * normal2_length))

    return axis_angle_to_rotation_matrix(cross(normal2, normal1), theta)
