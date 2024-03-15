import os
import unittest

from cmlibs.zinc.context import Context
from cmlibs.zinc.element import Element, Elementbasis
from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK

from cmlibs.utils.zinc.meshrefinement import MeshRefinement

here = os.path.abspath(os.path.dirname(__file__))


def _resource(name):
    return os.path.join(here, 'resources', name)


class ZincMeshRefinementTestCase(unittest.TestCase):

    def test_mesh_refinement_linear_lagrange(self):
        exf_file = _resource('warped_two_element_cube.exf')

        context = Context("test")
        source_region = context.createRegion()
        target_region = context.createRegion()
        result = source_region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        mr = MeshRefinement(source_region, target_region)

        mr.refine_all_elements_cube_standard3d(2, 3, 4)

        fm = target_region.getFieldmodule()
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mesh = fm.findMeshByDimension(3)

        self.assertEqual(105, nodes.getSize())
        self.assertEqual(48, mesh.getSize())

    def test_mesh_refinement_cubic_lagrange(self):
        exf_file = _resource('warped_two_element_cube.exf')

        context = Context("test")
        source_region = context.createRegion()
        target_region = context.createRegion()
        result = source_region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        mr = MeshRefinement(source_region, target_region, Elementbasis.FUNCTION_TYPE_CUBIC_LAGRANGE)

        mr.refine_all_elements_cube_standard3d(2, 3, 4)

        fm = target_region.getFieldmodule()
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mesh = fm.findMeshByDimension(3)

        self.assertEqual(1729, nodes.getSize())
        self.assertEqual(48, mesh.getSize())

    # def test_mesh_refinement_cubic_hermite(self):
    #     exf_file = _resource('warped_two_element_cube.exf')
    #
    #     context = Context("test")
    #     source_region = context.createRegion()
    #     target_region = context.createRegion()
    #     result = source_region.readFile(exf_file)
    #     self.assertTrue(result == RESULT_OK)
    #
    #     mr = MeshRefinement(source_region, target_region, Elementbasis.FUNCTION_TYPE_CUBIC_HERMITE)
    #
    #     mr.refine_all_elements_cube_standard3d(2, 1, 1)
    #
    #     fm = target_region.getFieldmodule()
    #     nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    #     mesh = fm.findMeshByDimension(3)
    #
    #     target_region.writeFile(_resources('refined_mesh.exf'))
    #     self.assertEqual(54, nodes.getSize())
    #     self.assertEqual(48, mesh.getSize())

    def test_mesh_refinement_quadratic_lagrange(self):
        exf_file = _resource('two_element_cube.exf')

        context = Context("test")
        source_region = context.createRegion()
        target_region = context.createRegion()
        result = source_region.readFile(exf_file)
        self.assertTrue(result == RESULT_OK)

        mr = MeshRefinement(source_region, target_region, Elementbasis.FUNCTION_TYPE_QUADRATIC_LAGRANGE)

        self.assertRaises(ValueError, mr.refine_all_elements_cube_standard3d, 4, 3, 2)


if __name__ == "__main__":
    unittest.main()
