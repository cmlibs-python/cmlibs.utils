import math
import os
import unittest
from opencmiss.utils.zinc.field import createFieldMeshIntegral, findOrCreateFieldCoordinates, \
    findOrCreateFieldGroup, findOrCreateFieldNodeGroup
from opencmiss.utils.zinc.finiteelement import createCubeElement, createSquareElement, createNodes, \
    createTriangleElements, evaluateFieldNodesetMean
from opencmiss.zinc.context import Context
from opencmiss.zinc.field import Field
from opencmiss.zinc.result import RESULT_OK

here = os.path.abspath(os.path.dirname(__file__))


def assertAlmostEqualList(testcase, actualList, expectedList, delta):
    assert len(actualList) == len(expectedList)
    for actual, expected in zip(actualList, expectedList):
        testcase.assertAlmostEqual(actual, expected, delta=delta)


class ZincUtilsTestCase(unittest.TestCase):

    def test_field_coordinates(self):
        """
        Test creation of finite element coordinates field.
        """
        context = Context("test");
        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = findOrCreateFieldCoordinates(fieldmodule)
        self.assertTrue(coordinates.isValid())
        self.assertEqual(3, coordinates.getNumberOfComponents())
        self.assertTrue(coordinates.isManaged())
        self.assertTrue(coordinates.isTypeCoordinate())

    def test_field_group(self):
        """
        Test creation of group fields.
        """
        context = Context("test");
        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        groupName = "bob"
        group = findOrCreateFieldGroup(fieldmodule, groupName)
        self.assertTrue(group.isValid())
        self.assertTrue(group.isManaged())
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        nodeGroup = findOrCreateFieldNodeGroup(group, nodes)
        self.assertTrue(nodeGroup.isValid())
        self.assertFalse(nodeGroup.isManaged())
        nodeGroupName = groupName + "." + nodes.getName()
        self.assertEqual(nodeGroupName, nodeGroup.getName())

    def test_create_nodes_and_elements(self):
        """
        Test zinc finite element utilities.
        """
        context = Context("test");
        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = findOrCreateFieldCoordinates(fieldmodule)

        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mesh1d = fieldmodule.findMeshByDimension(1)
        mesh2d = fieldmodule.findMeshByDimension(2)
        nodeCoordinates4 = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3]]
        createNodes(coordinates, nodeCoordinates4, node_set=nodes)
        self.assertEqual(4, nodes.getSize())
        meanCoordinates = evaluateFieldNodesetMean(coordinates, nodes)
        assertAlmostEqualList(self, [0.6, 0.7, 0.35], meanCoordinates, delta=1.0E-7)

        createTriangleElements(mesh2d, coordinates, [[1, 2, 3], [3, 2, 4]])
        self.assertEqual(2, mesh2d.getSize())
        self.assertEqual(5, mesh1d.getSize())
        surfaceAreaField = createFieldMeshIntegral(coordinates, mesh2d, numberOfPoints=1)
        fieldcache = fieldmodule.createFieldcache()
        result, surfaceArea = surfaceAreaField.evaluateReal(fieldcache, 1)
        self.assertEqual(RESULT_OK, result)
        self.assertAlmostEqual(1.0099504938362078, surfaceArea, delta=1.0E-7)

        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = findOrCreateFieldCoordinates(fieldmodule)
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mesh1d = fieldmodule.findMeshByDimension(1)
        mesh2d = fieldmodule.findMeshByDimension(2)
        nodeCoordinates4 = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3]]
        createSquareElement(mesh2d, coordinates, nodeCoordinates4)
        self.assertEqual(4, nodes.getSize())
        meanCoordinates = evaluateFieldNodesetMean(coordinates, nodes)
        assertAlmostEqualList(self, [0.6, 0.7, 0.35], meanCoordinates, delta=1.0E-7)
        self.assertEqual(1, mesh2d.getSize())
        self.assertEqual(4, mesh1d.getSize())
        surfaceAreaField = createFieldMeshIntegral(coordinates, mesh2d, numberOfPoints=4)
        fieldcache = fieldmodule.createFieldcache()
        result, surfaceArea = surfaceAreaField.evaluateReal(fieldcache, 1)
        self.assertEqual(RESULT_OK, result)
        self.assertAlmostEqual(1.0033255980907878, surfaceArea, delta=1.0E-7)

        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = findOrCreateFieldCoordinates(fieldmodule)
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mesh1d = fieldmodule.findMeshByDimension(1)
        mesh2d = fieldmodule.findMeshByDimension(2)
        mesh3d = fieldmodule.findMeshByDimension(3)
        nodeCoordinates8 = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3],
                            [0.1, 0.2, 1.3], [1.1, 0.2, 1.2], [0.1, 1.2, 1.2], [1.1, 1.2, 1.3]]
        createCubeElement(mesh3d, coordinates, nodeCoordinates8)
        self.assertEqual(8, nodes.getSize())
        meanCoordinates = evaluateFieldNodesetMean(coordinates, nodes)
        assertAlmostEqualList(self, [0.6, 0.7, 0.8], meanCoordinates, delta=1.0E-7)
        self.assertEqual(1, mesh3d.getSize())
        self.assertEqual(6, mesh2d.getSize())
        self.assertEqual(12, mesh1d.getSize())
        volumeField = createFieldMeshIntegral(coordinates, mesh3d, numberOfPoints=1)
        fieldcache = fieldmodule.createFieldcache()
        result, volume = volumeField.evaluateReal(fieldcache, 1)
        self.assertEqual(RESULT_OK, result)
        self.assertAlmostEqual(0.9, volume, delta=1.0E-7)


if __name__ == "__main__":
    unittest.main()
