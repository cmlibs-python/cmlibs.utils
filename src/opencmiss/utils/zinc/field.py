'''
Utilities for creating and working with Zinc Fields.
'''
from opencmiss.utils.zinc.general import ZincCacheChanges
from opencmiss.zinc.element import Mesh
from opencmiss.zinc.field import Field, FieldFiniteElement, FieldStoredMeshLocation
from opencmiss.zinc.fieldmodule import Fieldmodule
from opencmiss.zinc.result import RESULT_OK


def field_is_managed_coordinates(field : Field):
    """
    Conditional function returning True if the field is Finite Element
    type with 3 components, and is managed.
    """
    return field.castFiniteElement().isValid() and (field.getNumberOfComponents() == 3) and field.isManaged()


def field_is_managed_group(field : Field):
    """
    Conditional function returning True if the field is a managed Group.
    """
    return field.castGroup().isValid() and field.isManaged()


def assign_field_parameters(targetField : Field, sourceField : Field):
    """
    Copy parameters from sourceField to targetField.
    Currently only works for node parameters.
    """
    fieldassignment = targetField.createFieldassignment(sourceField)
    fieldassignment.assign()


def create_fields_displacement_gradients(coordinates: Field, referenceCoordinates: Field, mesh: Mesh):
    """
    :return: 1st and 2nd displacement gradients of (coordinates - referenceCoordinates) w.r.t. referenceCoordinates.
    """
    assert (coordinates.getNumberOfComponents() == 3) and (referenceCoordinates.getNumberOfComponents() == 3)
    fieldmodule = mesh.getFieldmodule()
    dimension = mesh.getDimension()
    with ZincCacheChanges(fieldmodule):
        if dimension == 3:
            u = coordinates  - referenceCoordinates
            displacementGradient = fieldmodule.createFieldGradient(u, referenceCoordinates)
            displacementGradient2 = fieldmodule.createFieldGradient(displacementGradient, referenceCoordinates)
        elif dimension == 2:
            # Note this needs improvement as missing cross terms
            # assume xi directions are approximately normal; effect is to penalise elements where this is not so, which is also desired
            dX_dxi1 = fieldmodule.createFieldDerivative(referenceCoordinates, 1)
            dX_dxi2 = fieldmodule.createFieldDerivative(referenceCoordinates, 2)
            dx_dxi1 = fieldmodule.createFieldDerivative(coordinates, 1)
            dx_dxi2 = fieldmodule.createFieldDerivative(coordinates, 2)
            dS1_dxi1 = fieldmodule.createFieldMagnitude(dX_dxi1)
            dS2_dxi2 = fieldmodule.createFieldMagnitude(dX_dxi2)
            du_dS1 = (dx_dxi1 - dX_dxi1)/dS1_dxi1
            du_dS2 = (dx_dxi2 - dX_dxi2)/dS2_dxi2
            displacementGradient = fieldmodule.createFieldConcatenate([du_dS1, du_dS2])
            # curvature:
            d2u_dSdxi1 = fieldmodule.createFieldDerivative(displacementGradient, 1)
            d2u_dSdxi2 = fieldmodule.createFieldDerivative(displacementGradient, 2)
            displacementGradient2 = fieldmodule.createFieldConcatenate([ d2u_dSdxi1/dS1_dxi1, d2u_dSdxi2/dS2_dxi2 ])
        else:  # dimension == 1
            dX_dxi1 = fieldmodule.createFieldDerivative(referenceCoordinates, 1)
            dx_dxi1 = fieldmodule.createFieldDerivative(coordinates, 1)
            dS1_dxi1 = fieldmodule.createFieldMagnitude(dX_dxi1)
            displacementGradient = (dx_dxi1 - dX_dxi1)/dS1_dxi1
            # curvature:
            displacementGradient2 = fieldmodule.createFieldDerivative(displacementGradient, 1)/dS1_dxi1
    return displacementGradient, displacementGradient2


def create_field_euler_angles_rotation_matrix(fieldmodule : Fieldmodule, eulerAngles : Field) -> Field:
    """
    From OpenCMISS-Zinc graphics_library.cpp, transposed.
    :param eulerAngles: 3-component field of angles in radians, components:
    1 = azimuth (about z)
    2 = elevation (about rotated y)
    3 = roll (about rotated x)
    :return: 3x3 rotation matrix field suitable for pre-multiplying [x, y, z].
    """
    assert eulerAngles.getNumberOfComponents() == 3
    with ZincCacheChanges(fieldmodule):
        azimuth = fieldmodule.createFieldComponent(eulerAngles, 1)
        cos_azimuth = fieldmodule.createFieldCos(azimuth)
        sin_azimuth = fieldmodule.createFieldSin(azimuth)
        elevation = fieldmodule.createFieldComponent(eulerAngles, 2)
        cos_elevation = fieldmodule.createFieldCos(elevation)
        sin_elevation = fieldmodule.createFieldSin(elevation)
        roll = fieldmodule.createFieldComponent(eulerAngles, 3)
        cos_roll = fieldmodule.createFieldCos(roll)
        sin_roll = fieldmodule.createFieldSin(roll)
        minus_one = fieldmodule.createFieldConstant([ -1.0 ])
        cos_azimuth_sin_elevation = cos_azimuth*sin_elevation
        sin_azimuth_sin_elevation = sin_azimuth*sin_elevation
        matrixComponents = [
            cos_azimuth*cos_elevation,
            cos_azimuth_sin_elevation*sin_roll - sin_azimuth*cos_roll,
            cos_azimuth_sin_elevation*cos_roll + sin_azimuth*sin_roll,
            sin_azimuth*cos_elevation,
            sin_azimuth_sin_elevation*sin_roll + cos_azimuth*cos_roll,
            sin_azimuth_sin_elevation*cos_roll - cos_azimuth*sin_roll,
            minus_one*sin_elevation,
            cos_elevation*sin_roll,
            cos_elevation*cos_roll ]
        rotationMatrix = fieldmodule.createFieldConcatenate(matrixComponents)
    return rotationMatrix


def create_field_finite_element_clone(sourceField : Field, targetName : str, managed=False) -> Field:
    """
    Copy an existing Finite Element Field to a new field of supplied name.

    :param sourceField: Zinc finite element field to copy.
    :param targetName: The name of the new field, asserts that no field of that name exists.
    :param managed: Managed state of field if created here.
    :return: New identically defined field with supplied name.
    """
    assert sourceField.castFiniteElement().isValid(), "opencmiss.utils.zinc.field.createFieldFiniteElementClone.  Not a Zinc finite element field"
    fieldmodule = sourceField.getFieldmodule()
    field = fieldmodule.findFieldByName(targetName)
    assert not field.isValid(), "opencmiss.utils.zinc.field.createFieldFiniteElementClone.  Target field name is in use"
    with ZincCacheChanges(fieldmodule):
        # Zinc needs a function to do this efficiently; currently serialise to string, replace field name and reload!
        sourceName = sourceField.getName()
        region = fieldmodule.getRegion()
        sir = region.createStreaminformationRegion()
        srm = sir.createStreamresourceMemory()
        sir.setFieldNames([ sourceName ])
        region.write(sir)
        result, buffer = srm.getBuffer()
        # small risk of modifying other text here:
        sourceBytes = bytes(") " + sourceName + ",", "utf-8")
        targetBytes = bytes(") " + targetName + ",", "utf-8")
        buffer = buffer.replace(sourceBytes, targetBytes)
        sir = region.createStreaminformationRegion()
        srm = sir.createStreamresourceMemoryBuffer(buffer)
        result = region.read(sir)
        assert result == RESULT_OK
    # note currently must have called endChange before field can be found
    field = fieldmodule.findFieldByName(targetName).castFiniteElement()
    field.setManaged(managed)
    assert field.isValid()
    return field


def create_field_mesh_integral(coordinates : Field, mesh : Mesh, numberOfPoints = 3):
    """
    Create a field integrating the coordinates to give scalar volume/area/length over
    the mesh, depending on its dimension.
    :param numberOfPoints: Number of Gauss points.
    :return: Field giving volume of coordinates field over mesh via Gaussian quadrature.
    """
    fieldmodule = coordinates.getFieldmodule()
    with ZincCacheChanges(fieldmodule):
        meshIntegralField = fieldmodule.createFieldMeshIntegral(fieldmodule.createFieldConstant(1.0), coordinates, mesh)
        meshIntegralField.setNumbersOfPoints(numberOfPoints)
    return meshIntegralField


def _create_plane_equation_formulation(fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
    """
    Create an iso-scalar field that is based on the plane equation.
    """
    d = fieldmodule.createFieldDotProduct(plane_normal_field, point_on_plane_field)
    iso_scalar_field = fieldmodule.createFieldDotProduct(finite_element_field, plane_normal_field) - d

    return iso_scalar_field


def create_field_image(fieldmodule, image_filename, field_name='image'):
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


def create_fields_transformations(coordinates : Field, rotationAngles = None, scaleValue : float = 1.0, translationOffsets = None):
    """
    Create constant fields for rotation, scale and translation containing the supplied
    values, plus the transformed coordinates applying them in the supplied order.
    :param coordinates: The coordinate field to scale, 3 components.
    :param rotationAngles: List of euler angles, length = number of components. See createEulerAnglesRotationMatrixField.
    :param scaleValue: Scalar to multiply all components of coordinates.
    :param translationOffsets: List of offsets, length = number of components.
    :return: 4 fields: transformedCoordinates, rotation, scale, translation
    """
    if rotationAngles is None:
        rotationAngles = [0.0, 0.0, 0.0]
    if translationOffsets is None:
        translationOffsets = [0.0, 0.0, 0.0]
    componentsCount = coordinates.getNumberOfComponents()
    assert (componentsCount == 3) and (len(rotationAngles) == componentsCount) and isinstance(scaleValue, float) \
        and (len(translationOffsets) == componentsCount), "createTransformationFields.  Invalid arguments"
    fieldmodule = coordinates.getFieldmodule()
    with ZincCacheChanges(fieldmodule):
        # scale, translate and rotate model, in that order
        rotation = fieldmodule.createFieldConstant(rotationAngles)
        scale = fieldmodule.createFieldConstant(scaleValue)
        translation = fieldmodule.createFieldConstant(translationOffsets)
        rotationMatrix = createEulerAnglesRotationMatrixField(fieldmodule, rotation)
        rotatedCoordinates = fieldmodule.createFieldMatrixMultiply(componentsCount, rotationMatrix, coordinates)
        transformedCoordinates = rotatedCoordinates*scale + translation
        assert transformedCoordinates.isValid()
    return transformedCoordinates, rotation, scale, translation


def create_field_volume_image(fieldmodule, image_filenames, field_name='volume_image'):
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


def create_field_plane_visibility(fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
    """
    Create an iso-scalar field that is based on the plane equation.
    """
    d = fieldmodule.createFieldSubtract(finite_element_field, point_on_plane_field)
    p = fieldmodule.createFieldDotProduct(d, plane_normal_field)
    t = fieldmodule.createFieldConstant(0.1)

    v = fieldmodule.createFieldLessThan(p, t)

    return v


def create_field_visibility_for_plane(region, coordinate_field, plane):
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


def create_field_iso_scalar(region, coordinate_field, plane):
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()
    normal_field = plane.getNormalField()
    rotation_point_field = plane.getRotationPointField()
    iso_scalar_field = _create_plane_equation_formulation(fieldmodule, coordinate_field, normal_field,
                                                          rotation_point_field)
    fieldmodule.endChange()

    return iso_scalar_field


def get_group_list(fieldmodule):
    """
    Get list of Zinc groups (FieldGroup) in fieldmodule.
    """
    groups = []
    field_iter = fieldmodule.createFielditerator()
    field = field_iter.next()
    while field.isValid():
        group = field.castGroup()
        if group.isValid():
            groups.append(group)
        field = field_iter.next()
    return groups


def get_managed_field_names(fieldmodule):
    """
    Get names of managed fields in fieldmodule.
    """
    field_names = []
    field_iter = fieldmodule.createFielditerator()
    field = field_iter.next()
    while field.isValid():
        if field.isManaged():
            field_names.append(field.getName())
        field = field_iter.next()
    return field_names


def field_exists(fieldmodule: Fieldmodule, field_name: str, field_type, components_count) -> bool:
    """
    Tests to determine if the field with the given name exists in the given field module.

    :param fieldmodule: Zinc field module to search.
    :param field_name: Name of field to find.
    :param field_type: Type of field if derived type. Default: finiteelement.
    :param components_count: Number of components in the field. Default: 3.
    :return: True if the field is found in the module with the given name and number of components,
    false otherwise.
    """
    field = fieldmodule.findFieldByName(field_name)
    if field.isValid():
        if hasattr(field, 'cast' + field_type):
            field = getattr(field, 'cast' + field_type)()
            return field.isValid() and field.getNumberOfComponents() == components_count

        return field.getNumberOfComponents() == components_count

    return False


def create_field_finite_element(fieldmodule: Fieldmodule, field_name: str, components_count: int,
                                component_names=None, managed=False, type_coordinate=False) -> FieldFiniteElement:
    with ZincCacheChanges(fieldmodule):
        field = fieldmodule.createFieldFiniteElement(components_count)
        field.setName(field_name)
        field.setManaged(managed)
        field.setTypeCoordinate(type_coordinate)
        if component_names is not None:
            for index, component_name in enumerate(component_names[:components_count]):
                field.setComponentName(index + 1, component_name)

    return field


def get_or_create_field_finite_element(fieldmodule: Fieldmodule, field_name: str, components_count: int,
                                       component_names=None, managed=False, type_coordinate=False)\
        -> FieldFiniteElement:
    """
    Finds or creates a finite element field for the specified number of real components.
    Asserts existing field is finite element type with correct attributes.

    :param fieldmodule:  Zinc Fieldmodule to find or create field in.
    :param field_name:  Name of field to find or create.
    :param components_count: Number of components / dimension of field, from 1 to 3.
    :param component_names: Optional list of component names.
    :param managed: Managed state of field if created here.
    :param type_coordinate: Default value of flag indicating field gives geometric coordinates.
    :return: Zinc Field.
    """
    assert (components_count > 0), "opencmiss.utils.zinc.field.get_or_create_field_finite_element." \
                                   "  Invalid components_count"
    assert (not component_names) or (len(component_names) == components_count),\
        "opencmiss.utils.zinc.field.get_or_create_field_finite_element.  Invalid component_names"
    if field_exists(fieldmodule, field_name, 'FiniteElement', components_count):
        field = fieldmodule.findFieldByName(field_name)
        return field.castFiniteElement()

    return create_field_finite_element(fieldmodule, field_name, components_count,
                                       component_names, managed, type_coordinate)


def create_field_coordinates(fieldmodule : Fieldmodule, name="coordinates", components_count=3, managed=False)\
        -> FieldFiniteElement:
    """
    Create RC coordinates finite element field of supplied name with
    number of components 1, 2, or 3 and the components named "x", "y" and "z" if used.
    New field is not managed by default.
    """
    return create_field_finite_element(fieldmodule, name, components_count,
                                       component_names=("x", "y", "z"), managed=managed, type_coordinate=True)


def get_or_create_field_coordinates(fieldmodule : Fieldmodule, name="coordinates", components_count=3)\
        -> FieldFiniteElement:
    """
    Get or create RC coordinates finite element field of supplied name with
    number of components 1, 2, or 3 and the components named "x", "y" and "z" if used.
    New field is managed.
    """
    assert 1 <= components_count <= 3
    return get_or_create_field_finite_element(fieldmodule, name, components_count,
                                              component_names=("x", "y", "z"), managed=True, type_coordinate=True)


def get_or_create_field_stored_mesh_location(fieldmodule: Fieldmodule, mesh: Mesh, name=None, managed=False)\
        -> FieldStoredMeshLocation:
    """
    Get or create a stored mesh location field for storing locations in the
    supplied mesh, used for storing data projections.
    Note can't currently verify existing field stores locations in the supplied mesh.
    Asserts that existing field of name is a Stored Mesh Location field.
    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param mesh:  Mesh to store locations in, from same fieldmodule.
    :param name:  Name of new field. If None, defaults to "location_" + mesh.getName().
    :param managed: Managed state of field if created here.
    """
    if not name:
        name = "location_" + mesh.getName()
    field = fieldmodule.findFieldByName(name)
    if field_exists(fieldmodule, name, 'StoredMeshLocation', mesh.getDimension()):
        meshLocationField = field.castStoredMeshLocation()
        return meshLocationField
    with ZincCacheChanges(fieldmodule):
        meshLocationField = fieldmodule.createFieldStoredMeshLocation(mesh)
        meshLocationField.setName(name)
        meshLocationField.setManaged(managed)
    return meshLocationField


def get_unique_field_name(fieldmodule: Fieldmodule, baseName: str) -> str:
    """
    Return a unique field name in fieldmodule either equal to baseName or
    appending a number starting at 1 and increasing.

    :param fieldmodule: The fieldmodule to get a unique name in.
    :param baseName: The name to match or append a number to.
    """
    field = fieldmodule.findFieldByName(baseName)
    if not field.isValid():
        return baseName
    number = 1
    while True:
        fieldName = baseName + str(number)
        field = fieldmodule.findFieldByName(fieldName)
        if not field.isValid():
            return fieldName
        number += 1


def orphan_field_of_name(fieldmodule : Fieldmodule, name : str):
    """
    Find existing field with the name in fieldmodule.
    If it exists, uniquely rename it (prefix with ".destroy_" and append unique number)
    and unmanage it so destroyed when no longer in use.
    """
    orphan_field = fieldmodule.findFieldByName(name)
    if orphan_field.isValid():
        orphan_field.setName(getUniqueFieldName(fieldmodule, ".destroy_" + name))
        orphan_field.setManaged(False)


# Create C++ style aliases for names of functions.
createFieldsDisplacementGradients = create_fields_displacement_gradients
createFieldsTransformations = create_fields_transformations
createFieldEulerAnglesRotationMatrix = create_field_euler_angles_rotation_matrix
createFieldFiniteElementClone = create_field_finite_element_clone
createFieldMeshIntegral = create_field_mesh_integral
createFieldVolumeImage = create_field_volume_image
createFieldPlaneVisibility = create_field_plane_visibility
createFieldVisibilityForPlane = create_field_visibility_for_plane
createFieldIsoScalar = create_field_iso_scalar
createFieldImage = create_field_image
createFieldCoordinates = create_field_coordinates
createFieldFiniteElement = create_field_finite_element
getGroupList = get_group_list
getManagedFieldNames = get_managed_field_names
getOrCreateFieldFiniteElement = get_or_create_field_finite_element
getOrCreateFieldCoordinates = get_or_create_field_coordinates
getOrCreateFieldStoredMeshLocation = get_or_create_field_stored_mesh_location
getUniqueFieldName = get_unique_field_name
orphanFieldOfName = orphan_field_of_name
fieldIsManagedCoordinates = field_is_managed_coordinates
fieldIsManagedGroup = field_is_managed_group
assignFieldParameters = assign_field_parameters
fieldExists = field_exists
