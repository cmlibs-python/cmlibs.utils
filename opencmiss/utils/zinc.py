'''
Created on May 21, 2015

@author: hsorby
'''
from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.zinc.node import Node
from opencmiss.zinc.field import Field
from opencmiss.zinc.status import OK as ZINC_OK
from opencmiss.utils.maths import vectorops


class AbstractNodeDataObject(object):

    def __init__(self, field_names, time_sequence=None, time_sequence_field_names=None):
        self._field_names = field_names
        self._time_sequence = time_sequence if time_sequence else []
        self._time_sequence_field_names = time_sequence_field_names if time_sequence_field_names else []
        for field_name in field_names:
            if not hasattr(self, field_name):
                raise NotImplementedError('Missing data method for field: %s' % field_name)

    def get_field_names(self):
        return self._field_names

    def get_time_sequence(self):
        return self._time_sequence

    def set_time_sequence(self, time_sequence):
        self._time_sequence = time_sequence

    def get_time_sequence_field_names(self):
        return self._time_sequence_field_names

    def set_time_sequence_field_names(self, time_sequence_field_names):
        self._time_sequence_field_names = time_sequence_field_names


def createFiniteElementField(region, dimension=3, field_name='coordinates', managed=True, type_coordinate=True):
    """
    Create a finite element field of three dimensions
    called 'coordinates' and set the coordinate type true.

    :param region: The region to create the finite  element field in.
    :param dimension: The dimension of the finite element field to create, defaults to 3.
    :param field_name: The name of the field, defaults to 'coordinates'.
    :param managed: Is managed, True or False.  Defaults to True.
    :param type_coordinate: Is type coordinate: True or False.  Defaults to True.
    """
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()

    # Create a finite element field with 3 components to represent 3 dimensions
    finite_element_field = fieldmodule.createFieldFiniteElement(dimension)

    # Set the name of the field
    finite_element_field.setName(field_name)
    # Set the attribute is managed to 1 so the field module will manage the field for us

    finite_element_field.setManaged(managed)
    finite_element_field.setTypeCoordinate(type_coordinate)
    fieldmodule.endChange()

    return finite_element_field


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
        field.assignReal(field_cache, getattr(data_object, field_name)())

    return node.getIdentifier()


def createNodes(finite_element_field, node_coordinate_set, node_set_name='nodes', time=None, node_set=None):
    """
    Create a node for every coordinate in the node_coordinate_set.

    :param finite_element_field:
    :param node_coordinate_set:
    :param node_set_name:
    :param time: The time to set for the node, defaults to None for nodes that are not time aware.
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


def createVisibilityFieldForPlane(region, coordinate_field, plane):
    """
    Create a
    :param region:
    :param coordinate_field:
    :param plane:
    :return:
    """
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()
    normal_field = plane.getNormalField()
    rotation_point_field = plane.getRotationPointField()
    visibility_field = createPlaneVisibilityField(fieldmodule, coordinate_field, normal_field, rotation_point_field)
    fieldmodule.endChange()

    return visibility_field


def defineStandardVisualisationTools(context):
    glyph_module = context.getGlyphmodule()
    glyph_module.defineStandardGlyphs()
    material_module = context.getMaterialmodule()
    material_module.defineStandardMaterials()


def transformCoordinates(field, rotationScale, offset, time = 0.0):
    '''
    Transform finite element field coordinates by matrix and offset, handling nodal derivatives and versions.
    Limited to nodal parameters, rectangular cartesian coordinates
    :param field: the coordinate field to transform
    :param rotationScale: square transformation matrix 2-D array with as many rows and columns as field components.
    :param offset: coordinates offset
    :return: True on success, otherwise false
    '''
    ncomp = field.getNumberOfComponents()
    if ((ncomp != 2) and (ncomp != 3)):
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
                if result != ZINC_OK:
                    success = False
                else:
                    newValues = vectorops.matrixvectormult(rotationScale, values)
                    if derivative == Node.VALUE_LABEL_VALUE:
                        newValues = vectorops.add(newValues, offset)
                    result = feField.setNodeParameters(cache, -1, derivative, v + 1, newValues)
                    if result != ZINC_OK:
                        success = False
        node = nodeIter.next()
    fm.endChange()
    if not success:
        print('zinc.transformCoordinates: failed to get/set some values')
    return success


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


def createImageField(fieldmodule, image_filename, field_name='image'):
    """
    Create an image field using the given fieldmodule.  The image filename must exist and
    be a known image type.

    :param fieldmodule: The fieldmodule to create the field in.
    :param image_filename: Image filename.
    :param field_name: Optional name of the image field, defaults to 'image'.
    :return: The image field created.
    """
    image_field = fieldmodule.createFieldImage()
    image_field.setName(field_name)
    image_field.setFilterMode(image_field.FILTER_MODE_LINEAR)

    # Create a stream information object that we can use to read the
    # image file from disk
    stream_information = image_field.createStreaminformationImage()

    # We are reading in a file from the local disk so our resource is a file.
    stream_information.createStreamresourceFile(image_filename)

    # Actually read in the image file into the image field.
    image_field.read(stream_information)

    return image_field


def createVolumeImageField(fieldmodule, image_filenames, field_name='volume_image'):
    """
    Create an image field using the given fieldmodule.  The image filename must exist and
    be a known image type.

    :param fieldmodule: The fieldmodule to create the field in.
    :param image_filenames: Image filename.
    :param field_name: Optional name of the image field, defaults to 'volume_image'.
    :return: The image field created.
    """
    image_field = fieldmodule.createFieldImage()
    image_field.setName(field_name)
    image_field.setFilterMode(image_field.FILTER_MODE_LINEAR)

    # Create a stream information object that we can use to read the
    # image file from disk
    stream_information = image_field.createStreaminformationImage()

    # We are reading in a file from the local disk so our resource is a file.
    for image_filename in image_filenames:
        stream_information.createStreamresourceFile(image_filename)

    # Actually read in the image file into the image field.
    image_field.read(stream_information)

    return image_field


def createMaterialUsingImageField(region, image_field, colour_mapping_type=None, image_range=None):
    """
    Use an image field in a material to create an OpenGL texture.  Returns the
    created material.

    :param region:
    :param spectrummodule:
    :param image_field:
    :param colour_mapping_type:
    :param image_range:
    :return: The material that contains the image field as a texture.
    """
    # create a graphics material from the graphics module, assign it a name
    # and set flag to true
    scene = region.getScene()
    materialmodule = scene.getMaterialmodule()
    spectrummodule = scene.getSpectrummodule()
    material = materialmodule.createMaterial()
    spectrum = spectrummodule.createSpectrum()
    component = spectrum.createSpectrumcomponent()
    if colour_mapping_type is None:
        colour_mapping_type = component.COLOUR_MAPPING_TYPE_RAINBOW
    component.setColourMappingType(colour_mapping_type)
    if image_range is not None:
        component.setRangeMinimum(image_range[0])
        component.setRangeMaximum(image_range[1])
    material.setTextureField(1, image_field)

    return material


# Create PEP8 conformant names of functions.
create_node = createNode
create_finite_element_field = createFiniteElementField
create_square_2d_finite_element = createSquare2DFiniteElement
create_volume_image_field = createVolumeImageField
create_material_using_image_field = createMaterialUsingImageField