import os
import unittest
from cmlibs.utils.zinc.group import group_evaluate_centroid, group_evaluate_representative_point
from cmlibs.zinc.context import Context
from cmlibs.zinc.element import Element
from cmlibs.zinc.result import RESULT_OK
from utilities import assert_almost_equal_list, get_test_resource_name


class ZincGroupTestCase(unittest.TestCase):

    def test_group_evaluate_representative_point(self):
        """
        Test creation of group fields.
        """
        context = Context("test")
        region = context.createRegion()
        exf_file_name = get_test_resource_name('quarter_tube.exf')
        self.assertEqual(RESULT_OK, region.readFile(exf_file_name))

        fieldmodule = region.getFieldmodule()
        coordinates = fieldmodule.findFieldByName("coordinates").castFiniteElement()
        self.assertTrue(coordinates.isValid())
        group = fieldmodule.findFieldByName("group1").castGroup()
        self.assertTrue(group.isValid())
        TOL = 1.0E-8

        centroid = group_evaluate_centroid(group, coordinates)
        expected_centroid = [0.2849576042633012, 0.28495760426330247, 0.5]
        assert_almost_equal_list(self, centroid, expected_centroid, delta=TOL)

        representative_point = group_evaluate_representative_point(
            group, coordinates, is_exterior=True, is_on_face=Element.FACE_TYPE_XI3_1)
        # a bit less than 0.5 * sin(45) = 0.35355339059327376, since cubic approximation
        expected_representative_point = [0.34817477, 0.34817477, 0.5]
        assert_almost_equal_list(self, representative_point, expected_representative_point, delta=TOL)

    def test_group_evaluate_representative_point_nodes(self):
        """
        Test creation of group fields.
        """
        context = Context("test")
        region = context.createRegion()
        exf_file_name = get_test_resource_name('quarter_tube.exf')
        self.assertEqual(RESULT_OK, region.readFile(exf_file_name))

        fieldmodule = region.getFieldmodule()
        mesh3d = fieldmodule.findMeshByDimension(3)
        mesh3d.destroyAllElements()
        self.assertEqual(mesh3d.getSize(), 0)

        coordinates = fieldmodule.findFieldByName("coordinates").castFiniteElement()
        self.assertTrue(coordinates.isValid())
        group = fieldmodule.findFieldByName("group1").castGroup()
        self.assertTrue(group.isValid())
        TOL = 1.0E-8

        centroid = group_evaluate_centroid(group, coordinates)
        expected_centroid = [0.225, 0.225, 0.5]
        assert_almost_equal_list(self, centroid, expected_centroid, delta=TOL)

        representative_point = group_evaluate_representative_point(
            group, coordinates, is_exterior=True, is_on_face=Element.FACE_TYPE_XI3_1)
        assert_almost_equal_list(self, representative_point, expected_centroid, delta=TOL)
