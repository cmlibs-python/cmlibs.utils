import unittest
from cmlibs.utils.zinc.field import createFieldMeshIntegral, findOrCreateFieldCoordinates, \
    findOrCreateFieldGroup
from cmlibs.utils.zinc.finiteelement import createCubeElement, createSquareElement, createNodes, \
    createTriangleElements, evaluateFieldNodesetMean
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK
from utilities import assert_almost_equal_list


class ZincUtilsTestCase(unittest.TestCase):

    def test_field_coordinates(self):
        """
        Test creation of finite element coordinates field.
        """
        context = Context("test")
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
        context = Context("test")
        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        group_name = "bob"
        group = findOrCreateFieldGroup(fieldmodule, group_name)
        self.assertTrue(group.isValid())
        self.assertTrue(group.isManaged())
        self.assertEqual(group.getName(), group_name)

    def test_create_nodes_and_elements(self):
        """
        Test zinc finite element utilities.
        """
        context = Context("test")
        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = findOrCreateFieldCoordinates(fieldmodule)

        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mesh1d = fieldmodule.findMeshByDimension(1)
        mesh2d = fieldmodule.findMeshByDimension(2)
        node_coordinates4 = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3]]
        createNodes(coordinates, node_coordinates4, node_set=nodes)
        self.assertEqual(4, nodes.getSize())
        mean_coordinates = evaluateFieldNodesetMean(coordinates, nodes)
        assert_almost_equal_list(self, [0.6, 0.7, 0.35], mean_coordinates, delta=1.0E-7)

        createTriangleElements(mesh2d, coordinates, [[1, 2, 3], [3, 2, 4]])
        self.assertEqual(2, mesh2d.getSize())
        self.assertEqual(5, mesh1d.getSize())
        surface_area_field = createFieldMeshIntegral(coordinates, mesh2d, number_of_points=1)
        fieldcache = fieldmodule.createFieldcache()
        result, surface_area = surface_area_field.evaluateReal(fieldcache, 1)
        self.assertEqual(RESULT_OK, result)
        self.assertAlmostEqual(1.0099504938362078, surface_area, delta=1.0E-7)

        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = findOrCreateFieldCoordinates(fieldmodule)
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mesh1d = fieldmodule.findMeshByDimension(1)
        mesh2d = fieldmodule.findMeshByDimension(2)
        node_coordinates4 = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3]]
        createSquareElement(mesh2d, coordinates, node_coordinates4)
        self.assertEqual(4, nodes.getSize())
        mean_coordinates = evaluateFieldNodesetMean(coordinates, nodes)
        assert_almost_equal_list(self, [0.6, 0.7, 0.35], mean_coordinates, delta=1.0E-7)
        self.assertEqual(1, mesh2d.getSize())
        self.assertEqual(4, mesh1d.getSize())
        surface_area_field = createFieldMeshIntegral(coordinates, mesh2d, number_of_points=4)
        fieldcache = fieldmodule.createFieldcache()
        result, surface_area = surface_area_field.evaluateReal(fieldcache, 1)
        self.assertEqual(RESULT_OK, result)
        self.assertAlmostEqual(1.0033255980907878, surface_area, delta=1.0E-7)

        region = context.createRegion()
        fieldmodule = region.getFieldmodule()
        coordinates = findOrCreateFieldCoordinates(fieldmodule)
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mesh1d = fieldmodule.findMeshByDimension(1)
        mesh2d = fieldmodule.findMeshByDimension(2)
        mesh3d = fieldmodule.findMeshByDimension(3)
        node_coordinates8 = [[0.1, 0.2, 0.3], [1.1, 0.2, 0.4], [0.1, 1.2, 0.4], [1.1, 1.2, 0.3],
                             [0.1, 0.2, 1.3], [1.1, 0.2, 1.2], [0.1, 1.2, 1.2], [1.1, 1.2, 1.3]]
        createCubeElement(mesh3d, coordinates, node_coordinates8)
        self.assertEqual(8, nodes.getSize())
        mean_coordinates = evaluateFieldNodesetMean(coordinates, nodes)
        assert_almost_equal_list(self, [0.6, 0.7, 0.8], mean_coordinates, delta=1.0E-7)
        self.assertEqual(1, mesh3d.getSize())
        self.assertEqual(6, mesh2d.getSize())
        self.assertEqual(12, mesh1d.getSize())
        volume_field = createFieldMeshIntegral(coordinates, mesh3d, number_of_points=1)
        fieldcache = fieldmodule.createFieldcache()
        result, volume = volume_field.evaluateReal(fieldcache, 1)
        self.assertEqual(RESULT_OK, result)
        self.assertAlmostEqual(0.9, volume, delta=1.0E-7)


if __name__ == "__main__":
    unittest.main()
