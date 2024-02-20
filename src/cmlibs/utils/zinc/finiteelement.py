"""
Utilities for creating and working with Zinc Finite Elements.
"""
from cmlibs.maths import vectorops
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.zinc.element import Element, Elementbasis, Elementfieldtemplate, Mesh
from cmlibs.zinc.field import Field
from cmlibs.zinc.fieldmodule import Fieldmodule
from cmlibs.zinc.node import Node, Nodeset
from cmlibs.zinc.result import RESULT_OK


def create_triangle_elements(mesh: Mesh, finite_element_field: Field, element_node_set):
    """
    Create a linear triangular element for every set of 3 local nodes in element_node_set.

    :param mesh: The Zinc Mesh to create elements in.
    :param finite_element_field: Zinc FieldFiniteElement to interpolate from nodes.
    :param element_node_set: Sequence of 3 node identifiers for each element.
    :return: None
    """
    assert mesh.getDimension() == 2
    assert finite_element_field.castFiniteElement().isValid()
    fieldmodule = finite_element_field.getFieldmodule()
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_TRIANGLE)
    linear_basis = fieldmodule.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_SIMPLEX)
    eft = mesh.createElementfieldtemplate(linear_basis)
    element_template.defineField(finite_element_field, -1, eft)
    with ChangeManager(fieldmodule):
        for element_nodes in element_node_set:
            element = mesh.createElement(-1, element_template)
            element.setNodesByIdentifier(eft, element_nodes)
    fieldmodule.defineAllFaces()


def create_cube_element(mesh: Mesh, finite_element_field: Field, node_coordinate_set):
    """
    Create a single finite element using the supplied
    finite element field and sequence of 8 n-D node coordinates.

    :param mesh: The Zinc Mesh to create elements in.
    :param finite_element_field:  Zinc FieldFiniteElement to interpolate on element.
    :param node_coordinate_set: Sequence of 8 coordinates each with as many components as finite element field.
    :return: None
    """
    assert mesh.getDimension() == 3
    assert finite_element_field.castFiniteElement().isValid()
    assert len(node_coordinate_set) == 8
    fieldmodule = finite_element_field.getFieldmodule()
    nodeset = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    node_template = nodeset.createNodetemplate()
    node_template.defineField(finite_element_field)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
    linear_basis = fieldmodule.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    eft = mesh.createElementfieldtemplate(linear_basis)
    element_template.defineField(finite_element_field, -1, eft)
    field_cache = fieldmodule.createFieldcache()
    with ChangeManager(fieldmodule):
        node_identifiers = []
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            field_cache.setNode(node)
            finite_element_field.assignReal(field_cache, node_coordinate)
        element = mesh.createElement(-1, element_template)
        element.setNodesByIdentifier(eft, node_identifiers)
    fieldmodule.defineAllFaces()


def create_square_element(mesh: Mesh, finite_element_field: Field, node_coordinate_set):
    """
    Create a single square 2-D finite element using the supplied
    finite element field and sequence of 4 n-D node coordinates.

    :param mesh: The Zinc Mesh to create elements in.
    :param finite_element_field:  Zinc FieldFiniteElement to interpolate on element.
    :param node_coordinate_set: Sequence of 4 coordinates each with as many components as finite element field.
    :return: None
    """
    assert mesh.getDimension() == 2
    assert finite_element_field.castFiniteElement().isValid()
    assert len(node_coordinate_set) == 4
    fieldmodule = finite_element_field.getFieldmodule()
    nodeset = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    node_template = nodeset.createNodetemplate()
    node_template.defineField(finite_element_field)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
    linear_basis = fieldmodule.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    eft = mesh.createElementfieldtemplate(linear_basis)
    element_template.defineField(finite_element_field, -1, eft)
    field_cache = fieldmodule.createFieldcache()
    with ChangeManager(fieldmodule):
        node_identifiers = []
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            field_cache.setNode(node)
            finite_element_field.assignReal(field_cache, node_coordinate)
        element = mesh.createElement(-1, element_template)
        element.setNodesByIdentifier(eft, node_identifiers)
    fieldmodule.defineAllFaces()


def create_line_element(mesh: Mesh, finite_element_field: Field, node_coordinate_set):
    """
    Create a single linear 1-D finite element using the supplied
    finite element field and sequence of 2 n-D node coordinates.

    :param mesh: The Zinc Mesh to create elements in.
    :param finite_element_field:  Zinc FieldFiniteElement to interpolate on element.
    :param node_coordinate_set: Sequence of 4 coordinates each with as many components as finite element field.
    :return: None
    """
    assert mesh.getDimension() == 1
    assert finite_element_field.castFiniteElement().isValid()
    assert len(node_coordinate_set) == 2
    fieldmodule = finite_element_field.getFieldmodule()
    nodeset = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    node_template = nodeset.createNodetemplate()
    node_template.defineField(finite_element_field)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_LINE)
    linear_basis = fieldmodule.createElementbasis(1, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    eft = mesh.createElementfieldtemplate(linear_basis)
    element_template.defineField(finite_element_field, -1, eft)
    field_cache = fieldmodule.createFieldcache()
    with ChangeManager(fieldmodule):
        node_identifiers = []
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            field_cache.setNode(node)
            finite_element_field.assignReal(field_cache, node_coordinate)
        element = mesh.createElement(-1, element_template)
        element.setNodesByIdentifier(eft, node_identifiers)


def find_node_with_name(nodeset: Nodeset, name_field: Field, name: str, ignore_case=False, strip_whitespace=False):
    """
    Get single node in nodeset with supplied name.
    :param nodeset: Zinc Nodeset or NodesetGroup to search.
    :param name_field: The name field to match.
    :param name: The name to match in nameField.
    :param ignore_case: Set to True to ignore case differences.
    :param strip_whitespace: Set to True to ignore leading and trailing whitespace differences.
    :return: Zinc Node with name, or None if 0 or multiple nodes with name.
    """
    match_name = name
    if strip_whitespace:
        match_name = match_name.strip()
    if ignore_case:
        match_name = match_name.casefold()
    fieldmodule = nodeset.getFieldmodule()
    fieldcache = fieldmodule.createFieldcache()
    nodeiter = nodeset.createNodeiterator()
    node_with_name = None
    node = nodeiter.next()
    while node.isValid():
        fieldcache.setNode(node)
        temp_name = name_field.evaluateString(fieldcache)
        if strip_whitespace:
            temp_name = temp_name.strip()
        if ignore_case:
            temp_name = temp_name.casefold()
        if temp_name == match_name:
            if node_with_name:
                return None
            node_with_name = node
        node = nodeiter.next()
    return node_with_name


def get_node_name_centres(nodeset: Nodeset, coordinates_field: Field, name_field: Field):
    """
    Find mean locations of node coordinate with the same names.
    :param nodeset: Zinc Nodeset or NodesetGroup to search.
    :param coordinates_field: The coordinate field to evaluate.
    :param name_field: The name field to match.
    :return: Dict of names -> coordinates.
    """
    components_count = coordinates_field.getNumberOfComponents()
    fieldmodule = nodeset.getFieldmodule()
    fieldcache = fieldmodule.createFieldcache()
    name_records = {}  # name -> (coordinates, count)
    nodeiter = nodeset.createNodeiterator()
    node = nodeiter.next()
    while node.isValid():
        fieldcache.setNode(node)
        name = name_field.evaluateString(fieldcache)
        coordinates_result, coordinates = coordinates_field.evaluateReal(fieldcache, components_count)
        if name and (coordinates_result == RESULT_OK):
            name_record = name_records.get(name)
            if name_record:
                name_centre = name_record[0]
                for c in range(components_count):
                    name_centre[c] += coordinates[c]
                name_record[1] += 1
            else:
                name_records[name] = [ coordinates, 1 ]
        node = nodeiter.next()
    # divide centre coordinates by count
    name_centres = {}
    for name in name_records:
        name_record = name_records[name]
        name_count = name_record[1]
        name_centre = name_record[0]
        if name_count > 1:
            scale = 1.0/name_count
            for c in range(components_count):
                name_centre[c] *= scale
        name_centres[name] = name_centre
    return name_centres


def evaluate_field_nodeset_range(field: Field, nodeset: Nodeset):
    """
    :return: min, max range of field over nodes.
    """
    fieldmodule = nodeset.getFieldmodule()
    components_count = field.getNumberOfComponents()
    with ChangeManager(fieldmodule):
        min_field = fieldmodule.createFieldNodesetMinimum(field, nodeset)
        max_field = fieldmodule.createFieldNodesetMaximum(field, nodeset)
        fieldcache = fieldmodule.createFieldcache()
        result, min_values = min_field.evaluateReal(fieldcache, components_count)
        assert result == RESULT_OK
        result, max_values = max_field.evaluateReal(fieldcache, components_count)
        assert result == RESULT_OK
        del min_field
        del max_field
        del fieldcache
    return min_values, max_values


def evaluate_field_nodeset_mean(field: Field, nodeset: Nodeset):
    """
    :return: Mean of field over nodeset.
    """
    fieldmodule = nodeset.getFieldmodule()
    components_count = field.getNumberOfComponents()
    with ChangeManager(fieldmodule):
        mean_field = fieldmodule.createFieldNodesetMean(field, nodeset)
        fieldcache = fieldmodule.createFieldcache()
        result, mean_values = mean_field.evaluateReal(fieldcache, components_count)
        assert result == RESULT_OK
        del mean_field
        del fieldcache
    return mean_values


def transform_coordinates(field: Field, rotation_scale, offset, time=0.0) -> bool:
    """
    Transform finite element field coordinates by matrix and offset, handling nodal derivatives and versions.
    Limited to nodal parameters, rectangular cartesian coordinates
    :param field: the coordinate field to transform
    :param rotation_scale: square transformation matrix 2-D array with as many rows and columns as field components.
    :param offset: coordinates offset.
    :param time: time value.
    :return: True on success, otherwise false.
    """
    ncomp = field.getNumberOfComponents()
    if (ncomp != 2) and (ncomp != 3):
        print('transform_coordinates: field has invalid number of components')
        return False
    if (len(rotation_scale) != ncomp) or (len(offset) != ncomp):
        print('transform_coordinates: invalid matrix number of columns or offset size')
        return False
    for matRow in rotation_scale:
        if len(matRow) != ncomp:
            print('transform_coordinates: invalid matrix number of columns')
            return False
    if field.getCoordinateSystemType() != Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN:
        print('transform_coordinates: field is not rectangular cartesian')
        return False
    fe_field = field.castFiniteElement()
    if not fe_field.isValid():
        print('transform_coordinates: field is not finite element field type')
        return False
    success = True
    fm = field.getFieldmodule()
    with ChangeManager(fm):
        cache = fm.createFieldcache()
        cache.setTime(time)
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        node_template = nodes.createNodetemplate()
        node_iter = nodes.createNodeiterator()
        node = node_iter.next()
        while node.isValid():
            node_template.defineFieldFromNode(fe_field, node)
            cache.setNode(node)
            for derivative in [Node.VALUE_LABEL_VALUE, Node.VALUE_LABEL_D_DS1, Node.VALUE_LABEL_D_DS2,
                               Node.VALUE_LABEL_D2_DS1DS2,
                               Node.VALUE_LABEL_D_DS3, Node.VALUE_LABEL_D2_DS1DS3, Node.VALUE_LABEL_D2_DS2DS3,
                               Node.VALUE_LABEL_D3_DS1DS2DS3]:
                versions = node_template.getValueNumberOfVersions(fe_field, -1, derivative)
                for v in range(versions):
                    result, values = fe_field.getNodeParameters(cache, -1, derivative, v + 1, ncomp)
                    if result != RESULT_OK:
                        success = False
                    else:
                        new_values = vectorops.matrix_vector_mult(rotation_scale, values)
                        if derivative == Node.VALUE_LABEL_VALUE:
                            new_values = vectorops.add(new_values, offset)
                        result = fe_field.setNodeParameters(cache, -1, derivative, v + 1, new_values)
                        if result != RESULT_OK:
                            success = False
            node = node_iter.next()

    if not success:
        print('transform_coordinates: failed to get/set some values')
    return success


def create_nodes(finite_element_field, node_coordinate_set, node_set_name='nodes', time=None, node_set=None):
    """
    Create a node for every coordinate in the node_coordinate_set.

    :param finite_element_field: Finite element field to assign node coordinates to.
    :param node_coordinate_set: A list of node coordinates of the same dimension as the finite element field.
    :param node_set_name: The name of the nodeset to create the node in, either 'nodes' (default) or 'datapoints'.
    :param time: The time to set for the node, defaults to None for nodes that are not time aware.
    :param node_set: The node set to use for creating nodes, if not set then the node set for creating nodes is
                     chosen by node_set_name.
    :return: A list of nodes.
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
    nodes = [None] * len(node_coordinate_set)
    for index, node_coordinate in enumerate(node_coordinate_set):
        node = nodeset.createNode(-1, node_template)
        # Set the node coordinates, first set the field cache to use the current node
        field_cache.setNode(node)
        if time:
            field_cache.setTime(time)
        # Pass in floats as an array
        result = finite_element_field.assignReal(field_cache, node_coordinate)
        if result == RESULT_OK:
            nodes[index] = node

    return nodes


def get_element_node_identifiers(element: Element, eft: Elementfieldtemplate) -> list:
    """
    Get list of node identifiers used by eft in element in the order for eft.

    :param element: The element to query.
    :param eft: The element field template the nodes are mapped for.
    :return: List of global node identifiers.
    """
    node_identifiers = []
    for n in range(eft.getNumberOfLocalNodes()):
        node = element.getNode(eft, n + 1)
        node_identifiers.append(node.getIdentifier())
    return node_identifiers


def get_element_node_identifiers_basis_order(element: Element, eft: Elementfieldtemplate) -> list:
    """
    Get list of node identifiers used by eft in element with the default number
    and order for the element basis. For example, with a bilinear lagrange
    basis, 4 node identifiers are always returned, possibly with repeats, even
    if the eft collapsed it to 3 nodes in an arbitrary order.

    :param element: The element to query.
    :param eft: The element field template the nodes are mapped for.
    :return: List of global node identifiers.
    """
    node_identifiers = []
    fn = 1
    element_basis = eft.getElementbasis()
    for n in range(eft.getElementbasis().getNumberOfNodes()):
        ln = eft.getTermLocalNodeIndex(fn, 1)
        node_identifiers.append(element.getNode(eft, ln).getIdentifier())
        fn += element_basis.getNumberOfFunctionsPerNode(n + 1)
    return node_identifiers


def get_highest_dimension_mesh(fieldmodule: Fieldmodule):
    """
    Get highest dimension non-empty mesh in Zinc fieldmodule.
    :return: Zinc Mesh or None if all are empty.
    """
    for dimension in range(3, 0, -1):
        mesh = fieldmodule.findMeshByDimension(dimension)
        if mesh.getSize() > 0:
            return mesh
    return None


def get_maximum_element_identifier(mesh: Mesh) -> int:
    """
    :return: Maximum element identifier in mesh or -1 if none.
    """
    maximum_element_id = -1
    element_iterator = mesh.createElementiterator()
    element = element_iterator.next()
    while element.isValid():
        element_id = element.getIdentifier()
        if element_id > maximum_element_id:
            maximum_element_id = element_id
        element = element_iterator.next()
    return maximum_element_id


def get_maximum_node_identifier(nodeset: Nodeset) -> int:
    """
    :return: Maximum node identifier in nodeset or -1 if none.
    """
    maximum_node_id = -1
    node_iterator = nodeset.createNodeiterator()
    node = node_iterator.next()
    while node.isValid():
        node_id = node.getIdentifier()
        if node_id > maximum_node_id:
            maximum_node_id = node_id
        node = node_iterator.next()
    return maximum_node_id


def get_next_unused_node_identifier(nodeset: Nodeset, start_identifier=1) -> int:
    """
    :return: Unused node identifier >= start_identifier.
    """
    identifier = start_identifier
    node = nodeset.findNodeByIdentifier(identifier)
    while node.isValid():
        identifier += 1
        node = nodeset.findNodeByIdentifier(identifier)
    return identifier


def get_identifiers(nodeset: Nodeset) -> list:
    """
    Create a list of all the identifiers used in the given nodeset.

    :param nodeset: Nodeset to search for identifiers.
    :return: A list of identifiers used by the given nodeset.
    """
    identifiers = [None] * nodeset.getSize()
    node_iterator = nodeset.createNodeiterator()
    node = node_iterator.next()
    node_index = 0
    while node.isValid():
        identifiers[node_index] = node.getIdentifier()
        node_index += 1
        node = node_iterator.next()

    return identifiers


def is_field_defined_for_nodeset(field, nodeset=None, nodeset_domain=None):
    """
    Determine if the given field is defined for any member of the given nodeset,
    return True if the field is defined on at least one member and False otherwise.
    If neither nodeset nor nodeset_domain is specified then False is returned.
    If nodeset is given and nodeset_domain is also passed then the nodeset_domain will be
    ignored.

    :param field: Field to use for determining if defined any member in the given nodeset.
    :param nodeset: Nodeset to determine if field is defined on any member.
    :param nodeset_domain: Nodeset domain to determine if field is defined on any member.

    :return: True if the field is defined on at least one member, False otherwise.
    """
    if nodeset is None and nodeset_domain is None:
        return False

    source_nodeset = nodeset
    field_module = field.getFieldmodule()
    if nodeset_domain is not None and nodeset is None:
        source_nodeset = field_module.findNodesetByFieldDomainType(nodeset_domain)

    field_cache = field_module.createFieldcache()
    node_iter = source_nodeset.createNodeiterator()
    node = node_iter.next()
    while node.isValid():
        field_cache.setNode(node)
        if field.isDefinedAtLocation(field_cache):
            return True
        node = node_iter.next()

    return False


createCubeElement = create_cube_element
createSquareElement = create_square_element
createLineElement = create_line_element
findNodeWithName = find_node_with_name
getNodeNameCentres = get_node_name_centres
evaluateFieldNodesetRange = evaluate_field_nodeset_range
evaluateFieldNodesetMean = evaluate_field_nodeset_mean
transformCoordinates = transform_coordinates
createNodes = create_nodes
createTriangleElements = create_triangle_elements
getElementNodeIdentifiers = get_element_node_identifiers
getElementNodeIdentifiersBasisOrder = get_element_node_identifiers_basis_order
getMaximumElementIdentifier = get_maximum_element_identifier
getMaximumNodeIdentifier = get_maximum_node_identifier
