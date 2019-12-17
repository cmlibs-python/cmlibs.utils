"""
Utilities for creating and working with Zinc Finite Elements.
"""
from opencmiss.utils.maths import vectorops
from opencmiss.utils.zinc.general import ZincCacheChanges
from opencmiss.zinc.element import Element, Elementbasis, Elementfieldtemplate, Mesh
from opencmiss.zinc.field import Field, FieldFiniteElement
from opencmiss.zinc.fieldmodule import Fieldmodule
from opencmiss.zinc.node import Node, Nodeset
from opencmiss.zinc.result import RESULT_OK


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
    eft = mesh.createElementfieldtemplate(linear_basis);
    element_template.defineField(finite_element_field, -1, eft)
    with ZincCacheChanges(fieldmodule):
        for element_nodes in element_node_set:
            element = mesh.createElement(-1, element_template)
            element.setNodesByIdentifier(eft, element_nodes)
    fieldmodule.defineAllFaces()


def create_cube_element(mesh: Mesh, finite_element_field: Field, node_coordinate_set):
    """
    Create a single finite element using the supplied
    finite element field and sequence of 8 n-D node coordinates.

    :param mesh: The Zinc Mesh to create elements in.
    :param fieldmodule: Owning fieldmodule for new elements and nodes.
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
    with ZincCacheChanges(fieldmodule):
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
    :param fieldmodule: Owning fieldmodule for new elements and nodes.
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
    eft = mesh.createElementfieldtemplate(linear_basis);
    element_template.defineField(finite_element_field, -1, eft)
    field_cache = fieldmodule.createFieldcache()
    with ZincCacheChanges(fieldmodule):
        node_identifiers = []
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            field_cache.setNode(node)
            finite_element_field.assignReal(field_cache, node_coordinate)
        element = mesh.createElement(-1, element_template)
        element.setNodesByIdentifier(eft, node_identifiers)
    fieldmodule.defineAllFaces()


def find_node_with_name(nodeset: Nodeset, nameField: Field, name):
    """
    Get single node in nodeset with supplied name.
    :param nodeset: Zinc Nodeset or NodesetGroup to search.
    :param nameField: The name field to match.
    :param name: The name to match in nameField.
    :return: Node with name, or None if 0 or multiple nodes with name.
    """
    fieldmodule = nodeset.getFieldmodule()
    fieldcache = fieldmodule.createFieldcache()
    nodeiter = nodeset.createNodeiterator()
    nodeWithName = None
    node = nodeiter.next()
    while node.isValid():
        fieldcache.setNode(node)
        tempName = nameField.evaluateString(fieldcache)
        if tempName == name:
            if nodeWithName:
                return None
            nodeWithName = node
        node = nodeiter.next()
    return nodeWithName


def get_node_name_centres(nodeset: Nodeset, coordinatesField: Field, nameField: Field):
    """
    Find mean locations of node coordinate with the same names.
    :param nodeset: Zinc Nodeset or NodesetGroup to search.
    :param coordinatesField: The coordinate field to evaluate.
    :param nameField: The name field to match.
    :return: Dict of names -> coordinates.
    """
    componentsCount = coordinatesField.getNumberOfComponents()
    fieldmodule = nodeset.getFieldmodule()
    fieldcache = fieldmodule.createFieldcache()
    nameRecords = {}  # name -> (coordinates, count)
    nodeiter = nodeset.createNodeiterator()
    node = nodeiter.next()
    while node.isValid():
        fieldcache.setNode(node)
        name = nameField.evaluateString(fieldcache)
        coordinatesResult, coordinates = coordinatesField.evaluateReal(fieldcache, componentsCount)
        if name and (coordinatesResult == RESULT_OK):
            nameRecord = nameRecords.get(name)
            if nameRecord:
                nameCentre = nameRecord[0]
                for c in range(componentsCount):
                    nameCentre[c] += coordinates[c]
                nameRecord[1] += 1
            else:
                nameRecords[name] = (coordinates, 1)
        node = nodeiter.next()
    # divide centre coordinates by count
    nameCentres = {}
    for name in nameRecords:
        nameRecord = nameRecords[name]
        nameCount = nameRecord[1]
        nameCentre = nameRecord[0]
        if nameCount > 1:
            scale = 1.0/nameCount
            for c in range(componentsCount):
                nameCentre[c] *= scale
        nameCentres[name] = nameCentre
    return nameCentres


def evaluate_field_nodeset_range(field: Field, nodeset: Nodeset):
    """
    :return: min, max range of field over nodes.
    """
    fieldmodule = nodeset.getFieldmodule()
    components_count = field.getNumberOfComponents()
    with ZincCacheChanges(fieldmodule):
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
    with ZincCacheChanges(fieldmodule):
        mean_field = fieldmodule.createFieldNodesetMean(field, nodeset)
        fieldcache = fieldmodule.createFieldcache()
        result, mean_values = mean_field.evaluateReal(fieldcache, components_count)
        assert result == RESULT_OK
        del mean_field
        del fieldcache
    assert result == RESULT_OK
    return mean_values


def transform_coordinates(field: Field, rotationScale, offset, time = 0.0) -> bool:
    """
    Transform finite element field coordinates by matrix and offset, handling nodal derivatives and versions.
    Limited to nodal parameters, rectangular cartesian coordinates
    :param field: the coordinate field to transform
    :param rotationScale: square transformation matrix 2-D array with as many rows and columns as field components.
    :param offset: coordinates offset
    :return: True on success, otherwise false
    """
    ncomp = field.getNumberOfComponents()
    if (ncomp != 2) and (ncomp != 3):
        print('zinc.transformCoordinates: field has invalid number of components')
        return False
    if (len(rotationScale) != ncomp) or (len(offset) != ncomp):
        print('zinc.transformCoordinates: invalid matrix number of columns or offset size')
        return False
    for matRow in rotationScale:
        if len(matRow) != ncomp:
            print('zinc.transformCoordinates: invalid matrix number of columns')
            return False
    if (field.getCoordinateSystemType() != Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN):
        print('zinc.transformCoordinates: field is not rectangular cartesian')
        return False
    feField = field.castFiniteElement()
    if not feField.isValid():
        print('zinc.transformCoordinates: field is not finite element field type')
        return False
    success = True
    fm = field.getFieldmodule()
    fm.beginChange()
    cache = fm.createFieldcache()
    cache.setTime(time)
    nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    nodetemplate = nodes.createNodetemplate()
    nodeIter = nodes.createNodeiterator()
    node = nodeIter.next()
    while node.isValid():
        nodetemplate.defineFieldFromNode(feField, node)
        cache.setNode(node)
        for derivative in [Node.VALUE_LABEL_VALUE, Node.VALUE_LABEL_D_DS1, Node.VALUE_LABEL_D_DS2, Node.VALUE_LABEL_D2_DS1DS2,
                           Node.VALUE_LABEL_D_DS3, Node.VALUE_LABEL_D2_DS1DS3, Node.VALUE_LABEL_D2_DS2DS3, Node.VALUE_LABEL_D3_DS1DS2DS3]:
            versions = nodetemplate.getValueNumberOfVersions(feField, -1, derivative)
            for v in range(versions):
                result, values = feField.getNodeParameters(cache, -1, derivative, v + 1, ncomp)
                if result != RESULT_OK:
                    success = False
                else:
                    newValues = vectorops.matrixvectormult(rotationScale, values)
                    if derivative == Node.VALUE_LABEL_VALUE:
                        newValues = vectorops.add(newValues, offset)
                    result = feField.setNodeParameters(cache, -1, derivative, v + 1, newValues)
                    if result != RESULT_OK:
                        success = False
        node = nodeIter.next()
    fm.endChange()
    if not success:
        print('zinc.transformCoordinates: failed to get/set some values')
    return success


def create_nodes(finite_element_field, node_coordinate_set, node_set_name='nodes', time=None, node_set=None):
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


def get_element_node_identifiers(element : Element, eft : Elementfieldtemplate) -> list:
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


def get_element_node_identifiers_basis_order(element : Element, eft : Elementfieldtemplate) -> list:
    '''
    Get list of node identifiers used by eft in element with the default number
    and order for the element basis. For example, with a bilinear lagrange
    basis, 4 node identifiers are always returned, possibly with repeats, even
    if the eft collapsed it to 3 nodes in an arbitrary order.

    :param element: The element to query.
    :param eft: The element field template the nodes are mapped for.
    :return: List of global node identifiers.
    '''
    node_identifiers = []
    fn = 1
    elementbasis = eft.getElementbasis()
    for n in range(eft.getElementbasis().getNumberOfNodes()):
        ln = eft.getTermLocalNodeIndex(fn, 1)
        node_identifiers.append(element.getNode(eft, ln).getIdentifier())
        fn += elementbasis.getNumberOfFunctionsPerNode(n + 1)
    return node_identifiers


def get_maximum_element_identifier(mesh : Mesh) -> int:
    """
    :return: Maximum element identifier in mesh or -1 if none.
    """
    maximumElementId = -1
    elementiterator = mesh.createElementiterator()
    element = elementiterator.next()
    while element.isValid():
        id = element.getIdentifier()
        if id > maximumElementId:
            maximumElementId = id
        element = elementiterator.next()
    return maximumElementId


def get_maximum_node_identifier(nodeset : Nodeset) -> int:
    """
    :return: Maximum node identifier in nodeset or -1 if none.
    """
    maximumNodeId = -1
    nodeiterator = nodeset.createNodeiterator()
    node = nodeiterator.next()
    while node.isValid():
        id = node.getIdentifier()
        if id > maximumNodeId:
            maximumNodeId = id
        node = nodeiterator.next()
    return maximumNodeId


createCubeElement = create_cube_element
createSquareElement = create_square_element
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
