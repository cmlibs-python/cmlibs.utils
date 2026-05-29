import math
import unittest

from cmlibs.utils.zinc.finiteelement import define_grid_field_on_mesh
from cmlibs.zinc.context import Context
from cmlibs.zinc.result import RESULT_OK
from utilities import assert_almost_equal_list, get_test_resource_name


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


if __name__ == "__main__":
    unittest.main()
