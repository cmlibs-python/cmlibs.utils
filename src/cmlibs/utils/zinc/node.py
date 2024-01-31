"""
Utilities for manipulating Zinc nodes.
"""
from cmlibs.zinc.node import Node
from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK
from cmlibs.maths.vectorops import dot, add, sub, mult, matrix_vector_mult
from cmlibs.utils.zinc.general import ChangeManager


def rotate_nodes(region, rotation_matrix, rotation_point, coordinate_field_name='coordinates'):
    """
    Rotate all nodes in the given region around the rotation point specified.

    :param region: The Zinc Region whose nodes are to be rotated.
    :param rotation_matrix: A rotation matrix defining the rotation to be applied to the nodes.
    :param rotation_point: The point that the nodes will be rotated around.
    :param coordinate_field_name: Optional; The name of the field defining the node coordinates.
    """

    def _transform_value(value):
        return add(matrix_vector_mult(rotation_matrix, sub(value, rotation_point)), rotation_point)

    def _transform_parameter(value):
        return matrix_vector_mult(rotation_matrix, value)

    _transform_node_values(region, coordinate_field_name, _transform_value, _transform_parameter)
    _transform_datapoint_values(region, "marker_data_coordinates", _transform_value)


def translate_nodes(region, delta, coordinate_field_name='coordinates'):
    """
    Translate all nodes in the given region by the value specified.

    :param region: The Zinc Region whose nodes are to be translated.
    :param delta: A vector specifying the direction and magnitude of the translation.
    :param coordinate_field_name: Optional; The name of the field defining the node coordinates.
    """

    def _transform_value(value):
        return add(value, delta)

    def _transform_parameter(value):
        return value

    _transform_node_values(region, coordinate_field_name, _transform_value, _transform_parameter)
    _transform_datapoint_values(region, "marker_data_coordinates", _transform_value)


def project_nodes(region, plane_point, plane_normal, coordinate_field_name='coordinates'):
    """
    Project all nodes in the given region onto the plane specified.

    :param region: The Zinc Region whose nodes are to be projected.
    :param plane_point: The point used to define the plane position.
    :param plane_normal: The normal vector defining the orientation of the plane.
    :param coordinate_field_name: Optional; The name of the field defining the node coordinates.
    """

    def _project_point(pt):
        v = sub(pt, plane_point)
        dist = dot(v, plane_normal)
        return sub(pt, mult(plane_normal, dist))

    def _project_vector(vec):
        dist = dot(vec, plane_normal)
        return sub(vec, mult(plane_normal, dist))

    _transform_node_values(region, coordinate_field_name, _project_point, _project_vector)
    _transform_datapoint_values(region, "marker_data_coordinates", _project_point)


def _transform_datapoint_values(region, coordinate_field_name, _node_values_fcn):
    _transform_domain_values(region, coordinate_field_name, _node_values_fcn, None, Field.DOMAIN_TYPE_DATAPOINTS)


def _transform_node_values(region, coordinate_field_name, _node_values_fcn, _node_parameters_fcn):
    _transform_domain_values(region, coordinate_field_name, _node_values_fcn, _node_parameters_fcn, Field.DOMAIN_TYPE_NODES)


def _transform_domain_values(region, coordinate_field_name, _node_values_fcn, _node_parameters_fcn, domain):
    fm = region.getFieldmodule()
    fc = fm.createFieldcache()
    node_derivatives = [Node.VALUE_LABEL_D_DS1, Node.VALUE_LABEL_D_DS2, Node.VALUE_LABEL_D_DS3,
                        Node.VALUE_LABEL_D2_DS1DS2, Node.VALUE_LABEL_D2_DS1DS3, Node.VALUE_LABEL_D2_DS2DS3, Node.VALUE_LABEL_D3_DS1DS2DS3]
    derivatives_count = len(node_derivatives)

    nodes = fm.findNodesetByFieldDomainType(domain)
    node_template = nodes.createNodetemplate()
    node_iter = nodes.createNodeiterator()

    coordinates = fm.findFieldByName(coordinate_field_name).castFiniteElement()
    components_count = coordinates.getNumberOfComponents()

    with ChangeManager(fm):

        node = node_iter.next()
        while node.isValid():
            fc.setNode(node)
            result, x = coordinates.evaluateReal(fc, components_count)
            if result == RESULT_OK:
                proj_x = _node_values_fcn(x)
                coordinates.assignReal(fc, proj_x)
                node_template.defineFieldFromNode(coordinates, node)
                for d in range(derivatives_count):
                    version_count = node_template.getValueNumberOfVersions(coordinates, -1, node_derivatives[d])
                    for version in range(1, version_count + 1):
                        result, values = coordinates.getNodeParameters(fc, -1, node_derivatives[d], version, components_count)
                        proj_param = _node_parameters_fcn(values)
                        coordinates.setNodeParameters(fc, -1, node_derivatives[d], version, proj_param)

            node = node_iter.next()
