import math
import unittest

from cmlibs.utils.zinc.field import find_or_create_field_coordinates
from cmlibs.utils.zinc.finiteelement import (
    create_element_from_node_identifiers, create_hermite_curve_elements, create_node_points, define_grid_field_on_mesh,
    get_mesh_element_node_identifiers_maps)
from cmlibs.utils.zinc.general import ChangeManager

from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.node import Node
from cmlibs.zinc.result import RESULT_OK

try:
    from utilities import assert_almost_equal_list, get_test_resource_name
except ImportError:
    from .utilities import assert_almost_equal_list, get_test_resource_name


class ZincFiniteElementTestCase(unittest.TestCase):

    def test_mesh1d_grid_vector(self):
        exf_file = get_test_resource_name('two_lines.exf')

        context = Context("test")
        region = context.createRegion()
        result = region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = region.getFieldmodule()
        mesh = fm.findMeshByDimension(1)

        define_grid_field_on_mesh(mesh, "grid_coordinates", [4], 3, value_type=float)

        coordinates = fm.findFieldByName("coordinates")
        grid_coordinates = fm.findFieldByName("grid_coordinates")
        self.assertTrue(grid_coordinates.isValid())
        self.assertEqual(grid_coordinates.getNumberOfComponents(), 3)

        # Fieldassignment doesn't work for grid, so assign to all points
        # fieldassignment = grid_coordinates.createFieldassignment(coordinates)
        # result = fieldassignment.assign()
        # self.assertTrue(result == RESULT_OK)
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi1 in (0.0, 0.25, 0.5, 0.75, 1.0):
                element = mesh.findElementByIdentifier(element_identifier)
                fieldcache.setMeshLocation(element, xi1)
                result, x = coordinates.evaluateReal(fieldcache, 3)
                self.assertTrue(result == RESULT_OK)
                result = grid_coordinates.assignReal(fieldcache, x)
                self.assertTrue(result == RESULT_OK)
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi1 in (0.0, 0.25, 0.5, 0.75, 1.0):
                element = mesh.findElementByIdentifier(element_identifier)
                fieldcache.setMeshLocation(element, xi1)
                result, x = coordinates.evaluateReal(fieldcache, 3)
                self.assertTrue(result == RESULT_OK)
                result, grid_x = grid_coordinates.evaluateReal(fieldcache, 3)
                self.assertTrue(result == RESULT_OK)
                assert_almost_equal_list(self, x, grid_x, delta=1.0E-8)

    def test_mesh2d_grid_scalar(self):
        exf_file = get_test_resource_name('square.exf')

        context = Context("test")
        region = context.createRegion()
        result = region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = region.getFieldmodule()
        mesh = fm.findMeshByDimension(2)

        define_grid_field_on_mesh(mesh, "grid_mag", [2, 4], 1, value_type=float)

        coordinates = fm.findFieldByName("coordinates")
        mag_coordinates = fm.createFieldMagnitude(coordinates)
        grid_mag = fm.findFieldByName("grid_mag")
        self.assertTrue(grid_mag.isValid())
        self.assertEqual(grid_mag.getNumberOfComponents(), 1)

        # Fieldassignment doesn't work for grid, so assign to all points
        # fieldassignment = grid_mag.createFieldassignment(mag_coordinates)
        # result = fieldassignment.assign()
        # self.assertTrue(result == RESULT_OK)
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi2 in (0.0, 0.25, 0.5, 0.75, 1.0):
                for xi1 in (0.0, 0.5, 1.0):
                    element = mesh.findElementByIdentifier(element_identifier)
                    fieldcache.setMeshLocation(element, [xi1, xi2])
                    result, mag_x = mag_coordinates.evaluateReal(fieldcache, 1)
                    self.assertTrue(result == RESULT_OK)
                    result = grid_mag.assignReal(fieldcache, mag_x)
                    self.assertTrue(result == RESULT_OK)
        # new field cache so not recalling from cache
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi2 in (0.0, 0.25, 0.5, 0.75, 1.0):
                for xi1 in (0.0, 0.5, 1.0):
                    element = mesh.findElementByIdentifier(element_identifier)
                    fieldcache.setMeshLocation(element, [xi1, xi2])
                    result, mag_x = mag_coordinates.evaluateReal(fieldcache, 1)
                    self.assertTrue(result == RESULT_OK)
                    result, grid_mag_x = grid_mag.evaluateReal(fieldcache, 1)
                    self.assertTrue(result == RESULT_OK)
                    self.assertAlmostEqual(mag_x, grid_mag_x, delta=1.0E-8)

    def test_mesh3d_grid_scalar(self):
        exf_file = get_test_resource_name('warped_two_element_cube.exf')

        context = Context("test")
        region = context.createRegion()
        result = region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = region.getFieldmodule()
        mesh = fm.findMeshByDimension(3)

        define_grid_field_on_mesh(mesh, "grid_mag", [2, 3, 4], 1, value_type=float)

        coordinates = fm.findFieldByName("coordinates")
        mag_coordinates = fm.createFieldMagnitude(coordinates)
        grid_mag = fm.findFieldByName("grid_mag")
        self.assertTrue(grid_mag.isValid())
        self.assertEqual(grid_mag.getNumberOfComponents(), 1)

        # Fieldassignment doesn't work for grid, so assign to all points
        # fieldassignment = grid_mag.createFieldassignment(mag_coordinates)
        # result = fieldassignment.assign()
        # self.assertTrue(result == RESULT_OK)
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi3 in (0.0, 0.25, 0.5, 0.75, 1.0):
                for xi2 in (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0):
                    for xi1 in (0.0, 0.5, 1.0):
                        element = mesh.findElementByIdentifier(element_identifier)
                        fieldcache.setMeshLocation(element, [xi1, xi2, xi3])
                        result, mag_x = mag_coordinates.evaluateReal(fieldcache, 1)
                        self.assertTrue(result == RESULT_OK)
                        result = grid_mag.assignReal(fieldcache, mag_x)
                        self.assertTrue(result == RESULT_OK)
        # new field cache so not recalling from cache
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi3 in (0.0, 0.25, 0.5, 0.75, 1.0):
                for xi2 in (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0):
                    for xi1 in (0.0, 0.5, 1.0):
                        element = mesh.findElementByIdentifier(element_identifier)
                        fieldcache.setMeshLocation(element, [xi1, xi2, xi3])
                        result, mag_x = mag_coordinates.evaluateReal(fieldcache, 1)
                        self.assertTrue(result == RESULT_OK)
                        result, grid_mag_x = grid_mag.evaluateReal(fieldcache, 1)
                        self.assertTrue(result == RESULT_OK)
                        self.assertAlmostEqual(mag_x, grid_mag_x, delta=1.0E-8)

    def test_mesh3d_grid_scalar_int(self):
        exf_file = get_test_resource_name('warped_two_element_cube.exf')

        context = Context("test")
        region = context.createRegion()
        result = region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = region.getFieldmodule()
        mesh = fm.findMeshByDimension(3)

        define_grid_field_on_mesh(mesh, "grid_mag", [2, 3, 4], 1, value_type=int)

        coordinates = fm.findFieldByName("coordinates")
        mag_coordinates = fm.createFieldMagnitude(coordinates)
        grid_mag = fm.findFieldByName("grid_mag")
        self.assertTrue(grid_mag.isValid())
        self.assertEqual(grid_mag.getNumberOfComponents(), 1)

        # Fieldassignment doesn't work for grid, so assign to all points
        # fieldassignment = grid_mag.createFieldassignment(mag_coordinates)
        # result = fieldassignment.assign()
        # self.assertTrue(result == RESULT_OK)
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi3 in (0.0, 0.25, 0.5, 0.75, 1.0):
                for xi2 in (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0):
                    for xi1 in (0.0, 0.5, 1.0):
                        element = mesh.findElementByIdentifier(element_identifier)
                        fieldcache.setMeshLocation(element, [xi1, xi2, xi3])
                        result, mag_x = mag_coordinates.evaluateReal(fieldcache, 1)
                        self.assertTrue(result == RESULT_OK)
                        int_mag_x = round(mag_x * 1000.0)
                        result = grid_mag.assignReal(fieldcache, int_mag_x)
                        self.assertTrue(result == RESULT_OK)
        # new field cache so not recalling from cache
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi3 in (0.0, 0.25, 0.5, 0.75, 1.0):
                for xi2 in (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0):
                    for xi1 in (0.0, 0.5, 1.0):
                        element = mesh.findElementByIdentifier(element_identifier)
                        fieldcache.setMeshLocation(element, [xi1, xi2, xi3])
                        result, mag_x = mag_coordinates.evaluateReal(fieldcache, 1)
                        self.assertTrue(result == RESULT_OK)
                        int_mag_x = round(mag_x * 1000.0)
                        result, grid_mag_x = grid_mag.evaluateReal(fieldcache, 1)
                        int_grid_mag_x = int(grid_mag_x)
                        self.assertTrue(result == RESULT_OK)
                        self.assertEqual(int_mag_x, int_grid_mag_x)

    def test_mesh3d_grid_vector(self):
        exf_file = get_test_resource_name('warped_two_element_cube.exf')

        context = Context("test")
        region = context.createRegion()
        result = region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = region.getFieldmodule()
        mesh = fm.findMeshByDimension(3)

        define_grid_field_on_mesh(mesh, "grid_coordinates", [4], 3, value_type=float)

        coordinates = fm.findFieldByName("coordinates")
        grid_coordinates = fm.findFieldByName("grid_coordinates")
        self.assertTrue(grid_coordinates.isValid())
        self.assertEqual(grid_coordinates.getNumberOfComponents(), 3)

        # Fieldassignment doesn't work for grid, so assign to all points
        # fieldassignment = grid_coordinates.createFieldassignment(coordinates)
        # result = fieldassignment.assign()
        # self.assertTrue(result == RESULT_OK)
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi3 in (0.0, 0.25, 0.5, 0.75, 1.0):
                for xi2 in (0.0, 0.25, 0.5, 0.75, 1.0):
                    for xi1 in (0.0, 0.25, 0.5, 0.75, 1.0):
                        element = mesh.findElementByIdentifier(element_identifier)
                        fieldcache.setMeshLocation(element, [xi1, xi2, xi3])
                        result, x = coordinates.evaluateReal(fieldcache, 3)
                        self.assertTrue(result == RESULT_OK)
                        result = grid_coordinates.assignReal(fieldcache, x)
                        self.assertTrue(result == RESULT_OK)
        fieldcache = fm.createFieldcache()
        for element_identifier in (1, 2):
            for xi3 in (0.0, 0.25, 0.5, 0.75, 1.0):
                for xi2 in (0.0, 0.25, 0.5, 0.75, 1.0):
                    for xi1 in (0.0, 0.25, 0.5, 0.75, 1.0):
                        element = mesh.findElementByIdentifier(element_identifier)
                        fieldcache.setMeshLocation(element, [xi1, xi2, xi3])
                        result, x = coordinates.evaluateReal(fieldcache, 3)
                        self.assertTrue(result == RESULT_OK)
                        result, grid_x = grid_coordinates.evaluateReal(fieldcache, 3)
                        self.assertTrue(result == RESULT_OK)
                        assert_almost_equal_list(self, x, grid_x, delta=1.0E-8)

    def test_create_element_from_node_identifiers(self):
        exf_file = get_test_resource_name('warped_two_element_cube.exf')

        context = Context("test")
        region = context.createRegion()
        result = region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = region.getFieldmodule()
        mesh = fm.findMeshByDimension(1)
        coordinates_field = fm.findFieldByName("coordinates")

        element_identifier = create_element_from_node_identifiers(mesh, coordinates_field, [1, 2])
        self.assertEqual(21, element_identifier)

        element_identifier = create_element_from_node_identifiers(mesh, coordinates_field, [134, 516])
        self.assertEqual(22, element_identifier)

    def test_create_hermite_curve(self):
        """
        Test finite element utility to create a hermite curve mesh.
        """
        ax = [
            [20614.63786414724, -2939.873650361369, -605.4150310438267],
            [19866.346579952475, -4452.963739972778, -662.9986048963924],
            [18688.55297975595, -5664.535791350198, -711.1634865902475]]
        ad1 = [
            [-490.70985052735557, -1622.8873929937577, -60.65382802572525],
            [-984.464558558513, -1380.6496536715067, -53.615308968309854],
            [-1342.5638510703225, -1036.3223530813373, -42.38892426110936]]
        context = Context("create hermite curve")
        region = context.getDefaultRegion()
        fieldmodule = region.getFieldmodule()
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        with ChangeManager(fieldmodule):
            group = fieldmodule.createFieldGroup()
            group_name = "vagus_branch"
            group.setName(group_name)
            mesh1d = fieldmodule.findMeshByDimension(1)
            mesh_group = group.getOrCreateMeshGroup(mesh1d)
            next_node_identifier, next_element_identifier = create_hermite_curve_elements(mesh_group, ax, ad1)
            self.assertEqual(next_node_identifier, 4)
            self.assertEqual(next_element_identifier, 3)
            nodeset_group = group.getNodesetGroup(nodes)
            self.assertTrue(nodeset_group.isValid())

        coordinates = fieldmodule.findFieldByName("coordinates").castFiniteElement()
        self.assertTrue(coordinates.isValid())
        self.assertEqual(nodeset_group.getSize(), 3)
        self.assertEqual(mesh_group.getSize(), 2)
        fieldcache = fieldmodule.createFieldcache()
        for n in range(3):
            node = nodes.findNodeByIdentifier(n + 1)
            self.assertTrue(node.isValid())
            fieldcache.setNode(node)
            result, x = coordinates.getNodeParameters(fieldcache, -1, Node.VALUE_LABEL_VALUE, 1, 3)
            self.assertEqual(result, RESULT_OK)
            result, d1 = coordinates.getNodeParameters(fieldcache, -1, Node.VALUE_LABEL_D_DS1, 1, 3)
            self.assertEqual(result, RESULT_OK)
            for c in range(3):
                self.assertAlmostEqual(x[c], ax[n][c], delta=1.0E-8)
                self.assertAlmostEqual(d1[c], ad1[n][c], delta=1.0E-8)

    def test_create_node_points(self):
        """
        Test creating node points with additional fields using utility.
        """
        px = [[0.0, 1.1, 2.2], [1.0, 2.1, 3.2], [2.0, 3.1, 4.2]]
        rv = [1.5, 3.0, 4.5]
        sv = ["bob", "fred", "joe"]
        context = Context("create node points")
        region = context.getDefaultRegion()
        fieldmodule = region.getFieldmodule()
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        with ChangeManager(fieldmodule):
            group = fieldmodule.createFieldGroup()
            group_name = "group"
            group.setName(group_name)
            nodeset_group = group.createNodesetGroup(nodes)
            next_node_identifier = create_node_points(
                nodeset_group, px, field_names_and_values=[("reals", rv), ("strings", sv)])

        coordinates = fieldmodule.findFieldByName("coordinates").castFiniteElement()
        self.assertTrue(coordinates.isValid())
        reals = fieldmodule.findFieldByName("reals").castFiniteElement()
        self.assertTrue(reals.isValid())
        strings = fieldmodule.findFieldByName("strings").castStoredString()
        self.assertTrue(strings.isValid())
        self.assertEqual(nodeset_group.getSize(), 3)
        fieldcache = fieldmodule.createFieldcache()
        for n in range(3):
            node = nodes.findNodeByIdentifier(n + 1)
            self.assertTrue(node.isValid())
            fieldcache.setNode(node)
            result, x = coordinates.getNodeParameters(fieldcache, -1, Node.VALUE_LABEL_VALUE, 1, 3)
            self.assertEqual(result, RESULT_OK)
            result, r = reals.getNodeParameters(fieldcache, -1, Node.VALUE_LABEL_VALUE, 1, 1)
            self.assertEqual(result, RESULT_OK)
            s = strings.evaluateString(fieldcache)
            for c in range(3):
                self.assertAlmostEqual(x[c], px[n][c], delta=1.0E-12)
            self.assertAlmostEqual(r, rv[n], delta=1.0E-12)
            self.assertEqual(s, sv[n])

    def test_get_mesh_element_node_identifiers_map(self):
        exf_file = get_test_resource_name('two_lines.exf')
        context = Context("test")
        region = context.createRegion()
        result = region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)
        fm = region.getFieldmodule()
        mesh = fm.findMeshByDimension(1)
        coordinates_field = fm.findFieldByName("coordinates")
        element_id_to_node_ids, node_id_to_element_ids = get_mesh_element_node_identifiers_maps(mesh, coordinates_field)
        self.assertEqual(element_id_to_node_ids, {1: [1, 2], 2: [2, 3]})
        self.assertEqual(node_id_to_element_ids, {1: [1], 2: [1, 2], 3: [2]})


if __name__ == "__main__":
    unittest.main()
