import os
import unittest
from cmlibs.utils.zinc.field import find_or_create_field_group
from cmlibs.utils.zinc.group import (
    group_add_group_local_contents, group_evaluate_centroid, group_remove_group_local_contents,
    group_evaluate_representative_point, groups_have_same_local_contents, match_fitting_group_names)
from cmlibs.zinc.context import Context
from cmlibs.zinc.element import Element
from cmlibs.zinc.field import Field
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

    def test_group_add_compare_group_local_contents(self):
        """
        Test utility functions for adding and comparing group local contents.
        """
        context = Context("test")
        region = context.createRegion()
        exf_file_name = get_test_resource_name('quarter_tube.exf')
        self.assertEqual(RESULT_OK, region.readFile(exf_file_name))

        fieldmodule = region.getFieldmodule()
        mesh3d = fieldmodule.findMeshByDimension(3)
        self.assertEqual(1, mesh3d.getSize())
        mesh2d = fieldmodule.findMeshByDimension(2)
        self.assertEqual(6, mesh2d.getSize())
        mesh1d = fieldmodule.findMeshByDimension(1)
        self.assertEqual(12, mesh1d.getSize())
        nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        self.assertEqual(8, nodes.getSize())
        datapoints = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        self.assertEqual(0, datapoints.getSize())

        group1 = fieldmodule.findFieldByName("group1").castGroup()
        self.assertTrue(group1.isValid())
        group2 = fieldmodule.createFieldGroup()
        group_add_group_local_contents(group2, group1)
        self.assertEqual(1, group2.getMeshGroup(mesh3d).getSize())
        self.assertEqual(6, group2.getMeshGroup(mesh2d).getSize())
        self.assertEqual(12, group2.getMeshGroup(mesh1d).getSize())
        self.assertEqual(8, group2.getNodesetGroup(nodes).getSize())
        self.assertTrue(groups_have_same_local_contents(group1, group2))

        group3 = fieldmodule.createFieldGroup()
        group3.createMeshGroup(mesh2d).addElement(mesh2d.findElementByIdentifier(3))
        group3.createNodesetGroup(nodes).addNode(nodes.findNodeByIdentifier(9))
        self.assertFalse(group3.isEmptyLocal())
        self.assertFalse(group3.isEmpty())
        self.assertFalse(groups_have_same_local_contents(group1, group3))
        group4 = fieldmodule.createFieldGroup()
        group_add_group_local_contents(group4, group3)
        self.assertEqual(0, group4.getMeshGroup(mesh3d).getSize())
        self.assertEqual(1, group4.getMeshGroup(mesh2d).getSize())
        self.assertEqual(0, group4.getMeshGroup(mesh1d).getSize())
        self.assertEqual(1, group4.getNodesetGroup(nodes).getSize())
        self.assertTrue(groups_have_same_local_contents(group3, group4))

        group_remove_group_local_contents(group2, group3)
        self.assertEqual(1, group2.getMeshGroup(mesh3d).getSize())
        self.assertEqual(5, group2.getMeshGroup(mesh2d).getSize())
        self.assertEqual(12, group2.getMeshGroup(mesh1d).getSize())
        self.assertEqual(7, group2.getNodesetGroup(nodes).getSize())

        group_remove_group_local_contents(group2, group1)
        self.assertEqual(0, group2.getMeshGroup(mesh3d).getSize())
        self.assertEqual(0, group2.getMeshGroup(mesh2d).getSize())
        self.assertEqual(0, group2.getMeshGroup(mesh1d).getSize())
        self.assertEqual(0, group2.getNodesetGroup(nodes).getSize())
        # check group 1 is unmodified
        self.assertEqual(1, group1.getMeshGroup(mesh3d).getSize())
        self.assertEqual(6, group1.getMeshGroup(mesh2d).getSize())
        self.assertEqual(12, group1.getMeshGroup(mesh1d).getSize())
        self.assertEqual(8, group1.getNodesetGroup(nodes).getSize())

        # test can remove group's own contents
        group_remove_group_local_contents(group1, group1)
        self.assertEqual(0, group1.getMeshGroup(mesh3d).getSize())
        self.assertEqual(0, group1.getMeshGroup(mesh2d).getSize())
        self.assertEqual(0, group1.getMeshGroup(mesh1d).getSize())
        self.assertEqual(0, group1.getNodesetGroup(nodes).getSize())


    def test_match_fitting_group_names(self):
        """
        Test utility functions for adding and comparing group local contents.
        """
        context = Context("test")
        model_region = context.createRegion()
        model_fieldmodule = model_region.getFieldmodule()
        find_or_create_field_group(model_fieldmodule, "bob", managed=True)
        find_or_create_field_group(model_fieldmodule, "fred", managed=True)
        find_or_create_field_group(model_fieldmodule, "two names", managed=True)

        data_region = context.createRegion()
        data_fieldmodule = data_region.getFieldmodule()
        data_group_bob = find_or_create_field_group(data_fieldmodule, " Bob")
        data_group_fred = find_or_create_field_group(data_fieldmodule, "  fRed\t")
        data_group_two_names = find_or_create_field_group(data_fieldmodule, "\t two NAMES  ")

        match_fitting_group_names(data_fieldmodule, model_fieldmodule, log_diagnostics=True)

        self.assertEqual(data_group_bob.getName(), "bob")
        self.assertEqual(data_group_fred.getName(), "fred")
        self.assertEqual(data_group_two_names.getName(), "two names")
