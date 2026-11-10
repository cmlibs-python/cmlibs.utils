"""
Utilities for reading and writing regions/field to/from a buffer.
"""
from cmlibs.zinc.result import RESULT_OK


def region_read_from_buffer(region, buffer):
    """
    Read the given buffer into the given region.

    :param region: A Zinc Region to read the buffer into.
    :param buffer: A buffer of bytes.
    :return: The result of the region read operation.
    """
    temp_sir = region.createStreaminformationRegion()
    temp_sir.createStreamresourceMemoryBuffer(buffer)
    return region.read(temp_sir)


def region_write_to_buffer(region, resource_domain_type=None, field_names=None,
                           recursion_mode=None):
    """
    Write the contents of the given region to a buffer.
    The content written to the buffer can be controlled with resource domain type and field names.

    :param region: The Zinc Region to write the content from.
    :param resource_domain_type: A logical OR of any values in Field.DOMAIN_TYPE_* e.g.
    Field.DOMAIN_TYPE_DATAPOINTS or Field.DOMAIN_TYPE_NODES or Field.DOMAIN_TYPE_MESH1D | Field.DOMAIN_TYPE_NODES.
    :param field_names: Optional list of field names to output, if omitted writes all fields.
    :param recursion_mode: Optionally specify mode controlling whether subregions are also output, currently either
    StreaminformationRegion.RECURSION_MODE_ON (default) to write all subregions, or
    StreaminformationRegion.RECURSION_MODE_OFF to write only this region and omit all groups.
    :return: The buffer in bytes written from the region, or None if failed.
    """
    sir = region.createStreaminformationRegion()
    srm = sir.createStreamresourceMemory()
    if resource_domain_type is not None:
        sir.setResourceDomainTypes(srm, resource_domain_type)
    if field_names is not None:
        sir.setFieldNames(field_names)
    if recursion_mode is not None:
        sir.setRecursionMode(recursion_mode)
    region.write(sir)
    result, buffer = srm.getBuffer()
    return buffer if result == RESULT_OK else None
