from cmlibs.zinc.field import FieldGroup

from cmlibs.utils.zinc.general import ChangeManager


def _get_element_identifiers(mesh):
    element_iterator = mesh.createElementiterator()
    element = element_iterator.next()
    element_identifiers = []
    while element.isValid():
        element_identifiers.append(element.getIdentifier())
        element = element_iterator.next()

    return element_identifiers


def _calculate_connected_elements(mesh, seed_element_identifier, shared_dimension):
    field_module = mesh.getFieldmodule()
    element = mesh.findElementByIdentifier(seed_element_identifier)

    with ChangeManager(field_module):
        field_group = field_module.createFieldGroup()
        field_group.setName('the_group')
        field_group.setSubelementHandlingMode(FieldGroup.SUBELEMENT_HANDLING_MODE_FULL)
        mesh_group = field_group.createMeshGroup(mesh)

        old_size = mesh_group.getSize()
        mesh_group.addElement(element)
        new_size = mesh_group.getSize()

        while new_size > old_size:
            old_size = new_size
            mesh_group.addAdjacentElements(shared_dimension)
            new_size = mesh_group.getSize()

        element_identifiers = _get_element_identifiers(mesh_group)

        del mesh_group
        del field_group

    return element_identifiers


def _transform_mesh_to_list_form(mesh, mesh_field):
    """
    Transform a mesh to a list of element identifiers and a list of node identifiers.

    :param mesh: The mesh to transform.
    :param mesh_field: A field defined over the elements in the mesh.
    :return: A list of element identifiers, a list of lists of node identifiers.
    """
    element_iterator = mesh.createElementiterator()
    element = element_iterator.next()
    element_nodes = []
    element_identifiers = []
    while element.isValid():
        eft = element.getElementfieldtemplate(mesh_field, -1)
        local_node_count = eft.getNumberOfLocalNodes()
        node_identifiers = []
        for index in range(local_node_count):
            node = element.getNode(eft, index + 1)
            node_identifiers.append(node.getIdentifier())

        element_identifiers.append(element.getIdentifier())
        element_nodes.append(node_identifiers)

        element = element_iterator.next()

    return element_identifiers, element_nodes


def _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh):
    repeats = _find_duplicates(element_nodes)
    for repeat in repeats:
        repeated_element = mesh.findElementByIdentifier(element_identifiers[repeat])
        mesh.destroyElement(repeated_element)
        del element_identifiers[repeat]
        del element_nodes[repeat]


def find_connected_mesh_elements_0d(mesh_field, mesh_dimension=3, remove_repeated=False):
    """
    Find the sets of connected elements from the mesh defined over the mesh_field.
    Each list of element identifiers returned is a connected set of elements.

    :param mesh_field: A field defined over the mesh.
    :param mesh_dimension: The dimension of the mesh to work with, default 3.
    :param remove_repeated: Find and remove elements that use the same nodes, default False.
    :return: A list of lists of element identifiers.
    """
    field_module = mesh_field.getFieldmodule()

    mesh = field_module.findMeshByDimension(mesh_dimension)
    element_identifiers, element_nodes = _transform_mesh_to_list_form(mesh, mesh_field)
    if remove_repeated:
        _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh)

    connected_sets = _find_connected(element_nodes)
    if connected_sets is None:
        return

    el_ids = []
    for connected_set in connected_sets:
        el_ids.append([element_identifiers[index] for index in connected_set])

    return el_ids


def find_connected_mesh_elements_1d(mesh_field, mesh_dimension=3, remove_repeated=False, shared_dimension=2):
    """
    Find the sets of connected elements from the mesh defined over the mesh_field.
    Only considers connected elements to the 1D level.

    :param mesh_field: A field defined over the mesh.
    :param mesh_dimension: The dimension of the mesh to work with, default 3.
    :param remove_repeated: Find and remove elements that use the same nodes, default False.
    :param shared_dimension: The dimension to match adjacent elements to, default 2.
    :return: A list of lists of element identifiers.
    """
    field_module = mesh_field.getFieldmodule()

    mesh = field_module.findMeshByDimension(mesh_dimension)
    element_identifiers, element_nodes = _transform_mesh_to_list_form(mesh, mesh_field)
    if remove_repeated:
        _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh)
    field_module.defineAllFaces()
    remainder_element_identifiers = element_identifiers[:]

    connected_sets = []
    while len(remainder_element_identifiers):
        connected_element_identifiers = _calculate_connected_elements(mesh, remainder_element_identifiers.pop(0), shared_dimension)
        connected_sets.append(connected_element_identifiers)
        remainder_element_identifiers = list(set(remainder_element_identifiers) - set(connected_element_identifiers))

    # _print_node_sets(mesh_field, connected_sets)
    return connected_sets


def _print_node_sets(mesh_field, sets):
    field_module = mesh_field.getFieldmodule()

    print("=======")
    mesh = field_module.findMeshByDimension(2)
    element_identifiers, element_nodes = _transform_mesh_to_list_form(mesh, mesh_field)
    for s in sets:
        node_ids = set()
        for el_id in s:
            index = element_identifiers.index(el_id)
            nodes = element_nodes[index]
            for n in nodes:
                node_ids.add(n)

        print(sorted(node_ids))


def _find_connected(element_nodes, seed_index=None):
    seeded = True
    if seed_index is None:
        seeded = False
        seed_index = 0

    connected_elements = [[seed_index]]
    connected_nodes = [set(element_nodes[seed_index])]
    for element_index, element in enumerate(element_nodes):
        if element_index == seed_index:
            continue

        working_index = len(connected_nodes)
        working_set = set(element_nodes[element_index])
        connected_elements.append([element_index])
        connected_nodes.append(working_set)

        connection_indices = []
        for target_index in range(working_index - 1, -1, -1):
            target_set = connected_nodes[target_index]
            if working_set & target_set:
                connection_indices.append(target_index)

        for connection_index in connection_indices:
            connected_elements[connection_index].extend(connected_elements[working_index])
            connected_nodes[connection_index].update(connected_nodes[working_index])
            del connected_elements[working_index]
            del connected_nodes[working_index]
            working_index = connection_index

    return connected_elements[0] if seeded else connected_elements


def _find_duplicates(element_nodes):
    """
    Given a list of integers, returns a list of all duplicate elements (with multiple duplicities).
    """
    num_count = {}
    duplicates = []

    for index, nodes in enumerate(element_nodes):
        sorted_nodes = tuple(sorted(nodes))
        if sorted_nodes in num_count:
            num_count[sorted_nodes].append(index)
        else:
            num_count[sorted_nodes] = [index]

    # Add duplicates to the result list
    for num, count in num_count.items():
        if len(count) > 1:
            duplicates.extend(count[1:])

    return sorted(duplicates, reverse=True)

