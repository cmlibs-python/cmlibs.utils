'''
Created on May 21, 2015

@author: hsorby
'''
from opencmiss.zinc.element import Element, Elementbasis


def createFiniteElementField(region):
    '''
    Create a finite element field of three dimensions
    called 'coordinates' and set the coordinate type true.
    '''
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()

    # Create a finite element field with 3 components to represent 3 dimensions
    finite_element_field = fieldmodule.createFieldFiniteElement(3)

    # Set the name of the field
    finite_element_field.setName('coordinates')
    # Set the attribute is managed to 1 so the field module will manage the field for us

    finite_element_field.setManaged(True)
    finite_element_field.setTypeCoordinate(True)
    fieldmodule.endChange()

    return finite_element_field


def createNodes(finite_element_field, node_coordinate_set):
    """
    Create a node for every coordinate in the node_coordinate_set.

    :param finite_element_field:
    :param node_coordinate_set:
    :return: None
    """
    fieldmodule = finite_element_field.getFieldmodule()
    # Find a special node set named 'nodes'
    nodeset = fieldmodule.findNodesetByName('nodes')
    node_template = nodeset.createNodetemplate()
    
    # Set the finite element coordinate field for the nodes to use
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()
    for node_coordinate in node_coordinate_set:
        node = nodeset.createNode(-1, node_template)
        # Set the node coordinates, first set the field cache to use the current node
        field_cache.setNode(node)
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
    

def createPlaneVisibilityField(fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
    """
    Create an iso-scalar field that is based on the plane equation.
    """
    d = fieldmodule.createFieldSubtract(finite_element_field, point_on_plane_field)
    p = fieldmodule.createFieldDotProduct(d, plane_normal_field)
    t = fieldmodule.createFieldConstant(0.1)
    
    v = fieldmodule.createFieldLessThan(p, t)

    return v
    

def createIsoScalarField(region, coordinate_field, plane):
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()
    normal_field = plane.getNormalField()
    rotation_point_field = plane.getRotationPointField()
    iso_scalar_field = _createPlaneEquationFormulation(fieldmodule, coordinate_field, normal_field, rotation_point_field)
    fieldmodule.endChange()
    
    return iso_scalar_field


