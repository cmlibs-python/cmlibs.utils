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


if __name__ == "__main__":
    unittest.main()
