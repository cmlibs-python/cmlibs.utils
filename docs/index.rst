CMLibs Utils
============

The **CMLibs Utils** is a collection of Python utilities to support working with the Zinc library.
This package provides six modules

#. geometry.plane
#. zinc.field
#. zinc.finiteelement
#. zinc.general
#. zinc.material
#. image

These modules are surfaced under the namespace package *cmlibs* within the *utils* package.
To use these modules the following import statement can be used::

  import cmlibs.utils.geometry.plane
  import cmlibs.utils.zinc.finiteelement

Geometry
--------

The *geometry* package contains a module *plane*.
The *plane* module encapsulates describing a plane (a point and a normal vector) in a Zinc way.
It also encapsulates a way to serialise a description of a plane.

Zinc
----

The *zinc* package is made up of four modules.
The modules are aimed at raising the API level of the Zinc library making it easier to perform common tasks.
The *field* module deals with creating and querying fields.
The *finiteelement* module deals with creating finite elements.
This includes creating nodes and querying node extents.
The *general* module makes available Python Context Managers for Zinc objects that send messages.
The *material* module add functionality to create a material from an image field.

Image
-----

The *image* module contains a function for extracting the coordinates of the corners of a DICOM image.

Package API
-----------

Geometry Package
****************

Plane
+++++

.. automodule:: cmlibs.utils.geometry.plane
   :members:

Zinc Package
************

Field
+++++

.. automodule:: cmlibs.utils.zinc.field
   :members:

FiniteElement
+++++++++++++

.. automodule:: cmlibs.utils.zinc.finiteelement
   :members:

General
+++++++

.. automodule:: cmlibs.utils.zinc.general
   :members:

Material
++++++++

.. automodule:: cmlibs.utils.zinc.material
   :members:

Image Module
************

.. automodule:: cmlibs.utils.image
   :members:
