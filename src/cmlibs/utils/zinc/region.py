from cmlibs.utils.zinc.finiteelement import get_identifiers, evaluate_field_nodeset_range
from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK

from cmlibs.utils.zinc.general import ChangeManager


def _find_missing(lst):
    return [i for x, y in zip(lst, lst[1:])
            for i in range(x + 1, y) if y - x > 1]


def convert_nodes_to_datapoints(target_region, source_region):
    source_fieldmodule = source_region.getFieldmodule()
    target_fieldmodule = target_region.getFieldmodule()
    with ChangeManager(source_fieldmodule), ChangeManager(target_fieldmodule):
        nodes = source_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        if nodes.getSize() > 0:
            datapoints = target_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
            if datapoints.getSize() > 0:
                existing_nodes_identifiers = sorted(get_identifiers(nodes))
                existing_nodes_identifiers_set = set(existing_nodes_identifiers)
                existing_datapoint_identifiers = sorted(get_identifiers(datapoints))
                in_use_identifiers = sorted(list(set(existing_datapoint_identifiers + existing_nodes_identifiers)))
                max_identifier = in_use_identifiers[-1]
                initial_available_identifiers = [i for i in range(1, in_use_identifiers[0])]
                available_identifiers = initial_available_identifiers + _find_missing(in_use_identifiers)
                datapoint_iterator = datapoints.createNodeiterator()
                datapoint = datapoint_iterator.next()
                identifier_map = {}
                while datapoint.isValid():
                    datapoint_identifier = datapoint.getIdentifier()
                    if datapoint_identifier in existing_nodes_identifiers_set and len(available_identifiers):
                        next_identifier = available_identifiers.pop(0)
                    else:
                        max_identifier += 1
                        next_identifier = max_identifier

                    identifier_map[datapoint_identifier] = next_identifier
                    datapoint = datapoint_iterator.next()

                for current_identifier, new_identifier in identifier_map.items():
                    datapoint = datapoints.findNodeByIdentifier(current_identifier)
                    datapoint.setIdentifier(new_identifier)

            # transfer nodes as datapoints to target_region
            sir = source_region.createStreaminformationRegion()
            srm = sir.createStreamresourceMemory()
            sir.setResourceDomainTypes(srm, Field.DOMAIN_TYPE_NODES)
            source_region.write(sir)
            result, buffer = srm.getBuffer()
            assert result == RESULT_OK, "Failed to write nodes"
            buffer = buffer.replace(bytes("!#nodeset nodes", "utf-8"), bytes("!#nodeset datapoints", "utf-8"))
            sir = target_region.createStreaminformationRegion()
            sir.createStreamresourceMemoryBuffer(buffer)
            result = target_region.read(sir)
            assert result == RESULT_OK, "Failed to load nodes as datapoints"
            nodes.destroyAllNodes()


def copy_nodeset(region, nodeset):
    """
    Copy nodeset to another region.
    Expects the corresponding nodeset in the region the nodeset is being copied to, to be empty.
    """
    source_region = nodeset.getFieldmodule().getRegion()
    sir = source_region.createStreaminformationRegion()
    srm = sir.createStreamresourceMemory()

    if nodeset.getName() == "datapoints":
        sir.setResourceDomainTypes(srm, Field.DOMAIN_TYPE_DATAPOINTS)
    else:
        sir.setResourceDomainTypes(srm, Field.DOMAIN_TYPE_NODES)

    source_region.write(sir)
    result, buffer = srm.getBuffer()
    assert result == RESULT_OK, f"Failed to write {nodeset.getName()}"
    sir = region.createStreaminformationRegion()
    sir.createStreamresourceMemoryBuffer(buffer)
    result = region.read(sir)
    assert result == RESULT_OK, f"Failed to load {nodeset.getName()}, result " + str(result)


def determine_appropriate_glyph_size(region, coordinates):
    fm = region.getFieldmodule()
    with ChangeManager(fm):
        fieldcache = fm.createFieldcache()
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        components_count = coordinates.getNumberOfComponents()
        # fixed width glyph size is based on average element size in all dimensions
        mesh1d = fm.findMeshByDimension(1)
        line_count = mesh1d.getSize()
        if line_count > 0:
            one = fm.createFieldConstant(1.0)
            sum_line_length = fm.createFieldMeshIntegral(one, coordinates, mesh1d)
            result, total_line_length = sum_line_length.evaluateReal(fieldcache, 1)
            glyph_width = 0.1 * total_line_length / line_count
            del sum_line_length
            del one
        if (line_count == 0) or (glyph_width == 0.0):
            # fallback if no lines: use graphics range
            min_x, max_x = evaluate_field_nodeset_range(coordinates, nodes)
            # use function of coordinate range if no elements
            if components_count == 1:
                max_scale = max_x - min_x
            else:
                first = True
                for c in range(components_count):
                    scale = max_x[c] - min_x[c]
                    if first or (scale > max_scale):
                        max_scale = scale
                        first = False
            if max_scale == 0.0:
                max_scale = 1.0
            glyph_width = 0.01 * max_scale
        del fieldcache

    return glyph_width
