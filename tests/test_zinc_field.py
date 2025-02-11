import math
import unittest

from cmlibs.utils.zinc.field import create_field_finite_element, create_xi_reference_jacobian_determinant_field
from cmlibs.utils.zinc.finiteelement import get_scalar_field_minimum_in_mesh
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
        jacobian = create_xi_reference_jacobian_determinant_field(coordinates)
        self.assertTrue(jacobian.isValid())

    def test_mesh_jacobian_result(self):
        exf_file = get_test_resource_name('two_element_cube.exf')

        context = Context("test")
        source_region = context.createRegion()
        result = source_region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        fm = source_region.getFieldmodule()
        coordinates = fm.findFieldByName("coordinates")
        jacobian = create_xi_reference_jacobian_determinant_field(coordinates)
        self.assertTrue(jacobian.isValid())

        result = get_scalar_field_minimum_in_mesh(jacobian)
        self.assertEqual(1, result[0])
        self.assertLess(0.0, result[1])

    def test_empty_mesh_jacobian_result(self):

        context = Context("test")
        source_region = context.createRegion()

        fm = source_region.getFieldmodule()
        coordinates = create_field_finite_element(fm, "coordinates", 3, type_coordinate=True)
        jacobian = create_xi_reference_jacobian_determinant_field(coordinates)
        self.assertTrue(jacobian is None)

        result = get_scalar_field_minimum_in_mesh(jacobian)
        self.assertEqual(-1, result[0])
        self.assertEqual(math.inf, result[1])

    def test_zero_size_mesh_jacobian_result(self):

        context = Context("test")
        source_region = context.createRegion()

        fm = source_region.getFieldmodule()
        coordinates = create_field_finite_element(fm, "coordinates", 3, type_coordinate=True)
        xi = create_field_finite_element(fm, "xi", 3)
        jacobian = create_xi_reference_jacobian_determinant_field(coordinates)
        self.assertTrue(jacobian.isValid())

        result = get_scalar_field_minimum_in_mesh(jacobian)
        self.assertEqual(-1, result[0])
        self.assertEqual(math.inf, result[1])

    def test_mesh_negative_jacobian_result(self):
        exf_file = get_test_resource_name('two_element_cube_negative_jacobian.ex3')

        context = Context("test")
        source_region = context.createRegion()
        result = source_region.readFile(exf_file)
        # source_region.writeFile(get_test_resource_name('two_element_cube_negative_jacobian.ex3'))
        self.assertTrue(result == RESULT_OK)

        fm = source_region.getFieldmodule()
        coordinates = fm.findFieldByName("coordinates")
        jacobian = create_xi_reference_jacobian_determinant_field(coordinates)
        self.assertTrue(jacobian.isValid())

        result = get_scalar_field_minimum_in_mesh(jacobian)
        self.assertEqual(1, result[0])
        self.assertGreater(0.0, result[1])

        group1 = fm.findFieldByName("group1")
        mesh = fm.findMeshByDimension(3)
        mesh_group = group1.castGroup().getMeshGroup(mesh)
        result = get_scalar_field_minimum_in_mesh(jacobian, mesh_group)
        self.assertEqual(1, result[0])
        self.assertGreater(0.0, result[1])


if __name__ == "__main__":
    unittest.main()
