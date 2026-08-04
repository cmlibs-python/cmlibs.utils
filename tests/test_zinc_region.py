import random
import unittest

from cmlibs.utils.zinc.field import find_or_create_field_coordinates
from cmlibs.utils.zinc.finiteelement import create_nodes
from cmlibs.utils.zinc.region import convert_nodes_to_datapoints, copy_nodeset
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field


class ZincRegionTestCase(unittest.TestCase):

    def test_transfer_nodes_I(self):
        """
        Test zinc region transferring 4 nodes to 4 datapoints.
        """
        context = Context("test")
        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = find_or_create_field_coordinates(fieldmodule)

        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        datapoints = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

        node_coordinates = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3]]
        create_nodes(coordinates, node_coordinates, node_set=nodes)
        self.assertEqual(4, nodes.getSize())
        self.assertEqual(0, datapoints.getSize())

        convert_nodes_to_datapoints(region, region)

        self.assertEqual(4, datapoints.getSize())
        self.assertEqual(0, nodes.getSize())

    def test_transfer_nodes_II(self):
        """
        Test transferring nodes to datapoints when a large set of datapoints already exists.
        """
        context = Context("test")
        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = find_or_create_field_coordinates(fieldmodule)

        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        datapoints = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

        size = int(1e5)
        node_coordinates = [[random.gauss(0.0, 100.0), random.gauss(0.0, 100.0), random.gauss(0.0, 100.0)] for _ in range(size)]
        datapoint_coordinates = [[random.gauss(0.0, 100.0), random.gauss(0.0, 100.0), random.gauss(0.0, 100.0)] for _ in range(size)]

        create_nodes(coordinates, node_coordinates, node_set=nodes)
        create_nodes(coordinates, datapoint_coordinates, node_set=datapoints)

        self.assertEqual(size, nodes.getSize())
        self.assertEqual(size, datapoints.getSize())

        convert_nodes_to_datapoints(region, region)

        self.assertEqual(2*size, datapoints.getSize())
        self.assertEqual(0, nodes.getSize())

    def test_transfer_nodes_III(self):
        """
        Test transferring nodes to datapoints when a large set of datapoints
        already exists but there are gaps in the nodes identifiers.
        """
        context = Context("test")
        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = find_or_create_field_coordinates(fieldmodule)

        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        datapoints = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

        size = int(1e5)
        node_coordinates = [[random.gauss(0.0, 100.0), random.gauss(0.0, 100.0), random.gauss(0.0, 100.0)] for _ in range(size)]
        reidentify_nodes = {13: size + 144, 14: size + 2333, 15: size + 4311}
        datapoint_coordinates = [[random.gauss(0.0, 100.0), random.gauss(0.0, 100.0), random.gauss(0.0, 100.0)] for _ in range(size)]

        create_nodes(coordinates, node_coordinates, node_set=nodes)
        create_nodes(coordinates, datapoint_coordinates, node_set=datapoints)
        for node_identifier in reidentify_nodes:
            node = nodes.findNodeByIdentifier(node_identifier)
            node.setIdentifier(reidentify_nodes[node_identifier])

        self.assertEqual(size, nodes.getSize())
        self.assertEqual(size, datapoints.getSize())

        convert_nodes_to_datapoints(region, region)

        self.assertEqual(2*size, datapoints.getSize())
        self.assertEqual(0, nodes.getSize())

    def test_copy_dataset_I(self):
        """
        Test zinc region copying 4 nodes to 4 nodes.
        """
        context = Context("test")
        region = context.createRegion()
        target_region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        target_fieldmodule = target_region.getFieldmodule()
        coordinates = find_or_create_field_coordinates(fieldmodule)

        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        target_nodes = target_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)

        node_coordinates = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3]]
        create_nodes(coordinates, node_coordinates, node_set=nodes)
        self.assertEqual(4, nodes.getSize())
        self.assertEqual(0, target_nodes.getSize())

        copy_nodeset(target_region, nodes)

        self.assertEqual(4, nodes.getSize())
        self.assertEqual(4, target_nodes.getSize())

    def test_copy_dataset_II(self):
        """
        Test zinc region copying 4 datapoints to 4 datapoints.
        """
        context = Context("test")
        region = context.createRegion()
        target_region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        target_fieldmodule = target_region.getFieldmodule()
        coordinates = find_or_create_field_coordinates(fieldmodule)

        datapoints = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        target_datapoints = target_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

        node_coordinates = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3]]
        create_nodes(coordinates, node_coordinates, node_set=datapoints)
        self.assertEqual(4, datapoints.getSize())
        self.assertEqual(0, target_datapoints.getSize())

        copy_nodeset(target_region, datapoints)

        self.assertEqual(4, datapoints.getSize())
        self.assertEqual(4, target_datapoints.getSize())

    def test_transfer_nodes_IV(self):
        """
        Test zinc region transferring nodes over datapoints.
        """
        context = Context("test")
        source_region = context.createRegion()
        target_region = context.createRegion()
        source_fieldmodule = source_region.getFieldmodule()
        target_fieldmodule = target_region.getFieldmodule()
        source_coordinates = find_or_create_field_coordinates(source_fieldmodule)
        target_coordinates = find_or_create_field_coordinates(target_fieldmodule)

        nodes = source_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        target_datapoints = target_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

        node_coordinates = [[1.0] * 3, [2.0] * 3, [3.0] * 3]
        datapoint_coordinates = [[-1.0] * 3, [-2.0] * 3, [-3.0] * 3]
        reidentify_nodes = {3: 4}

        create_nodes(source_coordinates, node_coordinates, node_set=nodes)
        create_nodes(target_coordinates, datapoint_coordinates, node_set=target_datapoints)

        for node_identifier in reidentify_nodes:
            node = nodes.findNodeByIdentifier(node_identifier)
            node.setIdentifier(reidentify_nodes[node_identifier])

        nodeset_group = source_fieldmodule.createFieldGroup()
        nodeset_group.setName('nodes_group')
        nodeset = nodeset_group.getOrCreateNodesetGroup(nodes)
        nodeset.addNode(nodes.findNodeByIdentifier(2))
        nodeset.addNode(nodes.findNodeByIdentifier(4))

        self.assertEqual(2, nodeset.getSize())

        datapointsset_group = target_fieldmodule.createFieldGroup()
        datapointsset_group.setName('datapoints_group')
        datapointsset = datapointsset_group.getOrCreateNodesetGroup(target_datapoints)
        datapointsset.addNode(target_datapoints.findNodeByIdentifier(2))
        datapointsset.addNode(target_datapoints.findNodeByIdentifier(3))

        self.assertEqual(2, datapointsset.getSize())

        self.assertEqual(3, nodes.getSize())
        self.assertEqual(3, target_datapoints.getSize())

        convert_nodes_to_datapoints(target_region, source_region)

        self.assertEqual(0, nodes.getSize())
        self.assertEqual(6, target_datapoints.getSize())

        ni = target_datapoints.createNodeiterator()
        datapoint = ni.next()
        fc = target_fieldmodule.createFieldcache()
        while datapoint.isValid():
            current_identifier = datapoint.getIdentifier()
            fc.setNode(datapoint)
            _, values = target_coordinates.evaluateReal(fc, 3)
            if current_identifier == 1:
                self.assertEqual(1, values[0])
            elif current_identifier == 2:
                self.assertEqual(2, values[0])
            elif current_identifier == 3:
                self.assertEqual(-3, values[0])
            elif current_identifier == 4:
                self.assertEqual(3, values[0])
            elif current_identifier == 5:
                self.assertEqual(-1, values[0])
            elif current_identifier == 6:
                self.assertEqual(-2, values[0])
            datapoint = ni.next()

        ni = datapointsset.createNodeiterator()
        datapoint = ni.next()
        while datapoint.isValid():
            identifier = datapoint.getIdentifier()
            self.assertIn(identifier, [3, 6])
            datapoint = ni.next()

        nodeset_group = target_fieldmodule.findFieldByName("nodes_group").castGroup()
        nodeset = nodeset_group.getNodesetGroup(target_datapoints)
        ni = nodeset.createNodeiterator()
        datapoint = ni.next()
        while datapoint.isValid():
            identifier = datapoint.getIdentifier()
            self.assertIn(identifier, [2, 4])
            datapoint = ni.next()

    def test_transfer_nodes_V(self):
        """
        Test zinc region transferring nodes over datapoints.
        """
        context = Context("test")
        source_region = context.createRegion()
        target_region = context.createRegion()
        source_fieldmodule = source_region.getFieldmodule()
        target_fieldmodule = target_region.getFieldmodule()
        source_coordinates = find_or_create_field_coordinates(source_fieldmodule)
        target_coordinates = find_or_create_field_coordinates(target_fieldmodule)

        nodes = source_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        target_datapoints = target_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

        node_coordinates = [[1.0] * 3, [2.0] * 3, [3.0] * 3, [4.0] * 3, [5.0] * 3]
        datapoint_coordinates = [[-1.0] * 3, [-2.0] * 3, [-3.0] * 3, [-4.0] * 3, [-5.0] * 3, [-6.0] * 3, [-7.0] * 3]

        create_nodes(source_coordinates, node_coordinates, node_set=nodes)
        create_nodes(target_coordinates, datapoint_coordinates, node_set=target_datapoints)

        reidentify_nodes = {1: 6, 2: 7, 4: 8}
        for node_identifier in reidentify_nodes:
            node = nodes.findNodeByIdentifier(node_identifier)
            node.setIdentifier(reidentify_nodes[node_identifier])

        reidentify_nodes = {1: 8, 2: 9, 4: 10}
        for node_identifier in reidentify_nodes:
            node = target_datapoints.findNodeByIdentifier(node_identifier)
            node.setIdentifier(reidentify_nodes[node_identifier])

        self.assertEqual(5, nodes.getSize())
        self.assertEqual(7, target_datapoints.getSize())

        convert_nodes_to_datapoints(target_region, source_region)

        self.assertEqual(0, nodes.getSize())
        self.assertEqual(12, target_datapoints.getSize())

        expected_values = {
            1: [-3.0, -3.0, -3.0],
            2: [-5.0, -5.0, -5.0],
            3: [3.0, 3.0, 3.0],
            4: [-6.0, -6.0, -6.0],
            5: [5.0, 5.0, 5.0],
            6: [1.0, 1.0, 1.0],
            7: [2.0, 2.0, 2.0],
            8: [4.0, 4.0, 4.0],
            9: [-2.0, -2.0, -2.0],
            10: [-4.0, -4.0, -4.0],
            11: [-7.0, -7.0, -7.0],
            12: [-1.0, -1.0, -1.0],
        }
        ni = target_datapoints.createNodeiterator()
        fc = target_fieldmodule.createFieldcache()
        datapoint = ni.next()
        while datapoint.isValid():
            fc.setNode(datapoint)
            identifier = datapoint.getIdentifier()
            _, value = target_coordinates.evaluateReal(fc, 3)
            self.assertEqual(expected_values[identifier], value)
            datapoint = ni.next()

    def test_transfer_nodes_VI(self):
        """
        Test zinc region transferring nodes over datapoints filtering fields.
        """
        context = Context("test")
        source_region = context.createRegion()
        target_region = context.createRegion()
        source_fieldmodule = source_region.getFieldmodule()
        target_fieldmodule = target_region.getFieldmodule()
        source_coordinates = find_or_create_field_coordinates(source_fieldmodule)
        alt_coordinates = find_or_create_field_coordinates(source_fieldmodule, name='alt_coordinates')

        source_datapoints = source_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        source_nodes = source_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)

        node_coordinates = [[1.0] * 3, [2.0] * 3, [3.0] * 3, [4.0] * 3, [5.0] * 3]
        datapoint_coordinates = [[-1.0] * 3, [-2.0] * 3, [-3.0] * 3, [-4.0] * 3, [-5.0] * 3, [-6.0] * 3, [-7.0] * 3]

        group_1 = source_fieldmodule.createFieldGroup()
        group_2 = source_fieldmodule.createFieldGroup()
        group_3 = source_fieldmodule.createFieldGroup()

        group_1.setName("group_1")
        group_2.setName("group_2")
        group_3.setName("group_3")

        create_nodes(source_coordinates, datapoint_coordinates, node_set=source_datapoints)
        create_nodes(alt_coordinates, node_coordinates, node_set=source_nodes)

        dataset_group = group_1.getOrCreateNodesetGroup(source_datapoints)
        dataset_group.addNode(source_datapoints.findNodeByIdentifier(1))
        dataset_group.addNode(source_datapoints.findNodeByIdentifier(2))

        dataset_group = group_2.getOrCreateNodesetGroup(source_datapoints)
        dataset_group.addNode(source_datapoints.findNodeByIdentifier(5))
        dataset_group.addNode(source_datapoints.findNodeByIdentifier(6))

        dataset_group = group_3.getOrCreateNodesetGroup(source_nodes)
        dataset_group.addNode(source_datapoints.findNodeByIdentifier(2))
        dataset_group.addNode(source_datapoints.findNodeByIdentifier(3))

        fi = target_fieldmodule.createFielditerator()
        field = fi.next()
        field_count = 0
        while field.isValid():
            field_count += 1
            field = fi.next()

        self.assertEqual(0, field_count)

        fi = source_fieldmodule.createFielditerator()
        field = fi.next()
        src_field_count = 0
        while field.isValid():
            src_field_count += 1
            field = fi.next()

        self.assertEqual(6, src_field_count)

        convert_nodes_to_datapoints(target_region, source_region, source_nodeset_type=Field.DOMAIN_TYPE_DATAPOINTS, field_names=['group_1', 'coordinates'])

        fi = target_fieldmodule.createFielditerator()
        field = fi.next()
        field_count = 0
        while field.isValid():
            field_count += 1
            field = fi.next()

        # Group fields do not get dropped by the stream information region field restriction.
        # This means we only lose the 'alt_coordinates' field from the source region.
        self.assertEqual(5, field_count)



if __name__ == "__main__":
    unittest.main()
