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
        return add(matrix_vector_mult(rotation_matrix, sub(value, rotation_point)), rotation_point)

    def _transform_parameter(value):
        return matrix_vector_mult(rotation_matrix, value)

    _transform_node_values(region, coordinate_field_name, _transform_value, _transform_parameter)


def translate_nodes(region, delta, coordinate_field_name='coordinates'):

    def _transform_value(value):
        return add(value, delta)

    def _transform_parameter(value):
        return value

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


def calculate_centroid(data_points):
    actual_points = np.array(data_points).transpose()
    centroid = np.mean(actual_points, axis=1, keepdims=True)
    centroid = centroid.flatten()

    return centroid


def calculate_normal(data_points):
    actual_points = np.array(data_points).transpose()
    centroid = np.mean(actual_points, axis=1, keepdims=True)
    U, S, Vh = np.linalg.svd(actual_points - centroid)

    return centroid.reshape(-1).tolist(), U[:, -1].tolist()


def calculate_orthogonal_vectors(points):
    vectors = [np.array(point) - points[0] for point in points[1:]]
    lengths = [np.linalg.norm(vector) for vector in vectors]
    max_index = int(np.argmax(lengths))
    vectors.pop(max_index)
    lengths.pop(max_index)

    return (vectors[0] / lengths[0]), (vectors[1] / lengths[1])


def get_nodes_coordinates(region, coordinate_field):
    fm = region.getFieldmodule()
    fc = fm.createFieldcache()

    nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
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


def calculate_line_plane_intersection(pt1, pt2, point_on_plane, plane_normal):
    line_direction = sub(pt2, pt1)
    d = dot(sub(point_on_plane, pt1), plane_normal) / dot(line_direction, plane_normal)
    intersection_point = add(mult(line_direction, d), pt1)
    if abs(dot(sub(point_on_plane, intersection_point), plane_normal)) < 1e-08:
        return intersection_point

    return None


def point_within_plane_boundaries(point, plane_corners):
    def barycentric_coordinates(p, a, b, c):
        v0 = b - a
        v1 = c - a
        v2 = p - a

        dot00 = np.dot(v0, v0)
        dot01 = np.dot(v0, v1)
        dot02 = np.dot(v0, v2)
        dot11 = np.dot(v1, v1)
        dot12 = np.dot(v1, v2)

        inv_denominator = 1 / (dot00 * dot11 - dot01 * dot01)
        _u = (dot11 * dot02 - dot01 * dot12) * inv_denominator
        _v = (dot00 * dot12 - dot01 * dot02) * inv_denominator

        return _u, _v

    x, y, z = point

    for i in range(len(plane_corners)):
        p1 = np.array(plane_corners[i % len(plane_corners)])
        p2 = np.array(plane_corners[(i + 1) % len(plane_corners)])
        p3 = np.array(plane_corners[(i + 2) % len(plane_corners)])

        u, v = barycentric_coordinates(np.array([x, y, z]), p1, p2, p3)

        if 0 <= u <= 1 and 0 <= v <= 1 and u + v <= 1:
            return True

    return False


DEFAULT_GRAPHICS_SPHERE_SIZE = 10.0
DEFAULT_NORMAL_ARROW_SIZE = 25.0
PLANE_MANIPULATION_SPHERE_GRAPHIC_NAME = 'plane_rotation_sphere'
PLANE_MANIPULATION_NORMAL_GRAPHIC_NAME = 'plane_normal_arrow'


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


def create_plane_normal_indicator(region, plane_normal_field, arrow_size=DEFAULT_NORMAL_ARROW_SIZE):
    scene = region.getScene()

    scene.beginChange()
    plane_normal_indicator = scene.createGraphicsPoints()
    plane_normal_indicator.setName(PLANE_MANIPULATION_NORMAL_GRAPHIC_NAME)
    plane_normal_indicator.setFieldDomainType(Field.DOMAIN_TYPE_POINT)
    plane_normal_indicator.setVisibilityFlag(False)

    fm = region.getFieldmodule()
    zero_field = fm.createFieldConstant([0, 0, 0])
    plane_normal_indicator.setCoordinateField(zero_field)

    attributes = plane_normal_indicator.getGraphicspointattributes()
    attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_ARROW_SOLID)
    attributes.setBaseSize([arrow_size, arrow_size / 4, arrow_size / 4])
    attributes.setScaleFactors([0, 0, 0])
    attributes.setOrientationScaleField(plane_normal_field)

    scene.endChange()

    return plane_normal_indicator


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
