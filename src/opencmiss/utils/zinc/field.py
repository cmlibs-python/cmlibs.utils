'''
Utilities for creating and working with Zinc Fields.
'''
from opencmiss.utils.zinc.general import ZincCacheChanges
from opencmiss.zinc.element import Element, Elementbasis, Mesh
from opencmiss.zinc.node import Node
from opencmiss.zinc.field import Field, FieldFiniteElement, FieldStoredMeshLocation
from opencmiss.zinc.fieldmodule import Fieldmodule
from opencmiss.zinc.result import RESULT_OK
from opencmiss.utils.maths import vectorops


def FieldIsManagedCoordinates(field : Field):
    """
    Conditional function returning True if the field is Finite Element
    type with 3 components, and is managed.
    """
    return field.castFiniteElement().isValid() and (field.getNumberOfComponents() == 3) and field.isManaged()


def FieldIsManagedGroup(field : Field):
    """
    Conditional function returning True if the field is a managed Group.
    """
    return field.castGroup().isValid() and field.isManaged()


def assignFieldParameters(targetField : Field, sourceField : Field):
    """
    Copy parameters from sourceField to targetField.
    Currently only works for node parameters.
    """
    fieldassignment = targetField.createFieldassignment(sourceField)
    fieldassignment.assign()


def createDisplacementGradientFields(coordinates : Field, referenceCoordinates : Field, mesh : Mesh):
    """
    :return: 1st and 2nd displacement gradients of (coordinates - referenceCoordinates) w.r.t. referenceCoordinates.
    """
    assert (coordinates.getNumberOfComponents() == 3) and (referenceCoordinates.getNumberOfComponents() == 3)
    fieldmodule = mesh.getFieldmodule()
    dimension = mesh.getDimension()
    displacementGradient = None
    displacementGradient2 = None
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


def createEulerAnglesRotationMatrixField(fieldmodule : Fieldmodule, eulerAngles : Field) -> Field:
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


def createFieldFiniteElementClone(sourceField : Field, targetName : str, managed=False) -> Field:
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


def createFieldMeshIntegral(coordinates : Field, mesh : Mesh, numberOfPoints = 3):
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


def createTransformationFields(coordinates : Field, rotationAngles = [ 0.0, 0.0, 0.0 ], scaleValue : float = 1.0, translationOffsets = [ 0.0, 0.0, 0.0 ]):
    """
    Create constant fields for rotation, scale and translation containing the supplied
    values, plus the transformed coordinates applying them in the supplied order.
    :param coordinates: The coordinate field to scale, 3 components.
    :param rotationAngles: List of euler angles, length = number of components. See createEulerAnglesRotationMatrixField.
    :param scaleValue: Scalar to multiply all components of coordinates.
    :param translationOffsets: List of offsets, length = number of components.
    :return: 4 fields: transformedCoordinates, rotation, scale, translation
    """
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


def getGroupList(fieldmodule):
    """
    Get list of Zinc groups (FieldGroup) in fieldmodule.
    """
    groups = []
    fielditer = fieldmodule.createFielditerator()
    field = fielditer.next()
    while field.isValid():
        group = field.castGroup()
        if group.isValid():
            groups.append(group)
        field = fielditer.next()
    return groups


def getManagedFieldNames(fieldmodule):
    """
    Get names of managed fields in fieldmodule.
    """
    fieldNames = []
    fieldIter = fieldmodule.createFielditerator()
    field = fieldIter.next()
    while field.isValid():
        if field.isManaged():
            fieldNames.append(field.getName())
        field = fieldIter.next()
    return fieldNames


def getOrCreateFieldFiniteElement(fieldmodule : Fieldmodule, fieldName : str, componentsCount : int,
        componentNames=None, managed=False, coordinate=False) -> FieldFiniteElement:
    """
    Finds or creates a finite element field for the specified number of real components.
    Asserts existing field is finite element type with correct attributes.

    :param fieldmodule:  Zinc Fieldmodule to find or create field in.
    :param fieldName:  Name of field to find or create.
    :param componentsCount: Number of components / dimension of field, from 1 to 3.
    :param componentNames: Optional list of component names.
    :param managed: Managed state of field if created here.
    :param coordinate: Default value of flag indicating field gives geometric coordinates.
    :return: Zinc Field.
    """
    assert (componentsCount > 0), "opencmiss.utils.zinc.field.getOrCreateFieldFiniteElement.  Invalid componentsCount"
    assert (not componentNames) or (len(componentNames) == componentsCount), "opencmiss.utils.zinc.field.getOrCreateRealField.  Invalid componentNames"
    field = fieldmodule.findFieldByName(fieldName)
    if field.isValid():
        field = field.castFiniteElement()
        assert field.isValid(), "opencmiss.utils.zinc.field.getOrCreateFieldFiniteElement.  Existing field " + fieldName + " is not finite element type"
        assert field.getNumberOfComponents() == componentsCount, "opencmiss.utils.zinc.field.getOrCreateFieldFiniteElement.  Existing field " + fieldName + " does not have " + str(componentsCount) + " components"
        return field
    with ZincCacheChanges(fieldmodule):
        field = fieldmodule.createFieldFiniteElement(componentsCount)
        field.setName(fieldName)
        field.setManaged(managed)
        field.setTypeCoordinate(coordinate)
        if componentNames:
            for c in range(componentsCount):
                field.setComponentName(c + 1, componentNames[c])
    return field


def getOrCreateCoordinatesField(fieldmodule : Fieldmodule, name="coordinates", componentsCount=3) -> FieldFiniteElement:
    '''
    Get or create RC coordinates finite element field of supplied name with
    from 1 to 3 components named "x", "y" and "z". New field is managed.
    '''
    assert 1 <= componentsCount <= 3
    return getOrCreateFieldFiniteElement(fieldmodule, name, componentsCount,
        componentNames=("x", "y", "z"), managed=True, coordinate=True)


def getOrCreateFieldStoredMeshLocation(fieldmodule : Fieldmodule, mesh : Mesh, name=None, managed=False) -> FieldStoredMeshLocation:
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
        name="location_" + mesh.getName()
    field = fieldmodule.findFieldByName(name)
    if field.isValid():
        meshLocationField = field.castStoredMeshLocation()
        assert meshLocationField.isValid(), "opencmiss.utils.zinc.field.getOrCreateFieldStoredMeshLocation.  " \
            "Existing field " + name + " is not StoredMeshLocation type"
        return meshLocationField
    with ZincCacheChanges(fieldmodule):
        meshLocationField = fieldmodule.createFieldStoredMeshLocation(mesh)
        meshLocationField.setName(name)
        meshLocationField.setManaged(managed)
    return meshLocationField


def getUniqueFieldName(fieldmodule : Fieldmodule, baseName : str) -> str:
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


def orphanFieldOfName(fieldmodule : Fieldmodule, name : str):
    """
    Find existing field with the name in fieldmodule.
    If it exists, uniquely rename it (prefix with ".destroy_" and append unique number)
    and unmanage it so destroyed when no longer in use.
    """
    orphanField = fieldmodule.findFieldByName(name)
    if orphanField.isValid():
        orphanField.setName(getUniqueFieldName(fieldmodule, ".destroy_" + name))
        orphanField.setManaged(False)
