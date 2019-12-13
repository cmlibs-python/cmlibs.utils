"""
General utilities for working with the OpenCMISS-Zinc library.
"""
from opencmiss.zinc.context import Context

class ZincCacheChanges:
    """
    Context manager for ensuring beginChange, endChange always called on
    supplied object, even with exceptions.
    Usage:
    with ZincCacheChanges(object):
        # make multiple changes to object or objects it owns
    """

    def __init__(self, object):
        """
        :param object: Zinc object with beginChange/endChange methods.
        """
        self._object = object

    def __enter__(self):
        self._object.beginChange()
        return self

    def __exit__(self, *args):
        self._object.endChange()


def defineStandardVisualisationTools(context : Context):
    glyphmodule = context.getGlyphmodule()
    glyphmodule.defineStandardGlyphs()
    materialmodule = context.getMaterialmodule()
    materialmodule.defineStandardMaterials()
