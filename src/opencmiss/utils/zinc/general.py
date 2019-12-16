"""
General utilities for working with the OpenCMISS-Zinc library.
"""
from opencmiss.zinc.context import Context


class AbstractNodeDataObject(object):

    def __init__(self, field_names, time_sequence=None, time_sequence_field_names=None):
        self._field_names = field_names
        self._time_sequence = time_sequence if time_sequence else []
        self._time_sequence_field_names = time_sequence_field_names if time_sequence_field_names else []
        self._check_field_names()

    def _check_field_names(self):
        for field_name in self._field_names:
            if not hasattr(self, field_name):
                raise NotImplementedError('Missing data method for field: %s' % field_name)

    def get_field_names(self):
        return self._field_names

    def set_field_names(self, field_names):
        self._field_names = field_names
        self._check_field_names()

    def get_time_sequence(self):
        return self._time_sequence

    def set_time_sequence(self, time_sequence):
        self._time_sequence = time_sequence

    def get_time_sequence_field_names(self):
        return self._time_sequence_field_names

    def set_time_sequence_field_names(self, time_sequence_field_names):
        self._time_sequence_field_names = time_sequence_field_names


class ZincCacheChanges:
    """
    Context manager for ensuring beginChange, endChange always called on
    supplied object, even with exceptions.
    Usage:
    with ZincCacheChanges(object):
        # make multiple changes to object or objects it owns
    """

    def __init__(self, object):
        """
        :param object: Zinc object with beginChange/endChange methods.
        """
        self._object = object

    def __enter__(self):
        self._object.beginChange()
        return self

    def __exit__(self, *args):
        self._object.endChange()


def defineStandardVisualisationTools(context : Context):
    glyphmodule = context.getGlyphmodule()
    glyphmodule.defineStandardGlyphs()
    materialmodule = context.getMaterialmodule()
    materialmodule.defineStandardMaterials()


def createNode(field_module, data_object, identifier=-1, node_set_name='nodes', time=None):
    """
    Create a Node in the field_module using the data_object.  The data object must supply a 'get_field_names' method
    and a 'get_time_sequence' method.  Derive a node data object from the 'AbstractNodeDataObject' class to ensure
    that the data object class meets it's requirements.

    Optionally use the identifier to set the identifier of the Node created, the time parameter to set
    the time value in the cache, or the node_set_name to specify which node set to use the default node set
    is 'nodes'.

    :param field_module: The field module that has at least the fields defined with names in field_names.
    :param data_object: The object that can supply the values for the field_names through the same named method.
    :param identifier: Identifier to assign to the node. Default value is '-1'.
    :param node_set_name: Name of the node set to create the node in.
    :param time: The time to set for the node, defaults to None for nodes that are not time aware.
    :return: The node identifier assigned to the created node.
    """
    # Find a special node set named 'nodes'
    node_set = field_module.findNodesetByName(node_set_name)
    node_template = node_set.createNodetemplate()

    # Set the finite element coordinate field for the nodes to use
    fields = []
    field_names = data_object.get_field_names()
    for field_name in field_names:
        fields.append(field_module.findFieldByName(field_name))
        node_template.defineField(fields[-1])
    if data_object.get_time_sequence():
        time_sequence = field_module.getMatchingTimesequence(data_object.get_time_sequence())
        for field_name in data_object.get_time_sequence_field_names():
            time_sequence_field = field_module.findFieldByName(field_name)
            node_template.setTimesequence(time_sequence_field, time_sequence)
    field_cache = field_module.createFieldcache()
    node = node_set.createNode(identifier, node_template)
    # Set the node coordinates, first set the field cache to use the current node
    field_cache.setNode(node)
    if time:
        field_cache.setTime(time)
    # Pass in floats as an array
    for i, field in enumerate(fields):
        field_name = field_names[i]
        field_value = getattr(data_object, field_name)()
        if isinstance(field_value, ("".__class__, u"".__class__)):
            field.assignString(field_cache, field_value)
        else:
            field.assignReal(field_cache, field_value)

    return node.getIdentifier()


def createNodes(finite_element_field, node_coordinate_set, node_set_name='nodes', time=None, node_set=None):
    """
    Create a node for every coordinate in the node_coordinate_set.

    :param finite_element_field:
    :param node_coordinate_set:
    :param node_set_name:
    :param time: The time to set for the node, defaults to None for nodes that are not time aware.
    :param node_set: The node set to use for creating nodes, if not set then the node set for creating nodes is
    chosen by node_set_name.
    :return: None
    """
    fieldmodule = finite_element_field.getFieldmodule()
    # Find a special node set named 'nodes'
    if node_set:
        nodeset = node_set
    else:
        nodeset = fieldmodule.findNodesetByName(node_set_name)
    node_template = nodeset.createNodetemplate()

    # Set the finite element coordinate field for the nodes to use
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()
    for node_coordinate in node_coordinate_set:
        node = nodeset.createNode(-1, node_template)
        # Set the node coordinates, first set the field cache to use the current node
        field_cache.setNode(node)
        if time:
            field_cache.setTime(time)
        # Pass in floats as an array
        finite_element_field.assignReal(field_cache, node_coordinate)


def createElements(finite_element_field, element_node_set):
    """
    Create an element for every element_node_set

    :param finite_element_field:
    :param element_node_set:
    :return: None
    """
    fieldmodule = finite_element_field.getFieldmodule()
    mesh = fieldmodule.findMeshByDimension(2)
    nodeset = fieldmodule.findNodesetByName('nodes')
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_TRIANGLE)
    element_node_count = 3
    element_template.setNumberOfNodes(element_node_count)
    # Specify the dimension and the interpolation function for the element basis function
    linear_basis = fieldmodule.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_SIMPLEX)
    # the indecies of the nodes in the node template we want to use.
    node_indexes = [1, 2, 3]

    # Define a nodally interpolated element field or field component in the
    # element_template
    element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

    for element_nodes in element_node_set:
        for i, node_identifier in enumerate(element_nodes):
            node = nodeset.findNodeByIdentifier(node_identifier)
            element_template.setNode(i + 1, node)

        mesh.defineElement(-1, element_template)


#     fieldmodule.defineAllFaces()


def createSquare2DFiniteElement(fieldmodule, finite_element_field, node_coordinate_set):
    """
    Create a single finite element using the supplied
    finite element field and node coordinate set.

    :param fieldmodule:
    :param finite_element_field:
    :param node_coordinate_set:
    :return: None
    """
    # Find a special node set named 'nodes'
    nodeset = fieldmodule.findNodesetByName('nodes')
    node_template = nodeset.createNodetemplate()

    # Set the finite element coordinate field for the nodes to use
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()

    node_identifiers = []
    # Create eight nodes to define a cube finite element
    for node_coordinate in node_coordinate_set:
        node = nodeset.createNode(-1, node_template)
        node_identifiers.append(node.getIdentifier())
        # Set the node coordinates, first set the field cache to use the current node
        field_cache.setNode(node)
        # Pass in floats as an array
        finite_element_field.assignReal(field_cache, node_coordinate)

    # Use a 3D mesh to to create the 2D finite element.
    mesh = fieldmodule.findMeshByDimension(2)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
    element_node_count = 4
    element_template.setNumberOfNodes(element_node_count)
    # Specify the dimension and the interpolation function for the element basis function
    linear_basis = fieldmodule.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    # the indecies of the nodes in the node template we want to use.
    node_indexes = [1, 2, 3, 4]

    # Define a nodally interpolated element field or field component in the
    # element_template
    element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

    for i, node_identifier in enumerate(node_identifiers):
        node = nodeset.findNodeByIdentifier(node_identifier)
        element_template.setNode(i + 1, node)

    mesh.defineElement(-1, element_template)
    fieldmodule.defineAllFaces()


def createCubeFiniteElement(fieldmodule, finite_element_field, node_coordinate_set):
    '''
    Create a single finite element using the supplied
    finite element field and node coordinate set.
    '''
    # Find a special node set named 'nodes'
    nodeset = fieldmodule.findNodesetByName('nodes')
    node_template = nodeset.createNodetemplate()

    # Set the finite element coordinate field for the nodes to use
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()

    node_identifiers = []
    # Create eight nodes to define a cube finite element
    for node_coordinate in node_coordinate_set:
        node = nodeset.createNode(-1, node_template)
        node_identifiers.append(node.getIdentifier())
        # Set the node coordinates, first set the field cache to use the current node
        field_cache.setNode(node)
        # Pass in floats as an array
        finite_element_field.assignReal(field_cache, node_coordinate)

    # Use a 3D mesh to to create the 2D finite element.
    mesh = fieldmodule.findMeshByDimension(3)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
    element_node_count = 8
    element_template.setNumberOfNodes(element_node_count)
    # Specify the dimension and the interpolation function for the element basis function
    linear_basis = fieldmodule.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    # the indecies of the nodes in the node template we want to use.
    node_indexes = [1, 2, 3, 4, 5, 6, 7, 8]

    # Define a nodally interpolated element field or field component in the
    # element_template
    element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

    for i, node_identifier in enumerate(node_identifiers):
        node = nodeset.findNodeByIdentifier(node_identifier)
        element_template.setNode(i + 1, node)

    mesh.defineElement(-1, element_template)
    fieldmodule.defineAllFaces()


def _createPlaneEquationFormulation(fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
    """
    Create an iso-scalar field that is based on the plane equation.
    """
    d = fieldmodule.createFieldDotProduct(plane_normal_field, point_on_plane_field)
    iso_scalar_field = fieldmodule.createFieldDotProduct(finite_element_field, plane_normal_field) - d

    return iso_scalar_field


def create2DFiniteElement(fieldmodule, finite_element_field, node_coordinate_set):
    '''
    Create a single finite element using the supplied
    finite element field and node coordinate set.
    '''
    # Find a special node set named 'nodes'
    nodeset = fieldmodule.findNodesetByName('nodes')
    node_template = nodeset.createNodetemplate()

    # Set the finite element coordinate field for the nodes to use
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()

    node_identifiers = []
    # Create eight nodes to define a cube finite element
    for node_coordinate in node_coordinate_set:
        node = nodeset.createNode(-1, node_template)
        node_identifiers.append(node.getIdentifier())
        # Set the node coordinates, first set the field cache to use the current node
        field_cache.setNode(node)
        # Pass in floats as an array
        finite_element_field.assignReal(field_cache, node_coordinate)

    # Use a 3D mesh to to create the 2D finite element.
    mesh = fieldmodule.findMeshByDimension(2)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
    element_node_count = 4
    element_template.setNumberOfNodes(element_node_count)
    # Specify the dimension and the interpolation function for the element basis function
    linear_basis = fieldmodule.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    # the indecies of the nodes in the node template we want to use.
    node_indexes = [1, 2, 3, 4]


    # Define a nodally interpolated element field or field component in the
    # element_template
    element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

    for i, node_identifier in enumerate(node_identifiers):
        node = nodeset.findNodeByIdentifier(node_identifier)
        element_template.setNode(i + 1, node)

    mesh.defineElement(-1, element_template)
    fieldmodule.defineAllFaces()
