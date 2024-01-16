# TODO: The following functions should all be moved to `cmlibs.utils` or `cmlibs.maths`.

import math
import numpy as np

from cmlibs.zinc.node import Node
from cmlibs.zinc.field import Field
from cmlibs.zinc.glyph import Glyph
from cmlibs.zinc.result import RESULT_OK
from cmlibs.maths.vectorops import dot, magnitude, cross, add, sub, mult, axis_angle_to_rotation_matrix, matrix_vector_mult
from cmlibs.utils.zinc.general import ChangeManager


def rotate_nodes(region, rotation_matrix, rotation_point, coordinate_field_name='coordinates'):

    def _transform_value(value):
        return add(matrix_vector_mult(rotation_matrix, sub(rotation_point, value)), rotation_point)

    def _transform_parameter(value):
        return matrix_vector_mult(rotation_matrix, value)

    _transform_node_values(region, coordinate_field_name, _transform_value, _transform_parameter)


def project_nodes(region, plane_point, plane_normal, coordinate_field_name='coordinates'):
    def _project_point(pt):
        v = sub(pt, plane_point)
        dist = dot(v, plane_normal)
        return sub(pt, mult(plane_normal, dist))

    def _project_vector(vec):
        dist = dot(vec, plane_normal)
        return sub(vec, mult(plane_normal, dist))

    _transform_node_values(region, coordinate_field_name, _project_point, _project_vector)


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


def define_rotation_matrix(normal1, normal2):
    normal_dot_product = dot(normal1, normal2)
    normal1_length = magnitude(normal1)
    normal2_length = magnitude(normal2)
    theta = math.acos(normal_dot_product / (normal1_length * normal2_length))

    return axis_angle_to_rotation_matrix(cross(normal2, normal1), theta)


def calculate_centroid(region):
    data_points = mesh_nodes_coordinates(region)
    actual_points = np.array(data_points).transpose()
    centroid = np.mean(actual_points, axis=1, keepdims=True)
    centroid = centroid.flatten()

    return centroid


def calculate_normal(region):
    data_points = mesh_nodes_coordinates(region)
    actual_points = np.array(data_points).transpose()
    centroid = np.mean(actual_points, axis=1, keepdims=True)
    U, S, Vh = np.linalg.svd(actual_points - centroid)

    return centroid.reshape(-1).tolist(), U[:, -1].tolist()


def mesh_nodes_coordinates(region):
    fm = region.getFieldmodule()
    fc = fm.createFieldcache()

    coordinates = fm.findFieldByName("coordinates").castFiniteElement()
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


def calculate_line_plane_intersection(pt1, pt2, point_on_plane, plane_normal):
    line_direction = sub(pt2, pt1)
    d = dot(sub(point_on_plane, pt1), plane_normal) / dot(line_direction, plane_normal)
    intersection_point = add(mult(line_direction, d), pt1)
    if abs(dot(sub(point_on_plane, intersection_point), plane_normal)) < 1e-08:
        return intersection_point

    return None


DEFAULT_GRAPHICS_SPHERE_SIZE = 10.0
PLANE_MANIPULATION_SPHERE_GRAPHIC_NAME = 'plane_rotation_sphere'


def create_plane_manipulation_sphere(region):
    scene = region.getScene()

    scene.beginChange()

    # Create transparent purple sphere
    plane_rotation_sphere = scene.createGraphicsPoints()
    plane_rotation_sphere.setName(PLANE_MANIPULATION_SPHERE_GRAPHIC_NAME)
    plane_rotation_sphere.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
    plane_rotation_sphere.setVisibilityFlag(False)
    fm = region.getFieldmodule()
    zero_field = fm.createFieldConstant([0, 0, 0])
    plane_rotation_sphere.setCoordinateField(zero_field)
    tessellation = plane_rotation_sphere.getTessellation()
    tessellation.setCircleDivisions(24)
    plane_rotation_sphere.setTessellation(tessellation)
    attributes = plane_rotation_sphere.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
    attributes.setBaseSize(DEFAULT_GRAPHICS_SPHERE_SIZE)

    scene.endChange()

    return plane_rotation_sphere


def set_glyph_position(glyph, position):
    if position is not None:
        position_field = glyph.getCoordinateField()
        field_module = position_field.getFieldmodule()
        field_cache = field_module.createFieldcache()
        position_field.assignReal(field_cache, position)


def get_glyph_position(glyph):
    position_field = glyph.getCoordinateField()
    field_module = position_field.getFieldmodule()
    field_cache = field_module.createFieldcache()
    _, position = position_field.evaluateReal(field_cache, 3)

    return position
