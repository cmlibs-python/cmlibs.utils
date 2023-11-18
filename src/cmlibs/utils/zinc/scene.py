"""
Utilities for working with zinc Scene including selection group.
"""
from cmlibs.zinc.glyph import Glyph
from cmlibs.zinc.graphics import Graphics

from cmlibs.utils.zinc.general import ChangeManager, HierarchicalChangeManager
from cmlibs.zinc.field import FieldGroup, Field
from cmlibs.zinc.scene import Scene
from cmlibs.zinc.region import Region

SELECTION_GROUP_NAME = '.scene_selection'


def scene_create_selection_group(scene: Scene, inherit_root_region: Region = None,
                                 subelementHandlingMode=FieldGroup.SUBELEMENT_HANDLING_MODE_FULL):
    """
    Create empty, unmanaged scene selection group of standard name.
    Should have already called scene_get_selection_group with same arguments and had None returned.
    Can discover orphaned group of standard name.
    :param scene: Zinc Scene to create selection group for.
    :param inherit_root_region: If set, find or create selection group in any ancestor up to thie region
    and return subregion group for scene's region. If not set, only create and set selection group explicitly in scene.
    :param subelementHandlingMode: Mode controlling how faces, lines and nodes are
    automatically added or removed with higher dimensional elements. Defaults to on/full.
    :return: Selection group for scene.
    """
    region = scene.getRegion()
    if inherit_root_region:
        ancestor_selection_group = scene_get_ancestor_selection_group(scene, inherit_region)
        if ancestor_selection_group:
            selection_group = ancestor_selection_group.getOrCreateSubregionFieldGroup(region)
            return selection_group
    top_region = inherit_root_region if inherit_root_region else region
    fieldmodule = top_region.getFieldmodule()
    with ChangeManager(top_region.getScene()), ChangeManager(scene), HierarchicalChangeManager(top_region):
        selection_group = fieldmodule.findFieldByName(SELECTION_GROUP_NAME)
        if selection_group.isValid():
            selection_group = selection_group.castGroup()
            assert selection_group.isValid(), "Invalid field is using reserved name '" + SELECTION_GROUP_NAME + "'"
            selection_group.clear()
            selection_group.setManaged(False)
        else:
            selection_group = fieldmodule.createFieldGroup()
            selection_group.setName(SELECTION_GROUP_NAME)
            selection_group.setSubelementHandlingMode(subelementHandlingMode)
        top_region.getScene().setSelectionField(selection_group)
        if top_region != region:
            selection_group = selection_group.getOrCreateSubregionFieldGroup(region)
    return selection_group


def scene_get_ancestor_selection_group(scene: Scene, inherit_root_region: Region = None):
    """
    Get selection group set for nearest ancestor of scene, if any.
    :param scene: Zinc Scene to get ancestroy selection group for.
    :param inherit_root_region: If set, limit ancestor to this region or below.
    :return: Existing selection FieldGroup in ancestor of scene, or None.
    """
    region = scene.getRegion()
    if region == inherit_root_region:
        return None
    ancestor_region = region.getParent()
    while ancestor_region.isValid():
        ancestor_scene = ancestor_region.getScene()
        ancestor_selection_group = ancestor_scene.getSelectionField().castGroup()
        if ancestor_selection_group.isValid():
            return ancestor_selection_group
        if ancestor_region == inherit_root_region:
            break
        ancestor_region = ancestor_region.getParent()
    return None


def scene_get_selection_group(scene: Scene, inherit_root_region: Region = None):
    """
    Get scene selection group directly set in scene or inherited from ancestor scene's selection group.
    :param scene: Zinc Scene to get existing selection group for.
    :param inherit_root_region: If set, find selection group in any ancestor up to this region
    and return subregion group for scene's region. If not set, only get selection group explicitly set in scene.
    :return: Existing selection FieldGroup in scene's region, or None.
    """
    selection_group = scene.getSelectionField().castGroup()
    if selection_group.isValid():
        return selection_group
    if inherit_root_region:
        ancestor_selection_group = scene_get_ancestor_selection_group(scene, inherit_root_region)
        if ancestor_selection_group:
            selection_group = ancestor_selection_group.getSubregionFieldGroup(scene.getRegion())
            if selection_group.isValid():
                return selection_group
    return None


def scene_get_or_create_selection_group(scene: Scene, inherit_root_region: Region = None):
    selection_group = scene_get_selection_group(scene, inherit_root_region)
    if selection_group is None:
        selection_group = scene_create_selection_group(scene, inherit_root_region)

    return selection_group


def scene_clear_selection_group(scene: Scene):
    selectionGroup = scene_get_selection_group(scene)
    if selectionGroup is not None:
        selectionGroup.clear()
        selectionGroup = Field()  # NULL
        scene.setSelectionField(selectionGroup)


def scene_create_node_derivative_graphics(scene, coordinates, node_derivative_fields, glyph_width, node_derivative_labels=None,
                                          display_node_derivatives=0, display_node_derivative_labels=None):
    """
    display_node_derivatives  # tri-state: 0=show none, 1=show selected, 2=show all
    display_node_derivative_labels # A list of derivative labels to display, 'D1', 'D2', etc.
    """
    mm = scene.getMaterialmodule()
    # names in same order as self._nodeDerivativeLabels 'D1', 'D2', 'D3', 'D12', 'D13', 'D23', 'D123' and nodeDerivativeFields

    node_derivative_material_names = ['gold', 'silver', 'green', 'cyan', 'magenta', 'yellow', 'blue']
    length_node_derivative_material_names = len(node_derivative_material_names)
    derivativeScales = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    if node_derivative_labels is None:
        node_derivative_labels = ['D1', 'D2', 'D3', 'D12', 'D13', 'D23', 'D123']

    if display_node_derivative_labels is None:
        display_node_derivative_labels = ['D1', 'D2', 'D3', 'D12', 'D13', 'D23', 'D123']

    node_derivative_graphics = []
    with ChangeManager(scene):
        for i, node_derivative_label in enumerate(node_derivative_labels):
            max_versions = len(node_derivative_fields[i])
            for v in range(max_versions):
                node_derivatives = scene.createGraphicsPoints()
                node_derivative_graphics.append(node_derivatives)
                node_derivatives.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
                node_derivatives.setCoordinateField(coordinates)
                point_attr = node_derivatives.getGraphicspointattributes()
                point_attr.setGlyphShapeType(Glyph.SHAPE_TYPE_ARROW_SOLID)
                point_attr.setOrientationScaleField(node_derivative_fields[i][v])
                point_attr.setBaseSize([0.0, glyph_width, glyph_width])
                point_attr.setScaleFactors([derivativeScales[i], 0.0, 0.0])
                if max_versions > 1:
                    point_attr.setLabelOffset([1.05, 0.0, 0.0])
                    point_attr.setLabelText(1, str(v + 1))
                material = mm.findMaterialByName(node_derivative_material_names[i % length_node_derivative_material_names])
                node_derivatives.setMaterial(material)
                node_derivatives.setSelectedMaterial(material)
                node_derivatives.setName('displayNodeDerivatives' + node_derivative_label)

                node_derivatives.setSelectMode(Graphics.SELECT_MODE_DRAW_SELECTED if (display_node_derivatives == 1) else Graphics.SELECT_MODE_ON)
                node_derivatives.setVisibilityFlag(bool(display_node_derivatives) and node_derivative_label in display_node_derivative_labels)

    return node_derivative_graphics
