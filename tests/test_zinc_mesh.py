import math
import unittest

from cmlibs.utils.zinc.field import create_field_finite_element
from cmlibs.utils.zinc.mesh import calculate_jacobian, report_on_lowest_value
from cmlibs.zinc.context import Context
from cmlibs.zinc.result import RESULT_OK

from utilities import get_test_resource_name


class ZincMeshTestCase(unittest.TestCase):

    def test_mesh_jacobian(self):
        exf_file = get_test_resource_name('warped_two_element_cube.exf')

        context = Context("test")
        source_region = context.createRegion()
        result = source_region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = source_region.getFieldmodule()
        coordinates = fm.findFieldByName("coordinates")
        jacobian = calculate_jacobian(coordinates)
        self.assertTrue(jacobian.isValid())

    def test_mesh_jacobian_report(self):
        exf_file = get_test_resource_name('two_element_cube.exf')

        context = Context("test")
        source_region = context.createRegion()
        result = source_region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = source_region.getFieldmodule()
        coordinates = fm.findFieldByName("coordinates")
        jacobian = calculate_jacobian(coordinates)
        self.assertTrue(jacobian.isValid())

        report = report_on_lowest_value(jacobian)
        self.assertEqual(1, report[0])
        self.assertLess(0.0, report[1])

    def test_empty_mesh_jacobian_report(self):

        context = Context("test")
        source_region = context.createRegion()

        fm = source_region.getFieldmodule()
        coordinates = create_field_finite_element(fm, "coordinates", 3, type_coordinate=True)
        jacobian = calculate_jacobian(coordinates)
        self.assertTrue(jacobian.isValid())

        report = report_on_lowest_value(jacobian)
        self.assertEqual(-1, report[0])
        self.assertEqual(math.inf, report[1])

    def test_mesh_negative_jacobian_report(self):
        exf_file = get_test_resource_name('two_element_cube_negative_jacobian.ex3')

        context = Context("test")
        source_region = context.createRegion()
        result = source_region.readFile(exf_file)
        # source_region.writeFile(get_test_resource_name('two_element_cube_negative_jacobian.ex3'))
        self.assertTrue(result == RESULT_OK)

        fm = source_region.getFieldmodule()
        coordinates = fm.findFieldByName("coordinates")
        jacobian = calculate_jacobian(coordinates)
        self.assertTrue(jacobian.isValid())

        report = report_on_lowest_value(jacobian)
        self.assertEqual(1, report[0])
        self.assertGreater(0.0, report[1])

        group1 = fm.findFieldByName("group1")
        report = report_on_lowest_value(jacobian, group1)
        self.assertEqual(1, report[0])
        self.assertGreater(0.0, report[1])


if __name__ == "__main__":
    unittest.main()
